#!/bin/bash

# ======================================================== #
#                      WORK IN PROGRESS                    #
# ======================================================== #

# 1. Authentification sur google DSK cli
# gcloud auth login

# 2. Set the project's parameters
PROJECT_ID="zapart-data-vlille"
echo "project_id: "$PROJECT_ID

REGION="europe-west9"
echo "region: "$REGION

# You can retrieve your billing account ID by running the following command:
# gcloud billing accounts list
BILLING_ACCOUNT_ID="011FA7-6A223F-37D9F8"
echo "billing_account_id: "$BILLING_ACCOUNT_ID


# ================================================================================
# Service account parameters
SERVICE_ACCOUNT="SA-"$PROJECT_ID
echo "service_account: "$SERVICE_ACCOUNT
SERVICE_ACCOUNT_EMAIL=$SERVICE_ACCOUNT"@"$PROJECT_ID".iam.gserviceaccount.com"
echo "service_account_email: "$SERVICE_ACCOUNT_EMAIL

# Docker/GCP Authentication
# Authentication to Artifact Registry with Docker, auto-confirm
ARTIFACT_REGISTRY_LOCATION=$REGION
gcloud auth configure-docker $ARTIFACT_REGISTRY_LOCATION-docker.pkg.dev --quiet

# Cloud functions parameters
FUNCTION_FOLDER="function"
DATA_BUCKET=$PROJECT_ID + "-data"
FUNCTION_BUCKET=$PROJECT_ID"-function"
DATASET_ID="vlille_dataset"

# Flask + Docker + Cloud Run parameters
DASHBOARD_APP_FOLDER="dashboard_app"
ARTIFACT_REGISTRY_REPO_NAME="dashboard-vlille"
CONTAINER_NAME="dashboard-container"
DASHBOARD_SERVICE_NAME="dashboard-service"
# ================================================================================

# Create new gcloud project
gcloud projects create $PROJECT_ID

# Activation 
gcloud config set project $PROJECT_ID

# Attribution du compte de facturation au projet
gcloud alpha billing projects link $PROJECT_ID --billing-account=$BILLING_ACCOUNT_ID

# Création d'un compte de service
gcloud iam service-accounts create $SERVICE_ACCOUNT

# Attribution des droits (bigquery admin) au compte de service
gcloud projects add-iam-policy-binding \
    $PROJECT_ID \
    --member="serviceAccount:"$SERVICE_ACCOUNT_EMAIL \
    --role="roles/bigquery.admin"

# Attribution des droits (storage admin) au compte de service
gcloud projects add-iam-policy-binding \
    $PROJECT_ID \
    --member="serviceAccount:"$SERVICE_ACCOUNT_EMAIL \
    --role="roles/storage.admin"

# Création d'une clé pour le compte de service
gcloud iam service-accounts keys create key-$PROJECT_ID.json --iam-account=$SERVICE_ACCOUNT_EMAIL
cp key-$PROJECT_ID.json $FUNCTION_FOLDER\key-$PROJECT_ID.json
cp key-$PROJECT_ID.json $DASHBOARD_APP_FOLDER\key-$PROJECT_ID.json



## 2. Collecte et stockage des données de l'API (Functions, Pub/Sub, Scheduler), BigQuery

# Utilisation de Cloud Functions pour collecter les données de l'API V'lille et les stocker dans un bucket GCS ainsi que dans une table BigQuery, triggée chaque minute par un Pub/Sub + Scheduler.
# Enabling APIs: Build, Functions, Pub/Sub, Scheduler
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

# Création des tables BigQuery
python create_tables.py $PROJECT_ID $DATASET_ID
    

### 2.1. Cloud Function :

PYTHON_FILE_PATH=$FUNCTION_FOLDER + "\main.py"

# Read the content of the Python file
CONTENT=Get-Content -Path $PYTHON_FILE_PATH

# Replace the specified line with the new project ID
NEW_CONTENT = $CONTENT   -replace 'project_name = .*', "project_name = '$PROJECT_ID'"
NEW_CONTENT = $NEW_CONTENT -replace 'bucket_name = .*', "bucket_name = '$DATA_BUCKET'"
NEW_CONTENT = $NEW_CONTENT -replace 'dataset_id_from_SH = .*', "dataset_id_from_SH = '$DATASET_ID'"

# Write the modified content back to the Python file
$NEW_CONTENT | Set-Content -Path $PYTHON_FILE_PATH

FUNCTION_FOLDER="function"
PROJECT_ID="allooo"

