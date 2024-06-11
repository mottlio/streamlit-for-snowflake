
import pandas as pd
import os
import urllib.parse
import webbrowser
import streamlit as st
import plotly.graph_objects as go


#print(os.getcwd())
#change working directory to the first-app folder
#os.chdir('first-app')


st.title('Employee Hierarchy')

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


df = pd.read_csv("data/employees.csv", header = 0).convert_dtypes()
#Show the dataframe in the streamlit app
        
st.dataframe(df)    

labels = df[df.columns[0]]
parents = df[df.columns[1]]

data = go.Treemap(
    ids=labels,
    labels=labels,
    parents=parents,
    root_color="lightgrey"
)

fig = go.Figure(data)

st.plotly_chart(fig, use_container_width=True)

data2 = go.Icicle(
    ids=labels,
    labels=labels,
    parents=parents,
    root_color="lightgrey"
)

fig2 = go.Figure(data2)

st.plotly_chart(fig2, use_container_width=True)

data3 = go.Sunburst(
    ids=labels,
    labels=labels,
    parents=parents,
    root_color="lightgrey"
)

fig3 = go.Figure(data3)

st.plotly_chart(fig3, use_container_width=True)


data4 = go.Sankey(
    node = dict(label = labels),
    link = dict(
        source = [list(labels).index(x) for x in labels],
        target=[-1 if pd.isna(x) else list(labels).index(x) for x in labels],
        label=labels,
        value=list(range(1, len(labels)))
    )
)

fig4 = go.Figure(data4)

st.plotly_chart(fig4, use_container_width=True)

# create digraph for employee_name and manager_name

edges = ""
for index, row in df.iterrows():
    if not pd.isna(row.iloc[1]):
        edges += f'\t"{row.iloc[0]}" -> "{row.iloc[1]}";\n'

d = f'digraph {{\n{edges}}}'

st.graphviz_chart(d)

#url = f'http://magjac.com/graphviz-visual-editor/?dot={urllib.parse.quote(d)}'
#webbrowser.open(url)
#print(d)

