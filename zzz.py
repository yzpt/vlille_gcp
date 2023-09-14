from google.cloud import storage

storage_client = storage.Client()
bucket = storage_client.bucket('test_copy_vlille_yzpt')
blobs = list(bucket.list_blobs())
print(len(list(blobs)), ' files')