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
            StructField("geo", ArrayType(FloatType())),  # Changed this line
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
json_data = spark.read.schema(json_schema).json("gs://vlille_data_json_sample/*.json")

# Flatten the nested JSON structure
flattened_data = json_data.select(col("nhits"),
                                  col("parameters.dataset").alias("dataset"),
                                  col("parameters.rows").alias("rows"),
                                  col("parameters.start").alias("start"),
                                  col("parameters.format").alias("format"),
                                  col("parameters.timezone").alias("timezone"),
                                  col("records.datasetid").alias("datasetid"),
                                  col("records.recordid").alias("recordid"),
                                  col("records.fields.nbvelosdispo").alias("nbvelosdispo"),
                                  col("records.fields.nbplacesdispo").alias("nbplacesdispo"),
                                  col("records.fields.libelle").alias("libelle"),
                                  col("records.fields.adresse").alias("adresse"),
                                  col("records.fields.nom").alias("nom"),
                                  col("records.fields.etat").alias("etat"),
                                  col("records.fields.commune").alias("commune"),
                                  col("records.fields.etatconnexion").alias("etatconnexion"),
                                  col("records.fields.type").alias("type"),
                                  col("records.fields.geo")[0].alias("latitude"),  # Extracting latitude
                                  col("records.fields.geo")[1].alias("longitude"),  # Extracting longitude
                                  col("records.fields.localisation").alias("localisation"),
                                  col("records.fields.datemiseajour").alias("datemiseajour"),
                                  col("records.geometry.type").alias("geometry_type"),
                                  col("records.geometry.coordinates").alias("geometry_coordinates"),
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
