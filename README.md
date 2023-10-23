# V'lille GCP

Collecte des données de l'<a href="https://opendata.lillemetropole.fr/explore/dataset/vlille-realtime/information/?flg=fr-fr&disjunctive.libelle&disjunctive.nom">API V'lille (Disponibilité en temps réel des stations)</a>, stockage et traitement sur GCP : Storage, Dataproc, Functions, Pub/Sub, Scheduler, BigQuery, Run + Docker.

L'objectif de ce projet consiste à interconnecter des services GCP couramment utilisés dans le traitement de la donnée.
<p>
    <img src="./vlille_diagram_SVG.svg" alt="drawing" width="800"/>
</p>

<p align="center">
    <a href="https://dashboard-service-kogwvm6oba-od.a.run.app/">
            <img src="flask_dashboard.png" alt="drawing" width="800"/>
            https://dashboard-service-kogwvm6oba-od.a.run.app/
    </a>
</p>

Ressources :
* <a href="https://cloud.google.com/sdk/docs?hl=fr">Documentation de la CLI Google CLoud</a>
* <a href="https://github.com/googleapis/google-cloud-python">Google Cloud Client Library for Python</a>


## 1. Configuration GCP

Créer un projet sur GCP après s'être authentifié sur google DSK cli

```sh 
# Création d'un nouveau projet gcloud
gcloud projects create vlille-gcp

# Liste des projets
gcloud projects list

# Activation du projet
gcloud config set project vlille-gcp

# Création d'un compte de service
gcloud iam service-accounts create admin-vlille-gcp

# Liste des comptes de services
gcloud iam service-accounts list
# admin-vlille-gcp@vlille-gcp.iam.gserviceaccount.com

# Attribution des droits (bigquery admin) au compte de service
gcloud projects add-iam-policy-binding vlille-gcp --member="serviceAccount:admin-vlille-gcp@vlille-gcp.iam.gserviceaccount.com" --role="roles/bigquery.admin"

# Attribution des droits (storage admin) au compte de service
gcloud projects add-iam-policy-binding vlille-gcp --member="serviceAccount:admin-vlille-gcp@vlille-gcp.iam.gserviceaccount.com" --role="roles/storage.admin"

# Création d'une clé pour le compte de service
gcloud iam service-accounts keys create key-vlille-gcp.json --iam-account=admin-vlille-gcp@vlille-gcp.iam.gserviceaccount.com

# Attribution du compte de facturation au projet
gcloud alpha billing accounts list
# ACCOUNT_ID            NAME                       OPEN  MASTER_ACCOUNT_ID
# 012A63-E71939-70F754  Mon compte de facturation  True
gcloud alpha billing projects link vlille-gcp --billing-account=012A63-E71939-70F754

```

## 2. Collecte et stockage des données de l'API (Functions, Pub/Sub, Scheduler), BigQuery

Utilisation de Cloud Functions pour collecter les données de l'API V'lille et les stocker dans un bucket GCS ainsi que dans une table BigQuery, triggée chaque minute par un Pub/Sub + Scheduler.

```sh
# Activation des API : Build, Functions, Pub/Sub, Scheduler
gcloud services enable cloudbuild.googleapis.com
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable pubsub.googleapis.com
gcloud services enable cloudscheduler.googleapis.com

# Création du bucket GCS de récolte des données
gcloud storage buckets create gs://vlille_gcp_data
# Création du bucket GCS de stockage de la fonction
gcloud storage buckets create gs://vlille_gcp_bucket

# Création d'un dataset BigQuery
bq mk vlille_gcp_dataset 
# Dataset 'vlille-gcp:vlille_gcp_dataset' successfully created.
```

Création des tables BigQuery

* Avec BigQuery UI :

    ```SQL
    CREATE TABLE vlille_gcp_dataset.stations (
        id INT64,
        nom STRING,
        libelle STRING,
        adresse STRING,
        commune STRING,
        type STRING,
        latitude FLOAT64,
        longitude FLOAT64
    );


    CREATE TABLE vlille_gcp_dataset.records (
        station_id INT64,
        etat STRING,
        nb_velos_dispo INT64,
        nb_places_dispo INT64,
        etat_connexion STRING,
        derniere_maj TIMESTAMP,
        record_timestamp TIMESTAMP
    );
    ```

