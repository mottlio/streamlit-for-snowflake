import os
import snowflake.connector

conn = snowflake.connector.connect(
    user="michal.mottl@COMCOM.GOVT.NZ",
    account = "comcomdataplatform.australia-east.azure",
    role="GRP_AZURE_DA_NONPROD_RPS_DEVELOPER",
    warehouse="DATAANALYTICS_WH_DEV",
    database="DATAANALYTICS_DB_DEV",
    schema= "RPS_OUTPUT",
    authenticator='externalbrowser')

# (1) fetching row by row
cur = conn.cursor()
cur.execute('select * from DATAANALYTICS_DB_DEV.DBT_MICHALM.aggregate_total_quarterly_system_transactions Limit 10;')
for row in cur: print(row)

# (2) getting the whole set
df = cur.fetch_pandas_all()
print(df)
