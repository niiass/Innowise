CREATE OR REPLACE FILE FORMAT stage1.csv_format
    TYPE = 'CSV'
    FIELD_DELIMITER = ','
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    NULL_IF = ('', 'NULL');

CREATE OR REPLACE STAGE stage1.dataset
    FILE_FORMAT = stage1.csv_format;

COPY INTO stage1.airlines
FROM (
    SELECT
        $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18
    FROM @stage1.dataset
)
FILE_FORMAT = (FORMAT_NAME = stage1.csv_format)
ON_ERROR = 'SKIP_FILE';