* Ou gcloud CLI :

    On définit les schémas des tables :

    ```javascript
    // json_list_schema_stations.json
    [
        {"name": "id",       "type": "INT64"},
        {"name": "nom",      "type": "STRING"},
        {"name": "libelle",  "type": "STRING"},
        {"name": "adresse",  "type": "STRING"},
        {"name": "commune",  "type": "STRING"},
        {"name": "type",     "type": "STRING"},
        {"name": "latitude", "type": "FLOAT64"},
        {"name": "longitude","type": "FLOAT64"}
    ]

    // json_list_schema_records.json
    [
        {"name": "station_id",       "type": "INT64"},
        {"name": "etat",             "type": "STRING"},
        {"name": "nb_velos_dispo",   "type": "INT64"},
        {"name": "nb_places_dispo",  "type": "INT64"},
        {"name": "etat_connexion",   "type": "STRING"},
        {"name": "derniere_maj",     "type": "TIMESTAMP"},
        {"name": "record_timestamp", "type": "TIMESTAMP"}
    ]
    ```

    Création des tables :

    ```sh
    bq mk --table vlille_gcp_dataset.stations json_list_schema_stations.json

    bq mk --table vlille_gcp_dataset.records json_list_schema_records.json
    ```

* Ou Python client, plus pratique ensuite pour alimenter une fois la table stations :

    ```python
    from google.cloud import bigquery
    import os

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key-vlille-gcp.json"

    client = bigquery.Client()

    # Create a 'stations' table
    table_id = "vlille-gcp.vlille_gcp_dataset.stations"
    schema = [
        bigquery.SchemaField("id", "INT64"), # id = libelle
        bigquery.SchemaField("nom", "STRING"),
        bigquery.SchemaField("adresse", "STRING"),
        bigquery.SchemaField("commune", "STRING"),
        bigquery.SchemaField("type", "STRING"),
        bigquery.SchemaField("latitude", "FLOAT64"),
        bigquery.SchemaField("longitude", "FLOAT64"),
    ]
    table = bigquery.Table(table_id, schema=schema)
    table = client.create_table(table)  # Make an API request.
    print(
        "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)
    )

    # Create a 'records' table
    table_id = "vlille-gcp.vlille_gcp_dataset.records"
    schema = [
        bigquery.SchemaField("station_id", "INT64"),
        bigquery.SchemaField("etat", "STRING"),
        bigquery.SchemaField("nb_velos_dispo", "INT64"),
        bigquery.SchemaField("nb_places_dispo", "INT64"),
        bigquery.SchemaField("etat_connexion", "STRING"),
        bigquery.SchemaField("derniere_maj", "TIMESTAMP"),
        bigquery.SchemaField("record_timestamp", "TIMESTAMP"),
    ]
    table = bigquery.Table(table_id, schema=schema)
    table = client.create_table(table)  # Make an API request.
    print(
        "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)
    )

    # On alimente la table stations une fois avec une requête:
    import requests

    url = "https://opendata.lillemetropole.fr/api/records/1.0/search/?dataset=vlille-realtime&rows=300&facet=libelle&facet=nom&facet=commune&facet=etat&facet=type&facet=etatconnexion"
    response = requests.get(url)
    data = response.json()

    rows_to_insert = []
    for record in data["records"]:
        rows_to_insert.append(
            (
                record["fields"]["libelle"], # id = libelle
                record["fields"]["nom"],
                record["fields"]["adresse"],
                record["fields"]["commune"],
                record["fields"]["type"],
                record["fields"]["localisation"][0],
                record["fields"]["localisation"][1],
            )
        )
    
    table_id = "vlille-gcp.vlille_gcp_dataset.stations"
    try:
        table = client.get_table(table_id)
        client.insert_rows(table, rows_to_insert)
        print("Inserted rows.")
    except Exception as e:
        print(e)
    
    ```

### 2.1. Cloud Function : contenu et transfert du script

