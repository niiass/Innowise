CREATE OR REPLACE PROCEDURE INNOWISE_SNOWFLAKE_LMS.STAGE2.LOAD_CLEAN_DATA()
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS CALLER
AS '
BEGIN
    LET rows_inserted INT := 0;
    BEGIN TRANSACTION;

    INSERT INTO stage2.airlines
    SELECT 
        PassengerID, FirstName, LastName, Gender, CAST(Age as INT), Nationality, AirportName, AirportCountryCode, CountryName,
        AirportContinent, Continents, TO_DATE(DepartureDate, ''MM/DD/YYYY''), ArrivalAirport, PilotName, FlightStatus,
        TicketType, PassengerStatus
    FROM stage1.airline_stream;

    rows_inserted := SQLROWCOUNT;

    COMMIT;

    RETURN TO_VARCHAR(rows_inserted);

EXCEPTION
    WHEN OTHER THEN
        ROLLBACK;
        RETURN 0;
END;
';