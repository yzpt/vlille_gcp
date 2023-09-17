# V'lille GCP

## Titre 2

### Titre 3

Collecte des données de l'<a href="https://opendata.lillemetropole.fr/explore/dataset/vlille-realtime/information/?flg=fr-fr&disjunctive.libelle&disjunctive.nom">API V'lille (Disponibilité en temps réel des stations)</a>, stockage et traitement sur GCP : Storage, Dataproc, Functions, Pub/Sub, Scheduler, BigQuery, Run + Docker

## 1. Configuration GCP

### 1. Création du projet

Créer un projet sur GCP après s'être authentifié.

```sh 
# Création d'un nouveau projet gcloud
gcloud projects create vlille

# Liste des projets
gcloud projects list

# Activation du projet
gcloud config set project vlille-396911

# Création d'un compte de service
gcloud iam service-accounts create vlille

# Liste des comptes de services
gcloud iam service-accounts list
# vlille@vlille-396911.iam.gserviceaccount.com

# Attribution des droits (bigquery admin) au compte de service
gcloud projects add-iam-policy-binding vlille-396911 --member="serviceAccount:vlille@vlille-396911.iam.gserviceaccount.com" --role="roles/bigquery.admin"

# Attribution des droits (storage admin) au compte de service
gcloud projects add-iam-policy-binding vlille-396911 --member="serviceAccount:vlille@vlille-396911.iam.gserviceaccount.com" --role="roles/storage.admin"

# Création d'une clé pour le compte de service
gcloud iam service-accounts keys create key-vlille.json --iam-account=vlille@vlille-396911.iam.gserviceaccount.com
```

## 2. Collecte et stockage des données de l'API (Functions, Pub/Sub, Scheduler), BigQuery

Utilisation de Cloud Functions pour collecter les données de l'API V'lille et les stocker dans un bucket GCS ainsi que dans une table BigQuery, triggée chaque minute par un Pub/Sub + Scheduler.

```sh
# Activation des API : Build, Functions, Pub/Sub
gcloud services enable cloudbuild.googleapis.com
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable pubsub.googleapis.com

# Création du bucket GCS de récolte des données
gcloud storage buckets create gs://vlille_data_json
# Création du bucket GCS de stockage de la fonction
gcloud storage buckets create gs://fct_yzpt 
```

A refaire automatiquement avec le schéma d'un fichier json de l'API V'lille

``` sh
# Création d'un dataset BigQuery
bq mk vlille_dataset
# Dataset 'vlille-396911:vlille_dataset' successfully created.
# Création d'une table BigQuery
bq mk --table vlille_dataset.vlille_table \
  recordid:STRING, \
  record_timestamp:STRING, \
  geometry:STRING, \
  nbvelosdispo:STRING, \
  ...
```

#### 2.1. Contenu et transfert des fichiers de la fonction

cf_get_data_and_store_to_gcs/<br>
├── key-vlille.json<br>
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

  ```

Zip du dossier et transfert sur un bucket GCS :

```sh
Compress-Archive -Path cf-example/main.py,cf-example/requirements.txt -DestinationPath cloud-function-vlille.zip

# Création d'un bucket sur gcs
gcloud storage buckets create gs://fct_yzpt

# Transfert du fichier cloud-function-vlille.zip sur le bucket
gsutil cp cloud-function-vlille.zip gs://fct_yzpt
```

#### 2.2. Création d'un topic Pub/Sub

```sh
# Création d'un topic Pub/Sub cloud-function-trigger-vlille
gcloud pubsub topics create cloud-function-trigger-vlille
```

#### 2.3. Création d'un job scheduler
  
  ```sh
  # Création d'un job scheduler qui envoie un message au topic Pub/Sub cloud-function-trigger-vlille toutes les minutes
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

#### 2.5. Déploiement de la fonction
  
  ```sh
  # Création d'une fonction cloud qui trigge sur le topic Pub/Sub cloud-function-trigger-vlille
  gcloud functions deploy allo --region=europe-west1 --runtime=python311 --trigger-topic=cloud-function-trigger-vlille --source=gs://fct_yzpt/cloud-function-vlille.zip --entry-point=vlille_pubsub
  ```

## 3. Docker Container + Compute Engine

Transfert et modification du nom des fichiers json collectés.

#### 3.1. Build du Docker Container

docker_storage_copy_files/<br>
├── Dockerfile<br>
├── requirements.txt<br>
└── storage_copy_file.py

    ```python
    import sys
import os
from google.cloud import storage

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key-vlille.json"

def copy_blob(bucket_name, blob_name, destination_bucket_name, destination_blob_name):
    storage_client = storage.Client()

    source_bucket = storage_client.bucket(bucket_name)
    source_blob = source_bucket.blob(blob_name)
    
    destination_bucket = storage_client.bucket(destination_bucket_name)
    destination_generation_match_precondition = 0

    source_bucket.copy_blob(source_blob, destination_bucket, destination_blob_name, if_generation_match=destination_generation_match_precondition)

def copy_all_files(bucket_name, destination_bucket_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blobs = list(bucket.list_blobs())[:100]
    print(len(list(blobs)), ' files to copy')
    for i,blob in enumerate(blobs):
        new_name = blob.name.replace(":","_").replace("-","_")
        copy_blob(bucket_name=bucket_name, blob_name=blob.name, destination_bucket_name=destination_bucket_name, destination_blob_name=new_name)
        print(f"Blob {blob.name} has been copied to {new_name} in bucket {destination_bucket_name}")

def create_new_bucket(bucket_name):
    storage_client = storage.Client()
    bucket = storage_client.create_bucket(bucket_name)
    print("Bucket {} created".format(bucket.name))

def delete_bucket(bucket_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    bucket.delete()
    print("Bucket {} deleted".format(bucket.name))

if __name__ == "__main__":
    create_new_bucket('vlille_sample_data_yzpt')
    copy_all_files('vlille_data_json', 'vlille_sample_data_yzpt')

    ```

