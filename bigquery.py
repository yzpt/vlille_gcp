from datetime import datetime
import pytz
from google.cloud import bigquery

def create_dataset(dataset_id: str) -> None:

    # [START bigquery_create_dataset]


    # Construct a BigQuery client object.
    client = bigquery.Client()

    # TODO(developer): Set dataset_id to the ID of the dataset to create.
    dataset_id = "{}.{}".format(client.project, dataset_id)

    # Construct a full Dataset object to send to the API.
    dataset = bigquery.Dataset(dataset_id)

    # TODO(developer): Specify the geographic location where the dataset should reside.
    dataset.location = "EU"

    # Send the dataset to the API for creation, with an explicit timeout.
    # Raises google.api_core.exceptions.Conflict if the Dataset already
    # exists within the project.
    dataset = client.create_dataset(dataset, timeout=30)  # Make an API request.
    print("Created dataset {}.{}".format(client.project, dataset.dataset_id))
    # [END bigquery_create_dataset]

if __name__ == "__main__":
    paris_tz = pytz.timezone('Europe/Paris')
    str_time_paris = datetime.now(paris_tz).strftime('%Y_%m_%d_%H_%M_%S')
    create_dataset(dataset_id="allo_{}".format(str_time_paris))
