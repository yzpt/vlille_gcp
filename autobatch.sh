<a href="https://dashboard-service-kogwvm6oba-od.a.run.app/">https://dashboard-service-kogwvm6oba-od.a.run.app/</a>

# V'lille GCP

# Collecte des données de l'<a href="https://opendata.lillemetropole.fr/explore/dataset/vlille-realtime/information/?flg=fr-fr&disjunctive.libelle&disjunctive.nom">API V'lille (Disponibilité en temps réel des stations)</a>, stockage et traitement sur GCP : Storage, Dataproc, Functions, Pub/Sub, Scheduler, BigQuery, Run + Docker.

# L'objectif de ce projet consiste à interconnecter des services GCP couramment utilisés dans le traitement de la donnée.

# <img src="./vlille_diagram_SVG.svg" alt="drawing" width="800"/>

# Ressources :
# * <a href="https://cloud.google.com/sdk/docs?hl=fr">Documentation de la CLI Google CLoud</a>
# * <a href="https://github.com/googleapis/google-cloud-python">Google Cloud Client Library for Python</a>


## 1. Configuration GCP

# Créer un projet sur GCP après s'être authentifié sur google DSK cli


# Authentification sur google DSK cli
# gcloud auth login

# $PROJECT_ID = "zapart-data-vlille"
# $SERVICE_ACCOUNT = "SA-vlille"
# $REGION = "europe-west1"
# gcloud alpha billing accounts list
# # ACCOUNT_ID            NAME                       OPEN  MASTER_ACCOUNT_ID
# # 011FA7-6A223F-37D9F8  Mon compte de facturation  True
# $BILLING_ACCOUNT_ID = "011FA7-6A223F-37D9F8"


$PROJECT_ID = "yzpt-test-2659-bis"
$SERVICE_ACCOUNT = "SA-" + $PROJECT_ID	
$REGION = "europe-west1"
# gcloud alpha billing accounts list
# ACCOUNT_ID            NAME                       OPEN  MASTER_ACCOUNT_ID
# 011FA7-6A223F-37D9F8  Mon compte de facturation  True
$BILLING_ACCOUNT_ID = "011FA7-6A223F-37D9F8"

$function_folder = "function_2"

# ================================================================================ 

$DATA_BUCKET = $PROJECT_ID + "-data"
$FUNCTION_BUCKET = $PROJECT_ID + "-function"
$DATASET_ID = "vlille_dataset"

# Création d'un nouveau projet gcloud
gcloud projects create $PROJECT_ID

# Activation du projet
gcloud config set project $PROJECT_ID

# Attribution du compte de facturation au projet
gcloud alpha billing projects link $PROJECT_ID --billing-account=$BILLING_ACCOUNT_ID

# Création d'un compte de service
gcloud iam service-accounts create $SERVICE_ACCOUNT

$SERVICE_ACCOUNT_EMAIL = $SERVICE_ACCOUNT + "@" + $PROJECT_ID + ".iam.gserviceaccount.com"

# Attribution des droits (bigquery admin) au compte de service
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:"$SERVICE_ACCOUNT_EMAIL --role="roles/bigquery.admin"

# Attribution des droits (storage admin) au compte de service
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:"$SERVICE_ACCOUNT_EMAIL --role="roles/storage.admin"

# Création d'une clé pour le compte de service
gcloud iam service-accounts keys create key-vlille.json --iam-account=$SERVICE_ACCOUNT_EMAIL

cp key-vlille.json $function_folder\key-vlille.json


## 2. Collecte et stockage des données de l'API (Functions, Pub/Sub, Scheduler), BigQuery

# Utilisation de Cloud Functions pour collecter les données de l'API V'lille et les stocker dans un bucket GCS ainsi que dans une table BigQuery, triggée chaque minute par un Pub/Sub + Scheduler.

# Activation des API : Build, Functions, Pub/Sub, Scheduler
gcloud services enable cloudbuild.googleapis.com
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable pubsub.googleapis.com
gcloud services enable cloudscheduler.googleapis.com


# Création du bucket GCS de récolte des données
gcloud storage buckets create gs://$DATA_BUCKET

# Création du bucket GCS de stockage de la fonction
gcloud storage buckets create gs://$FUNCTION_BUCKET

# Création d'un dataset BigQuery
bq mk $DATASET_ID
# Dataset 'vlille-gcp:vlille_gcp_dataset' successfully created.

# Création des tables BigQuery

# bq mk --table vlille_gcp_dataset.stations json_list_schema_stations.json
$STATIONS_TABLE = $DATASET_ID + ".stations"
bq mk --table $STATIONS_TABLE json_list_schema_stations.json
$RECORDS_TABLE = $DATASET_ID + ".records"
bq mk --table $RECORDS_TABLE json_list_schema_records.json
# delete dataset
bq rm -r -f $DATASET_ID


python create_tables.py $PROJECT_ID $DATASET_ID
    

### 2.1. Cloud Function :

$pythonFilePath = ".\function_2\main.py"

# Read the content of the Python file
$content = Get-Content -Path $pythonFilePath

# Replace the specified line with the new project ID
$newContent = $content -replace 'project_name = .*', "project_name = '$PROJECT_ID'"
$newContent = $newContent -replace 'bucket_name = .*', "bucket_name = '$DATA_BUCKET'"
$newContent = $newContent -replace 'dataset_id_from_SH = .*', "dataset_id_from_SH = '$DATASET_ID'"

# Write the modified content back to the Python file
$newContent | Set-Content -Path $pythonFilePath

$function_folder = "function_2"

Compress-Archive -Path $function_folder\main.py, $function_folder\requirements.txt, $function_folder\key-vlille.json -DestinationPath cf-$PROJECT_ID.zip 

# Transfert du fichier cf-$PROJECT_ID.zip sur le bucket $FUNCTION_BUCKET
gsutil cp cf-$PROJECT_ID.zip gs://$FUNCTION_BUCKET

### 2.2. Topic Pub/Sub

# Création d'un topic Pub/Sub cf-trigger-$PROJECT_ID
gcloud pubsub topics create cf-trigger-$PROJECT_ID 

### 2.3. Job scheduler
  
# Création d'un job scheduler qui envoie un message au topic Pub/Sub cf-trigger-$PROJECT_ID toutes les minutes
gcloud scheduler jobs create pubsub cf-$PROJECT_ID-minute --schedule="* * * * *" --topic=cf-trigger-$PROJECT_ID --message-body="{Message du scheduler pubsub cf-$PROJECT_ID-minute}" --time-zone="Europe/Paris" --location=$REGION --description="Scheduler toutes les minutes" 


### 2.5. Déploiement Cloud Functions
  
# Création d'une fonction cloud qui trigge sur le topic Pub/Sub cf-trigger-$PROJECT_ID
gcloud functions deploy $PROJECT_ID-scheduled-function --region=$REGION --runtime=python311 --trigger-topic=cf-trigger-$PROJECT_ID --source=gs://$FUNCTION_BUCKET/cf-$PROJECT_ID.zip --entry-point=vlille_pubsub

# Logs :
gcloud functions logs read $PROJECT_ID-scheduled-function --region=$REGION

