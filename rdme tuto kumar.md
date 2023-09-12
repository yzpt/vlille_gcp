# Apache Spark on GCP Dataproc
Série de vidéos sur Apache Spark on Dataproc | Google Cloud Series :
https://www.youtube.com/watch?v=mexsZ5aK0XU&list=PLeOtIjHQdqvFtYzoFL-DCYx_Sw-5iBJQ4&ab_channel=SushilKumar


## 1. Configuration GCP
* Création d'un projet GCP
    ```bash 
    gcloud projects create spark-dataproc-yzpt
    ```

* Association d'un compte de facturation au projet
    ```bash
    gcloud alpha billing projects link spark-dataproc-yzpt --billing-account=*****-*****-*****
    ```

* Activation API Dataproc
    ```bash
    gcloud services enable dataproc.googleapis.com --project spark-dataproc-yzpt 
    ```

* Création d'un cluster Dataproc
    ```bash
    gcloud dataproc clusters \ 
    create cluster-spark-dataproc \ 
    --region us-east1 \ 
    --zone us-east1-c \ 
    --master-machine-type n1-standard-2 \  
    --master-boot-disk-size 50 \ 
    --num-workers 2 \ 
    --worker-machine-type n1-standard-2 \ 
    --worker-boot-disk-size 50 \ 
    --image-version 2.1-debian11 \ 
    --project spark-dataproc-yzpt
    ```

* Création d'un bucket GCS
    ```bash
    gsutil mb -p spark-dataproc-yzpt gs://spark-dataproc-bucket
    ```

## 2. Création d'un job Spark + Hive

* Fichier spark_write_demo.py
    ```python
    from pyspark.sql import SparkSession

    # Create a spark session
    spark = SparkSession.builder.master("local").enableHiveSupport().getOrCreate()

    print("Storing random numbers in a hive table")
    spark.range(100).write.mode("overwrite").saveAsTable("random_numbers")
    print('complete')
    ```

* Copie du fichier spark_write_demo.py sur le bucket
    ```bash
    gsutil cp spark_write_demo.py gs://spark-dataproc-bucket
    ```

* Lancement du job spark_write_demo.py sur le cluster
    ```bash
    gcloud dataproc jobs submit pyspark --cluster cluster-spark-dataproc gs://spark-dataproc-bucket/spark_write_demo.py --region us-east1 --project spark-dataproc-yzpt
    ```



## 3. Job Spark + GCS

* Fichier spark_gcs_demo.py
    ```python
    from pyspark.sql import SparkSession

    # Create a spark session
    spark = SparkSession.builder.master("local").enableHiveSupport().getOrCreate()

    print("Storing random numbers in GCS")
    spark.range(100).write.mode("overwrite").parquet("gs://spark-dataproc-bucket/random_numbers")
    print('complete')
    ```

* Copie du fichier spark_gcs_demo.py sur le bucket
    ```bash
    gsutil cp spark_gcs_demo.py gs://spark-dataproc-bucket
    ```

* Lancement du job spark_gcs_demo.py sur le cluster
    ```bash
    gcloud dataproc jobs submit pyspark --cluster cluster-spark-dataproc gs://spark-dataproc-bucket/spark_gcs_demo.py --region us-east1 --project spark-dataproc-yzpt
    ```

Les données sont maintenant stockées sur le bucket spark-dataproc-bucket/random_numbers

* Suppression du cluster
    ```bash
    gcloud dataproc clusters delete cluster-spark-dataproc --region us-east1 --project spark-dataproc-yzpt
    ```

* Suppression du bucket GCS
    ```bash
    gsutil rm -r gs://spark-dataproc-bucket/random_numbers
    ```