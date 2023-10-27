from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType, FloatType, TimestampType
import subprocess

# Specify your source bucket name
bucket_name = "vlille_data_json_sample"

# To prevent problems caused by ":" characters in file names, it is necessary to create a list of files along with their complete paths.
# Function to list files in a bucket
def list_files_in_bucket(bucket_name):
    # Run the gsutil ls command and capture the output
    command = f"gsutil ls gs://{bucket_name}"
    try:
        # Run the command and capture the output as a byte string
        output = subprocess.check_output(command, shell=True)
        
        # Decode the byte string to a regular string and split it into lines
        file_paths = output.decode("utf-8").strip().split("\n")
        
        # Return the list of file paths
        return file_paths
    except subprocess.CalledProcessError as e:
        # Handle any errors that occurred during the command execution
        print(f"Error: {e}")
        return []

file_paths = list_files_in_bucket(bucket_name)

print(len(file_paths), 'files, to insert', len(file_paths)*289, 'rows in bigquery')
# 91,549 files, translating to approximately 26,457,661 rows in BigQuery, 
# represent around 2 months of data extraction:
# 289 stations * 60 minutes * 24 hours * 60 days =~ 25 million rows.

# Function to read JSON data in batches
def read_json_data_in_batches(spark, file_paths, batch_size):
    for i in range(0, len(file_paths), batch_size):
        batch_files = file_paths[i:i+batch_size]
        batch_data = spark.read.schema(json_schema).json(batch_files)
        yield batch_data

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("JsonToBigQuery") \
    .getOrCreate()

# Define JSON schema
json_schema = StructType([
    StructField("nhits", IntegerType()),
    StructField("parameters", StructType([
        StructField("dataset", StringType()),
        StructField("rows", IntegerType()),
        StructField("start", IntegerType()),
        StructField("format", StringType()),
        StructField("timezone", StringType())
    ])),
    StructField("records", ArrayType(StructType([
        StructField("datasetid", StringType()),
        StructField("recordid", StringType()),
        StructField("fields", StructType([
            StructField("nbvelosdispo", IntegerType()),
            StructField("nbplacesdispo", IntegerType()),
            StructField("libelle", StringType()),
            StructField("adresse", StringType()),
            StructField("nom", StringType()),
            StructField("etat", StringType()),
            StructField("commune", StringType()),
            StructField("etatconnexion", StringType()),
            StructField("type", StringType()),
            StructField("geo", ArrayType(FloatType())),
            StructField("localisation", ArrayType(FloatType())),
            StructField("datemiseajour", TimestampType())
        ])),
        StructField("geometry", StructType([
            StructField("type", StringType()),
            StructField("coordinates", ArrayType(FloatType()))
        ])),
        StructField("record_timestamp", TimestampType())
    ])))
])

# Specify the batch size (416160 rows represent one day of data)
batch_size = 1440 * 289

# Read JSON data in batches and process
for batch_data in read_json_data_in_batches(spark, file_paths, batch_size):
    # Flatten the nested JSON structure
    flattened_data = batch_data.select(col("records.fields.nbvelosdispo").alias("nb_available_bikes"),
                                       col("records.fields.nbplacesdispo").alias("nb_available_places"),
                                       col("records.fields.libelle").alias("station_id"),
                                       col("records.fields.etat").alias("operational_state"),
                                       col("records.fields.etatconnexion").alias("connexion"),
                                       col("records.fields.datemiseajour").alias("datemiseajour"),
                                       col("records.record_timestamp").alias("record_timestamp"))

    # Write data to BigQuery
    flattened_data.write \
        .format("bigquery") \
        .mode("overwrite") \
        .option("temporaryGcsBucket", "dataproc_test_yzpt") \
        .option("parentProject", "zapart-data-vlille") \
        .option("table", "zapart-data-vlille.vlille_dataset.dataproc_test_2") \
        .save()

# Stop the Spark session
spark.stop()

print("Data loaded into BigQuery successfully.")
