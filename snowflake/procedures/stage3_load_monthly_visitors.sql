CREATE OR REPLACE PROCEDURE INNOWISE_SNOWFLAKE_LMS.STAGE3.LOAD_MONTHLY_VISITORS()
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS CALLER
AS '
BEGIN
    LET rows_affected INT := 0;
    BEGIN TRANSACTION;
    
    INSERT INTO stage3.visitors_per_month (
        DestinationCountry, TravelMonth, TotalVisitors, AveragePassengerAge)
    SELECT CountryName, TO_CHAR(DepartureDate, ''YYYY-MM'') as TravelMonth, 
        COUNT(PassengerID) as TotalVisitors, AVG(Age) as AveragePassengerAge
    FROM stage2.airlines_stream
    GROUP BY CountryName, TO_CHAR(DepartureDate, ''YYYY-MM'');

    rows_affected := SQLROWCOUNT;
    COMMIT;

    RETURN TO_VARCHAR(rows_affected);
EXCEPTION
    WHEN OTHER THEN
        ROLLBACK;
        RETURN 0;
END;
';