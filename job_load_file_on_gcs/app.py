from google.cloud import storage
import os
from datetime import datetime
import pytz
from flask import Flask
import sys

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key-vlille.json"

app = Flask(__name__)

# storage function upload a file
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