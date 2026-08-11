# Snowflake Task3

## Roles
- `DEVELOPMENT` - Owns the database. Full control: create, alter, drop schemas/tables, manage grants, everything  
- `READ_ONLY_ROLE` - The most restricted consumer. Read-only access on tables, views and materialized views with no write or DDL permissions 

## Grants
### Development
``` sql
GRANT OWNERSHIP ON DATABASE {db} TO ROLE {role};
GRANT OWNERSHIP ON ALL SCHEMAS IN DATABASE {db} TO ROLE {role};
GRANT OWNERSHIP ON ALL TABLES IN DATABASE {db} TO ROLE {role};
GRANT OWNERSHIP ON ALL VIEWS IN DATABASE {db} TO ROLE {role};
GRANT OWNERSHIP ON ALL MATERIALIZED VIEWS IN DATABASE {db} TO ROLE {role};
GRANT OWNERSHIP ON ALL PROCEDURES IN DATABASE {db} TO ROLE {role};
GRANT OWNERSHIP ON ALL FUNCTIONS IN DATABASE {db} TO ROLE {role};

GRANT ALL PRIVILEGES ON FUTURE SCHEMAS IN DATABASE {db} TO ROLE {role};
GRANT ALL PRIVILEGES ON FUTURE TABLES IN DATABASE {db} TO ROLE {role};
GRANT ALL PRIVILEGES ON FUTURE VIEWS IN DATABASE {db} TO ROLE {role};
GRANT ALL PRIVILEGES ON FUTURE MATERIALIZED VIEWS IN DATABASE {db} TO ROLE {role};
GRANT ALL PRIVILEGES ON FUTURE PROCEDURES IN DATABASE {db} TO ROLE {role};
GRANT ALL PRIVILEGES ON FUTURE FUNCTIONS IN DATABASE {db} TO ROLE {role};
```
Development role needs to have access to everything in a database. That is why ownership and privileges are granted to every current or future schemas, tables, views, materialized views, procedures and functions. Transferring ownership on existing cloned objects guarantees developers can modify or drop them, while future grants ensure full operational privileges on newly created objects.


### Read only role
``` sql
GRANT USAGE ON DATABASE {db} TO ROLE {role};
GRANT USAGE ON ALL SCHEMAS IN DATABASE {db} TO ROLE {role};
GRANT USAGE ON FUTURE SCHEMAS IN DATABASE {db} TO ROLE {role};

GRANT SELECT ON ALL TABLES IN DATABASE {db} TO ROLE {role};
GRANT SELECT ON FUTURE TABLES IN DATABASE {db} TO ROLE {role};
GRANT SELECT ON ALL VIEWS IN DATABASE {db} TO ROLE {role};
GRANT SELECT ON FUTURE VIEWS IN DATABASE {db} TO ROLE {role};
GRANT SELECT ON ALL MATERIALIZED VIEWS IN DATABASE {db} TO ROLE {role};
GRANT SELECT ON FUTURE MATERIALIZED VIEWS IN DATABASE {db} TO ROLE {role};

```
Read only role should be able to get any kind of information from the database without a chance of them changing a single thing there. That is why only usage is granted on schemas. This way users with read only role are unable to modify any schema or table structure. They are able to access children current or future tables and views of all schemas. However, this access includes strictly only SELECT privilege. Read only role is only able to seek for the information throughout whole database without modifying its structure.