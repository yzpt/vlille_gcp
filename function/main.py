import base64
from datetime import datetime
from google.cloud import storage
from google.cloud import bigquery
import requests
import json
import pytz
import os
import sys

# Define variables for Cloud Functions
project_name = 'vlille-gcp'
bucket_name = 'vlille_gcp_data'
dataset_id = 'vlille_gcp_dataset'
table_id = 'records'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key-" + project_name + ".json"

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
    dataset_id = dataset_id
    table_id = 'records'
    table_ref = client.dataset(dataset_id).table(table_id)
    table = client.get_table(table_ref)  # API call

    data_to_insert = []
    for record in data['records']:
        row = {}
        row["station_id"]           = record["fields"]["libelle"]
        row["operational_state"]    = record["fields"]["etat"]
        row["nb_available_bikes"]   = record["fields"]["nbvelosdispo"]
        row["nb_available_places"]  = record["fields"]["nbplacesdispo"]
        row["connexion"]            = record["fields"]["etatconnexion"]
        row["last_update"]          = record["fields"]["datemiseajour"]
        row["record_timestamp"]     = record["record_timestamp"]
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