zip -r cf-$PROJECT_ID.zip \
    $FUNCTION_FOLDER/main.py \
    $FUNCTION_FOLDER/requirements.txt \
    $FUNCTION_FOLDER/key-$PROJECT_ID.json

# Transfert du fichier cf-$PROJECT_ID.zip sur le bucket $FUNCTION_BUCKET
gsutil cp cf-$PROJECT_ID.zip gs://$FUNCTION_BUCKET

### 2.2. Topic Pub/Sub

# Création d'un topic Pub/Sub cf-trigger-$PROJECT_ID
gcloud pubsub topics create cf-trigger-$PROJECT_ID 

### 2.3. Job scheduler
  
# Création d'un job scheduler qui envoie un message au topic Pub/Sub cf-trigger-$PROJECT_ID toutes les minutes
gcloud scheduler jobs create pubsub cf-$PROJECT_ID-minute --schedule="* * * * *" --topic=cf-trigger-$PROJECT_ID --message-body="{Message dfrom scheduler pubsub cf-$PROJECT_ID-minute}" --time-zone="Europe/Paris" --location=$REGION --description="Scheduler every minutes" --docker-registry=artifact-registry


### 2.5. Déploiement Cloud Functions
  
# Création d'une fonction cloud qui trigge sur le topic Pub/Sub cf-trigger-$PROJECT_ID
gcloud functions deploy $PROJECT_ID-scheduled-function --region=$REGION --runtime=python311 --trigger-topic=cf-trigger-$PROJECT_ID --source=gs://$FUNCTION_BUCKET/cf-$PROJECT_ID.zip --entry-point=vlille_pubsub
# WARNING: Effective May 15, 2023, Container Registry (used by default by Cloud Functions 1st gen for storing build artifacts) is deprecated: https://cloud.google.com/artifact-registry/docs/transition/transition-from-gcr. Artifact Registry is the recommended successor that you can use by adding the '--docker_registry=artifact-registry' flag.
# WARNING: Secuirty check for Container Registry repository that stores this function's image has not succeeded. To mitigate risks of disclosing sensitive data, it is recommended to keep your repositories private. This setting can be verified in Google Container Registry.

# Logs :
# gcloud functions logs read $PROJECT_ID-scheduled-function --region=$REGION


### 3. Déploiement Flask + Docker sur Cloud Run

# modify the Dockerfile
DOCKER_FILE_PATH=$DASHBOARD_APP_FOLDER"\Dockerfile"

# Read the content of the Dockerfile
CONTENT=Get-Content -Path $DOCKER_FILE_PATH

# Replace the specified line with the new PROJECT_ID and dataset_name
# CMD ["python3", "app.py", $PROJECT_ID, $DATASET_ID]
NEW_LINE='CMD ["python3", "app.py", "' + $PROJECT_ID + '", "' + $DATASET_ID + '"]'
NEW_CONTENT=$CONTENT -replace 'CMD .*', $NEW_LINE

# Write the modified content back to the Dockerfile
$NEW_CONTENT | Set-Content -Path $DOCKER_FILE_PATH

# Build Docker image
docker build -t \
    $ARTIFACT_REGISTRY_LOCATION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REGISTRY_REPO_NAME/$CONTAINER_NAME \
    $DASHBOARD_APP_FOLDER

# Set Artifact Registry administrator permissions for the service account
gcloud projects add-iam-policy-binding \
    $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/artifactregistry.admin"

# Create a repository on Artifact Registry
gcloud artifacts repositories create \
    $ARTIFACT_REGISTRY_REPO_NAME \
    --repository-format=docker \
    --location=$ARTIFACT_REGISTRY_LOCATION \
    --description="Dashboard V'lille"

# Push Docker to GCP Artifact Registry
docker push $ARTIFACT_REGISTRY_LOCATION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REGISTRY_REPO_NAME/$CONTAINER_NAME

# Cloud Run deployment
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Granting permissions (run admin) to the service account
gcloud projects add-iam-policy-binding \
    $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/run.admin"

# Creating a Cloud Run service
gcloud run deploy \
    $DASHBOARD_SERVICE_NAME \
    --image=$ARTIFACT_REGISTRY_LOCATION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REGISTRY_REPO_NAME/$CONTAINER_NAME \
    --region=$REGION \
    --platform=managed \
    --allow-unauthenticated

# Logs:
# gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$DASHBOARD_SERVICE_NAME" --limit=10

# delete Cloud Run service
# gcloud run services delete $DASHBOARD_SERVICE_NAME --region=$REGION -q

