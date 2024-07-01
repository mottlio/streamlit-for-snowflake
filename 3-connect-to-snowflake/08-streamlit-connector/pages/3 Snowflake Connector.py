import streamlit as st

st.title("Connecting to Snowflake")
st.header("Streamlit SnowflakeConnection")

conn = st.connection("snowflake")
df = conn.query("select * from DATAANALYTICS_DB_DEV.DBT_MICHALM.calculate_icf_flows_2023_approach3",
    ttl=3600, show_spinner="Running query...")

st.dataframe(df)
