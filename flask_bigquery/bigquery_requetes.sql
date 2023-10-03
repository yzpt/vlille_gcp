I want to select and group all the "nom"


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


