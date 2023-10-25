# GCS bucket with viewer role for the current service account:
$raw_json_files_bucket = 'gs://vlille_data_json'

# BigQuery variables:
$project_id                                 = 'vlille-gcp'
$key_file_path                              = 'key-vlille-gcp.json'
$dataset_name                               = 'vlille_dataset'
$raw_records_table_name                     = "raw_records"
$transformed_records_from_raw_table_name    = "transformed_records_from_raw_records"
$records_table_name                         = "records" # /!\ production table /!\
$date_inf                                   = "2023-08-25 00:00:00"
$date_sup                                   = "2023-10-04 00:00:00"

# Temporary tables creation :
bq mk --table $dataset_name"."$raw_records_table_name json_list_schema_raw_data.json
bq mk --table $dataset_name"."$transformed_records_from_raw_table_name json_list_schema_records

# load raw data from GCS bucket to BigQuery raw_records table
bq load --source_format=NEWLINE_DELIMITED_JSON $dataset_name"."$raw_records_table_name gs://vlille_data_json/*.json json_list_schema_raw_data.json
# taking almot 150 seconds for 2 months of data (august 25th to october 24th 2023)

# run python job:
# Usage: python bq_loading_raw_json_files.py <project-id> <key-file-path> <dataset-name> <raw_records_table_name> <transformed_records_from_raw_table_name> <records_table_name>
python bq_loading_raw_json_files.py $project_id $key_file_path $dataset_name $raw_records_table_name $transformed_records_from_raw_table_name $records_table_name $date_inf $date_sup

# delete the temporary tables
bq rm -f -t $dataset_name"."$raw_records_table_name
bq rm -f -t $dataset_name"."$transformed_records_from_raw_table_name