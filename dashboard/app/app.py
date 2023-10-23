from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify
from google.cloud import bigquery
import pandas as pd
import os
import requests

app = Flask(__name__)

# Configuration de BigQuery
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key-vlille-gcp.json"
client = bigquery.Client()

# Configuration de Google Maps
with open('GOOGLE_MAPS_API_KEY.txt', 'r') as f:
    GOOGLE_MAPS_API_KEY = f.read()

@app.route('/')
def index():
    stations_infos = get_realtime_data()
    general_infos = {
        "nb_available_bikes":                           sum([station["nb_available_bikes"] for station in stations_infos]),
        "nb_available_places":                          sum([station["nb_available_places"] for station in stations_infos]),
        "nb_empty_stations":                            sum([(station["nb_available_bikes"] == 0) and (station['operational_state'] == "EN SERVICE") for station in stations_infos]),
        "nb_full_stations":                             sum([(station["nb_available_places"] == 0) and (station['operational_state'] == "EN SERVICE") for station in stations_infos]),
        "nb_stations_w_n_bikes_greater_than_zero":      sum([station["nb_available_bikes"] > 0 and (station['operational_state'] == "EN SERVICE") for station in stations_infos]),
        "nb_stations_w_n_places_greater_than_zero":     sum([(station["nb_available_places"] > 0) and (station['operational_state'] == "EN SERVICE") for station in stations_infos]),
        "nb_stations_in_serice":                        sum([station["operational_state"] == "EN SERVICE" for station in stations_infos]),
        "nb_stations_in_maintenance":                   sum([station["operational_state"] == "IN_MAINTENANCE" for station in stations_infos]),
        "nb_stations_reformed":                         sum([station["operational_state"] == "RÉFORMÉ" for station in stations_infos]),        
    }
    
    timeline_sum            = sum_velos_dispos_last_24h('today')
    
    return render_template('index.html', 
                            stations_infos  =   stations_infos,
                            general_infos   =   general_infos,
                            timeline_sum = timeline_sum,
                            todays_loan_count = todays_loan_count(),
                            GOOGLE_MAPS_API_KEY = GOOGLE_MAPS_API_KEY
                           )


def get_realtime_data(station_id=None):
    response = requests.get("https://opendata.lillemetropole.fr/api/records/1.0/search/?dataset=vlille-realtime&rows=300")
    records = response.json()["records"]

    data = []
    for record in records:
        # Check if station_libelle is specified and matches the current station's libelle
        if station_id and record["fields"]["libelle"].lower() != station_id.lower():
            continue
        
        station = {}
        station["name"]                 = record["fields"]["nom"]
        station["id"]                   = record["fields"]["libelle"]
        station["adress"]               = record["fields"]["adresse"]
        station["city"]                 = record["fields"]["commune"]
        station["type"]                 = record["fields"]["type"]
        station["latitude"]             = record["fields"]["localisation"][0]
        station["longitude"]            = record["fields"]["localisation"][1]
        station["operational_state"]    = record["fields"]["etat"]
        station["nb_available_bikes"]   = record["fields"]["nbvelosdispo"]
        station["nb_available_places"]  = record["fields"]["nbplacesdispo"]
        station["connexion"]            = record["fields"]["etatconnexion"]
        station["last_update"]          = record["fields"]["datemiseajour"]
        station["record_timestamp"]     = record["record_timestamp"]
        
        data.append(station)
    
    return data

@app.route('/get_station_infos/<station_libelle>', methods=['GET'])
def get_station_infos(station_libelle):
    
    # Call the modified get_realtime_data function with the specified station_libelle
    stations_data = get_realtime_data(station_libelle=station_libelle)
    
    # Return the data as JSON
    return stations_data
    

