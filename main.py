from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

INITIAL_COUNTRY_NAME = "Switzerland"
INITIAL_FIRST_FACTOR = "Perception"
INITIAL_SECOND_FACTOR = "Perception"
INITIAL_FROM_VALUE = "2008"

# TODO: Use proper factors...
AVAILABLE_FACTORS  = ["Perception", "Factor 2", "Factor 3"]

app = Dash(__name__, external_stylesheets=[dbc.themes.MATERIA])

def get_country_names(data):
    return list(set(data["Country Name"])) 

def get_country_years(data):
    return list(set(data["Year"])) 

def prepare_dataset():
    data = pd.read_csv("./data_cleaned.csv", encoding="UTF-8")
    return data

def prepare_layout():
    # Define basic layout
    app_header = dbc.Row([html.H1("World Happiness Dashboard")], className="border rounded p-2")

    # World Map
    world_map = html.Div([html.H5("Life Ladder Overview for Year ...", id="world_map_title"), dcc.Graph(id="world_map")])
    country_detail = html.Div([html.H5("Information about selected country"), html.Div(id="country_detail_container")])
    world_map_section = dbc.Row([dbc.Col([world_map], width=8), dbc.Col([country_detail], width=4)], className="border rounded p-2 my-3")

    # Scatter Plot
    first_factor_dropdown = dcc.Dropdown(options=AVAILABLE_FACTORS, id="first_factor", value=INITIAL_FIRST_FACTOR, multi=False)
    second_factor_dropdown = dcc.Dropdown(options=AVAILABLE_FACTORS, id="second_factor", value=INITIAL_SECOND_FACTOR, multi=False)
    first_factor_div = html.Div([dbc.Label("First Factor", html_for="first_factor"), first_factor_dropdown], className="mb-3")
    second_factor_div = html.Div([dbc.Label("Second Factor", html_for="second_factor"), second_factor_dropdown], className="mb-3")
    factors = dbc.Form([html.H5("Choose your two factors"), first_factor_div, second_factor_div])
    simplified_explanation = html.Div([html.H5("In a nuthsell"), html.Div(id="simplified_explanation_container")])
    scatter_plot = html.Div([html.H5("In a graph"), dcc.Graph(id="scatter_plot")])
    scatter_plot_section = dbc.Row([dbc.Col([factors], width=4), dbc.Col([simplified_explanation], width=4), dbc.Col([scatter_plot], width=4)], className="border rounded p-2 my-3")

    # Heatmap
    heatmap_section = dbc.Row([html.H5("Correlation Heatmap"), dcc.Graph(id="heatmap")], className="border rounded p-2 my-3") 

    # Filter
    country_dropdown = dcc.Dropdown(options=country_names, value=INITIAL_COUNTRY_NAME, id='selected_country', multi=False)
    country_div = html.Div([dbc.Label("Select country", html_for="selected_country"), country_dropdown], className="mb-3")
    from_dropdown = dcc.Dropdown(options=country_years, id="from", value=INITIAL_FROM_VALUE, multi=False)
    from_div = html.Div([dbc.Label("From", html_for="from"), from_dropdown], className="mb-3")
    floating_filter = dbc.Form([country_div, from_div], className="p-4 border rounded bg-light position-sticky shadow", style={"bottom": "10rem", "width": "60%", "left": "calc(50vw - 30%)"})

    return html.Div([app_header, world_map_section, scatter_plot_section, heatmap_section, floating_filter], className="p-4")

# Load Dataset and initial layout
df = prepare_dataset()
country_names = get_country_names(df)
country_years = get_country_years(df)
app.layout = prepare_layout() 

@app.callback(Output("country_detail_container", "children"), Input("selected_country", "value"))
def generate_country_detail(selected_country):
    # TODO: Display needed information such as Log GDP etc.
    overall_happiness_card = dbc.Card(dbc.CardBody([html.H6("Overall Happiness Score", className="card-title"), html.H4("8.2"), html.P("Ranked 12th in the World")]), className="my-3")
    return [overall_happiness_card, overall_happiness_card, overall_happiness_card, overall_happiness_card]

@app.callback(Output("simplified_explanation_container", "children"), Input("selected_country", "value"))
def generate_simplified_explanation_detail(selected_country):
    # TODO: Display proper factors etc.
    text_card = dbc.Card(dbc.CardBody([html.H6("Some useful and helpful explanation...")]), className="p-2 my-3")
    return [text_card, text_card]


@app.callback(Output("world_map", "figure"), Output("world_map_title", "children"), Input("from", "value"))
def update_world_map(from_value):
    # Implemented with reference to https://plotly.com/python/choropleth-maps/

    # As we cannot display values over a period of time (e.g from 2008 to 2012 etc.) we pick the selected from value (e.g 2008)
    dff = df.copy()
    dff = dff[(dff["Year"] == int(from_value))]
    locations = dff["Country Code"]
    z  = dff["Life Ladder"]
    text = dff["Country Name"]

    fig = go.Figure(data = go.Choropleth(
        locations = locations,
        z = z,
        text = text,
        colorscale="Greens"
    ))
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            geo=dict(showframe=False, projection_type="equirectangular")
    )

    world_map_title = f"Life Ladder Overview for Year {from_value}"
    return fig, world_map_title

if __name__ == '__main__':
    app.run_server(debug=True, port=8014)
