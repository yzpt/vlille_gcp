from google.cloud import bigquery
import requests
import os
import sys

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key-vlille.json"

client = bigquery.Client()

# get the args from the command line
try:
    project_id = sys.argv[1]
    dataset_id = sys.argv[2]
except Exception as e:
    print(e)
    print("Usage: python3 create_tables.py <project_id> <dataset_id>")
    sys.exit(1)

# Create a 'stations' table
table_id = project_id + '.' + dataset_id + '.stations'

stations_schema = [
    bigquery.SchemaField("id",          "INT64"), # id = libelle
    bigquery.SchemaField("name",        "STRING"),
    bigquery.SchemaField("adress",      "STRING"),
    bigquery.SchemaField("city",        "STRING"),
    bigquery.SchemaField("type",        "STRING"),
    bigquery.SchemaField("latitude",    "FLOAT64"),
    bigquery.SchemaField("longitude",   "FLOAT64"),
]
table = bigquery.Table(table_id, schema=stations_schema)
table = client.create_table(table)  # Make an API request.
print(
    "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)
)

# Create a 'records' table
table_id = project_id + '.' + dataset_id + '.records'
record_schema = [
    bigquery.SchemaField("station_id",              "INT64"),
    bigquery.SchemaField("operational_state",       "STRING"),
    bigquery.SchemaField("nb_available_bikes",      "INT64"),
    bigquery.SchemaField("nb_available_places",     "INT64"),
    bigquery.SchemaField("connexion",               "STRING"),
    bigquery.SchemaField("last_update",             "TIMESTAMP"),
    bigquery.SchemaField("record_timestamp",        "TIMESTAMP"),
]
table = bigquery.Table(table_id, schema=record_schema)
table = client.create_table(table)  # Make an API request.
print(
    "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)
)

# Populate the stations table once with a query:
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

table_id = project_id + '.' + dataset_id + '.stations'
try:
    table = client.get_table(table_id)
    client.insert_rows(table, rows_to_insert)
    print("Station's rows inserted into table {}".format(table_id))
except Exception as e:
    print(e)