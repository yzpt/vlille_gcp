from google.cloud import bigquery
import sys
import os

# Usage: python bq_loading_raw_json_files.py <project-id> <key-file-path> <dataset-name> <raw_records_table_name> <transformed_records_from_raw_table_name> <records_table_name> <date_inf> <date_sup>

def run_queries(project_id, dataset_name, raw_records_table_name, transformed_records_from_raw_table_name, records_table_name, date_inf, date_sup):
    # Initialize the BigQuery client
    client = bigquery.Client(project=project_id)

    # Define the queries
    queries = [
        """
        CREATE OR REPLACE TABLE `{project_id}.{dataset_name}.{transformed_records_from_raw_table_name}` AS
        WITH transformed_data AS (
          SELECT
            CAST(records.fields.libelle AS INT64) AS station_id,
            records.fields.etat AS operational_state,
            records.fields.nbvelosdispo AS nb_available_bikes,
            records.fields.nbplacesdispo AS nb_available_places,
            records.fields.etatconnexion AS connexion,
            TIMESTAMP(records.fields.datemiseajour) AS last_update,
            TIMESTAMP(records.record_timestamp) AS record_timestamp
          FROM
            `{project_id}.{dataset_name}.{raw_records_table_name}`, UNNEST(records) AS records
        )
        SELECT * FROM transformed_data;
        """,
        """
        DELETE FROM 
            `{project_id}.{dataset_name}.{transformed_records_from_raw_table_name}`
        WHERE 
               record_timestamp < TIMESTAMP('{date_inf}') 
            OR record_timestamp >= TIMESTAMP('{date_sup}');
        """,
        """
        INSERT INTO 
            `{project_id}.{dataset_name}.{records_table_name}` 
            (station_id, operational_state, nb_available_bikes, nb_available_places, connexion, last_update, record_timestamp)
        SELECT 
            * 
        FROM 
            `{project_id}.{dataset_name}.{transformed_records_from_raw_table_name}`
        WHERE
            station_id is not NULL;
        """
    ]

    # Run the queries
    for query in queries:
        formatted_query = query.format(
                                project_id                              = project_id, 
                                dataset_name                            = dataset_name, 
                                raw_records_table_name                  = raw_records_table_name, 
                                transformed_records_from_raw_table_name = transformed_records_from_raw_table_name, 
                                records_table_name                      = records_table_name,
                                date_inf                                = date_inf,
                                date_sup                                = date_sup
                                )
        query_job = client.query(formatted_query)
        query_job.result()  # Wait for the query to finish

    print("Queries executed successfully.")

if __name__ == "__main__":
    try:
        project_id                                      = sys.argv[1]
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"]    = sys.argv[2]
        dataset_name                                    = sys.argv[3]
        raw_records_table_name                          = sys.argv[4]
        transformed_records_from_raw_table_name         = sys.argv[5]
        records_table_name                              = sys.argv[6]
        date_inf                                        = sys.argv[7]
        date_sup                                        = sys.argv[8]
        
        run_queries(project_id, dataset_name, raw_records_table_name, transformed_records_from_raw_table_name, records_table_name, date_inf, date_sup)

    except Exception as e:
        print(e)
        print("Usage: python bq_loading_raw_json_files.py <project-id> <key-file-path> <dataset-name> <raw_records_table_name> <transformed_records_from_raw_table_name> <records_table_name>")
    