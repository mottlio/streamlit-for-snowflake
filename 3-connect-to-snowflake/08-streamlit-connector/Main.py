import streamlit as st
import uuid

st.title("Interchange Fee Estimation Tool")

st.write("This tool estimates the impact of changing interchange fee caps on the flows of interchange fees between acquirers and issuers. The tool uses data from the Snowflake database.")
st.write("The impact is estimated based on the assumption that the transaction value does not change. The tool calculates the new interchange fee based on the new cap and compares it to the actual interchange fee paid in 2023. The difference is the estimated impact of the cap change. The tool also calculates the new flow of interchange fees between acquirers and issuers based on the new cap.")

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

#Connect to Snowflake and run a query to get the data:

st.header("Estimate impact of cap changes on ICF flows")

#Snowflake connection parameters are stored in secrets.toml file in the same folder (added to .gitignore)
# You'll need to create your own secrets.toml file to connect to Snowflake (or choose a different connection method)

conn = st.connection("snowflake")
flows_df = conn.query(
    "select * from DATAANALYTICS_DB_DEV.dbt_michalm.calculate_icf_flows_2023_approach3", ttl=3600, show_spinner="Fetching interchange data...")

caps_df = conn.query(
    """
with icf_caps as 
(select transaction_category as category, 
transaction_icf_cap_description as cap, 
round(sum(icf_paid)/sum(value_of_transactions)*100, 2) as icf_rate_reported, 
transaction_icf_cap
from DATAANALYTICS_DB_DEV.dbt_michalm.calculate_icf_flows_2023_approach3 group by 1, 2, 4)
select
category,
cap,
icf_rate_reported,
case
when cap = 'Unregulated' then 5
else transaction_icf_cap
end
as new_cap
from icf_caps
"""
    ,ttl=3600, show_spinner="Fetching fee cap information...")

st.info("Change ICF caps in the 'NEW_CAP' column and press the 'ESTIMATE IMPACT' button.")

# Define a variable as a key of the data editor.
if 'dek' not in st.session_state:
    st.session_state.dek = str(uuid.uuid4())

def reset_editor():
    # Change the key of the data editor to start over.
    st.session_state.dek = str(uuid.uuid4())


def bgcolor_correct_or_incorrect(value):
    bgcolor = "#F8F9FB"
    return f"background-color: {bgcolor};"

# Create empty dataframe 'changes':
changes = pd.DataFrame()

# Create a function called update_changes which, when it runs, updates the value of 'changes' dataframe with the value of edited_rows

def data_editor_changed():
    global changes
    changes = pd.DataFrame.from_dict(st.session_state[st.session_state.dek]["edited_rows"]).transpose()
    
   
new_caps_df = st.data_editor(caps_df.style.applymap(bgcolor_correct_or_incorrect, subset=['CATEGORY', 'CAP', 'ICF_RATE_REPORTED']).format({'ICF_RATE_REPORTED': '{:,}%'}), 
    key=st.session_state.dek,
    on_change = data_editor_changed,
    column_config={
        1: "Transaction Category",
        2: "ICF Cap",
        3: st.column_config.NumberColumn(
            "Avg 2023 ICF (%)",
            help="ICF rate actually applied (%)",
            format="%.2f %%"
        ),
        4: st.column_config.NumberColumn(
            "New Cap",
            help="Choose a new ICF cap value (%)",
            min_value=0,
            max_value=5,
            step=0.1,
            # format with a percent sign
            format="%.2f %%"
        )
    },
    disabled=[1, 2, 3],
    hide_index=True)

col1, col2, col3 = st.columns([1,1,1])

with col1:
    estimate_impact_button = st.button("Estimate Impact", on_click = data_editor_changed)
with col2:
    st.empty()
with col3:
    st.button("Reset", on_click=reset_editor)

# Create a function that will chaneg a cell background depending on whether impact is positive or negative

def bgcolor_positive_or_negative(value):
    bgcolor = "lightcoral" if value < 0 else "lightgreen"
    return f"background-color: {bgcolor};"

# If the estimate_impact_button is clicked, calculate the impact of the new caps on the ICF flows:

