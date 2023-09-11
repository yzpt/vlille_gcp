import base64
from datetime import datetime
import pandas as pd
from google.cloud import storage
from google.cloud import bigquery
import requests
import json
import time
import pytz
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key-vlille.json"
url = 'https://opendata.lillemetropole.fr/api/records/1.0/search/?dataset=vlille-realtime&q=&rows=300&timezone=Europe%2FParis'
paris_tz = pytz.timezone('Europe/Paris')
str_time_paris = datetime.now(paris_tz).strftime('%Y-%m-%d_%H:%M:%S')

# Define variables for Cloud Functions
bucket_name = 'vlille_data_json'
project_name = 'vlille-396911'

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
    blob = bucket.blob(object_name)

    # Convert data to JSON string and upload to GCS
    json_data = json.dumps(data)
    blob.upload_from_string(json_data)


def insert_data_json_to_bigquery(data):
    client = bigquery.Client(project=project_name)
    dataset_id = 'vlille_dataset'
    table_id = 'vlille_table'
    table_ref = client.dataset(dataset_id).table(table_id)
    table = client.get_table(table_ref)  # API call

    data_to_insert = []
    for record in data['records']:
        row = {
            "recordid": record['recordid'],
            "record_timestamp": record['record_timestamp'],
            "nbvelosdispo": record['fields']['nbvelosdispo'],
            "nbplacesdispo": record['fields']['nbplacesdispo'],
            "libelle": record['fields']['libelle'],
            "adresse": record['fields']['adresse'],
            "nom": record['fields']['nom'],
            "etat": record['fields']['etat'],
            "commune": record['fields']['commune'],
            "etatconnexion": record['fields']['etatconnexion'],
            "type": record['fields']['type'],
            "longitude": record['fields']['localisation'][0],
            "latitude": record['fields']['localisation'][1],
            "datemiseajour": record['fields']['datemiseajour']
        }
        data_to_insert.append(row)
    client.insert_rows(table, data_to_insert)


def vlille_pubsub(event, context):
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    print(pubsub_message)
    str_time_paris = datetime.now(paris_tz).strftime('%Y-%m-%d_%H:%M:%S')
    
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
