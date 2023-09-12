# Vlille - Cloud functions + Pub/Sub + Scheduler
# https://www.youtube.com/watch?v=4Uqd71SUyLM&ab_channel=Cloud4DataScience

# Configuration gcloud =============================================
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
# Attribution des droits au compte de service
gcloud projects add-iam-policy-binding vlille-396911 --member="serviceAccount:vlille@vlille-396911.iam.gserviceaccount.com" --role="roles/bigquery.admin"
gcloud projects add-iam-policy-binding vlille-396911 --member="serviceAccount:vlille@vlille-396911.iam.gserviceaccount.com" --role="roles/storage.admin"


# Création d'une clé pour le compte de service
gcloud iam service-accounts keys create key-vlille.json --iam-account=vlille@vlille-396911.iam.gserviceaccount.com

# On doit activer les API : Build, Functions, Logging, Pub/Sub
gcloud services enable cloudbuild.googleapis.com
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable pubsub.googleapis.com

# Pub/Sub  GUI =====================================================
# Création d'un topic Pub/Sub : cloud-function-trigger

# Transfert du fichier cloud-function-example.zip sur un bucket ====
# powershell command to zip the files cf-example/main.py and cf-example/requirements.txt in the root of the archive
Compress-Archive -Path cf-example/main.py,cf-example/requirements.txt -DestinationPath cloud-function-example.zip
# Création d'un bucket sur gcs
gcloud storage buckets create gs://fct_yzpt
# Transfert du fichier cloud-function-example.zip sur le bucket
gsutil cp cloud-function-example.zip gs://fct_yzpt
# Liste des fichiers du bucket fct_yzpt
gsutil ls gs://fct_yzpt

# BigQuery =========================================================
# Création d'un dataset
bq mk test

# Cloud Functions GUI ==============================================
# Création d'une fonction cloud
# Nom : cf-gui
# Génération : 1ère
# Déclencheur : Pub/Sub
# Topic : cloud-function-trigger
# Type de fonction : Zip from GCS
# Emplacement du code source : gs://fct_yzpt/cloud-function-example.zip

# Cloud scheduler GUI ==============================================
# ok tout simple

# ========================   CLI   =================================

# Pub/Sub CLI ======================================================
# Suppression d'un topic Pub/Sub cloud-function-trigger-cmd
gcloud pubsub topics delete cloud-function-trigger-cmd
# Création d'un topic Pub/Sub cloud-function-trigger-cli
gcloud pubsub topics create cloud-function-trigger-cli

# Cloud Functions CLI ==============================================
# Création d'une function
gcloud functions deploy generate-data-cli --region=europe-west1 --runtime=python37 --trigger-topic=cloud-function-trigger-cli --source=gs://fct_yzpt/cloud-function-example.zip --entry-point=hello_pubsub

# Cloud scheduler CLI ==============================================
# Création d'un job scheduler
gcloud scheduler jobs create pubsub cf-daily-cli --schedule="0 0 * * *" --topic=cloud-function-trigger-cli --message-body="{Message du scheduler}" --time-zone="Europe/Paris" --location=europe-west1

# Commande pour déclencher manuellement le scheduler
gcloud scheduler jobs run cf-daily-cli --location=europe-west1



# ===== scheduler > pub/sub > function === vlille api -> gcs bucket =====

# zip du code
Compress-Archive -Path cf_get_data_and_store_to_gcs/main.py,cf_get_data_and_store_to_gcs/requirements.txt,cf_get_data_and_store_to_gcs/key-vlille.json -DestinationPath cloud-function-vlille-api-to-gcs.zip -Force

# Transfert sur un bucket
gsutil cp cloud-function-vlille-api-to-gcs.zip gs://fct_yzpt

# Création d'un topic Pub/Sub cloud-function-trigger-vlille
gcloud pubsub topics create cloud-function-trigger-vlille

# Création d'une function
gcloud functions deploy vlille_pubsub --region=europe-west1 --runtime=python311 --trigger-topic=cloud-function-trigger-vlille --source=gs://fct_yzpt/cloud-function-vlille-api-to-gcs.zip --entry-point=vlille_pubsub

# liste des fonctions
gcloud functions list

# Création d'un job scheduler
gcloud scheduler jobs create pubsub cf-vlille-minute --schedule="* * * * *" --topic=cloud-function-trigger-vlille --message-body="{Message du scheduler pubsub cf-vlille-minute}" --time-zone="Europe/Paris" --location=europe-west1 --description="Scheduler toutes les minutes" 

