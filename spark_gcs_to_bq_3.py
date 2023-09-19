from pyspark.sql import SparkSession

# Create a SparkSession
spark = SparkSession.builder \
    .appName("Spark SQL - vlille") \
    .config("spark.driver.maxResultSize", "10g") \
    .config("spark.driver.memory", "10g") \
    .getOrCreate()

# Define the GCS bucket and path
json_dir = "gs://vlille_sample_data_yzpt/"

# List the JSON files in the directory
json_files = spark.sparkContext.binaryFiles(json_dir + "*.json")

# Initialize a counter for processed files
processed_files = 0

# Iterate through each JSON file
for json_file in json_files.collect()[:3]:
    # Read the JSON file
    df = spark.read.json(json_file[0])
    
    # Create a view
    df.createOrReplaceTempView("vlille")
    
    # Query the view
    df = spark.sql("SELECT * FROM vlille")
    
    # Show the results (optional)
    df.show()
    
    # Write the results to a BigQuery table
    df.write \
        .format("bigquery") \
        .option("table", "vlille-396911.test_dataproc.vlille-4") \
        .option("temporaryGcsBucket", "yzpt-temp-bucket") \
        .mode("overwrite") \
        .save()
    
    # Increment the processed files counter
    processed_files += 1
    
    # Print progress information
    print(f"Processed {processed_files} files")

# Stop the session
spark.stop()
