import subprocess
import os
from multiprocessing import Pool
import sys

try:
    bucket_id = sys.argv[1]
except Exception as e:
    print("Error: ", e)
    print("Usage: python multiproc_gsutil_mv.py <bucket_id>")
    print("Usage: bucket_id = 'gs://<your_bucket_name>'")
    sys.exit(1)

# Run the gsutil command and capture its output
gsutil_list_command = "gsutil ls " + bucket_id
result = subprocess.run(gsutil_list_command, stdout=subprocess.PIPE, shell=True)

# Decode and split the output into individual file paths
decoded_output = result.stdout.decode(encoding='utf-8').splitlines()

# Function to rename a file
def rename_file(file_path):
    # Extract the filename from the full path
    file_name = os.path.basename(file_path)
    # Replace ":" and "-" characters with "_"
    new_file_name = file_name.replace(':', '_').replace('-', '_')
    # Rename the file by moving it to the new name
    os.system(f"gsutil mv {file_path} {bucket_id}/{new_file_name}")

# Use multiprocessing to rename files in parallel
if __name__ == "__main__":
    # Specify the number of parallel processes
    num_processes = 8  # You can adjust this based on your system's capabilities
    # Create a pool of processes
    with Pool(processes=num_processes) as pool:
        # Map the rename_file function to the list of file paths
        pool.map(rename_file, decoded_output)