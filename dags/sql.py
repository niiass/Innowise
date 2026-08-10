POPULATE_STAGE1='''
COPY INTO stage1.airlines
FROM (
    SELECT
        $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18
    FROM @stage1.dataset
)
FILE_FORMAT = (FORMAT_NAME = stage1.csv_format)
ON_ERROR = 'SKIP_FILE';
'''

LOG_STAGE2_AUDIT='''
INSERT INTO {audit_table} (PipelineName, SourceStage, TargetStage, RowsInserted)
VALUES (
    'Populate stage2', 'stage1', 'stage2', { rows }
);
'''

LOG_STAGE3_AUDIT='''
INSERT INTO {audit_table} (PipelineName, SourceStage, TargetStage, RowsInserted)
VALUES (
'Each Country Monthly Visitors', 'stage2', 'stage3', { rows }
);
'''