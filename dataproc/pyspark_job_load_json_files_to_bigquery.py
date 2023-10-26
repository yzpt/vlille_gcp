from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType, FloatType, TimestampType

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

# Read JSON data from Google Cloud Storage
json_data = spark.read.schema(json_schema).json("gs://zapart-data-vlille-data/*.json")

# Flatten the nested JSON structure
flattened_data = json_data.select(col("records.fields.nbvelosdispo").alias("nb_available_bikes"),
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
    .option("table", "zapart-data-vlille.vlille_dataset.dataproc_test") \
    .save()

# Stop the Spark session
spark.stop()
