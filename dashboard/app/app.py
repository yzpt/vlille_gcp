from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify
from google.cloud import bigquery
import pandas as pd
import os
import requests
import pytz

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
        "nb_velos_dispo":                   sum([station["nb_velos_dispo"] for station in stations_infos]),
        "nb_places_dispo":                  sum([station["nb_places_dispo"] for station in stations_infos]),
        "nb_stations_vides":                sum([(station["nb_velos_dispo"] == 0) and (station['etat'] == "EN SERVICE") for station in stations_infos]),
        "nb_stations_pleines":              sum([(station["nb_places_dispo"] == 0) and (station['etat'] == "EN SERVICE") for station in stations_infos]),
        "nb_stations_nbvelos_sup_to_0":     sum([station["nb_velos_dispo"] > 0 and (station['etat'] == "EN SERVICE") for station in stations_infos]),
        "nb_stations_nbplaces_sup_to_0":    sum([(station["nb_places_dispo"] > 0) and (station['etat'] == "EN SERVICE") for station in stations_infos]),
        "nb_stations_en_service":           sum([station["etat"] == "EN SERVICE" for station in stations_infos]),
        "nb_stations_en_maintenance":       sum([station["etat"] == "IN_MAINTENANCE" for station in stations_infos]),
        "nb_stations_reformees":            sum([station["etat"] == "RÉFORMÉ" for station in stations_infos]),        
        "nb_sations_connectees":            sum([station["etat_connexion"] == "CONNECTÉE" for station in stations_infos]),
        "nb_sations_deconnectees":          sum([station["etat_connexion"] == "DÉCONNECTÉ" for station in stations_infos])
    }
    # dernieres_transactions  = get_transactions()
    timeline_sum            = sum_velos_dispos_last_24h()
    stations_vides        = [{"nom": station['nom'], "nb_velos_dispo": station['nb_velos_dispo']} for station in stations_infos if station['nb_velos_dispo'] == 0 and station['etat'] == "EN SERVICE"]
    
    return render_template('index.html', 
                            stations_infos  =   stations_infos,
                            general_infos   =   general_infos,
                            # dernieres_transactions = dernieres_transactions,
                            timeline_sum = timeline_sum,
                            stations_vides = stations_vides,
                            todays_transactions_count = todays_transactions_count(),
                            GOOGLE_MAPS_API_KEY = GOOGLE_MAPS_API_KEY
                           )


def get_realtime_data(station_libelle=None):
    response = requests.get("https://opendata.lillemetropole.fr/api/records/1.0/search/?dataset=vlille-realtime&rows=300")
    records = response.json()["records"]

    data = []
    for record in records:
        # Check if station_libelle is specified and matches the current station's libelle
        if station_libelle and record["fields"]["libelle"].lower() != station_libelle.lower():
            continue
        
        station = {}
        station["nom"] = record["fields"]["nom"]
        station["libelle"] = record["fields"]["libelle"]
        station["adresse"] = record["fields"]["adresse"]
        station["commune"] = record["fields"]["commune"]
        station["type"] = record["fields"]["type"]
        station["latitude"] = record["fields"]["localisation"][0]
        station["longitude"] = record["fields"]["localisation"][1]
        station["etat"] = record["fields"]["etat"]
        station["nb_velos_dispo"] = record["fields"]["nbvelosdispo"]
        station["nb_places_dispo"] = record["fields"]["nbplacesdispo"]
        station["etat_connexion"] = record["fields"]["etatconnexion"]
        station["derniere_maj"] = record["fields"]["datemiseajour"]
        station["record_timestamp"] = record["record_timestamp"]
        data.append(station)
    
    return data

@app.route('/get_station_infos/<station_libelle>', methods=['GET'])
def get_station_infos(station_libelle):
    
    # Call the modified get_realtime_data function with the specified station_libelle
    stations_data = get_realtime_data(station_libelle=station_libelle)
    
    # Return the data as JSON
    return stations_data
    