function/<br>
├── key-vlille-gcp.json<br>
├── requirements.txt<br>
└── main.py

* main.py

```python
import base64
from datetime import datetime
from google.cloud import storage
from google.cloud import bigquery
import requests
import json
import pytz
import os

# Define variables for Cloud Functions
bucket_name = 'vlille_gcp_data'
project_name = 'vlille-gcp'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key-vlille-gcp.json"

url = 'https://opendata.lillemetropole.fr/api/records/1.0/search/?dataset=vlille-realtime&q=&rows=300&timezone=Europe%2FParis'
paris_tz = pytz.timezone('Europe/Paris')
str_time_paris = datetime.now(paris_tz).strftime('%Y-%m-%d_%H:%M:%S')


def get_json_data(url):
    # extract data from API
    response = requests.get(url)
    return response.json()

def store_data_json_to_gcs_bucket(data, bucket_name, str_time_paris):
    # store data to GCS bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # Replace with the desired object name
    object_name = "data___" + str_time_paris + ".json"
    #  replace object_name characters ":" and "-" with "_", anticipating Spark process
    object_name = object_name.replace(":", "_").replace("-", "_")
    blob = bucket.blob(object_name)

    # Convert data to JSON string and upload to GCS
    json_data = json.dumps(data)
    blob.upload_from_string(json_data)


def insert_data_json_to_bigquery(data):
    client = bigquery.Client(project=project_name)
    dataset_id = 'vlille_gcp_dataset'
    table_id = 'records'
    table_ref = client.dataset(dataset_id).table(table_id)
    table = client.get_table(table_ref)  # API call

    data_to_insert = []
    for record in data['records']:
        row = {}
        row["station_id"] = record["fields"]["libelle"]
        row["etat"] = record["fields"]["etat"]
        row["nb_velos_dispo"] = record["fields"]["nbvelosdispo"]
        row["nb_places_dispo"] = record["fields"]["nbplacesdispo"]
        row["etat_connexion"] = record["fields"]["etatconnexion"]
        row["derniere_maj"] = record["fields"]["datemiseajour"]
        row["record_timestamp"] = record["record_timestamp"]
        data_to_insert.append(row)
    client.insert_rows(table, data_to_insert)


def vlille_pubsub(event, context):
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    print(pubsub_message)
    str_time_paris = datetime.now(paris_tz).strftime('%Y_%m_%d_%H_%M_%S')

    try:
        json_data = get_json_data(url)
        print("Data extracted from API")
    except Exception as e:
        print(e)
    
    try:
        store_data_json_to_gcs_bucket(json_data, bucket_name, str_time_paris)
        print("File uploaded to gs://" +  bucket_name + "/{}.".format("data___" + str_time_paris + ".json"))
    except Exception as e:
        print(e)

    try:
        insert_data_json_to_bigquery(json_data)
        print("Data inserted into BigQuery")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    vlille_pubsub('data', 'context')
```

Zip du dossier et transfert sur un bucket GCS :

```sh
Compress-Archive -Path function/main.py, function/requirements.txt, function/key-vlille-gcp.json -DestinationPath cloud-function-vlille-gcp.zip

# Transfert du fichier cloud-function-vlille-gcp.zip
gsutil cp cloud-function-vlille-gcp.zip gs://vlille_gcp_bucket
```

### 2.2. Topic Pub/Sub

```sh
# Création d'un topic Pub/Sub cloud-function-trigger-vlille
gcloud pubsub topics create cloud-function-trigger-vlille
```

### 2.3. Job scheduler
  
  ```sh
  # Création d'un job scheduler qui envoie un message au topic Pub/Sub cloud-function-trigger-vlille chaque minute
gcloud scheduler jobs create pubsub cf-vlille-minute --schedule="* * * * *" --topic=cloud-function-trigger-vlille --message-body="{Message du scheduler pubsub cf-vlille-minute}" --time-zone="Europe/Paris" --location=europe-west1 --description="Scheduler toutes les minutes" 

  # Déclencher manuellement le job scheduler
  gcloud scheduler jobs run cf-vlille-minute --location=europe-west1

  # Liste des jobs scheduler
  gcloud scheduler jobs list

  # Pause du job scheduler
  gcloud scheduler jobs pause cf-vlille-minute --location=europe-west1

  # Suppression du job scheduler
  gcloud scheduler jobs delete cf-vlille-minute --location=europe-west1

  ```

