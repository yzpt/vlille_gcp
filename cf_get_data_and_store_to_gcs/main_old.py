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

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keyfile.json"
url = 'https://opendata.lillemetropole.fr/api/records/1.0/search/?dataset=vlille-realtime&q=&rows=300&timezone=Europe%2FParis'
paris_tz = pytz.timezone('Europe/Paris')
str_time_paris = datetime.now(paris_tz).strftime('%Y-%m-%d_%H:%M:%S')

# Define variables for Cloud Functions
bucket_name = 'fct_yzpt'
project_name = 'vlille-396911'
dataset_name = 'test'
table_name = 'example_data'

def get_data_and_store_to_gcs_bucket(url, bucket_name):
    # extract data from API
    response = requests.get(url)
    data = response.json()

    # store data to GCS bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # Replace with the desired object name
    object_name = "data___" + str_time_paris + ".json"
    blob = bucket.blob(object_name)

    # Convert data to JSON string and upload to GCS
    json_data = json.dumps(data)
    blob.upload_from_string(json_data)



def generate_data():
     # Generate data
     timestamps = [datetime.datetime.now() for i in range(5)]
     strings = ['foo', 'bar', 'baz', 'qux', 'quux']
     numbers = [10, 20, 30, 40, 50]

     # Create a dictionary with keys 'Timestamp', 'String', and 'Number' and the corresponding lists as its values
     data = {'Timestamp': timestamps,'String': strings, 'Number': numbers}

     # Create a pandas DataFrame from the dictionary
     df = pd.DataFrame(data)

     # Convert the DataFrame to a CSV string
     csv_string = df.to_csv(index=False)

     # Get the current time
     today = datetime.datetime.now().strftime('%Y-%m-%d')

     # Upload CSV file to Cloud Storage
     client = storage.Client()
     bucket = client.get_bucket(bucket_name)
     blob = bucket.blob(f'cloud_function_data/example_data_{today}.csv')
     blob.upload_from_string(csv_string)

     # Upload the CSV file from Cloud Storage to BigQuery
     client = bigquery.Client()
     table_id = project_name + '.' + dataset_name + '.' + table_name
     job_config = bigquery.LoadJobConfig(
          autodetect=True,
          source_format=bigquery.SourceFormat.CSV,
          write_disposition='WRITE_TRUNCATE'
     )
     uri = f"gs://{bucket_name}/{blob.name}"
     load_job = client.load_table_from_uri(
          uri, table_id, job_config=job_config
     )  
     load_job.result()  

     # Make an API request and display number of loaded rows
     destination_table = client.get_table(table_id) 
     print("Loaded {} rows.".format(destination_table.num_rows))

def hello_pubsub(event, context):
     pubsub_message = base64.b64decode(event['data']).decode('utf-8')
     print(pubsub_message)
     # generate_data()
     str_time_paris = datetime.now(paris_tz).strftime('%Y-%m-%d_%H:%M:%S')

     try:
          get_data_and_store_to_gcs_bucket(url, bucket_name)
          print("File uploaded to gs://" +  bucket_name + "/{}.".format("data___" + str_time_paris + ".json"))
     except Exception as e:
          print(e)



if __name__ == "__main__":
     hello_pubsub('data', 'context')



