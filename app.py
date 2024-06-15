import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# Configure the page
st.set_page_config(
    page_title="Zurich in Numbers",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS to enhance the design
st.markdown("""
    <style>
        .main {
            background-color: #f5f5f5;
        }
        h1 {
            color: #3D4A5A;
        }
        h2 {
            color: #3D4A5A;
        }
        .main p {
            color: #3D4A5A;
            font-size: 24px;

        }
        .st-bx, .st-bt, .st-cn, .st-al {
            margin-bottom: 2px;
        }
        .sidebar-header{
            color: white !important;
            font-size: 24px;
            font-weight: bold;
        }
        .sidebar p {
            color: white !important;
        }

    </style>
""", unsafe_allow_html=True)



# Title and Description
st.title(":bar_chart: Zurich in Numbers Dashboard :bar_chart:")
st.markdown("""
Explore the criminal activities over time, median income, and nationality distribution across various districts (Kreise) in Zurich.
""")
# Tab layout
tabs = st.tabs(["Crimes Over Time", "Median Income","Nationality Distribution by District"])

# Load the data
@st.cache_data
def load_data():
    data = pd.read_csv("data/Clean_Zurich_Data_Income_Crime_Nationalities.csv")
    return data

data = load_data()
years = data["Year"].unique()

# Load GeoJSON data
@st.cache_data
def load_geojson():
    with open("data/stzh.adm_stadtkreise_a.json") as f:
        geojson_data = json.load(f)
    return geojson_data

geojson_data = load_geojson()


topics = ["Crimes","Median Income","Nationality Count"]

def plot_data(df,topic):
    # Plot the line chart for criminal incidents by year 
    df_t = df.groupby("Year")[topic].mean().reset_index()
    st.header(topic + " Over Time")
    fig_criminal_growth = go.Figure()

    if "All" in district_select:
        fig_criminal_growth.add_trace(go.Scatter(
            x=df["Year"],
            y=df["topic"],
            mode='lines+markers',
            name='All Straftaten',
            hovertemplate='Year: %{x} <br>: {topic} %{y}'
        ))
    else:
        for district in district_select:
            tempo = df[df["District"] == district]
            fig_criminal_growth.add_trace(go.Scatter(
                x=tempo["Year"],
                y=tempo[topic],
                mode='lines+markers',
                name=topic + ' in ' + district,
                hovertemplate=f'District: {district} <br>Year: %{{x}} <br>{topic}: %{{y}}'
            ))

    # Add a trace for the mean criminal incidents across all districts
    fig_criminal_growth.add_trace(go.Scatter(
        x=df_t["Year"],
        y=df_t[topic],
        mode='lines+markers',
        name=topic +' mean',
        hovertemplate=f'Year: %{{x}} <br>{topic}: %{{y}}'
    ))

    fig_criminal_growth.update_layout(
        xaxis_title='Year',
        yaxis_title=topic,
        showlegend=True,
        template='plotly_white'
    )

    st.plotly_chart(fig_criminal_growth, use_container_width=True)


    # Plot the box chart for criminal incidents by year and Kreis
    st.header(topic + "by District for 2009-2022")
    fig_criminal_box = go.Figure()

    if "All" in district_select:
        fig_criminal_box.add_trace(go.Box(
                x=df["District"],
                y=df[topic],
                name=topic+ 'in '+kreis,
                hovertemplate=f'District: %{{x}} <br>{topic}: %{{y}}' ))
    else:
        for kreis in district_select:
            tempo = df[df["District"]==kreis]
            fig_criminal_box.add_trace(go.Box(
                    x=tempo["District"],
                    y=tempo[topic],
                    name=topic + 'in '+kreis,
                    hovertemplate=f'District: %{{x}} <br>{topic}: %{{y}}'))


        fig_criminal_box.update_layout(
                xaxis_title='District',
            yaxis_title=topic,
            showlegend=True,
            template='plotly_white'
        )

    st.plotly_chart(fig_criminal_box, use_container_width=True)
    if topic == "Crimes":
        value_list = ["Crimes", "C/P"]
    elif topic == "Median Income":
        value_list = ["Median Income", "M/P"]
    else:
        value_list = ["Nationality Count", "N/P"]

    if toggle_adjusted_data:
        flag = 1
    else:
        flag = 0
    # Plot the choropleth map for total incidents
    st.header(topic +" by Districts")
    fig_total = px.choropleth_mapbox(   
        df[df["Year"]==year_slider], 
        geojson=geojson_data, 
        locations='District',
            color=value_list[flag],
        featureidkey="properties.bezeichnung",  
        color_continuous_scale="Plasma",
        range_color=(df[df["Year"]==year_slider][value_list[flag]].min(), df[df["Year"]==year_slider][value_list[flag]].max()),
        mapbox_style="open-street-map",
        zoom=10.8,
        center={"lat": 47.3769, "lon": 8.5417},
        opacity=0.5,
        hover_name="District"
    )

    fig_total.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0}
    )

    st.plotly_chart(fig_total, use_container_width=True)



st.sidebar.markdown('<div class="sidebar-header">Settings</div>', unsafe_allow_html=True)

# Sidebar for year selection
districts = data["District"].unique()
districts = sorted(districts, key=lambda x: int(x.split('Kreis ')[1]))
district_select = st.sidebar.multiselect("Select Districts", districts, default="Kreis 1")
year_slider = st.sidebar.slider('Select Year', 2009, 2021, 2021)
toggle_adjusted_data = st.sidebar.checkbox("Adjust Data by population")

with tabs[0]:  
    plot_data(data,topics[0])

with tabs[1]:  
    plot_data(data,topics[1])

with tabs[2]:  
    plot_data(data,topics[2])

# Footer
st.markdown("""
---
**Data Source**: [Stadt Zurich Open Data](https://data.stadt-zuerich.ch)
""")