@app.route('/get_timeline_nbvelos/<station_libelle>/<span>', methods=['GET'])
def get_timeline_nbvelos(station_libelle, span):
    
    datetime_now_ptz = (datetime.utcnow() + timedelta(hours=2))

    if span == 'today':
        start_date = datetime_now_ptz.date()
    elif span == '24h':
        start_date = (datetime_now_ptz - timedelta(hours=24))
    elif span == '7d':
        start_date = (datetime_now_ptz - timedelta(days=7)).date()

    query = f"""
            SELECT station_id, nb_velos_dispo, record_timestamp
            FROM `vlille-gcp.vlille_gcp_dataset.records`
            WHERE 
                record_timestamp >= TIMESTAMP('{start_date}')
            AND station_id = {station_libelle}
            ORDER BY record_timestamp
            """
    
    # Run the BigQuery query
    query_job = client.query(query)
    results = query_job.result()

    # Process and return the results as needed
    data = [(row.record_timestamp, row.nb_velos_dispo) for row in results]

    # Add missing rows for the missing minutes, aim: grid displaying missing when no data at HH:00 time
    df = pd.DataFrame(data, columns=['record_timestamp', 'nb_velos_dispo'])
    df['record_timestamp'] = pd.to_datetime(df['record_timestamp']).dt.strftime('%Y-%m-%d %H:%M')
    df['record_timestamp'] = pd.to_datetime(df['record_timestamp'])
    df = add_missing_rows(df, 'record_timestamp', 'nb_velos_dispo')
    
    count = 1440 - len(df)
    while count > 0:
        # add a row with timestamp+1minute, nb_velos_dispo=None
        new_row = {
            'record_timestamp': df.iloc[-1]['record_timestamp'] + timedelta(minutes=1),
            'nb_velos_dispo': None
        }

        # Concatenate the original DataFrame with the new row
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        count -= 1


    # return two list: labels and values, respectively df['record_timestamp'] and df['nb_velos_dispo']
    response_data = {
        'labels': [row for row in df['record_timestamp']],
        'values': [row for row in df['nb_velos_dispo']]
    }

    return response_data



@app.route('/get_timeline_sum/<span>', methods=['GET'])
def sum_velos_dispos_last_24h(span):
    datetime_now_ptz = (datetime.utcnow() + timedelta(hours=2))
    
    if span == 'today':
        start_date = datetime_now_ptz.date()
    elif span == '24h':
        start_date = (datetime_now_ptz - timedelta(hours=24))
    elif span == '7d':
        start_date = (datetime_now_ptz - timedelta(days=7)).date()

    query = f"""
            SELECT 
                TIMESTAMP_ADD(record_timestamp, INTERVAL 2 HOUR) AS record_timestamp_ptz,
                sum(nb_velos_dispo) AS total_velos
            FROM `vlille-gcp.vlille_gcp_dataset.records`
            WHERE 
                record_timestamp >= TIMESTAMP_SUB('{start_date}', INTERVAL 2 HOUR)
            GROUP BY record_timestamp_ptz
                HAVING total_velos > 1500 AND total_velos < 2300
            ORDER BY record_timestamp_ptz ASC;
            """
    
    # Run the BigQuery query
    query_job = client.query(query)
    results = query_job.result()

    # Process and return the results as needed
    data = [(row.record_timestamp_ptz, row.total_velos) for row in results]

    # Add missing rows for the missing minutes, aim: grid displaying missing when no data at HH:00 time
    df = pd.DataFrame(data, columns=['record_timestamp_ptz', 'total_velos'])
    df['record_timestamp_ptz'] = pd.to_datetime(df['record_timestamp_ptz']).dt.strftime('%Y-%m-%d %H:%M')
    df['record_timestamp_ptz'] = pd.to_datetime(df['record_timestamp_ptz'])
    df = add_missing_rows(df, 'record_timestamp_ptz', 'total_velos')
    
    count = 1440 - len(df)
    while count > 0:
        # add a row with timestamp+1minute, total_velos=None
        new_row = {
            'record_timestamp_ptz': df.iloc[-1]['record_timestamp_ptz'] + timedelta(minutes=1),
            'total_velos': None
        }

        # Concatenate the original DataFrame with the new row
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        count -= 1


    # return two list: labels and values, respectively df['record_timestamp_ptz'] and df['total_velos']
    response_data = {
        'labels': [row for row in df['record_timestamp_ptz']],
        'values': [row for row in df['total_velos']]
    }
    return response_data


def get_stations_pleines():
    query = f"""
            SELECT nom
            FROM `vlille-gcp.vlille_gcp_dataset.records`, `vlille-gcp.vlille_gcp_dataset.stations`
            WHERE 
                record_timestamp >= TIMESTAMP('2023-08-25') 
            AND record_timestamp <  TIMESTAMP('2023-09-26')
            AND nbvelosdispo = 0
            AND etat = "EN SERVICE"
            ORDER BY record_timestamp, nom ASC
            """
    
    # Run the BigQuery query
    query_job = client.query(query)
    results = query_job.result()

    # Process and return the results as needed
    data = [row.nom for row in results]
    return data


