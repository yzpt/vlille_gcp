BigQuery schema Description :
nhits	                INTEGER	NULLABLE		
parameters	            RECORD	NULLABLE
    /dataset                STRING	NULLABLE
    /rows	                INTEGER	NULLABLE
    /start	                INTEGER	NULLABLE
    /format	                STRING	NULLABLE
    /timezone	            STRING	NULLABLE
records	                RECORD	REPEATED
    /datasetid          STRING NULLABLE
    /recordid           STRING NULLABLE
    /fields	            RECORD	NULLABLE
        /nbvelosdispo	    INTEGER	NULLABLE
        /nbplacesdispo	    INTEGER	NULLABLE
        /libelle	        INTEGER	NULLABLE
        /adresse	        STRING	NULLABLE
        /nom	            STRING	NULLABLE
        /etat	            STRING	NULLABLE
        /commune	        STRING	NULLABLE
        /etatconnexion	    STRING	NULLABLE
        /type	            STRING	NULLABLE
        /geo	            FLOAT	REPEATED
        /localisation	    FLOAT	REPEATED
        /datemiseajour	    TIMESTAMP	NULLABLE
    /geometry	        RECORD	NULLABLE
    /record_timestamp	TIMESTAMP	NULLABLE

nhits	                		
parameters	            
    /dataset            
    /rows	            
    /start	            
    /format	            
    /timezone	        
records	                
    /datasetid          
    /recordid           
    /fields	            
        /nbvelosdispo	
        /nbplacesdispo	
        /libelle	    
        /adresse	    
        /nom	        
        /etat	        
        /commune	    
        /etatconnexion	
        /type	        
        /geo	        
        /localisation	
        /datemiseajour	
    /geometry	        
    /record_timestamp	

-- dim table des stations
SELECT DISTINCT 
    r.fields.nom AS nom, 
    r.fields.libelle AS libelle,
    r.fields.adresse AS adresse,
    r.fields.commune AS commune,
    r.fileds.type AS type,
    r.fields.geo AS geo,
FROM `vlille_dataset.vlille_table_direct_from_bq`,
    UNNEST(records) AS r
ORDER BY r.fields.libelle DESC;

------------------------------------------------------
CREATE OR REPLACE TABLE `vlille-396911.vlille_dataset.allo` AS
SELECT
  r.datasetid,
  r.recordid,
  r.fields.nbvelosdispo,
  r.fields.nbplacesdispo,
  r.fields.libelle,
  r.fields.adresse,
  r.fields.nom,
  r.fields.etat,
  r.fields.commune,
  r.fields.etatconnexion,
  r.fields.type,
  r.fields.geo,
  r.fields.localisation,
  r.fields.datemiseajour,
  r.geometry,
  r.record_timestamp
FROM
  `vlille-396911.vlille_dataset.vlille_table_direct_from_bq` AS t,
UNNEST(records) AS r;
------------------------------------------------------
-- allo table schema :
-- datasetid	STRING	NULLABLE				
-- recordid	STRING	NULLABLE				
-- nbvelosdispo	INTEGER	NULLABLE				
-- nbplacesdispo	INTEGER	NULLABLE				
-- libelle	INTEGER	NULLABLE				
-- adresse	STRING	NULLABLE				
-- nom	STRING	NULLABLE				
-- etat	STRING	NULLABLE				
-- commune	STRING	NULLABLE				
-- etatconnexion	STRING	NULLABLE				
-- type	STRING	NULLABLE				
-- geo	FLOAT	REPEATED				
-- localisation	FLOAT	REPEATED				
-- datemiseajour	TIMESTAMP	NULLABLE				
-- geometry	RECORD	NULLABLE				
-- record_timestamp	TIMESTAMP	NULLABLE
------------------------------------------------------
CREATE OR REPLACE TABLE `vlille-396911.vlille_dataset.cleaned_columns` AS
SELECT
    *,
    geo[OFFSET(0)] AS latitude,
    geo[OFFSET(1)] AS longitude
FROM
    `vlille-396911.vlille_dataset.allo`;
------------------------------------------------------
--bigquery command to delete a column from a table
ALTER TABLE `vlille-396911.vlille_dataset.allo`
DROP COLUMN geometry

ALTER TABLE `vlille-396911.vlille_dataset.cleaned_columns`
DROP COLUMN geo;

ALTER TABLE `vlille-396911.vlille_dataset.cleaned_columns`
DROP COLUMN localisation;
------------------------------------------------------
SELECT DISTINCT 
    nom, 
    libelle,
    adresse,
    commune,
    type,
    latitude,
    longitude
