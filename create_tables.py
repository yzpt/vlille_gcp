from google.cloud import bigquery
import os
import sys

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key-vlille.json"

client = bigquery.Client()

# get the args from the command line
project_id = sys.argv[1]
dataset_id = sys.argv[2]

# Create a 'stations' table
table_id = project_id + "." + dataset_id + ".stations"
schema = [
    bigquery.SchemaField("id", "INT64"), # id = libelle
    bigquery.SchemaField("nom", "STRING"),
    bigquery.SchemaField("adresse", "STRING"),
    bigquery.SchemaField("commune", "STRING"),
    bigquery.SchemaField("type", "STRING"),
    bigquery.SchemaField("latitude", "FLOAT64"),
    bigquery.SchemaField("longitude", "FLOAT64"),
]
table = bigquery.Table(table_id, schema=schema)
table = client.create_table(table)  # Make an API request.
print(
    "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)
)

# Create a 'records' table
table_id = project_id + "." + dataset_id + ".records"
schema = [
    bigquery.SchemaField("station_id", "INT64"),
    bigquery.SchemaField("etat", "STRING"),
    bigquery.SchemaField("nb_velos_dispo", "INT64"),
    bigquery.SchemaField("nb_places_dispo", "INT64"),
    bigquery.SchemaField("etat_connexion", "STRING"),
    bigquery.SchemaField("derniere_maj", "TIMESTAMP"),
    bigquery.SchemaField("record_timestamp", "TIMESTAMP"),
]
table = bigquery.Table(table_id, schema=schema)
table = client.create_table(table)  # Make an API request.
print(
    "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)
)

# On alimente la table stations une fois avec une requête:
import requests

url = "https://opendata.lillemetropole.fr/api/records/1.0/search/?dataset=vlille-realtime&rows=300&facet=libelle&facet=nom&facet=commune&facet=etat&facet=type&facet=etatconnexion"
response = requests.get(url)
data = response.json()

rows_to_insert = []
for record in data["records"]:
    rows_to_insert.append(
        (
            record["fields"]["libelle"], # id = libelle
            record["fields"]["nom"],
            record["fields"]["adresse"],
            record["fields"]["commune"],
            record["fields"]["type"],
            record["fields"]["localisation"][0],
            record["fields"]["localisation"][1],
        )
    )

table_id = project_id + "." + dataset_id + ".stations"
try:
    table = client.get_table(table_id)
    client.insert_rows(table, rows_to_insert)
    print("Inserted rows.")
except Exception as e:
    print(e)