import math

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc

INITIAL_COUNTRY_NAME = "Switzerland"

app = Dash(__name__, external_stylesheets=[dbc.themes.MATERIA])

def get_country_names(data):
    return list(set(data["Country Name"])) 

def get_country_data(data, country_name):
    return data.get_group(country_name)

def prepare_dataset():
    data = pd.read_csv("./data.csv", encoding="UTF-8")
    country_names = get_country_names(data) 
    grouped_data = data.groupby("Country Name")
    return (grouped_data, country_names)

def prepare_layout():
    # Define basic layout
    app_header = dbc.Row([html.H1("World Happiness Dashboard")], className="border rounded p-2")

    # World Map
    world_map = html.Div([html.H5("Choose your country of interest"), dcc.Graph(id="world_map")])
    country_detail = html.Div([html.H5("Information about selected country"), html.Div(id="country_detail_container")])
    world_map_section = dbc.Row([dbc.Col([world_map], width=8), dbc.Col([country_detail], width=4)], className="border rounded p-2 my-3")

    # Scatter Plot
    factors = html.Div([html.H5("Choose your two factors"), html.Div(id="factors_container")])
    simplified_explanation = html.Div([html.H5("In a nuthsell"), html.Div(id="simplified_explanation_container")])
    scatter_plot = html.Div([html.H5("In a graph"), dcc.Graph(id="scatter_plot")])
    scatter_plot_section = dbc.Row([dbc.Col([factors], width=4), dbc.Col([simplified_explanation], width=4), dbc.Col([scatter_plot], width=4)], className="border rounded p-2 my-3")

    # Heatmap
    heatmap_section = dbc.Row([html.H5("Correlation Heatmap"), dcc.Graph(id="heatmap")], className="border rounded p-2 my-3") 

    # Filter
    country_dropdown = dcc.Dropdown(options=country_names, value=INITIAL_COUNTRY_NAME, id='selected_country', multi=False)
    country_div = html.Div([dbc.Label("Select country", html_for="selected_country"), country_dropdown], className="mb-3")
    from_dropdown = dcc.Dropdown(options=[], id="from", multi=False)
    from_div = html.Div([dbc.Label("From", html_for="from"), from_dropdown], className="mb-3")
    to_dropdown = dcc.Dropdown(options=[], id="to", multi=False)
    to_div = html.Div([dbc.Label("To", html_for="to"), to_dropdown], className="mb-3")
    floating_filter = dbc.Form([country_div, from_div, to_div], className="p-4 border rounded bg-light position-sticky shadow", style={"bottom": "1rem", "width": "60%", "left": "calc(50vw - 30%)"})

    return html.Div([app_header, world_map_section, scatter_plot_section, heatmap_section, floating_filter], className="p-4")

# Load Dataset and initial layout
df, country_names = prepare_dataset()
app.layout = prepare_layout() 

@app.callback(Output("country_detail_container", "children"), Input("selected_country", "value"))
def generate_country_detail(selected_country):
    # TODO: Display needed information such as Log GDP etc.
    overall_happiness_card = dbc.Card(dbc.CardBody([html.H6("Overall Happiness Score", className="card-title"), html.H4("8.2"), html.P("Ranked 12th in the World")]), className="my-3")
    return [overall_happiness_card, overall_happiness_card, overall_happiness_card, overall_happiness_card]

@app.callback(Output("factors_container", "children"), Input("selected_country", "value"))
def generate_factors_detail(selected_country):
    # TODO: Display proper factors etc.
    factors_description = [("Perception", "Subtitle"), ("Title 2", "Subtitle 2"), ("Title 2", "Subtitle 2"), ("Title 2", "Subtitle 2"), ("Title 2", "Subtitle 2")]
    detail = [dbc.Button(f"{title} - {subtitle}", className="w-100 my-2") for title, subtitle in factors_description]
    return detail

@app.callback(Output("simplified_explanation_container", "children"), Input("selected_country", "value"))
def generate_simplified_explanation_detail(selected_country):
    # TODO: Display proper factors etc.
    text_card = dbc.Card(dbc.CardBody([html.H6("Some useful and helpful explanation...")]), className="p-2 my-3")
    return [text_card, text_card]


@app.callback(Output("world_map", "figure"), Input("selected_country", "value"))
def update_world_map(selected_country):
    df = px.data.election()
    geojson = px.data.election_geojson()
    fig = px.choropleth(df, geojson=geojson, locations="district", featureidkey="properties.district", projection="mercator", range_color=[0, 6500])
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

# TODO: Implement Updating and drawing Scatter plot



if __name__ == '__main__':
    app.run_server(debug=True, port=8014)