FROM `vlille-396911.vlille_dataset.cleaned_columns`
WHERE nom IS NOT NULL;
------------------------------------------------------
CREATE OR REPLACE TABLE `vlille-396911.flask_dataset.data_copy` AS
SELECT
  r.fields.nbvelosdispo,
  r.fields.nbplacesdispo,
  r.fields.libelle,
  r.fields.adresse,
  r.fields.nom,
  r.fields.etat,
  r.fields.commune,
  r.fields.etatconnexion,
  r.fields.type,
  r.fields.geo[0] AS latitude,
  r.fields.geo[1] AS longitude,
  r.fields.datemiseajour,
FROM
  `vlille-396911.flask_dataset.data_copy` AS t,
UNNEST(records) AS r;
------------------------------------------------------
DELETE FROM `vlille-396911.flask_dataset.data_copy`
WHERE nom IS NULL;
------------------------------------------------------
SELECT DISTINCT st.nom, max_dates.max_datemiseajour, r.datemiseajour, r.nbvelosdispo
FROM `flask_dataset.dim_stations` st
INNER JOIN (
  SELECT nom, MAX(datemiseajour) as max_datemiseajour
  FROM `flask_dataset.data_copy`
  WHERE datemiseajour < '2023-09-15 15:00:00'
  GROUP BY nom
) max_dates
ON st.nom = max_dates.nom
INNER JOIN `flask_dataset.data_copy` r
ON st.nom = r.nom AND max_dates.max_datemiseajour = r.datemiseajour
------------------------------------------------------
CREATE OR REPLACE TABLE flask_dataset.distinct_dates AS (
  SELECT DISTINCT datemiseajour
  FROM `flask_dataset.data_copy`
  ORDER BY datemiseajour ASC
)
------------------------------------------------------
CREATE TABLE `vlille-396911.flask_dataset.data_rm_duplicate` AS
SELECT DISTINCT *
FROM `vlille-396911.flask_dataset.data_copy`
------------------------------------------------------
-- remove all rows with null values
DELETE FROM `vlille-396911.flask_dataset.data_rm_duplicate`
WHERE nom IS NULL;
------------------------------------------------------
SELECT nom, nbvelosdispo, datemiseajour
FROM `vlille-396911.flask_dataset.data_rm_duplicate` 
WHERE 
      datemiseajour >= TIMESTAMP('2023-08-25') 
  AND datemiseajour <  TIMESTAMP('2023-08-26')
  AND libelle = 2
ORDER BY libelle, datemiseajour ASC
------------------------------------------------------
CREATE OR REPLACE TABLE `vlille-396911.flask_dataset.transactions_test` AS
WITH RankedTransactions AS (
  SELECT
    nom,
    datemiseajour AS date,
    nbvelosdispo AS nbvelosdispo_current,
    LAG(nbvelosdispo, 1) OVER (PARTITION BY nom ORDER BY datemiseajour) AS nbvelosdispo_previous
  FROM
    `vlille-396911.flask_dataset.data_rm_duplicate`
  
  WHERE datemiseajour >= '2023-09-06' and datemiseajour <'2023-09-07' 
)

SELECT
  nom,
  date,
  IFNULL(nbvelosdispo_previous, 0) - nbvelosdispo_current AS transaction_value
FROM
  RankedTransactions
WHERE
  nbvelosdispo_previous IS NOT NULL
  and (IFNULL(nbvelosdispo_previous, 0) - nbvelosdispo_current) <> 0
ORDER BY
  date DESC;

------------------------------------------------------
SELECT datemiseajour, SUM(nbvelosdispo) AS total_nbvelosdispo
FROM your_dataset.your_table
GROUP BY datemiseajour
ORDER BY datemiseajour;
------------------------------------------------------
WITH RankedTransactions AS (
  SELECT
    station_id,
    EXTRACT(HOUR FROM date) AS hour_of_day,
    transaction_value
  FROM
    `vlille-gcp.vlille_gcp_dataset.transactions_test`
  WHERE
    DATE(date) >= '2023-08-25'
)

SELECT
  hour_of_day,
  SUM(IF(transaction_value > 0, transaction_value, 0)) AS sum_positive_transactions,
  SUM(IF(transaction_value < 0, - transaction_value, 0)) AS sum_negative_transactions,
  COUNT(transaction_value) AS transactions_count
FROM
  RankedTransactions
GROUP BY
  hour_of_day
ORDER BY
  hour_of_day;
  ------------------------------------------------------
  