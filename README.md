# Snowflake Task3

## Roles
For the demonstration purposes, I came up with 4 roles. Below is given every of them and their job:
- `DEVELOPMENT` - Owns the database. Full control: create, alter, drop schemas/tables, manage grants, everything  
- `DATA_ENGINEER` - Builds and maintains data pipelines. Needs to read and write data, but shouldn't be able to restructure or drop the database itself  
- `ANALYST` - Explores and reports on data. Read-only, but needs access to both raw tables and curated views  
- `READ_ONLY_ROLE` - The most restricted consumer. Read-only, and only through views, no raw tables  

## Grants
### Development
``` sql
GRANT OWNERSHIP ON DATABASE {db} TO ROLE {role} COPY CURRENT GRANTS;
```
- Ownership already includes every privilege there is, so a single `OWNERSHIP` grant gives full structural control  
***Note: `COPY CURRENT GRANTS` matters because transferring ownership normally wipes any grants already made to other roles***

### Data Engineer
``` sql
GRANT USAGE ON DATABASE {db} TO ROLE {role};
GRANT USAGE ON ALL SCHEMAS IN DATABASE {db} TO ROLE {role};
GRANT USAGE ON FUTURE SCHEMAS IN DATABASE {db} TO ROLE {role};
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN DATABASE {db} TO ROLE {role};
GRANT SELECT, INSERT, UPDATE, DELETE ON FUTURE TABLES IN DATABASE {db} TO ROLE {role};
```
- The three `USAGE` grants are to give a role access to specific tables and schemas. Without them, with `SELECT` grants they would still see nothing  
- `SELECT, INSERT, UPDATE, DELETE` are grants for a role for full read/write on data. `CREATE`/`DROP`/`ALTER` are excluded so that they can't touch structure  
- `FUTURE TABLES` auto-applies the same permission to any table created later  

### Analyst
``` sql
GRANT USAGE ON DATABASE {db} TO ROLE {role};
GRANT USAGE ON ALL SCHEMAS IN DATABASE {db} TO ROLE {role};
GRANT USAGE ON FUTURE SCHEMAS IN DATABASE {db} TO ROLE {role};
GRANT SELECT ON ALL TABLES IN DATABASE {db} TO ROLE {role};
GRANT SELECT ON FUTURE TABLES IN DATABASE {db} TO ROLE {role};
GRANT SELECT ON ALL VIEWS IN DATABASE {db} TO ROLE {role};
GRANT SELECT ON FUTURE VIEWS IN DATABASE {db} TO ROLE {role};
```
- The three `USAGE` grants are to give a role access to specific tables and schemas. Without them, with `SELECT` grants they would still see nothing  
- `SELECT` on tables is grant for a role to only read, no write  
- `SELECT` on views is granted separately because Snowflake treats them as a distinct object type
- `FUTURE` for tables and views auto-applies the same permissions to any table or views created later

### Read only role
``` sql
GRANT USAGE ON DATABASE {db} TO ROLE {role};
GRANT USAGE ON ALL SCHEMAS IN DATABASE {db} TO ROLE {role};
GRANT USAGE ON FUTURE SCHEMAS IN DATABASE {db} TO ROLE {role};
GRANT SELECT ON ALL VIEWS IN DATABASE {db} TO ROLE {role};
GRANT SELECT ON FUTURE VIEWS IN DATABASE {db} TO ROLE {role};
```
- The three `USAGE` grants are to give a role access to specific tables and schemas. Without them, with `SELECT` grants they would still see nothing  
- `SELECT` on `VIEWS` and not on `TABLES` means that this role has access only to a filtered data from views
- `FUTURE` for views auto-applies the same permissions to any table or views created later
