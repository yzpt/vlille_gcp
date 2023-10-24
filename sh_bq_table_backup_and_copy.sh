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

# bucket copy for automation & dataproc ============================= #
gcloud config list
# gcloud auth login
# gcloud auth activate-service-account --key-file=keyfile-zapart-data-vlille.json
# ?
gcloud auth login
gcloud config set project zapart-data-vlille
gcloud config set project vlille-gcp

# login as previous account to authorize access to bucket for this account
gcloud auth login
# set user access to bucket
gsutil iam ch user:zapart.data@gmail.com:objectViewer gs://vlille_gcp_data_copy_until_2023_10_19

# login with new account
gcloud auth login
gcloud config set project zapart-data-vlille
# files list
gsutil ls gs://vlille_gcp_data_copy_until_2023_10_19
# create new bucket
gsutil mb -l europe-west1 gs://vlille_records_until_2023_10_19
# copy data from bucket to bucket
gsutil cp gs://vlille_gcp_data_copy_until_2023_10_19/records-*.csv gs://vlille_records_until_2023_10_19

# viewer role for zapart.data@gmail.com for vlille-396911.vlille_data_json created on GUI
gsutil ls gs://vlille_data_json
# json files since 2023-08-25 to today (2023-10-24)
# create new bucket
gsutil mb -l europe-west1 gs://vlille_data_json_2023_08_25_to_2023_10_24
# copy data from bucket to bucket
gsutil -m cp gs://vlille_data_json/*.json gs://vlille_data_json_2023_08_25_to_2023_10_24
# delete bucket
gsutil rm -r gs://vlille_data_json_2023_08_25_to_2023_10_24

# 










# create table in bq ================================================ #
# get the schema of records table format json list
# bq show --schema --format=prettyjson zapart-data-vlille:vlille_dataset.records > schema_records.json
# bq create table 
bq mk --table zapart-data-vlille:vlille_dataset.records_backup 
bq load --source_format=CSV --skip_leading_rows=1 --autodetect vlille_dataset.records_backup gs://vlille_gcp_data_copy_until_2023_10_19/records-*.csv 
