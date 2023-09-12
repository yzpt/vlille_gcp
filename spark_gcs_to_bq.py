from pyspark.sql import SparkSession

# Create a SparkSession
spark = SparkSession.builder \
    .appName("Spark SQL - vlille") \
    .getOrCreate()

# Read json files from a bucket
# df = spark.read.json("gs://vlille_data_json_copy/*.json")
df = spark.read.json("gs://vlille_data_json_copy/vlille_data_json/data___2023_08_25_03_34_00.json")

# get the number of rows
df.count()

# Create a view
df.createOrReplaceTempView("vlille")

# Query the view
df = spark.sql("SELECT * FROM vlille LIMIT 10")

# Show the results
df.show()

# Write the results to a BigQuery table
df.write \
    .format("bigquery") \
    .option("table", "vlille-396911.test_dataproc.vlille") \
    .option("temporaryGcsBucket", "yzpt-temp-bucket") \
    .mode("overwrite") \
    .save()

# Stop the session
spark.stop()

