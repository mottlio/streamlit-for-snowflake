import streamlit as st

st.title("Connecting to Snowflake")
st.info("Select one method from the sidebar")

st.sidebar.title("Select a method")
st.sidebar.radio("Method", ["Snowflake Connection", "Snowflake Connector"])

# Create a form in the sidebar in the shape of a table with one column "New cap" and four rows: "Contacted Debit", "Contactless Debit", "Online Debit", "Personal Credit":
form = st.sidebar.form(key="form")
contacted_debit_cap = form.text_input("Contacted Debit", value="0")
contactless_debit_cap = form.text_input("Contactless Debit", value="0")
online_debit_cap = form.text_input("Online Debit", value="0")
personal_credit_cap = form.text_input("Personal Credit", value="0")
submit_button = form.form_submit_button("Estimate Impact")

#Capture the values from the form into a new dataframe:
import pandas as pd
data = pd.DataFrame({
    "New cap": ["Contacted Debit", "Contactless Debit", "Online Debit", "Personal Credit"],
    "Value": [contacted_debit_cap, contactless_debit_cap, online_debit_cap, personal_credit_cap]
})

#Display the dataframe when the form is submitted   
if submit_button:
    st.dataframe(data)

