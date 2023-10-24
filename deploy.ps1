## 1. Configuration GCP

# Créer un projet sur GCP après s'être authentifié sur google DSK cli


# 1. Authentification sur google DSK cli
# gcloud auth login

# 2. Set the project's parameters
$PROJECT_ID = "zapart-data-vlille"
$PROJECT_ID

$REGION = "europe-west9"
$REGION

$BILLING_ACCOUNT_ID = "011FA7-6A223F-37D9F8"
$BILLING_ACCOUNT_ID
# You can retrieve your billing account ID by running the following command:
gcloud billing accounts list


# ================================================================================
# Service account parameters
$SERVICE_ACCOUNT = "SA-" + $PROJECT_ID
$SERVICE_ACCOUNT_EMAIL = $SERVICE_ACCOUNT + "@" + $PROJECT_ID + ".iam.gserviceaccount.com"

# Docker/GCP Authentication
# Authentication to Artifact Registry with Docker, auto-confirm
$artifact_registry_location = $REGION
gcloud auth configure-docker $artifact_registry_location-docker.pkg.dev --quiet

# Cloud functions parameters
$FUNCTION_FOLDER = "function"
$DATA_BUCKET = $PROJECT_ID + "-data"
$FUNCTION_BUCKET = $PROJECT_ID + "-function"
$DATASET_ID = "vlille_dataset"

# Flask + Docker + Cloud Run parameters
$dashboard_app_folder = "dashboard_app"
$artifact_registry_repo_name = "dashboard-vlille"
$container_name = "dashboard-container"
$dashboard_service_name = "dashboard-service"
# ================================================================================

# Création d'un nouveau projet gcloud
gcloud projects create $PROJECT_ID

# Activation du projet
gcloud config set project $PROJECT_ID

# Attribution du compte de facturation au projet
gcloud alpha billing projects link $PROJECT_ID --billing-account=$BILLING_ACCOUNT_ID

# Création d'un compte de service
gcloud iam service-accounts create $SERVICE_ACCOUNT

# Attribution des droits (bigquery admin) au compte de service
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:"$SERVICE_ACCOUNT_EMAIL --role="roles/bigquery.admin"

# Attribution des droits (storage admin) au compte de service
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:"$SERVICE_ACCOUNT_EMAIL --role="roles/storage.admin"

# Création d'une clé pour le compte de service
gcloud iam service-accounts keys create key-$PROJECT_ID.json --iam-account=$SERVICE_ACCOUNT_EMAIL
cp key-$PROJECT_ID.json $function_folder\key-$PROJECT_ID.json
cp key-$PROJECT_ID.json $dashboard_app_folder\key-$PROJECT_ID.json



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

$pythonFilePath = $FUNCTION_FOLDER + "\main.py"

# Read the content of the Python file
$content = Get-Content -Path $pythonFilePath

# Replace the specified line with the new project ID
$newContent = $content -replace 'project_name = .*', "project_name = '$PROJECT_ID'"
$newContent = $newContent -replace 'bucket_name = .*', "bucket_name = '$DATA_BUCKET'"
$newContent = $newContent -replace 'dataset_id_from_SH = .*', "dataset_id_from_SH = '$DATASET_ID'"

# Write the modified content back to the Python file
$newContent | Set-Content -Path $pythonFilePath


Compress-Archive -Path $function_folder\main.py, $function_folder\requirements.txt, $function_folder\key-vlille.json -DestinationPath cf-$PROJECT_ID.zip 

# Transfert du fichier cf-$PROJECT_ID.zip sur le bucket $FUNCTION_BUCKET
gsutil cp cf-$PROJECT_ID.zip gs://$FUNCTION_BUCKET

### 2.2. Topic Pub/Sub

# Création d'un topic Pub/Sub cf-trigger-$PROJECT_ID
gcloud pubsub topics create cf-trigger-$PROJECT_ID 

### 2.3. Job scheduler
  
# Création d'un job scheduler qui envoie un message au topic Pub/Sub cf-trigger-$PROJECT_ID toutes les minutes
gcloud scheduler jobs create pubsub cf-$PROJECT_ID-minute --schedule="* * * * *" --topic=cf-trigger-$PROJECT_ID --message-body="{Message du scheduler pubsub cf-$PROJECT_ID-minute}" --time-zone="Europe/Paris" --location=$REGION --description="Scheduler toutes les minutes" --docker-registry=artifact-registry


### 2.5. Déploiement Cloud Functions
  
# Création d'une fonction cloud qui trigge sur le topic Pub/Sub cf-trigger-$PROJECT_ID
gcloud functions deploy $PROJECT_ID-scheduled-function --region=$REGION --runtime=python311 --trigger-topic=cf-trigger-$PROJECT_ID --source=gs://$FUNCTION_BUCKET/cf-$PROJECT_ID.zip --entry-point=vlille_pubsub
# WARNING: Effective May 15, 2023, Container Registry (used by default by Cloud Functions 1st gen for storing build artifacts) is deprecated: https://cloud.google.com/artifact-registry/docs/transition/transition-from-gcr. Artifact Registry is the recommended successor that you can use by adding the '--docker_registry=artifact-registry' flag.
# WARNING: Secuirty check for Container Registry repository that stores this function's image has not succeeded. To mitigate risks of disclosing sensitive data, it is recommended to keep your repositories private. This setting can be verified in Google Container Registry.

# Logs :
# gcloud functions logs read $PROJECT_ID-scheduled-function --region=$REGION


### 3. Déploiement Flask + Docker sur Cloud Run

# modify the Dockerfile
$dockerFilePath = $dashboard_app_folder + "\Dockerfile"

# Read the content of the Dockerfile
$content = Get-Content -Path $dockerFilePath

# Replace the specified line with the new PROJECT_ID and dataset_name
# CMD ["python3", "app.py", $PROJECT_ID, $DATASET_ID]
$newLine = 'CMD ["python3", "app.py", "' + $PROJECT_ID + '", "' + $DATASET_ID + '"]'
$newContent = $content -replace 'CMD .*', $newLine

# Write the modified content back to the Dockerfile
$newContent | Set-Content -Path $dockerFilePath

# Build Docker image
docker build -t $artifact_registry_location-docker.pkg.dev/$PROJECT_ID/$artifact_registry_repo_name/$container_name $dashboard_app_folder

# Set Artifact Registry administrator permissions for the service account
# gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" --role="roles/artifactregistry.admin"

# Create a repository on Artifact Registry
gcloud artifacts repositories create $artifact_registry_repo_name --repository-format=docker --location=$artifact_registry_location --description="Dashboard V'lille"

# Push Docker to GCP Artifact Registry
docker push $artifact_registry_location-docker.pkg.dev/$PROJECT_ID/$artifact_registry_repo_name/$container_name

# Cloud Run deployment
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Granting permissions (run admin) to the service account
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" --role="roles/run.admin"

# Creating a Cloud Run service
gcloud run deploy $dashboard_service_name --image=$artifact_registry_location-docker.pkg.dev/$PROJECT_ID/$artifact_registry_repo_name/$container_name --region=$REGION --platform=managed --allow-unauthenticated

# Logs:
# gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$dashboard_service_name" --limit=10

# delete Cloud Run service
# gcloud run services delete $dashboard_service_name --region=$REGION -q

