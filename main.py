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
    # Because a set is not ensured to be sorted the right way we need to explicitly sort here
    return list(sorted(set(data["Year"]))) 

def prepare_dataset():
    data = pd.read_csv("./data_cleaned.csv", encoding="UTF-8")
    # Sort descending by year (Reference: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html)
    data = data.sort_values(by="Year", ascending=True)
    return data

def generate_world_map():
    # Implemented with reference to: 
    # - https://plotly.com/python/choropleth-maps/
    # - https://stackoverflow.com/questions/70773315/how-to-colorize-lands-which-have-missing-values-and-get-their-name-in-plotly-cho
    # We decided not to generate data for some missing countries (like setting the value to 999) etc.
    # As a consequence of this not all countries will be seen at every point in time (for example 2005 vs. 2022).

    dff = df.copy()
    hover_data = ["Country Name", "Life Ladder", "Year"]
    fig = px.choropleth(dff, locations=dff["Country Code"], color="Life Ladder", color_continuous_scale=px.colors.sequential.Greens, animation_frame="Year", hover_data=hover_data)
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            geo=dict(showframe=False, projection_type="equirectangular")
    )
    return fig

def prepare_layout():
    # Header 
    app_header = dbc.Row([html.H1("World Happiness Dashboard")], className="border rounded p-2")

    # World Map
    choropleth_map = generate_world_map()
    world_map = html.Div([html.H4("Life Ladder Overview"), dcc.Graph(figure=choropleth_map)])
    world_map_section = dbc.Row([dbc.Col([world_map], width=12)], className="border rounded p-2 my-3")

    # Country Detail
    country_detail = html.Div([html.H5("Country Detail Title", id="country_detail_title"), html.Div(id="country_detail_container")])
    country_detail_section = dbc.Row([dbc.Col([html.H4("General Information"), country_detail], width=12)], className="border rounded p-2 my-3")

    # Scatter Plot
    first_factor_dropdown = dcc.Dropdown(options=AVAILABLE_FACTORS, id="first_factor", value=INITIAL_FIRST_FACTOR, multi=False)
    second_factor_dropdown = dcc.Dropdown(options=AVAILABLE_FACTORS, id="second_factor", value=INITIAL_SECOND_FACTOR, multi=False)
    first_factor_div = html.Div([dbc.Label("First Factor", html_for="first_factor"), first_factor_dropdown], className="mb-3")
    second_factor_div = html.Div([dbc.Label("Second Factor", html_for="second_factor"), second_factor_dropdown], className="mb-3")
    factors = dbc.Form([html.H5("Choose your two factors"), first_factor_div, second_factor_div])
    simplified_explanation = html.Div([html.H5("In a nuthsell"), html.Div(id="simplified_explanation_container")])
    scatter_plot = html.Div([html.H5("In a graph"), dcc.Graph(id="scatter_plot")])
    scatter_plot_section = dbc.Row([html.H4("Detail Information"), dbc.Col([factors], width=4), dbc.Col([simplified_explanation], width=4), dbc.Col([scatter_plot], width=4)], className="border rounded p-2 my-3")

    # Heatmap
    heatmap_section = dbc.Row([html.H4("Correlation Overview"), html.H5("Correlation Overview Title", id="correlation_overview_title"), dcc.Graph(id="heatmap")], className="border rounded p-2 my-3") 

    # Filter
    country_dropdown = dcc.Dropdown(options=country_names, value=INITIAL_COUNTRY_NAME, id='selected_country', multi=False)
    country_div = html.Div([dbc.Label("Select country", html_for="selected_country"), country_dropdown], className="mb-3")
    from_dropdown = dcc.Dropdown(options=country_years, id="from", value=INITIAL_FROM_VALUE, multi=False)
    from_div = html.Div([dbc.Label("From", html_for="from"), from_dropdown], className="mb-3")
    floating_filter = dbc.Form([country_div, from_div], className="p-4 border rounded bg-light position-sticky shadow", style={"bottom": "10rem", "width": "60%", "left": "calc(50vw - 30%)"})

    # Toast container used for displaying toasts.
    toast_container = html.Div(id="toast_container")
    return html.Div([app_header, world_map_section, country_detail_section, scatter_plot_section, heatmap_section, floating_filter, toast_container], className="p-4")
    

def create_toast(content, header, duration=4000):
    toast = dbc.Toast(
        [html.P(content, className="mb-0")],
        header=header,
        icon="primary",
        dismissable=True,
        duration=duration,
        is_open=True,
        style={"position": "fixed", "top": 66, "right": "calc(50% - 25vw)", "width": "50vw"},
    )
    return toast

# Load Dataset and initial layout
df = prepare_dataset()
country_names = get_country_names(df)
country_years = get_country_years(df)
app.layout = prepare_layout()

@app.callback(Output("toast_container", "children"), Input("selected_country", "value"), Input("from", "value"))
def generate_toast_detail(selected_country, from_value):
    dff = df.copy()
    dff_country = dff[(dff["Country Name"] == selected_country) & (dff["Year"] == from_value)]
    if dff_country.empty:
        toast = create_toast(f"No information found for {selected_country} in Year {from_value}", "No Results")
        return [toast]
    return []

@app.callback(Output("country_detail_title", "children"), Output("country_detail_container", "children"), Input("selected_country", "value"), Input("from", "value"))
def generate_country_detail(selected_country, from_value):
    dff = df.copy()
    dff_country = dff[(dff["Country Name"] == selected_country) & (dff["Year"] == from_value)]
    if dff_country.empty:
        return f"No information found for {selected_country} in Year {from_value}", []

    overall_happiness_card = dbc.Card(dbc.CardBody([html.H6("Overall Happiness Score", className="card-title"), html.H4("8.2"), html.P("Ranked 12th in the World")]), className="my-3")
    country_detail_title = f"General Information about {selected_country} for Year {from_value}"
    country_detail = [overall_happiness_card, overall_happiness_card, overall_happiness_card, overall_happiness_card]
    return country_detail_title, country_detail

@app.callback(Output("simplified_explanation_container", "children"), Input("selected_country", "value"))
def generate_simplified_explanation_detail(selected_country):
    # TODO: Display proper factors etc.
    text_card = dbc.Card(dbc.CardBody([html.H6("Some useful and helpful explanation...")]), className="p-2 my-3")
    return [text_card, text_card]

@app.callback(Output("correlation_overview_title", "children"), Output("heatmap", "figure"), Input("selected_country", "value"))
def update_heatmap(selected_country):
    # Implemented with reference to: https://plotly.com/python/heatmaps/
    dff = df.copy()
    dff_country = dff[(dff["Country Name"] == selected_country)]
    if dff_country.empty:
        # As we have no data to shown we pass in an empty data frame
        return f"No information found for {selected_country}", None  
    columns = ["Confidence In National Government", "Life Ladder"]
    dff_country = dff_country[columns]
    correlation = dff_country.corr(numeric_only=True)
    heatmap = px.imshow(correlation, x=columns, y=columns, aspect="auto")
    heatmap.update_xaxes(side="top")
    return f"Correlation Information about {selected_country}", heatmap


if __name__ == '__main__':
    app.run_server(debug=True, port=8014)
