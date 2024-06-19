import os
from snowflake.snowpark import Session

pars = {
    "user": 'michal.mottl@COMCOM.GOVT.NZ',
    "account": 'comcomdataplatform.australia-east.azure',
    "role":'GRP_AZURE_DA_NONPROD_RPS_DEVELOPER',
   " warehouse": 'DATAANALYTICS_WH_DEV',
    "database":'DATAANALYTICS_DB_DEV',
    "schema": 'RPS_OUTPUT',
    "authenticator":'externalbrowser'
}
session = Session.builder.configs(pars).create()

# basic usage
df = session.sql('select * from DATAANALYTICS_DB_DEV.DBT_MICHALM.aggregate_total_quarterly_system_transactions Limit 10;')
rows = df.collect()
for row in rows:
    print(row)

# alternative w/ pandas DataFrame
dfp = df.to_pandas()
print(dfp)