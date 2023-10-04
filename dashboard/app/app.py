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
    dernieres_transactions  = get_transactions()
    timeline_sum            = sum_velos_dispos_last_24h()
    stations_vides        = [{"nom": station['nom'], "nb_velos_dispo": station['nb_velos_dispo']} for station in stations_infos if station['nb_velos_dispo'] == 0 and station['etat'] == "EN SERVICE"]
    return render_template('index.html', 
                            stations_infos  =   stations_infos,
                            general_infos   =   general_infos,
                            dernieres_transactions = dernieres_transactions,
                            timeline_sum = timeline_sum,
                            stations_vides = stations_vides,
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
    date_sup = datetime(2023, 9, 15, 12, 0)
    date_inf = twenty_four_hours_ago = date_sup - timedelta(hours=24*int(nb_days_ago))
            # FROM `vlille-396911.flask_dataset.data_rm_duplicate` 

    query = f"""
            SELECT nom, nbvelosdispo, datemiseajour
            FROM `vlille-396911.flask_dataset.data_rm_duplicate` 
            WHERE 
                datemiseajour >= TIMESTAMP('{date_inf}')
            AND datemiseajour <  TIMESTAMP('{date_sup}')
            AND libelle = {station_libelle}
            ORDER BY libelle, datemiseajour ASC
            """
    
    # Run the BigQuery query
    query_job = client.query(query)
    results = query_job.result()

    # Process and return the results as needed
    data = [(row.datemiseajour, row.nbvelosdispo) for row in results]
    response_data = {
        'labels': [row[0] for row in data],
        'values': [row[1] for row in data]
    }
    return jsonify(response_data)



def get_transactions():
    # bigquery query that list all the transactions in a table (schéma : date datetime, nom string, libelle int, value int):
    query = f"""
            WITH RankedTransactions AS (
            SELECT
                nom,
                datemiseajour AS date,
                nbvelosdispo AS nbvelosdispo_current,
                LAG(nbvelosdispo, 1) OVER (PARTITION BY nom ORDER BY datemiseajour) AS nbvelosdispo_previous
            FROM
                `vlille-396911.flask_dataset.data_rm_duplicate`
            
            WHERE datemiseajour >= '2023-09-06' and datemiseajour <'2023-09-07' 
            )

            SELECT
                nom,
                date,
                IFNULL(nbvelosdispo_previous, 0) - nbvelosdispo_current AS transaction_value
            FROM
                RankedTransactions
            WHERE
                nbvelosdispo_previous IS NOT NULL
                and (IFNULL(nbvelosdispo_previous, 0) - nbvelosdispo_current) <> 0
            ORDER BY
                date DESC
            LIMIT 5
            """
    # Run the BigQuery query
    query_job = client.query(query)
    results = query_job.result()

    # Process and return the results as needed
    data = [{
                "date": row.date.strftime("%Y-%m-%d %H:%M:%S"),
                "nom": row.nom,
                "value": row.transaction_value if row.transaction_value < 0 else "+" + str(row.transaction_value)
            } for row in results]
    return data

@app.route('/get_timeline_sum', methods=['GET'])
def sum_velos_dispos_last_24h():
    # get the datetime 24h before now
    twenty_four_hours_ago_datetime = datetime.utcnow() - timedelta(hours=24) 

    query = f"""
            SELECT record_timestamp, sum(nb_velos_dispo) AS total_velos
            FROM `vlille-gcp.vlille_gcp_dataset.records`
            WHERE 
                record_timestamp >= '{twenty_four_hours_ago_datetime}'
            GROUP BY record_timestamp
                HAVING total_velos > 1500 AND total_velos < 2300
            ORDER BY record_timestamp ASC;
            """
    
    # Run the BigQuery query
    query_job = client.query(query)
    results = query_job.result()

    # Process and return the results as needed
    data = [(row.datemiseajour, row.somme_velos) for row in results]
    response_data = {
        'labels': [row[0] for row in data],
        'values': [row[1] for row in data]
    }
    # return jsonify(response_data)
    return response_data

def get_stations_pleines():
    query = f"""
            SELECT nom, nbvelosdispo, datemiseajour
            FROM `vlille-396911.flask_dataset.data_rm_duplicate` 
            WHERE 
                datemiseajour >= TIMESTAMP('2023-08-25') 
            AND datemiseajour <  TIMESTAMP('2023-09-26')
            AND nbvelosdispo = 0
            AND etat = "EN SERVICE"
            ORDER BY nom, datemiseajour ASC
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
    start_date = pd.Timestamp('2023-08-25')
    end_date = pd.Timestamp('2023-09-15')

    # Create a list of days of the week in order
    days_of_week = {'Dimanche': 1, 'Lundi': 2, 'Mardi': 3, 'Mercredi': 4, 'Jeudi': 5, 'Vendredi': 6, 'Samedi': 7}
    day_index = days_of_week[week_day]
    print('day_index: ', day_index)

    query = f"""
    SELECT
        EXTRACT(HOUR FROM datemiseajour) AS hour_of_day,
        AVG(nbvelosdispo) AS avg_nbvelosdispo
    FROM
        `vlille-396911.flask_dataset.data_rm_duplicate`
    WHERE
        datemiseajour >= TIMESTAMP('{start_date.date()}')
        AND datemiseajour < TIMESTAMP('{end_date.date()}')
        AND libelle = {libelle}
        AND EXTRACT(DAYOFWEEK FROM datemiseajour) = {day_index}
    GROUP BY
        hour_of_day
    ORDER BY
        hour_of_day
    """
    
    # Run the BigQuery query
    query_job = client.query(query)
    results = query_job.result()

    data = [(row.hour_of_day, row.avg_nbvelosdispo) for row in results]
    response_data = {
        'labels': [row[0] for row in data],
        'values': [row[1] for row in data]
    }

    return response_data


@app.route('/get_transactions_count', methods=['GET'])
def transactions_count():
    query = f"""
              WITH RankedTransactions AS (
                SELECT
                  nom,
                  libelle,
                  EXTRACT(HOUR FROM date) AS hour_of_day,
                  transaction_value
                FROM
                  `vlille-396911.flask_dataset.transactions_test`
                WHERE
                  DATE(date) = '2023-09-12'
              )

              SELECT
                hour_of_day,
                SUM(IF(transaction_value > 0, transaction_value, 0)) AS sum_positive_transactions,
                SUM(IF(transaction_value < 0, - transaction_value, 0)) AS sum_negative_transactions
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
    response_data = {
        'labels': [row[0] for row in data],
        'values': [row[1] for row in data],
        'values2': [row[2] for row in data]
    }
    return response_data



@app.route('/get_nbvelosdispo', methods=['GET'])
def sum_nbvelosdispo():
    query = f"""
            SELECT record_timestamp, sum(nb_velos_dispo) AS total_velos
            FROM `vlille-396911.flask_dataset.data_rm_duplicate`
            WHERE 
                DATE(record_timestamp) >= '2023-08-25'
            GROUP BY record_timestamp
                HAVING total_velos > 1500 AND total_velos < 2300
            ORDER BY record_timestamp ASC;
            """
    
    # Run the BigQuery query
    query_job = client.query(query)
    results = query_job.result()

    # Process and return the results as needed
    # data = [(row.datemiseajour, row.total_nbvelosdispo) for row in results]
    data = [(row.record_timestamp, row.total_velos) for row in results if row.total_nbvelosdispo > 1500]
    response_data = {
        'labels': [row[0] for row in data],
        'values': [row[1] for row in data]
    }
    return (response_data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)