from google.cloud import storage

# Initialize a client for Google Cloud Storage
client = storage.Client()

# Specify your GCS bucket name and the prefix for the files you want to rename
bucket_name = 'vlille_data_json_copy'
prefix = 'vlille_data_json/data___'

# List the files in the bucket with the specified prefix
bucket = client.get_bucket(bucket_name)
blobs = bucket.list_blobs(prefix=prefix)

# Iterate through the files and rename them
for blob in blobs:
    old_name = blob.name
    new_name = old_name.replace(':', '_').replace('-', '_')
    
    # Check if renaming is needed
    if new_name != old_name:
        # Rename the file
        new_blob = bucket.rename_blob(blob, new_name)
        print(f'Renamed: {old_name} -> {new_name}')
    else:
        print(f'No need to rename: {old_name}')

# copy all the files in gs://vlille_data_json_copy/vlille_data_json/ to gs://vlille_data_json_copy/ (root of the bucket)
# gsutil -m cp -r gs://vlille_data_json_copy/vlille_data_json/ gs://vlille_data_json_copy/