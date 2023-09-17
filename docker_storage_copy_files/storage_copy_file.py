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


# function that loop all the files in a bucket and rename them in a new bucket using copy_blob
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
