import math
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# generate random normal distributed data for x and y
# and store it in a pandas DataFrame

df = pd.DataFrame({'y': np.random.normal(loc=0, scale=10, size=1000),
                   'x': np.random.normal(loc=10, scale=2, size=1000)})

app.layout = html.Div([html.H1("Dashboard 2"),
    dbc.Row([
        dbc.Col([dcc.Dropdown(options=['red', 'green', 'blue'], value='red', id='color_histogram', multi=False)], width=6),
        dbc.Col([dcc.Dropdown(options=['red', 'green', 'blue'], value='red', id='color_scatter', multi=False)], width=6),
    ]),
    dbc.Row([
        dbc.Col([dcc.RangeSlider(min=math.floor(df['y'].min()), max=math.ceil(df['y'].max()), allowCross=False, tooltip={"placement": "bottom", "always_visible": True}, id="range_slider_histogram")
            ], width=6),
        dbc.Col([dcc.RangeSlider(min=math.floor(df['y'].min()), max=math.ceil(df['y'].max()), allowCross=False, tooltip={"placement": "bottom", "always_visible": True}, id="range_slider_scatter")
            ], width=6),
    ]),
    dbc.Row([
        dbc.Col([dcc.Graph(id="histogram")], width=6),
        dbc.Col([dcc.Graph(id="scatter")], width=6)
    ], className="m-4")])

@app.callback(Output("histogram", "figure"), Input("color_histogram", "value"), Input("range_slider_histogram", "value"))
def update_histogram(color, range_slider_value):
    dff = df.copy()
    if range_slider_value != None:    
        min_value = range_slider_value[0]
        max_value = range_slider_value[1]
        dff = dff[(dff["y"] >= min_value) & (dff["y"] <= max_value)]
    fig = px.histogram(dff, x="y", color_discrete_sequence=[color])
    fig.update_layout()
    return fig

@app.callback(Output("scatter", "figure"), Input("color_scatter", "value"), Input("range_slider_scatter", "value"))
def update_scatter(color, range_slider_value):
    dff = df.copy()
    if range_slider_value != None:    
        min_value = range_slider_value[0]
        max_value = range_slider_value[1]
        dff = dff[(dff["y"] >= min_value) & (dff["y"] <= max_value)]
    fig = px.scatter(dff, x="y", color_discrete_sequence=[color])
    fig.update_layout()
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8000)
