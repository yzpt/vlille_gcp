gcloud auth login
# zapart.mslp

# set project
gcloud config set project vlille-gcp

# bq ls
bq ls vlille_gcp_dataset

# buckets list
gsutil ls

# create bucket, region europe-west1
gsutil mb -l europe-west1 gs://vlille_gcp_data_copy_until_2023_10_19

# copy data from bq to bucket
bq extract --destination_format=CSV vlille-gcp:vlille_gcp_dataset.records gs://vlille_gcp_data_copy_until_2023_10_19/records-*.csv

gsutil ls gs://vlille_gcp_data_copy_until_2023_10_19

gsutil iam ch serviceAccount:SA-vlille@zapart-data-vlille.iam.gserviceaccount.com:objectViewer gs://vlille_gcp_data_copy_until_2023_10_19

gcloud auth login
# zapart.data

gcloud config set project zapart-data-vlille





gsutil ls gs://vlille_gcp_data_copy_until_2023_10_19

# get keyfile for service account
gcloud iam service-accounts keys create keyfile-zapart-data-vlille.json --iam-account=SA-vlille@zapart-data-vlille.iam.gserviceaccount.com

gcloud auth activate-service-account --key-file=keyfile-zapart-data-vlille.json


# get the schema of records table format json list
# bq show --schema --format=prettyjson zapart-data-vlille:vlille_dataset.records > schema_records.json

# bq create table 
bq mk --table zapart-data-vlille:vlille_dataset.records_backup 

bq load --source_format=CSV --skip_leading_rows=1 --autodetect vlille_dataset.records_backup gs://vlille_gcp_data_copy_until_2023_10_19/records-*.csv 
