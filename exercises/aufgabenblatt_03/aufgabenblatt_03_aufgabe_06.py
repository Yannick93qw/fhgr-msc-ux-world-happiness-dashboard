import math
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc

# new: plotly template="plotly_white", https://plotly.com/python/templates/

"""
Generates some sample data for a country. Samples is the number of data which should be generated.
Currently it creates a random happiness value per day.
"""
def generate_country_data(samples):
    dates = pd.date_range('2023-05-21', periods=samples, freq='1D')
    return pd.DataFrame({'date': dates, 'happiness': np.random.normal(loc=10, scale=10, size=samples)})


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

df = pd.DataFrame({'y': np.random.normal(loc=0, scale=10, size=1000), 'x': np.random.normal(loc=10, scale=2, size=1000)})

# The name of the countries which can be selected in the dropdown on tab 2.
countries = ["Switzerland", "Sweden"]

# Create dictionary where the keys are the name of the countries. This makes it easier to get out the specific data for a country.
df_countries = {country_name: generate_country_data(30) for country_name in countries}


# Read in real data...
df_real_data = pd.read_csv("./data.csv", encoding="utf-8")
df_real_data_grouped_by_country = df_real_data.groupby("Country Name")
real_countries = list(df_real_data["Country Name"].unique())

app.layout = html.Div([html.Div([html.H1("Dashboard 3")], className="header"), html.Div([dcc.Tabs(id="tabs", children=[
    dcc.Tab(label='Tab One', id="tab_1_graphs", children=[html.Div([
        dbc.Row([dbc.Col([dcc.Dropdown(options=['red','green','blue'], value='red', id='color', multi=False)], width=6),
                 dbc.Col([dcc.Slider(min=math.floor(df['y'].min()),max=math.ceil(df['y'].max()),id="min_value")], width=6)]),
        dbc.Row([dbc.Col([dcc.Graph(id="graph_1")],width=6),
                 dbc.Col([dcc.Graph(id="graph_2")],width=6)])], className="tab_content"),]),
        dcc.Tab(label='Tab Two', id="tab_2_graphs", children=[html.Div([
            dbc.Row([
                dbc.Col([dcc.Dropdown(options=countries, value=countries[0], id='countries', multi=False)], width=6), 
                dbc.Col([html.H1("Average Happiness")], width=6)]),
            dbc.Row([
                dbc.Col([dcc.Graph(id="tab_2_bar")], width=6),
                dbc.Col([html.H3(id="tab_2_avg_happiness")], width=6), ])
            ],className="tab_content")]),

        dcc.Tab(label='Tab Three', id="tab_3_graphs", children=[html.Div([
            dbc.Row([
                dbc.Col([dcc.Dropdown(options=real_countries, value=real_countries[0], id='real_countries', multi=False)], width=6), 
                dbc.Col([html.H1("Average Life Ladder")], width=6)]),
            dbc.Row([
                dbc.Col([dcc.Graph(id="tab_3_bar")], width=6),
                dbc.Col([html.H3(id="tab_3_avg_life_ladder")], width=6), ])
            ],className="tab_content")]),
        ])], className="content")])


# Tab 1
@app.callback(Output("graph_1", "figure"), Input("color", "value"))
def update_graph_1(dropdown_value_color):
    fig = px.histogram(df, x="y", color_discrete_sequence=[dropdown_value_color])
    fig.update_layout(template="plotly_white")
    return fig

# Tab 2
@app.callback(Output("tab_2_bar", "figure"), Input("countries", "value"))
def update_tab_2_bar(dropdown_countries_value):
    fig = px.bar(df_countries[dropdown_countries_value], x="date", y="happiness")
    fig.update_layout(template="plotly_white")
    return fig

@app.callback(Output("tab_2_avg_happiness", "children"), Input("countries", "value"))
def update_tab_2_avg_happiness(dropdown_countries_value):
    df_country = df_countries[dropdown_countries_value]
    avg = df_country["happiness"].mean()
    return f"{dropdown_countries_value} has an average happiness of {avg}"

# Tab 3 
@app.callback(Output("tab_3_bar", "figure"), Input("real_countries", "value"))
def update_tab_3_bar(dropdown_countries_value):
    df_real_country = df_real_data_grouped_by_country.get_group(dropdown_countries_value)
    print(df_real_country)
    fig = px.bar(df_real_country, x="Year", y="Life Ladder")
    fig.update_layout(template="plotly_white")
    return fig

@app.callback(Output("tab_3_avg_life_ladder", "children"), Input("real_countries", "value"))
def update_tab_3_avg_life_ladder(dropdown_countries_value):
    df_real_country = df_real_data_grouped_by_country.get_group(dropdown_countries_value)
    avg = df_real_country["Life Ladder"].mean()
    return f"{dropdown_countries_value} has an average Life Ladder of {avg}"


if __name__ == '__main__':
    app.run_server(debug=True, port=8000)
