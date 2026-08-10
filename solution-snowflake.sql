CREATE OR REPLACE DATABASE INNOWISE_SNOWFLAKE_LMS_TASK2;

CREATE OR REPLACE TABLE sources(
    src_date1 DATE,
    src_date2 TIMESTAMP,
	src_date3 DATE
);

INSERT INTO sources VALUES
	('2025-02-06','2025-02-12 09:38:25.999982000', '2025-01-28'),
	('2025-02-14','2025-02-14 16:17:14.095384000', '2025-02-06'),
	('2025-02-20','2025-02-21 08:41:53.643244000', '2025-02-14'),
	('2025-02-25','2025-03-11 15:52:28.575590000', '2025-02-20'),
	('2025-03-06','2025-03-13 15:35:21.729785000', '2025-02-25'),
	('2025-03-13','2025-03-13 16:32:27.178218000', '2025-03-06'),
	('2025-03-20','2025-03-26 08:35:19.585812000', '2025-03-13'),
	('2025-03-27','2025-03-28 07:23:03.611707000', '2025-03-20'),
	('2025-04-07','2025-04-08 18:57:03.804270000', '2025-03-27'),
	('2025-04-10','2025-04-15 11:19:51.275211000', '2025-04-07'),
	('2025-04-14','2025-04-15 14:34:32.097939000', '2025-04-10'),
	('2025-04-24','2025-04-24 14:41:48.705573000', '2025-04-14'),
	('2025-05-02','2025-05-08 11:05:44.640510000', '2025-04-24'),
	('2025-05-15','2025-05-21 10:00:08.361011000', '2025-05-02'),
	('2025-05-22','2025-05-28 08:07:06.096731000', '2025-05-15'),
	('2025-05-29','2025-05-30 10:01:45.906511000', '2025-05-22'),
	('2025-06-05','2025-06-09 09:22:04.668390000', '2025-05-29'),
	('2025-06-19','2025-07-03 08:27:40.115104000', '2025-06-05'),
	('2025-06-26','2025-07-03 09:15:38.292950000', '2025-06-19'),
	('2025-07-03','2025-07-07 10:53:30.915895000', '2025-06-26');

CREATE OR REPLACE TABLE destination(
	dest_date1 DATE,
	dest_date2 TIMESTAMP,
	dest_date3 DATE
);

CREATE OR REPLACE PROCEDURE test_2(
	proc_date1 DATE,
	proc_date2 TIMESTAMP,
	proc_date3 DATE
)
RETURNS STRING
LANGUAGE SQL
AS $$
BEGIN
	INSERT INTO destination VALUES(:proc_date1, :proc_date2, :proc_date3);

	RETURN 'successful';
END;
$$;

CREATE OR REPLACE PROCEDURE task_2_cursor()
RETURNS STRING
LANGUAGE SQL
AS $$
DECLARE
    cur CURSOR FOR SELECT src_date1, src_date2, src_date3 FROM sources;
    v_date1 DATE;
    v_date2 TIMESTAMP;
    v_date3 DATE;
BEGIN
    FOR record IN cur DO
        v_date1 := record.src_date1;
        v_date2 := record.src_date2;
        v_date3 := record.src_date3;

        CALL test_2(:v_date1, :v_date2, :v_date3);
    END FOR;
  
    RETURN 'task_2_cursor executed successfully';
END;
$$;

CREATE OR REPLACE PROCEDURE task_2_resultset()
RETURNS STRING
LANGUAGE SQL
AS $$
DECLARE
    res RESULTSET DEFAULT (SELECT src_date1, src_date2, src_date3 FROM sources);
    v_date1 DATE;
    v_date2 TIMESTAMP;
    v_date3 DATE;
BEGIN
    FOR record IN res DO
        v_date1 := record.src_date1;
        v_date2 := record.src_date2;
        v_date3 := record.src_date3;

        CALL test_2(:v_date1, :v_date2, :v_date3);
    END FOR;
  
    RETURN 'task_2_resultset executed successfully';
END;
$$;

CALL task_2_resultset();