@app.route('/get_avg_bars/<libelle>/<week_day>', methods=['GET'])
def get_avg_bars(libelle, week_day):
    # Define the start and end dates
    start_date  = datetime(2023, 8, 25)
    end_date    = datetime.utcnow()

    # Create a list of days of the week in order
    days_of_week = {'Dimanche': 1, 'Lundi': 2, 'Mardi': 3, 'Mercredi': 4, 'Jeudi': 5, 'Vendredi': 6, 'Samedi': 7}
    day_index = days_of_week[week_day]
    print('day_index: ', day_index)

    query = f"""
    SELECT
        EXTRACT(HOUR FROM record_timestamp) AS hour_of_day,
        AVG(nb_velos_dispo) AS avg_nb_velos_dispo
    FROM
        `vlille-gcp.vlille_gcp_dataset.records`
    WHERE
        record_timestamp >= TIMESTAMP('{start_date.date()}')
        AND record_timestamp < TIMESTAMP('{end_date.date()}')
        AND station_id = {libelle}
        AND EXTRACT(DAYOFWEEK FROM record_timestamp) = {day_index}
    GROUP BY
        hour_of_day
    ORDER BY
        hour_of_day
    """
    
    # Run the BigQuery query
    query_job = client.query(query)
    results = query_job.result()
    data = [(row.hour_of_day, row.avg_nb_velos_dispo) for row in results]
    response_data = {
        'labels': [row[0] for row in data],
        'values': [row[1] for row in data]
    }
    return response_data



@app.route('/get_transactions_count', methods=['GET'])
def transactions_count():
    today = datetime.utcnow()
    query = f"""
              WITH ComparisonTable AS (
                SELECT
                    station_id,
                    TIMESTAMP_ADD(record_timestamp, INTERVAL 2 HOUR) AS date, -- Convert to Paris timezone
                    nb_velos_dispo AS nb_velos_dispo_current,
                    LAG(nb_velos_dispo, 1) OVER (PARTITION BY station_id ORDER BY record_timestamp) AS nb_velos_dispo_previous
                FROM
                    `vlille_gcp_dataset.records`
                WHERE EXTRACT(DATE FROM TIMESTAMP_ADD(record_timestamp, INTERVAL 2 HOUR)) = DATE('{today}', 'Europe/Paris') -- Paris date
                ), TransactionsTable AS (
                SELECT
                    station_id,
                    date,
                    IFNULL(nb_velos_dispo_previous, 0) - nb_velos_dispo_current AS transaction_value
                FROM
                    ComparisonTable
                WHERE
                    nb_velos_dispo_previous IS NOT NULL
                    AND (IFNULL(nb_velos_dispo_previous, 0) - nb_velos_dispo_current) <> 0
                ), RankedTransaCtions AS (
                SELECT
                    station_id, 
                    EXTRACT(HOUR FROM date) AS hour_of_day, 
                    transaction_value
                FROM
                    TransactionsTable
                )

                SELECT
                    hour_of_day,
                    SUM(IF(transaction_value > 0, transaction_value, 0)) AS sum_positive_transactions,
                    SUM(IF(transaction_value < 0, -transaction_value, 0)) AS sum_negative_transactions
                FROM
                    RankedTransactions
                GROUP BY
                    hour_of_day
                ORDER BY
                    hour_of_day;

            """
    
    # Run the BigQuery query
    query_job = client.query(query)
    results = query_job.result()

    # Process and return the results as needed
    data = [(row.hour_of_day, row.sum_positive_transactions, row.sum_negative_transactions) for row in results]
    while len(data) < 24:
        data.append((len(data), 0, 0, 0))
      
    response_data = {
        'labels': [row[0] for row in data],
        'values': [row[1] for row in data],
        'values2': [row[2] for row in data]
    }
    return (response_data)


def todays_loan_count():
    data = transactions_count()
    sum = 0
    for i in range(0, len(data['values'])):
        sum += data['values'][i] # summming only borrowed bikes
    return sum



# Add missing rows for the missing minutes, aim: grid displaying missing when no data at HH:00 time
def add_missing_rows(input_df, timestamp_column_str, value_column_str):
    new_rows = []
    for index, row in input_df.iterrows():
        if index < len(input_df) - 1:
            next_row = input_df.iloc[index + 1]
            time_diff = (next_row[timestamp_column_str] - row[timestamp_column_str]).total_seconds()
            if time_diff > 60:  # If the time difference is greater than 1 minute
                current_time = row[timestamp_column_str]
                while (current_time + timedelta(minutes=1)) < next_row[timestamp_column_str]:
                    current_time += timedelta(minutes=1)
                    new_row = {
                        timestamp_column_str: current_time,
                        value_column_str: row[value_column_str]
                    }
                    new_rows.append(new_row)
    # Create a new DataFrame with missing rows
    new_df = pd.concat([input_df, pd.DataFrame(new_rows)], ignore_index=True)
    # Sort the DataFrame by 'record_timestamp_ptz'
    new_df = new_df.sort_values(by=timestamp_column_str).reset_index(drop=True)
    return new_df


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)