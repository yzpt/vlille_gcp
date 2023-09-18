# V'lille GCP

Collecte des données de l'<a href="https://opendata.lillemetropole.fr/explore/dataset/vlille-realtime/information/?flg=fr-fr&disjunctive.libelle&disjunctive.nom">API V'lille (Disponibilité en temps réel des stations)</a>, stockage et traitement sur GCP : Storage, Dataproc, Functions, Pub/Sub, Scheduler, BigQuery, Run + Docker

## 1. Configuration GCP

Créer un projet sur GCP après s'être authentifié sur google DSK cli

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

### 2.1. Cloud Function : contenu et transfert du script

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
  gcloud functions deploy allo --region=europe-west1 --runtime=python311 --trigger-topic=cloud-function-trigger-vlille --source=gs://fct_yzpt/cloud-function-vlille.zip --entry-point=vlille_pubsub
  ```

## 3. Docker Container + Cloud Run

Transfert et modification du nom des fichiers json collectés.

### 3.1. Build du Docker Container

job_load_file_on_gcs/<br>
├── Dockerfile<br>
├── requirements.txt<br>
├── key-vlille.json<br>
└── app.py

<details>
  <summary>app.py</summary>

```python
import sys
import os
from google.cloud import storage
from datetime import datetime
import pytz
from flask import Flask

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key-vlille.json"

app = Flask(__name__)

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        print(f"File {source_file_name} uploaded to {destination_blob_name} in bucket {bucket_name}")
    except Exception as e:
        print(e)

@app.route('/')
def upload_file():
    bucket_name             = "allo_bucket_yzpt"
    source_file_name        = "file_to_load.txt"
    destination_blob_name   = "loaded_file_" + datetime.now(pytz.timezone('Europe/Paris')).strftime("%Y%m%d_%H%M%S") + ".txt" 

    upload_blob(bucket_name, source_file_name, destination_blob_name)
    return "File upload complete: " + destination_blob_name

if __name__ == "__main__":
    # upload_file()
    app.run(host='0.0.0.0', port=8080)
```
</details>  <br>

```sh
# build du container Docker
docker build -t europe-west9-docker.pkg.dev/vlille-396911/gcs-copy/storage_copy_file .
```	

### 3.2. Push du Docker Container sur Artifact Registry

```sh	
# Définir les autorisations d'administrateur de l'Artifact Registry pour le compte de service
gcloud projects add-iam-policy-binding vlille-396911 --member="serviceAccount:vlille@vlille-396911.iam.gserviceaccount.com" --role="roles/artifactregistry.admin" --project=vlille-396911

# création d'un dépôt sur Artifact Registry
gcloud artifacts repositories create gcs-copy --repository-format=docker --location=europe-west9 --project=vlille-396911

# Authentification Docker/GCP
gcloud auth configure-docker europe-west9-docker.pkg.dev

# Push Docker --> GCP Artifact Registry
docker push europe-west9-docker.pkg.dev/vlille-396911/gcs-copy/storage_copy_file
```

### 3.3. Cloud Run + Docker

```sh
# Attribution des droits (run admin) au compte de service
gcloud projects add-iam-policy-binding vlille-396911 --member="serviceAccount:vlille@vlille-396911.iam.gserviceaccount.com" --role="roles/run.admin" --project=vlille-396911

# Création d'un service Cloud Run
gcloud run deploy load-file-flask --image europe-west9-docker.pkg.dev/vlille-396911/gcs-copy/load_file_flask --platform managed --region europe-west1 --project vlille-396911 --allow-unauthenticated

# Le script s'exécute sur Cloud Run après chaque requête http sur l'URL du service

# Logs :
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=load-file-flask" --project vlille-396911 --format json > logs_cloud_run.json

# suppression du service Cloud Run
gcloud run services delete load-file-flask --region europe-west1 -q
```

## 4. Dataproc + PySpark

```sh
# Création d'un cluster Dataproc : 1 master, 7 workers n1-standard-2
gcloud dataproc clusters create cluster-dataproc-vlille --region us-east1 --master-machine-type n1-standard-4 --master-boot-disk-size 50 --num-workers 7 --worker-machine-type n1-standard-2 --worker-boot-disk-size 50 --image-version 2.1-debian11 --project vlille-396911

# Transfert du script PySpark sur un bucket
gsutil cp spark_gcs_to_bq.py gs://allo_bucket_yzpt

# Lancement du job PySpark sur le cluster Dataproc
gcloud dataproc jobs submit pyspark gs://allo_bucket_yzpt/spark_gcs_to_bq.py --cluster cluster-dataproc-vlille --region us-east1 --project vlille-396911 

# Suppression du cluster
gcloud dataproc clusters delete cluster-dataproc-vlille --region us-east1 --project vlille-396911 -q
```