# Interrompre le scheduler
gcloud scheduler jobs pause cf-vlille-minute --location=europe-west1

# Reprise du scheduler
gcloud scheduler jobs resume cf-vlille-minute --location=europe-west1

# Arrêter le scheduler
gcloud scheduler jobs delete cf-vlille-minute --location=europe-west1


# Série de cmd car je change le code main.py ========================

# Création d'un bucket sur gcs
gsutil mb gs://vlille_data_json

# main.py > bucket_name = 'vlille_data_json'

# Zip du code
Compress-Archive -Path cf_get_data_and_store_to_gcs/main.py,cf_get_data_and_store_to_gcs/requirements.txt,cf_get_data_and_store_to_gcs/key-vlille.json -DestinationPath cloud-function-vlille-api-to-gcs.zip -Force

# Transfert sur le bucket de fonctions
gsutil cp cloud-function-vlille-api-to-gcs.zip gs://fct_yzpt

# Suppression de la fonction
gcloud functions delete vlille_pubsub --region=europe-west1

# Création d'une function
gcloud functions deploy vlille_pubsub --region=europe-west1 --runtime=python311 --trigger-topic=cloud-function-trigger-vlille --source=gs://fct_yzpt/cloud-function-vlille-api-to-gcs.zip --entry-point=vlille_pubsub

# Pause du scheduler
gcloud scheduler jobs pause cf-vlille-minute --location=europe-west1

# Reprise du scheduler
gcloud scheduler jobs resume cf-vlille-minute --location=europe-west1

# Suppression des fichiers du bucket
gsutil -m rm gs://vlille_data_json/**

# liste des schedulers
gcloud scheduler jobs list --location=europe-west1

# Suppression des anciens schedulers
gcloud scheduler jobs delete cf-daily-cli --location=europe-west1
gcloud scheduler jobs delete cf-daily-gui --location=us-central1

# Informations sur le scheduler
gcloud scheduler jobs describe cf-vlille-minute --location=europe-west1


# Série de cmd : j'enlève le if __name__ == '__main__': ==============
# Création d'un bucket sur gcs
gsutil mb gs://allo_bucket_yzpt

# main.py > pas de if __name__ == '__main__':
# main.py > bucket_name = 'allo_bucket_yzpt'

# Zip du code
Compress-Archive -Path cf_get_data_and_store_to_gcs/main.py,cf_get_data_and_store_to_gcs/requirements.txt,cf_get_data_and_store_to_gcs/key-vlille.json -DestinationPath cloud-function-allo.zip -Force

# Transfert sur le bucket de fonctions
gsutil cp cloud-function-allo.zip gs://fct_yzpt

# Suppression fonction
gcloud functions delete allo --region=europe-west1

# Création d'une function
gcloud functions deploy allo --region=europe-west1 --runtime=python311 --trigger-topic=cloud-function-trigger-vlille --source=gs://fct_yzpt/cloud-function-allo.zip --entry-point=vlille_pubsub

# La fonction est triggée par le même topic que la fonction vlille_pubsub

# Suppression fonction
gcloud functions delete allo --region=europe-west1




# ===== json_data_file > bigquery ===================================

# Création d'un dataset sur bigquery
bq mk vlille_dataset
# Dataset 'vlille-396911:vlille_dataset' successfully created.

# Champs pour bigquery :
# recordid = d['records'][0]['recordid']
# record_timestamp = d['records'][0]['record_timestamp']
# geometry = str(d['records'][0]['geometry'])
# nbvelosdispo = d['records'][0]['fields']['nbvelosdispo']
# nbplacesdispo = d['records'][0]['fields']['nbplacesdispo']
# libelle = d['records'][0]['fields']['libelle']
# adresse = d['records'][0]['fields']['adresse']
# nom = d['records'][0]['fields']['nom']
# etat = d['records'][0]['fields']['etat']
# commune = d['records'][0]['fields']['commune']
# etatconnexion = d['records'][0]['fields']['etatconnexion']
# type_station = d['records'][0]['fields']['type']
# geo = d['records'][0]['fields']['geo']
# localisation = d['records'][0]['fields']['localisation']
# datemiseajour = d['records'][0]['fields']['datemiseajour']

# Création d'une table sur bigquery selon les champs cités plus haut:
bq mk --table vlille_dataset.vlille_table recordid:STRING,record_timestamp:STRING,geometry:STRING,nbvelosdispo:STRING,nbplacesdispo:STRING,libelle:STRING,adresse:STRING,nom:STRING,etat:STRING,commune:STRING,etatconnexion:STRING,type_station:STRING,geo:STRING,localisation:STRING,datemiseajour:STRING

