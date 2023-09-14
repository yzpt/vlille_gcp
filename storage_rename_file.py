#!/usr/bin/env python

# Copyright 2021 Google LLC. All Rights Reserved.
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

# [START storage_rename_file]
from google.cloud import storage


def rename_blob(bucket_name, blob_name, new_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    new_blob = bucket.rename_blob(blob, new_name)

    print(f"Blob {blob.name} has been renamed to {new_blob.name}")




# function that loop all the files in a bucket and rename them
def rename_all_files(bucket_name):
    storage_client = storage.Client()
    # service account
    # storage_client = storage.Client.from_service_account_json('key-vlille.json')
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs()
    for i,blob in enumerate(blobs):
        new_name = "allo_" + str(i) + ".txt"
        new_blob = bucket.rename_blob(blob, new_name)
        print(f"Blob {blob.name} has been renamed to {new_blob.name}")

# [END storage_rename_file]

if __name__ == "__main__":
    # rename_blob(bucket_name=sys.argv[1], blob_name=sys.argv[2], new_name=sys.argv[3])
    # rename_blob(bucket_name="allo_bucket_yzpt", blob_name="file_renamed_3.py", new_name="file_renamed_4.py")
    rename_all_files(bucket_name="allo_bucket_yzpt")

