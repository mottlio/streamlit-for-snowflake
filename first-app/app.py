
import pandas as pd
import os
import urllib.parse
import webbrowser
import streamlit as st
import plotly.graph_objects as go
from io import StringIO


#print(os.getcwd())
#change working directory to the first-app folder
#os.chdir('first-app')

def getGraph(df):
    edges = ""
    for index, row in df.iterrows():
        if not pd.isna(row.iloc[1]):
            edges += f'\t"{row.iloc[0]}" -> "{row.iloc[1]}";\n'
    return f'digraph {{\n{edges}}}'

def OnShowList(filename):
    if "names" in st.session_state:
        filenames = st.session_state["names"]
        if filename in filenames:
            st.error("Critical file found")
            st.stop()
    


#Setting ttl in caching to 3600 seconds - entries in cache will expire after 1 hour
# Prevents reloading of the entire file each time a control changes
@st.cache_data(ttl=3600, show_spinner="Loading...")
def loadFile(filename):
    return pd.read_csv(filename, header = 0).convert_dtypes()

if "names" in st.session_state:
    filenames = st.session_state["names"]
else:
    filenames = ["employees.csv"]
    st.session_state["names"] = filenames

filename = "data/employees.csv"

st.title('ComCom Data Catalogue')
uploaded_file = st.sidebar.file_uploader("Choose a csv file", type = "csv", accept_multiple_files = False)
if uploaded_file is not None:
    filename = StringIO(uploaded_file.getvalue().decode("utf-8"))
    file = uploaded_file.name
    if file not in filenames:
        filenames.append(file)


btn = st.sidebar.button("Show Recent Files",
                        on_click=OnShowList, args=("portfolio.csv",))
if btn:
    for f in filenames:
        st.sidebar.write(f)

df_orig = loadFile(filename)
#Show the dataframe in the streamlit app
with st.sidebar:
    with st.form("my_form"):
        child = st.selectbox("Child Column Name", list(df_orig.columns), index = 0)
        parent = st.selectbox("Parent Column Name", list(df_orig.columns), index = 1)
        submit_button = st.form_submit_button("Refresh Data")
df = df_orig[[child, parent]]

st.sidebar.text_input("Snowflake Role")
st.sidebar.number_input("Role ID", min_value = 1, max_value = 100, value = 1, step = 1)
st.sidebar.date_input("Date of Birth")
st.sidebar.time_input("Time of Birth")
st.sidebar.color_picker("Favorite Color")
st.sidebar.slider("Number of Children", min_value = 0, max_value = 10, value = 5, step = 1)
st.sidebar.multiselect("Select Children", list(df[child]), default = list(df[child])[0:2])
st.sidebar.text_area("Comments", "Enter comments here")
st.sidebar.radio("Pick one", ["Cats", "Dogs", "Birds"])
st.sidebar.download_button("Download", "Download", "Click here to download")
st.sidebar.toggle("Toggle me")


tabs = st.tabs(["Source", "Graph", "Dot Code"])

tabs[0].dataframe(df)
tabs[0].data_editor(df)

tabs[1].graphviz_chart(getGraph(df))

url = f'http://magjac.com/graphviz-visual-editor/?dot={urllib.parse.quote(getGraph(df))}'
tabs[2].link_button("Visualize Online", url)
tabs[2].code(getGraph(df))

st.header("This is a header")
st.subheader("This is a subheader")
st.caption("Caption is here")

st.write("Typical text")

st.text("fixed text")

st.code("print('Hello, World!')\nprint('Im Bob!')")

st.markdown("This is **bold** and this is *italic*")

st.divider()

st.latex(r"\int_a^b x^2 dx")

st.error("This is an error message")

st.info("This is an info message")

st.warning("This is a warning message")

st.success("This is a success message")

st.link_button("Click here", "https://www.google.com")

#st.balloons()
#st.snow()



        
st.dataframe(df)    

labels = df[df.columns[0]]
parents = df[df.columns[1]]

def makeTreemap(labels, parents):
    data = go.Treemap(
        ids=labels,
        labels=labels,
        parents=parents,
        root_color="lightgrey"
    )
    fig = go.Figure(data)
    return fig

def makeIcicle(labels, parents):
    data = go.Icicle(
        ids=labels,
        labels=labels,
        parents=parents,
        root_color="lightgrey"
    )
    fig = go.Figure(data)
    return fig

def makeSunburst(labels, parents):
    data = go.Sunburst(
        ids=labels,
        labels=labels,
        parents=parents,
        root_color="lightgrey"
    )
    fig = go.Figure(data)
    return fig

def makeSankey(labels, parents):
    data = go.Sankey(
        node = dict(label = labels),
        link = dict(
            source = [list(labels).index(x) for x in labels],
            target=[-1 if pd.isna(x) else list(labels).index(x) for x in labels],
            label=labels,
            value=list(range(1, len(labels)))
        )
    )
    fig = go.Figure(data)
    return fig

st.title("Hierarchical Data Charts")



with st.expander("Treemap", expanded = True):
    fig = makeTreemap(labels, parents)
    st.plotly_chart(fig, use_container_width=True)

with st.expander("Icicle"):
    fig = makeIcicle(labels, parents)
    st.plotly_chart(fig, use_container_width=True)

with st.expander("Sunburst"):
    fig = makeSunburst(labels, parents)
    st.plotly_chart(fig, use_container_width=True)

with st.expander("Sankey"):    
    fig = makeSankey(labels, parents)
    st.plotly_chart(fig, use_container_width=True)

tabs = st.tabs(["Treemap", "Icicle", "Sunburst", "Sankey"])

with tabs[0]:
    fig = makeTreemap(labels, parents)
    st.plotly_chart(fig, use_container_width=True)

with tabs[1]:
    fig = makeIcicle(labels, parents)
    st.plotly_chart(fig, use_container_width=True)

with tabs[2]:
    fig = makeSunburst(labels, parents)
    st.plotly_chart(fig, use_container_width=True)

with tabs[3]:    
    fig = makeSankey(labels, parents)
    st.plotly_chart(fig, use_container_width=True)

cols = st.columns(3) # Side-by-side containers
cols[0].write("Column1")
cols[1].write("Column2")
cols[2].write("Column3")

# Use st.empty() as a place where new text can appear. Whenever you add new text, it will replace existing text

with st.empty():
    st.write("This is empty")
    st.write("This is not empty")

st.container() #Can only be one - can be populated with controls

first_container = st.container()
first_container.write("This is the first container")
st.write("outside of container")
first_container.write("This is still the first container")

st.sidebar.title("Employee Hierarchy")

st.sidebar.selectbox("Select a chart", ["Treemap", "Icicle", "Sunburst", "Sankey"])



# create digraph for employee_name and manager_name



#url = f'http://magjac.com/graphviz-visual-editor/?dot={urllib.parse.quote(d)}'
#webbrowser.open(url)
#print(d)

st.plotly_chart(fig, use_container_width=True)