@app.route('/get_timeline_nbvelos/<station_libelle>/<nb_days_ago>', methods=['GET'])
def get_timeline_nbvelos(station_libelle, nb_days_ago):

    # Get the current date and time
    date_inf = datetime.utcnow() - timedelta(hours=24*int(nb_days_ago))
    query = f"""
            SELECT station_id, nb_velos_dispo, record_timestamp
            FROM `vlille-gcp.vlille_gcp_dataset.records`
            WHERE 
                record_timestamp >= TIMESTAMP('{date_inf}')
            AND station_id = {station_libelle}
            ORDER BY record_timestamp
            """
    
    # Run the BigQuery query
    query_job = client.query(query)
    results = query_job.result()

    # Process and return the results as needed
    data = [(row.record_timestamp, row.nb_velos_dispo) for row in results]
    response_data = {
        'labels': [row[0] for row in data],
        'values': [row[1] for row in data]
    }
    return jsonify(response_data)



@app.route('/get_timeline_sum', methods=['GET'])
def sum_velos_dispos_last_24h():
    # twenty_four_hours_ago_datetime = datetime.utcnow() - timedelta(hours=24) 
    todays_date_ptz = datetime.utcnow().date() - timedelta(hours=2)
    query = f"""
            SELECT 
                TIMESTAMP_ADD(record_timestamp, INTERVAL 2 HOUR) AS record_timestamp_ptz,
                sum(nb_velos_dispo) AS total_velos
            FROM `vlille-gcp.vlille_gcp_dataset.records`
            WHERE 
                record_timestamp >= TIMESTAMP_SUB('{todays_date_ptz}', INTERVAL 2 HOUR)
            GROUP BY record_timestamp_ptz
                HAVING total_velos > 1500 AND total_velos < 2300
            ORDER BY record_timestamp_ptz ASC;
            """
    
    # Run the BigQuery query
    query_job = client.query(query)
    results = query_job.result()

    # Process and return the results as needed
    data = [(row.record_timestamp_ptz, row.total_velos) for row in results]

    while data[-1][0].date() < datetime.utcnow().date() + timedelta(days=1):
        data.append((data[-1][0] + timedelta(minutes=1), None))

    response_data = {
        'labels': [row[0] for row in data],
        'values': [row[1] for row in data]
    }
    # return jsonify(response_data)
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
                    EXTRACT(HOUR FROM TIMESTAMP_SUB(date, INTERVAL 2 HOUR)) AS hour_of_day, -- Convert to Paris timezone
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


def todays_transactions_count():
    data = transactions_count()
    sum = 0
    for i in range(0, len(data['values'])):
        # sum += data['values'][i] + data['values2'][i]
        sum += data['values'][i] # compte des emprunts uniquement
    return sum




@app.route('/get_nbvelosdispo', methods=['GET'])
def sum_nbvelosdispo():
    # get the today date without the hours
    today = datetime.utcnow().date()
    query = f"""
            SELECT TIMESTAMP_ADD(record_timestamp, INTERVAL 2 HOUR) AS paris_timestamp, 
                SUM(nb_velos_dispo) AS total_velos
            FROM 
                `vlille-gcp.vlille_gcp_dataset.records`
            WHERE 
                record_timestamp >= TIMESTAMP_SUB('2023-10-06', INTERVAL 2 HOUR) 
            GROUP BY 
                paris_timestamp
            HAVING 
                total_velos > 1500 AND total_velos < 2300
            ORDER BY 
                paris_timestamp ASC;
            """
    
    # Run the BigQuery query
    query_job = client.query(query)
    results = query_job.result()

    # Process and return the results as needed
    # data = [(row.datemiseajour, row.total_nbvelosdispo) for row in results]
    data = [(row.paris_timestamp, row.total_velos) for row in results if row.total_velos > 1500 and row.total_velos < 2300]
    # print('len(data):', len(data))
    # while len(data) < 1440:
    #     data.append((len(data), None))
    response_data = {
        'labels': [row[0] for row in data],
        'values': [row[1] for row in data]
    }
    return (response_data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)