### 2.5. Déploiement Cloud Functions
  
```sh
# Création d'une fonction cloud qui trigge sur le topic Pub/Sub cloud-function-trigger-vlille
gcloud functions deploy vlille_scheduled_function --region=europe-west1 --runtime=python311 --trigger-topic=cloud-function-trigger-vlille --source=gs://vlille_gcp_bucket/cloud-function-vlille-gcp.zip --entry-point=vlille_pubsub

# Logs :
gcloud functions logs read vlille_scheduled_function --region=europe-west1
```

## 3. Insert raw data in BigQuery table from json files on a GCS bucket

Since august 25th 2023, the data are collected in a GCS bucket without transformation (almost raw json format as provided by the V'Lille API). We need to insert these data in the BigQuery table vlille_gcp:vlille_gcp_dataset.records

Scheme of the raw data :

* json_list_schema_raw_data.json

```javascript
[
    {"name": "nhits",    "type": "INTEGER"},
    {"name": "parameters",    "type": "RECORD",    "mode": "NULLABLE",    "fields": [
        {"name": "dataset",        "type": "STRING"},
        {"name": "timezone",        "type": "STRING"},
        {"name": "rows",        "type": "INTEGER"},
        {"name": "format",        "type": "STRING"},
        {"name": "start",        "type": "INTEGER"}
    ]},
    {"name": "records",    "type": "RECORD",    "mode": "REPEATED",    "fields": [
        {"name": "recordid",        "type": "STRING"},
        {"name": "fields",        "type": "RECORD",        "mode": "NULLABLE",        "fields": [
            {"name": "etatconnexion",            "type": "STRING"},
            {"name": "nbplacesdispo",            "type": "INTEGER"},
            {"name": "libelle",            "type": "STRING"},
            {"name": "geo",            "type": "FLOAT",            "mode": "REPEATED"},
            {"name": "etat",            "type": "STRING"},
            {"name": "datemiseajour",            "type": "TIMESTAMP"},
            {"name": "nbvelosdispo",            "type": "INTEGER"},
            {"name": "adresse",            "type": "STRING"},
            {"name": "localisation",            "type": "FLOAT",            "mode": "REPEATED"},
            {"name": "type",            "type": "STRING"},
            {"name": "nom",            "type": "STRING"},
            {"name": "commune",            "type": "STRING"}
        ]},
        {"name": "record_timestamp",        "type": "TIMESTAMP"},
        {"name": "datasetid",        "type": "STRING"},
        {"name": "geometry",        "type": "RECORD",        "mode": "NULLABLE",        "fields": [
            {"name": "type",            "type": "STRING"},
            {"name": "coordinates",            "type": "FLOAT",            "mode": "REPEATED"}
        ]}
    ]}
]
```

```sh
# GCS bucket with raw files:    gs://vlille_data_json

# Temporary raw table creation :
bq mk --table vlille_gcp_dataset.raw_records json_list_schema_raw_data.json

# load raw data from GCS bucket to BigQuery table
bq load --source_format=NEWLINE_DELIMITED_JSON vlille_gcp_dataset.raw_records gs://vlille_data_json/*.json json_list_schema_raw_data.json
```

Query to transform the raw data in the BigQuery table vlille_gcp_dataset.raw_records to the BigQuery table vlille_gcp_dataset.records_from_raw :

```SQL
CREATE OR REPLACE TABLE `vlille-gcp.vlille_gcp_dataset.records_from_raw` AS
WITH transformed_data AS (
  SELECT
    CAST(records.fields.libelle AS INT64) AS station_id,
    records.fields.etat AS etat,
    records.fields.nbvelosdispo AS nb_velos_dispo,
    records.fields.nbplacesdispo AS nb_places_dispo,
    records.fields.etatconnexion AS etat_connexion,
    TIMESTAMP(records.fields.datemiseajour) AS derniere_maj,
    TIMESTAMP(records.record_timestamp) AS record_timestamp
  FROM
    `vlille-gcp.vlille_gcp_dataset.raw_records`, UNNEST(records) AS records
)
SELECT * FROM transformed_data;


-- Query to remove all datas with: 
--     record_timestamp < 2021-08-25  (for clean data)
--     and record_timestamp >= 2021-10-04 (because the scheduled function started on the 2023-10-03's evening)

DELETE FROM `vlille-gcp.vlille_gcp_dataset.records_from_raw`
WHERE record_timestamp < TIMESTAMP('2023-08-25 00:00:00') OR record_timestamp >= TIMESTAMP('2023-10-04 00:00:00')


-- copy all rows from the temporary table records_from_raw to the table records
INSERT INTO `vlille-gcp.vlille_gcp_dataset.records` (station_id, etat, nb_velos_dispo, nb_places_dispo, etat_connexion, derniere_maj, record_timestamp)
SELECT * FROM `vlille-gcp.vlille_gcp_dataset.records_from_raw`

-- check wrong rows :
SELECT record_timestamp, COUNT( DISTINCT station_id ) AS nb
  FROM `vlille-gcp.vlille_gcp_dataset.records`
  WHERE DATE(record_timestamp) = '2023-09-10'
  GROUP BY record_timestamp
  ORDER BY nb ASC;

```

## 3. Flask dashboard (charts.js & google maps) + Docker + Cloud Run

Using :

* <a href="https://developers.google.com/maps/documentation/javascript/overview">Google API maps Javascript</a>

* <a href="https://www.chartjs.org/">Charts.js</a> to display the data from the BigQuery tables.

* <a href="https://github.com/xriley/portal-theme-bs5">Portal Bootstrap 5 Theme</a> template.

### 3.1. Flask

``` txt
dashboard_app/ 
├── static/ 
│   ├── css/ 
│   ├── js/
│   │   ├── addMarker.js    -- google maps
│   │   ├── initMap.js      -- google maps
│   │   ├── app.js          -- general js scripts
│   │   ├── display[...].js -- chart.js
│   │   └── fetch[...].js   -- chart.js
│   ├── images/ 
│   ├── plugins/ 
│   └── scss/ 
├── templates/ 
│   └── index.html          
├── app.py                  -- Flask API
├── Dockerfile 
├── GOOGLE_MAPS_API_KEY.txt 
├── key-vlille-gcp.json 
└── requirements.txt
```

app.py :

* On the entry point, we request the data from the bike sharing service API and render the dashboard's template index.html

    ```python
    from datetime import datetime, timedelta
    from flask import Flask, render_template, request, jsonify
    from google.cloud import bigquery
    import pandas as pd
    import os
    import requests

    project_id = "vlille-gcp"
    dataset_name = "vlille_gcp_dataset"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key-" + project_id + ".json"
    GOOGLE_MAPS_API_KEY = "your_google_maps_api_key"

    client = bigquery.Client()

    app = Flask(__name__)

    @app.route('/')
    def index():
        # Real-time stations infos are requested from the bike sharing service API, and stored in the variable stations_infos via the get_realtime_data call. 
        # Data is used by the google maps API for displaying markers and stations informations on the map
        stations_infos = get_realtime_data()
        
        # General stats for html displaying
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
            "todays_loan_count":                            todays_loan_count(),
        }
        
        return render_template('index.html', 
                                stations_infos  =   stations_infos,
                                general_infos   =   general_infos,
                                GOOGLE_MAPS_API_KEY = GOOGLE_MAPS_API_KEY
                            )
    ```

* get_realtime_data() : request the data from the bike sharing service API

    ```python
    def get_realtime_data(station_id=None):
        response = requests.get("https://opendata.lillemetropole.fr/api/records/1.0/search/?dataset=vlille-realtime&rows=300")
        records = response.json()["records"]

        data = []
        for record in records:
            # Check if station_id is specified and matches the current station's libelle
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
    ```

* The others endpoints request the Bigquery tables for the charts, here for example the transactions count by hour of day :

    ```python
    @app.route('/get_transactions_count', methods=['GET'])
    def transactions_count():
        today = datetime.utcnow()

        # The requets build CTEs to compare the bikes count of each stations, function of the record_timestamp, with the previous one
        # Then the transactions are calculated by substracting the current bikes count with the previous one
        # Finally, the transactions are grouped by hour of day and the sum of positive and negative transactions are calculated

        query = f"""
                WITH ComparisonTable AS (
                    SELECT
                        station_id,
                        TIMESTAMP_ADD(record_timestamp, INTERVAL 2 HOUR) AS date, -- Convert to Paris timezone
                        nb_velos_dispo AS current_bikes_count,
                        LAG(nb_velos_dispo, 1) OVER (PARTITION BY station_id ORDER BY record_timestamp) AS previous_bike_count
                    FROM
                        `{project_id}.{dataset_name}.records`
                    WHERE EXTRACT(DATE FROM TIMESTAMP_ADD(record_timestamp, INTERVAL 2 HOUR)) = DATE('{today}', 'Europe/Paris') -- Paris date
                    ), TransactionsTable AS (
                    SELECT
                        station_id,
                        date,
                        IFNULL(previous_bike_count, 0) - current_bikes_count AS transaction_value
                    FROM
                        ComparisonTable
                    WHERE
                        previous_bike_count IS NOT NULL
                        AND (IFNULL(previous_bike_count, 0) - current_bikes_count) <> 0
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
            # records_timestamp_ptz
            'labels': [row[0] for row in data],

            # count of positive transactions : bikes returned
            'values': [row[1] for row in data],

            # count of negative transactions : bikes loaned
            'values2': [row[2] for row in data]
        }
        return (response_data)
    ```

* There is a need of filling missing values for displaying timeseries charts without holes. Using pandas :

    ```python
        @app.route('/get_timeline_sum/<span>', methods=['GET'])
        def total_bikes_count(span):
            
            #       ... 
            # [BigQuery query] 
            #       ...
            
            df = pd.DataFrame(data, columns=['record_timestamp', 'total_bikes'])
            # cleaning timestamp column (remove seconds)
            df['record_timestamp'] = pd.to_datetime(df['record_timestamp']).dt.strftime('%Y-%m-%d %H:%M')
            # set timestamp as index
            df.index = pd.to_datetime(df['record_timestamp'])
            # remove duplicates
            df = df.groupby(df.index).first()
            # resample to 1min and fill missing values
            df = df.resample('1min').ffill()

            # fill missing values at the end of the day when needed (case span == 'today')
            count = 1440 - len(df)
            while count > 0:
                # add a row with timestamp+1minute, total_bikes=None
                new_row = {
                    'record_timestamp_ptz': df.iloc[-1]['record_timestamp_ptz'] + timedelta(minutes=1),
                    'total_bikes': None
                }

                # Concatenate the original DataFrame with the new row
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                count -= 1


            # return two list: labels and values, respectively df['record_timestamp_ptz'] and df['total_bikes']
            response_data = {
                'labels': [row for row in df['record_timestamp_ptz']],
                'values': [row for row in df['total_bikes']]
            }
            return response_data
    ```



### 3.1. Build du Docker Container

### 3.2. Push du Docker Container sur Artifact Registry

```sh	
# Définir les autorisations d'administrateur de l'Artifact Registry pour le compte de service
gcloud projects add-iam-policy-binding vlille-gcp --member="serviceAccount:admin-vlille-gcp@vlille-gcp.iam.gserviceaccount.com" --role="roles/artifactregistry.admin"

# création d'un dépôt sur Artifact Registry
gcloud artifacts repositories create dashboard-repo --repository-format=docker --location=europe-west9

# Authentification Docker/GCP
gcloud auth configure-docker europe-west9-docker.pkg.dev

# build du container Docker
docker build -t europe-west9-docker.pkg.dev/vlille-gcp/dashboard-repo/dashboard-container .

# Push Docker --> GCP Artifact Registry
docker push europe-west9-docker.pkg.dev/vlille-gcp/dashboard-repo/dashboard-container

```

### 3.3. Run du container

```sh
# Attribution des droits (run admin) au compte de service
gcloud projects add-iam-policy-binding vlille-gcp --member="serviceAccount:admin-vlille-gcp@vlille-gcp.iam.gserviceaccount.com" --role="roles/run.admin"

# Création d'un service Cloud Run
gcloud run deploy dashboard-service --image europe-west9-docker.pkg.dev/vlille-gcp/dashboard-repo/dashboard-container --region europe-west9 --platform managed --allow-unauthenticated

# Logs :
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=dashboard-service" 

# suppression du service Cloud Run
gcloud run services delete dashboard-service --region europe-west9 -q
```

## 4. Dataproc + PySpark

Chargement des données vers BigQuery avec Dataproc et PySpark.

<!-- <details> -->
  <!-- <summary>script PySpark : spark_gcs_to_bq_3.py</summary> -->
* Script PySpark : spark_gcs_to_bq_3.py

```python
from pyspark.sql import SparkSession

# Create a SparkSession
spark = SparkSession.builder \
    .appName("Spark SQL - vlille") \
    .config("spark.driver.maxResultSize", "10g") \
    .config("spark.driver.memory", "10g") \
    .getOrCreate()

# Define the GCS bucket and path
json_dir = "gs://vlille_sample_data_yzpt/"

# List the JSON files in the directory
json_files = spark.sparkContext.binaryFiles(json_dir + "*.json")

# Initialize a counter for processed files
processed_files = 0

# Iterate through each JSON file
for json_file in json_files.collect()[:3]:
    # Read the JSON file
    df = spark.read.json(json_file[0])
    
    # Create a view
    df.createOrReplaceTempView("vlille")
    
    # Query the view
    df = spark.sql("SELECT * FROM vlille")
    
    # Show the results (optional)
    df.show()
    
    # Write the results to a BigQuery table
    df.write \
        .format("bigquery") \
        .option("table", "vlille-396911.test_dataproc.vlille-4") \
        .option("temporaryGcsBucket", "yzpt-temp-bucket") \
        .mode("overwrite") \
        .save()
    
    # Increment the processed files counter
    processed_files += 1
    
    # Print progress information
    print(f"Processed {processed_files} files")

# Stop the session
spark.stop()
```
<!-- </details>  <br> -->

Cluster dataproc et éxécution du script :
```sh
# Création d'un cluster Dataproc : 1 master, 7 workers n1-standard-2
gcloud dataproc clusters create cluster-dataproc-vlille --region us-east1 --master-machine-type n1-standard-2 --master-boot-disk-size 50 --num-workers 7 --worker-machine-type n1-standard-2 --worker-boot-disk-size 50 --image-version 2.1-debian11 --project vlille-396911

# Transfert du script PySpark sur un bucket
gsutil cp spark_gcs_to_bq_3.py gs://allo_bucket_yzpt

# Lancement du job PySpark sur le cluster Dataproc
gcloud dataproc jobs submit pyspark gs://allo_bucket_yzpt/spark_gcs_to_bq_3.py --cluster cluster-dataproc-vlille --region us-east1 --project vlille-396911 

# Le traitement est très long (plusieurs heures) car les workers ne sont pas performants.

# Suppression du cluster
gcloud dataproc clusters delete cluster-dataproc-vlille --region us-east1 --project vlille-396911 -q
```

## 5. Chargement direct du bucket depuis BigQuery

Rapide.

```sh
# Création d'une table BigQuery
bq mk --table vlille_dataset.vlille_table_direct_from_bq

# Chargement des données récoltées dans le bucket vlille_json_data vers bigquery :
bq load --source_format=NEWLINE_DELIMITED_JSON vlille_dataset.vlille_table_direct_from_bq gs://vlille_data_json/*.json json_list_schema.json
# 16 secs (36k rows)

# l'autodetect allonge le délai de traitement : 24 secs.
bq load --source_format=NEWLINE_DELIMITED_JSON --autodetect vlille_dataset.vlille_table_direct_from_bq gs://vlille_data_json/*.json
```

## 6. Dataviz

https://pypi.org/project/flask-googlemaps/
https://github.com/topics/flask-dashboard

