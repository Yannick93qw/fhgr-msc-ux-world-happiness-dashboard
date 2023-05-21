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
                       dbc.Row([dbc.Col([dcc.RangeSlider(min=math.floor(df['y'].min()), max=math.ceil(df['y'].max()), allowCross=False , id="range_slider")
                                         ], width=6),
                                dbc.Col([dcc.Dropdown(options=['red', 'green', 'blue'], value='red', id='color', multi=False)], width=6),
                                ]),
                       dbc.Row([dbc.Col([dcc.Graph(id="histogram")], width=6),
                                dbc.Col([dcc.Graph(id="scatter")], width=6)
                                ])], className="m-4")


@app.callback(Output("scatter", "figure"), Input("color", "value"))
def update_scatter(dropdown_value_color):
    fig = px.scatter(df, x="y", color_discrete_sequence=[dropdown_value_color])
    fig.update_layout()
    return fig


@app.callback(Output("histogram", "figure"), Input("range_slider", "value"))
def update_histogram(range_slider):
    dff = df.copy()
    # Check if we actually have a value and we have our two expected values (length of 2 for min and max.)
    if range_slider is not None and len(range_slider) == 2:
        min_value = range_slider[0]
        max_value = range_slider[1]
        # Filter by min and max value
        dff = df[(df['y'] >= min_value) & (df['y'] <= max_value)]
    fig = px.histogram(dff, x='x', y='y')
    fig.update_layout()
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8000)