# suppression de la table avec auto-confirmation
bq rm -f vlille_dataset.vlille_table

# liste des tables
bq ls vlille_dataset

# =============== Voir json_to_bigquery.ipynb =======================
# Redéfinir les champs de la table bigquery (interger, array, etc)
# Faire un ETL pour insérer proprement directement dans bigquery

# ajout fonction insert_json_to_bigquery dans main.py

# Zip du code
Compress-Archive -Path cf_get_data_and_store_to_gcs/main.py,cf_get_data_and_store_to_gcs/requirements.txt,cf_get_data_and_store_to_gcs/key-vlille.json -DestinationPath cloud-function-vlille-api-to-gcs-and-bigquery.zip -Force

# Transfert sur le bucket de fonctions
gsutil cp cloud-function-vlille-api-to-gcs-and-bigquery.zip gs://fct_yzpt

# Suppression fonction auto-confirmation
gcloud functions delete vlille_pubsub --region=europe-west1 -q

# Création d'une function
gcloud functions deploy vlille_pubsub --region=europe-west1 --runtime=python311 --trigger-topic=cloud-function-trigger-vlille --source=gs://fct_yzpt/cloud-function-vlille-api-to-gcs-and-bigquery.zip --entry-point=vlille_pubsub


# cli cmd to query bigquery

# github cmd to create a repo
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin

# git delete remote
git remote rm origin



# dataproc bucket --> bigquery ======================================

# activation api dataproc
gcloud services enable dataproc.googleapis.com --project=vlille-396911

# création d'un cluster dataproc
gcloud dataproc clusters create cluster-dataproc-vlille --region us-east1 --master-machine-type n1-standard-2 --master-boot-disk-size 50 --num-workers 2 --worker-machine-type n1-standard-2 --worker-boot-disk-size 50 --image-version 2.1-debian11 --project vlille-396911

# bucket GCS pour stocker le script spark
gsutil mb -p vlille-396911 gs://vlille-spark-yzpt

# job spark --> spark_gcs_to_bq.py

# transfert du script spark sur le bucket
gsutil cp spark_gcs_to_bq.py gs://vlille-spark-yzpt

# lancement du job spark
gcloud dataproc jobs submit pyspark gs://vlille-spark-yzpt/spark_gcs_to_bq.py --cluster cluster-dataproc-vlille --region us-east1 --project vlille-396911

# erreur visiblement à cause du timestamp dans le nom des fichiers json

# gcs create a bucket
gsutil mb gs://vlille_data_json_copy

# gcs copy a entire bucket to another bucket
gsutil -m cp -r gs://vlille_data_json gs://vlille_data_json_copy

# try avec un seul fichier au nom modifié :
#  gs://vlille_data_json_copy/vlille_data_json/data___2023_08_25_03_34_00.json
# job spark_gcs_to_bq.py > df = spark.read.json("gs://vlille_data_json_copy/vlille_data_json/data___2023_08_25_03_34_00.json")

# transfert du script spark sur le bucket
gsutil cp spark_gcs_to_bq.py gs://vlille-spark-yzpt

# temp bucket needed pour spark job
gsutil mb -l europe-west1 gs://yzpt-temp-bucket

# lancement du job spark
gcloud dataproc jobs submit pyspark gs://vlille-spark-yzpt/spark_gcs_to_bq.py --cluster cluster-dataproc-vlille --region us-east1 --project vlille-396911

# ça marche, effectivement timestamp dans le nom fait chier

# tâche secondaire : renommer l'ensemble des fichiers json dans le bucket gs://vlille_data_json en remplaçant les caractères spéciaux ":" du timestamp par des "_"
# le nombre de fichier est trop grand pour utilser gsutil
# --> dataflow

# Dataflow ===================================================

# activation api dataflow
gcloud services enable dataflow.googleapis.com --project=vlille-396911

# cli to create a new bucket
gsutil mb gs://vlille_data_json_renamed

# installer apache beam avec les dépandances pour gcp
!pip install apache_beam[gcp]
# Pourquoi ? le script est censé tourner sur gcp ...

# job dataflow --> dataflow_rename_files.py
# transfert du script sur le bucket allo_bucket_yzpt
gsutil cp dataflow_rename_files.py gs://allo_bucket_yzpt
# path : 
gs://allo_bucket_yzpt/dataflow_rename_files.py

# putain le gros bordel de dataflow