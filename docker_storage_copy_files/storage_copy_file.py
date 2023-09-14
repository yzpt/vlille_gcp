#!/usr/bin/env python

# Copyright 2019 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os
# [START storage_copy_file]
from google.cloud import storage

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key-vlille.json"

def copy_blob(
    bucket_name, blob_name, destination_bucket_name, destination_blob_name,
):
    """Copies a blob from one bucket to another with a new name."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"
    # destination_bucket_name = "destination-bucket-name"
    # destination_blob_name = "destination-object-name"

    storage_client = storage.Client()

    source_bucket = storage_client.bucket(bucket_name)
    source_blob = source_bucket.blob(blob_name)
    destination_bucket = storage_client.bucket(destination_bucket_name)

    # Optional: set a generation-match precondition to avoid potential race conditions
    # and data corruptions. The request to copy is aborted if the object's
    # generation number does not match your precondition. For a destination
    # object that does not yet exist, set the if_generation_match precondition to 0.
    # If the destination object already exists in your bucket, set instead a
    # generation-match precondition using its generation number.
    # There is also an `if_source_generation_match` parameter, which is not used in this example.
    destination_generation_match_precondition = 0

    blob_copy = source_bucket.copy_blob(
        source_blob, destination_bucket, destination_blob_name, if_generation_match=destination_generation_match_precondition,
    )

    # print(
    #     "Blob {} in bucket {} copied to blob {} in bucket {}.".format(
    #         source_blob.name,
    #         source_bucket.name,
    #         blob_copy.name,
    #         destination_bucket.name,
    #     )
    # )

# function that loop all the files in a bucket and rename them in a new bucket using copy_blob
def copy_all_files(bucket_name, destination_bucket_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blobs = list(bucket.list_blobs())
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

    try:
        delete_bucket('test_copy_vlille_yzpt')
    except:
        print("Bucket does not exist")
    
    try:
        create_new_bucket('test_copy_vlille_yzpt')
    except:
        print("Bucket already exists")
        
    copy_all_files('vlille_data_json', 'test_copy_vlille_yzpt')
