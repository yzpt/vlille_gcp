from pyspark.sql import SparkSession

# Create a SparkSession
spark = SparkSession.builder \
    .appName("Spark SQL - vlille") \
    .config("spark.driver.maxResultSize", "10g") \
    .config("spark.driver.memory", "10g") \
    .getOrCreate()

# Read json files from a bucket
# df = spark.read.json("gs://vlille_data_json_copy/*.json")
# df = spark.read.json("gs://test_copy_vlille_yzpt/data___2023_08_24_19_54_00.json")
df = spark.read.json("gs://test_copy_vlille_yzpt/*.json")


# get the number of rows
print('******************************')
print(df.count())
print('******************************')

# Create a view
df.createOrReplaceTempView("vlille")

# Query the view
df = spark.sql("SELECT * FROM vlille LIMIT 1000")

# Show the results
df.show()

# Write the results to a BigQuery table
df.write \
    .format("bigquery") \
    .option("table", "vlille-396911.test_dataproc.vlille-3") \
    .option("temporaryGcsBucket", "yzpt-temp-bucket") \
    .mode("overwrite") \
    .save()

# Stop the session
spark.stop()

