from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

INITIAL_COUNTRY_NAME = "Switzerland"
INITIAL_FROM_VALUE = "2020"

# Will be displayed in the Dropdowns in a more human readable form
FEATURES_HUMAN_READABLE = ["Life Ladder", "Log GDP", "Social Support", "Life Expectancy", "Freedom to Make Life Choices", "Generosity", "Perception of Corruption", "Positive Affect", "Negative Affect"]

# Actual feature names used in the data, note that the order must be the same as the human readable definition above.
FEATURES_IN_DATA = ["life_ladder", "log_gdp", "social_support", "life_expectancy", "freedom", "generosity", "corruption", "positive_affect", "negative_affect"]

# Dictionary to quickly lookup the actual feature names for the data given a human readable feature name
FEATURES_DICT = {feature_human_readable: feature_in_data for (feature_human_readable, feature_in_data) in zip(FEATURES_HUMAN_READABLE, FEATURES_IN_DATA)}

INITIAL_FIRST_FEATURE = "Life Ladder"
INITIAL_SECOND_FEATURE = "Generosity"

app = Dash(__name__, external_stylesheets=[dbc.themes.MATERIA])

def get_country_names(data):
    return list(set(data["country_name"])) 

def get_country_years(data):
    # Because a set is not ensured to be sorted the right way we need to explicitly sort here
    return list(sorted(set(data["year"]))) 

def prepare_dataset():
    data = pd.read_csv("./data_cleaned.csv", encoding="UTF-8")
    # Sort descending by year (Reference: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html)
    data = data.sort_values(by="year", ascending=True)
    return data
def generate_world_map():
    # Implemented with reference to: 
    # - https://plotly.com/python/choropleth-maps/
    # - https://stackoverflow.com/questions/70773315/how-to-colorize-lands-which-have-missing-values-and-get-their-name-in-plotly-cho
    # We decided not to generate data for some missing countries (like setting the value to 999) etc.
    # As a consequence of this not all countries will be seen at every point in time (for example 2005 vs. 2022).

    dff = df.copy()
    hover_data = ["country_name", "life_ladder", "year"]
    fig = px.choropleth(dff, locations=dff["country_code_iso"], color="life_ladder", color_continuous_scale=px.colors.sequential.Greens, animation_frame="year", hover_data=hover_data)
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
    first_feature_dropdown = dcc.Dropdown(options=FEATURES_HUMAN_READABLE, id="first_feature", value=INITIAL_FIRST_FEATURE, multi=False)
    second_feature_dropdown = dcc.Dropdown(options=FEATURES_HUMAN_READABLE, id="second_feature", value=INITIAL_SECOND_FEATURE, multi=False)
    first_feature_div = html.Div([dbc.Label("First Feature", html_for="first_feature"), first_feature_dropdown], className="mb-3")
    second_feature_div = html.Div([dbc.Label("Second Feature", html_for="second_feature"), second_feature_dropdown], className="mb-3")
    features = dbc.Form([html.H5("Choose your two features to compare", id="features_title"), first_feature_div, second_feature_div])
    simplified_explanation = html.Div([html.H5("In a nuthsell"), html.Div(id="simplified_explanation_container")])
    scatter_plot = html.Div([html.H5("In a graph"), dcc.Graph(id="scatter_plot")])
    scatter_plot_section = dbc.Row([html.H4("Detail Information"), dbc.Col([features], width=4), dbc.Col([simplified_explanation], width=4), dbc.Col([scatter_plot], width=4)], className="border rounded p-2 my-3")

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

def create_country_card(title, value, rank, total_number_of_ranks):
    # The entire value is quite verbose. In order to improve readability we only show the value with a precision of two after the decimal point.
    # See: https://stackoverflow.com/questions/8885663/how-to-format-a-floating-number-to-fixed-width-in-python
    card = dbc.Card(dbc.CardBody([html.H6(title, className="card-title"), html.H4(f"{value:4.2f}"), html.P(f"Ranked {rank} out of {total_number_of_ranks} in the World")]), className="my-3")
    return card


# Load Dataset and initial layout
df = prepare_dataset()
country_names = get_country_names(df)
country_years = get_country_years(df)
app.layout = prepare_layout()

@app.callback(Output("toast_container", "children"), Input("selected_country", "value"), Input("from", "value"))
def generate_toast_detail(selected_country, from_value):
    dff = df.copy()
    dff_country = dff[(dff["country_name"] == selected_country) & (dff["year"] == int(from_value))]
    if dff_country.empty:
        toast = create_toast(f"No information found for {selected_country} in Year {from_value}", "No Results")
        return [toast]
    return []

@app.callback(Output("country_detail_title", "children"), Output("country_detail_container", "children"), Input("selected_country", "value"), Input("from", "value"))
def generate_country_detail(selected_country, from_value):
    dff = df.copy()
    dff_country = dff[(dff["country_name"] == selected_country) & (dff["year"] == int(from_value))]
    if dff_country.empty:
        return f"No information found for {selected_country} in Year {from_value}", []

    country_detail = [create_country_card(feature_human_readable, dff_country[feature].values[0], dff_country[f"{feature}_rank"].values[0], dff_country["total_number_of_ranks"].values[0]) for (feature_human_readable, feature) in zip(FEATURES_HUMAN_READABLE, FEATURES_IN_DATA)]
    country_detail_title = f"General Information about {selected_country} for Year {from_value}"
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
    dff_country = dff[(dff["country_name"] == selected_country)]
    if dff_country.empty:
        return f"No information found for {selected_country}", None  
    columns = FEATURES_IN_DATA
    dff_country = dff_country[columns]
    correlation = dff_country.corr(numeric_only=True)
    heatmap = px.imshow(correlation, x=columns, y=columns, aspect="auto")
    heatmap.update_xaxes(side="top")
    return f"Correlation Information about {selected_country}", heatmap

@app.callback(Output("features_title", "children"), Output("scatter_plot", "figure"), Input("selected_country", "value"), Input("first_feature", "value"), Input("second_feature", "value"))
def update_scatter_plot(selected_country, first_feature, second_feature):
    dff = df.copy()
    dff_country = dff[(dff["country_name"] == selected_country)]
    if dff_country.empty:
        return f"No information found for {selected_country}", None  
    
    first_feature_data = FEATURES_DICT.get(first_feature, None)
    second_feature_data = FEATURES_DICT.get(second_feature, None)

    if first_feature_data == None or second_feature_data == None:
        return f"Please choose at least two features", None

    scatter_plot = px.scatter(dff_country, x=first_feature_data, y=second_feature_data)
    return f"Comparing {first_feature} and {second_feature} for {selected_country}", scatter_plot


if __name__ == '__main__':
    app.run_server(debug=True, port=8014)