changes_df = pd.DataFrame.from_dict(st.session_state[st.session_state.dek]["edited_rows"]).transpose()


if estimate_impact_button:

    st.subheader("Summary of proposed cap changes")
    if changes_df.empty:
        st.warning("No changes to the fee caps have been made.")
    else:
        index_mapping = {0: 'Personal Credit', 1: 'Contactless Debit', 2: 'Online/Other Debit', 3: 'Commercial Credit', 4: 'International'}
        changes_df['Transaction Category'] = changes_df.index.map(index_mapping)
        # Select the columns 'Transaction Category' and 'New Cap' from the changes_df dataframe:
        changes_df = pd.DataFrame(changes_df[['Transaction Category', 'NEW_CAP']])
        st.dataframe(
            changes_df, hide_index=True,
            column_config={
            1: "Transaction Category",
            2: st.column_config.NumberColumn(
                "New Cap",
                help="New hypothetical ICF cap (%)",
                format="%.2f %%"
            )
            }
            )
    #st.dataframe(new_caps_df, hide_index=True)

    # In the new_caps_df dataframe create a new column 'applied_rate' which is the least of the 'new_cap' and 'icf_rate_reported' columns:
    #new_caps_df['applied_rate'] = new_caps_df[['NEW_CAP', 'ICF_RATE_REPORTED']].min(axis=1)
    
    # Create a new dataframe by selecting the columns 'transaction_category' and 'new_cap' from the new_caps_df dataframe:
    
    new_caps_df = new_caps_df[['CATEGORY', 'NEW_CAP']]

    # Merge the new_caps_df dataframe with the flows_df dataframe on the column 'transaction_category':
    flows_df = flows_df.merge(new_caps_df, left_on='TRANSACTION_CATEGORY', right_on='CATEGORY', how='left')

    #Transform the 'REPORTED_ICF_RATE' column by multiplying it by 100 (to compare with NEW_CAP):
    flows_df['REPORTED_ICF_RATE'] = flows_df['REPORTED_ICF_RATE'] * 100

    #Create a new column 'applied_rate' in the flows_df dataframe which is the least of the 'NEW_CAP' and 'icf_rate_reported' columns:
    flows_df['applied_rate'] = flows_df[['NEW_CAP', 'REPORTED_ICF_RATE']].min(axis=1)

    #Create a new column 'estimated_icf" in the flows_df dataframe which is the product of the 'value_of_transactions' and 'applied_rate' columns:
    flows_df['new_icf_paid'] = flows_df['VALUE_OF_TRANSACTIONS'] * flows_df['applied_rate'] / 100
    #Create a new column 'impact' in the flows_df dataframe which is the difference between the 'estimated_icf' and 'icf_paid' columns:
    flows_df['acquirer_icf_impact'] = flows_df['new_icf_paid'] - flows_df['ICF_PAID']
    #Create a new colun 'new flow' in the flows_df dataframe which is the product of 'new_icf_paid' and 'ISSUER_CATEGORY_ICF_SHARE' columns:
    flows_df['new_flow'] = flows_df['new_icf_paid'] * flows_df['ISSUER_CATEGORY_ICF_SHARE']


    st.subheader("Estimated impact")

    tabs = st.tabs(["Total ICF", "Personal Credit", "Contactless Debit", "Online Debit", "Commercial Credit", "International"])
    
    #Total ICF flows
    
    #Function which creates a summary table:

    def flows_summary_table(flows_df):
        #Create a new dataframe 'icf_flows_total' by grouping the flows_df dataframe by 'ACQUIRER' and 'ISSUER' columns and summing the 'ICF_FLOW' and 'new_flow' columns:
        icf_flows_total = flows_df.groupby(['ACQUIRER', 'ISSUER']).agg({'ICF_FLOW': 'sum', 'new_flow': 'sum'}).reset_index()
        #Create a new dataframe 'icf_paid_table' by grouping 'icf_flows_total' by acquirer and summing the 'ICF_FLOW' and 'new_flow' columns and renaming them to 'icf_paid' and 'new_icf_paid' respectively:
        icf_paid_table = icf_flows_total.groupby('ACQUIRER').agg({'ICF_FLOW': 'sum', 'new_flow': 'sum'}).reset_index()
        #Rename columns
        icf_paid_table.rename(columns={'ICF_FLOW': 'icf_paid', 'new_flow': 'new_icf_paid'}, inplace=True)
        #Create a new dataframe 'icf_received_table' by grouping 'icf_flows_total' by issuer and summing the 'ICF_FLOW' and 'new_flow' columns:
        icf_received_table = icf_flows_total.groupby('ISSUER').agg({'ICF_FLOW': 'sum', 'new_flow': 'sum'}).reset_index()
        #Rename columns
        icf_received_table.rename(columns={'ICF_FLOW': 'icf_received', 'new_flow': 'new_icf_received'}, inplace=True)
        #Create a new dataframe 'icf_flows_table' as a full join of 'icf_paid_table' and 'icf_received_table' on the 'ACQUIRER' and 'ISSUER' columns:
        icf_flows_table = icf_paid_table.merge(icf_received_table, left_on='ACQUIRER', right_on='ISSUER', how='outer')
        #Merge the ACQUIRER and ISSUER columns into one 'company' column:
        icf_flows_table['company'] = icf_flows_table['ACQUIRER'].combine_first(icf_flows_table['ISSUER'])
        #Fill the missing values in columns with 0:
        icf_flows_table.fillna(0, inplace=True)
        return icf_flows_table
    
    icf_flows_table_total = flows_summary_table(flows_df)

    #Calculate the sum of the column 'icf_received" and format it as dollars:
    icf_received_total_2023 = icf_flows_table_total['icf_received'].sum()
    
    #Calculate the sum of the column 'new_icf_received":
    icf_received_total_new = icf_flows_table_total['new_icf_received'].sum()
    
    def impact_summary_table(icf_flows_table):
        #Create new columns 'old_balance' and 'new_balance' in the icf_flows_table dataframe which are the difference between 'icf_paid' and 'icf_received' and 'new_icf_paid' and 'new_icf_received' columns respectively:
        icf_flows_table['2023_net_position'] = icf_flows_table['icf_received'] - icf_flows_table['icf_paid']
        icf_flows_table['estimated_net_position'] = icf_flows_table['new_icf_received'] - icf_flows_table['new_icf_paid']
        icf_flows_table['estimated_impact'] = icf_flows_table['estimated_net_position'] - icf_flows_table['2023_net_position']
        #Drop the ACQUIRER and ISSUER columns and select the 'company', 'icf_paid', 'icf_received', 'old_balance' 'new_icf_paid', 'new_icf_received', 'new_balance' columns:
        icf_flows_table = icf_flows_table.drop(['ACQUIRER', 'ISSUER'], axis=1)[['company', 'estimated_impact','2023_net_position', 'estimated_net_position']]

        # Style the icf_flows_table dataframe:
        # Round all numeric values in the dataframe to a full number
        icf_flows_table = icf_flows_table.round(0)
        icf_flows_table = icf_flows_table.style.applymap(bgcolor_positive_or_negative, subset=['estimated_impact']).format({'estimated_impact': '${:,}', 'estimated_net_position': '${:,}', '2023_net_position': '${:,}'})
    
        return icf_flows_table
    
    total_impact_table = impact_summary_table(icf_flows_table_total)

    tabs[0].markdown(f"""Interchange fees paid in 2023: {"${:,.2f} million".format(icf_received_total_2023 / 1_000_000)}""")
    tabs[0].markdown(f"""Estimated ICF based on new caps: {"${:,.2f} million".format(icf_received_total_new / 1_000_000)}""")
    tabs[0].markdown(f"""Impact of cap changes: {"${:,.2f} million".format((icf_received_total_new - icf_received_total_2023) / 1_000_000)}""")

    tabs[0].dataframe(total_impact_table, hide_index=True)
    
    
    # Personal Credit ICF Flows

    #Create a new dataframe 'icf_flows_personal_credit' by filtering flows_df on TRANSACTION_CATEGORY = 'Personal Credit'
    icf_flows_personal_credit = flows_df[flows_df['TRANSACTION_CATEGORY'] == 'Personal Credit']
    
    #Create a new dataframe 'icf_flows_table_personal_credit' by applying the function flows_summary_table to the icf_flows_personal_credit dataframe:
    icf_flows_table_personal_credit = flows_summary_table(icf_flows_personal_credit)

    #Create a new dataframe 'impact_table_personal_credit' by applying the function impact_summary_table to the icf_flows_table_personal_credit dataframe:
    impact_table_personal_credit = impact_summary_table(icf_flows_table_personal_credit)
    
    #Calculate the sum of the column 'icf_received" and format it as dollars:
    icf_received_personal_credit_2023 = icf_flows_table_personal_credit['icf_received'].sum()
    
    #Calculate the sum of the column 'new_icf_received":
    icf_received_personal_credit_new = icf_flows_table_personal_credit['new_icf_received'].sum()
    
    tabs[1].markdown(f"""Interchange fees paid in 2023: {"${:,.2f} million".format(icf_received_personal_credit_2023 / 1_000_000)}""")
    tabs[1].markdown(f"""Estimated ICF based on new caps: {"${:,.2f} million".format(icf_received_personal_credit_new / 1_000_000)}""")
    tabs[1].markdown(f"""Impact of cap changes: {"${:,.2f} million".format((icf_received_personal_credit_new - icf_received_personal_credit_2023) / 1_000_000)}""")

    tabs[1].dataframe(impact_table_personal_credit, hide_index=True)
    
    # Contactless Debit ICF Flows

    #Create a new dataframe 'icf_flows_contactless_debit' by filtering flows_df on TRANSACTION_CATEGORY = 'Contactless Debit'
    icf_flows_contactless_debit = flows_df[flows_df['TRANSACTION_CATEGORY'] == 'Contactless Debit']

    #Create a new dataframe 'icf_flows_table_contactless_debit' by applying the function flows_summary_table to the icf_flows_contactless_debit dataframe:
    icf_flows_table_contactless_debit = flows_summary_table(icf_flows_contactless_debit)

    #Create a new dataframe 'impact_table_contactless_debit' by applying the function impact_summary_table to the icf_flows_table_contactless_debit dataframe:
    impact_table_contactless_debit = impact_summary_table(icf_flows_table_contactless_debit)

    #Calculate the sum of the column 'icf_received" and format it as dollars:
    icf_received_contactless_debit_2023 = icf_flows_table_contactless_debit['icf_received'].sum()

    #Calculate the sum of the column 'new_icf_received":
    icf_received_contactless_debit_new = icf_flows_table_contactless_debit['new_icf_received'].sum()

    tabs[2].markdown(f"""Interchange fees paid in 2023: {"${:,.2f} million".format(icf_received_contactless_debit_2023 / 1_000_000)}""")
    tabs[2].markdown(f"""Estimated ICF based on new caps: {"${:,.2f} million".format(icf_received_contactless_debit_new / 1_000_000)}""")
    tabs[2].markdown(f"""Impact of cap changes: {"${:,.2f} million".format((icf_received_contactless_debit_new - icf_received_contactless_debit_2023) / 1_000_000)}""")

    tabs[2].dataframe(impact_table_contactless_debit, hide_index=True)

    # Online Debit ICF Flows

    #Create a new dataframe 'icf_flows_online_debit' by filtering flows_df on TRANSACTION_CATEGORY = 'Online Debit'
    icf_flows_online_debit = flows_df[flows_df['TRANSACTION_CATEGORY'] == 'Online/Other Debit']

    #Create a new dataframe 'icf_flows_table_online_debit' by applying the function flows_summary_table to the icf_flows_online_debit dataframe:
    icf_flows_table_online_debit = flows_summary_table(icf_flows_online_debit)

    #Create a new dataframe 'impact_table_online_debit' by applying the function impact_summary_table to the icf_flows_table_online_debit dataframe:
    impact_table_online_debit = impact_summary_table(icf_flows_table_online_debit)

    #Calculate the sum of the column 'icf_received" and format it as dollars:
    icf_received_online_debit_2023 = icf_flows_table_online_debit['icf_received'].sum()

    #Calculate the sum of the column 'new_icf_received":
    icf_received_online_debit_new = icf_flows_table_online_debit['new_icf_received'].sum()

    tabs[3].markdown(f"""Interchange fees paid in 2023: {"${:,.2f} million".format(icf_received_online_debit_2023 / 1_000_000)}""")
    tabs[3].markdown(f"""Estimated ICF based on new caps: {"${:,.2f} million".format(icf_received_online_debit_new / 1_000_000)}""")
    tabs[3].markdown(f"""Impact of cap changes: {"${:,.2f} million".format((icf_received_online_debit_new - icf_received_online_debit_2023) / 1_000_000)}""")

    tabs[3].dataframe(impact_table_online_debit, hide_index=True)

    # Commercial Credit ICF Flows

    #Create a new dataframe 'icf_flows_commercial_credit' by filtering flows_df on TRANSACTION_CATEGORY = 'Commercial Credit'
    icf_flows_commercial_credit = flows_df[flows_df['TRANSACTION_CATEGORY'] == 'Commercial Credit']

    #Create a new dataframe 'icf_flows_table_commercial_credit' by applying the function flows_summary_table to the icf_flows_commercial_credit dataframe:
    icf_flows_table_commercial_credit = flows_summary_table(icf_flows_commercial_credit)

    #Create a new dataframe 'impact_table_commercial_credit' by applying the function impact_summary_table to the icf_flows_table_commercial_credit dataframe:
    impact_table_commercial_credit = impact_summary_table(icf_flows_table_commercial_credit)

    #Calculate the sum of the column 'icf_received" and format it as dollars:
    icf_received_commercial_credit_2023 = icf_flows_table_commercial_credit['icf_received'].sum()

    #Calculate the sum of the column 'new_icf_received":
    icf_received_commercial_credit_new = icf_flows_table_commercial_credit['new_icf_received'].sum()

    tabs[4].markdown(f"""Interchange fees paid in 2023: {"${:,.2f} million".format(icf_received_commercial_credit_2023 / 1_000_000)}""")
    tabs[4].markdown(f"""Estimated ICF based on new caps: {"${:,.2f} million".format(icf_received_commercial_credit_new / 1_000_000)}""")
    tabs[4].markdown(f"""Impact of cap changes: {"${:,.2f} million".format((icf_received_commercial_credit_new - icf_received_commercial_credit_2023) / 1_000_000)}""")

    tabs[4].dataframe(impact_table_commercial_credit, hide_index=True)

    # International ICF Flows

    #Create a new dataframe 'icf_flows_international' by filtering flows_df on TRANSACTION_CATEGORY = 'International'
    icf_flows_international = flows_df[flows_df['TRANSACTION_CATEGORY'] == 'International']

    #Create a new dataframe 'icf_flows_table_international' by applying the function flows_summary_table to the icf_flows_international dataframe:
    icf_flows_table_international = flows_summary_table(icf_flows_international)

    #Create a new dataframe 'impact_table_international' by applying the function impact_summary_table to the icf_flows_table_international dataframe:
    impact_table_international = impact_summary_table(icf_flows_table_international)

    #Calculate the sum of the column 'icf_received" and format it as dollars:
    icf_received_international_2023 = icf_flows_table_international['icf_received'].sum()

    #Calculate the sum of the column 'new_icf_received":
    icf_received_international_new = icf_flows_table_international['new_icf_received'].sum()

    tabs[5].markdown(f"""Interchange fees paid in 2023: {"${:,.2f} million".format(icf_received_international_2023 / 1_000_000)}""")
    tabs[5].markdown(f"""Estimated ICF based on new caps: {"${:,.2f} million".format(icf_received_international_new / 1_000_000)}""")
    tabs[5].markdown(f"""Impact of cap changes: {"${:,.2f} million".format((icf_received_international_new - icf_received_international_2023) / 1_000_000)}""")

    tabs[5].dataframe(impact_table_international, hide_index=True)


