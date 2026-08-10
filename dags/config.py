SNOWFLAKE_CONN_ID='snowflake_default'
SNOWFLAKE_OBJECTS_DIR='opt/airflow/snowflake'
FOLDER_ORDER=['schemas', 'formats', 'stages', 'tables', 'streams', 'policies', 'procedures', 'views']
STAGE2_PROCEDURE='innowise_snowflake_lms.stage2.load_clean_data()'
AUDIT_TABLE='innowise_snowflake_lms.stage2.audit'
STAGE3_PROCEDURE='innowise_snowflake_lms.stage3.load_monthly_visitors()'