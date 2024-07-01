import os
from snowflake.snowpark import Session
from dotenv import load_dotenv

load_dotenv('C:/Users/Michalm/OneDrive - Commerce Commission/Python/Streamlit/streamlit Snowflake course/streamlit-for-snowflake/.env')

pars = {
    "user": os.environ['USER'],
    "account": os.environ['ACCOUNT'],
    "role": os.environ['ROLE'],
   " warehouse": os.environ['WAREHOUSE'],
    "database": os.environ['DATABASE'],
    "schema": os.environ['SCHEMA'],
    "authenticator": os.environ['AUTHENTICATOR']
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