-- Backup the table
CREATE TABLE `zapart-data-vlille.vlille_dataset.records_backup` AS
SELECT * 
FROM `zapart-data-vlille.vlille_dataset.records`;


# Standard SQL
BEGIN TRANSACTION;

-- Step 1: Delete the rows
DELETE FROM `zapart-data-vlille.vlille_dataset.records`
WHERE record_timestamp >= '2023-11-22 22:35:00 UTC' AND record_timestamp <= '2023-11-23 13:40:00 UTC';

-- Step 2: Select and modify the rows
CREATE TEMPORARY TABLE TempTable AS
SELECT * EXCEPT(record_timestamp), TIMESTAMP_ADD(record_timestamp, INTERVAL 7*24 HOUR) as new_record_timestamp
FROM `zapart-data-vlille.vlille_dataset.records`
WHERE record_timestamp >= '2023-11-15 22:35:00 UTC' AND record_timestamp <= '2023-11-16 13:40:00 UTC';

-- Step 3: Insert the modified rows back into the table
INSERT INTO `zapart-data-vlille.vlille_dataset.records`
SELECT * EXCEPT(new_record_timestamp), new_record_timestamp as record_timestamp
FROM TempTable;

COMMIT;

