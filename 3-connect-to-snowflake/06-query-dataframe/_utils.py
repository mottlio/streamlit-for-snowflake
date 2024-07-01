import os
from snowflake.snowpark import Session
from dotenv import load_dotenv

load_dotenv('C:/Users/Michalm/OneDrive - Commerce Commission/Python/Streamlit/streamlit Snowflake course/streamlit-for-snowflake/.env')

def getSession():
    return Session.builder.configs({
    "user": os.environ['USER'],
    "account": os.environ['ACCOUNT'],
    "role": os.environ['ROLE'],
    "warehouse": os.environ['WAREHOUSE'],
    "database": os.environ['DATABASE'],
    "schema": os.environ['SCHEMA'],
    "authenticator": os.environ['AUTHENTICATOR']
}).create()
