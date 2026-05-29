-- DDL 1
DROP TABLE STAGE2.AIRLINES;
SELECT * FROM STAGE2.AIRLINES;
UNDROP TABLE STAGE2.AIRLINES;
SELECT * FROM STAGE2.AIRLINES;

-- DDL 2
CREATE OR REPLACE TABLE stage2.airlines_restored
CLONE stage2.airlines
BEFORE (STATEMENT => '01c4b050-0306-fc77-0005-0972000317d6');

-- DML 1
SELECT * FROM stage3.visitors_per_month AT(OFFSET=>-7200)

-- DML 2
SELECT * FROM stage2.airlines BEFORE(STATEMENT=>'01c4b050-0306-fc77-0005-0972000317d6');


-- Create Secure View

CREATE OR REPLACE ROW ACCESS POLICY stage3.airline_policy
AS (current_role STRING) RETURNS BOOLEAN ->
  CURRENT_ROLE() = 'ACCOUNTADMIN'
;

CREATE OR REPLACE SECURE VIEW stage3.secure_airlines_fact AS
SELECT * FROM stage2.airlines;

-- Attach Row Level Security Policy

ALTER TABLE stage3.secure_airlines_fact 
ADD ROW ACCESS POLICY stage3.airline_policy ON (PassengerID);