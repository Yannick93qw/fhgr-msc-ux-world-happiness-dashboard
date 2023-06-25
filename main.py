from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

# Initial values 
INITIAL_COUNTRY_NAME = "Switzerland"
INITIAL_FROM_VALUE = "2020"
INITIAL_FIRST_FEATURE = "Life Ladder"
INITIAL_SECOND_FEATURE = "Generosity"

# Will be displayed in the Dropdowns in a more human readable form
FEATURES_HUMAN_READABLE = ["Life Ladder", "Log GDP", "Social Support", "Life Expectancy", "Freedom to Make Life Choices", "Generosity", "Perception of Corruption", "Positive Affect", "Negative Affect"]

# Actual feature names used in the data, note that the order must be the same as the human readable definition above.
FEATURES_IN_DATA = ["life_ladder", "log_gdp", "social_support", "life_expectancy", "freedom", "generosity", "corruption", "positive_affect", "negative_affect"]

# Dictionary to quickly lookup the actual feature names for the data given a human readable feature name
FEATURES_DICT = {feature_human_readable: feature_in_data for (feature_human_readable, feature_in_data) in zip(FEATURES_HUMAN_READABLE, FEATURES_IN_DATA)}

Z_INDEX_OVERLAY = 2
Z_INDEX_FILTER = 3

# Styles which should be applied to the overlays depending if they are shown or not.
OVERLAY_SHOWN_STYLE = {"top": "3rem", "left": 0, "bottom": 0, "width": "99%", "zIndex": Z_INDEX_OVERLAY, "display": "flex"}
OVERLAY_HIDDEN_STYLE = {"top": "3rem", "left": 0, "bottom": 0, "width": "99%", "zIndex": Z_INDEX_OVERLAY, "display": "none"}

app = Dash(__name__, external_stylesheets=[dbc.themes.MATERIA])
app.title = "Msc FHGR - World Happiness Dashboard"
server = app.server

def get_country_names(data):
    """
    Returns a unique list of country names
        Parameters:
            data (DataFrame): DataFrame constructed from the cleaned up version of the World Happiness Report dataset

        Returns:
            unique_country_names (list): A unique list of country names.
    """
    unique_country_names = list(set(data["country_name"]))
    return unique_country_names 

def get_country_years(data):
    """
    Returns a unique list of years 
        Parameters:
            data (DataFrame): DataFrame constructed from the cleaned up version of the World Happiness Report dataset

        Returns:
            unique_country_years (list): A unique list of country years.
    """
    # Because a set is not ensured to be sorted the right way we need to explicitly sort here
    unique_country_years = list(sorted(set(data["year"])))
    return unique_country_years 

def prepare_dataset():
    """
    Loads the cleaned up version of the World Happiness Report dataset and sorts the values by year in ascending order.
    """
    data = pd.read_csv("./data_cleaned.csv", encoding="UTF-8")
    # Sort descending by year (Reference: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html)
    data = data.sort_values(by="year", ascending=True)
    return data

def generate_world_map():
    """
    Generates a choropleth map in order to display the Life Ladder indicator for all countries over the entire dataset
    """
    # Implemented with reference to: 
    # - https://plotly.com/python/choropleth-maps/
    # - https://stackoverflow.com/questions/70773315/how-to-colorize-lands-which-have-missing-values-and-get-their-name-in-plotly-cho
    # We decided not to generate data for some missing countries (like setting the value to 999) etc.
    # As a consequence of this not all countries will be seen at every point in time (for example 2005 vs. 2022).

    dff = df.copy()
    hover_data = ["country_name", "life_ladder", "year"]
    fig = px.choropleth(dff, locations=dff["country_code_iso"], color="life_ladder", color_continuous_scale=px.colors.sequential.Blues, animation_frame="year", hover_data=hover_data)
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            geo=dict(showframe=False, projection_type="equirectangular")
            )
    return fig

def prepare_layout():
    """
    Sets up the layout of the dashboard
    """
    # Header 
    app_header = dbc.Row([html.H1("World Happiness Dashboard")], className="border rounded p-2")

    # World Map
    choropleth_map = generate_world_map()
    world_map = html.Div([html.H4("Life Ladder Overview"), dcc.Graph(figure=choropleth_map)])
    world_map_section = dbc.Row([dbc.Col([world_map], width=12)], className="border rounded p-2 my-3")

    # Country Detail
    country_detail = html.Div([html.H5(id="country_detail_overlay", className="justify-content-center align-items-center position-absolute bg-white", style=OVERLAY_HIDDEN_STYLE), html.H5(id="country_detail_title"), html.Div(id="country_detail_container")])
    country_detail_section = dbc.Row([dbc.Col([html.H4("General Information about selected country"), country_detail], width=12)], className="position-relative border rounded p-2 my-3", style={"minHeight": 250})

    # Scatter Plot
    first_feature_dropdown = dcc.Dropdown(options=FEATURES_HUMAN_READABLE, id="first_feature", value=INITIAL_FIRST_FEATURE, multi=False)
    second_feature_dropdown = dcc.Dropdown(options=FEATURES_HUMAN_READABLE, id="second_feature", value=INITIAL_SECOND_FEATURE, multi=False)
    first_feature_div = html.Div([dbc.Label("First Feature", html_for="first_feature"), first_feature_dropdown], className="mb-3")
    second_feature_div = html.Div([dbc.Label("Second Feature", html_for="second_feature"), second_feature_dropdown], className="mb-3")
    features = dbc.Form([first_feature_div, second_feature_div])
    simplified_explanation = html.Div([html.H5("In a nuthsell"), html.H5(id="simplified_explanation_overlay", className="justify-content-center align-items-center position-absolute bg-white", style=OVERLAY_HIDDEN_STYLE), html.Div(id="simplified_explanation_container")], className="position-relative", style={"minHeight": 250})
    scatter_plot = html.Div([html.H5("In a graph"), html.H5(id="scatter_plot_overlay", className="justify-content-center align-items-center position-absolute bg-white", style=OVERLAY_HIDDEN_STYLE), dcc.Graph(id="scatter_plot")], className="position-relative", style={"minHeight": 250})
    scatter_plot_section = dbc.Row([html.H4("Detail Information"), html.H5(id="features_title"), dbc.Col([features], width=2), dbc.Col([simplified_explanation], width=2), dbc.Col([scatter_plot], width=8)], className="border rounded p-2 my-3")

    # Heatmap
    heatmap_section = dbc.Row([html.H4("Correlation Overview"), html.H5(id="heatmap_overlay", className="justify-content-center align-items-center position-absolute bg-white", style=OVERLAY_HIDDEN_STYLE), html.H5(id="correlation_overview_title"), dcc.Graph(id="heatmap")], className="border rounded p-2 my-3 position-relative") 

    # Filter
    country_dropdown = dcc.Dropdown(options=country_names, value=INITIAL_COUNTRY_NAME, id='selected_country', multi=False)
    country_div = html.Div([dbc.Label("Select country", html_for="selected_country"), country_dropdown], className="mb-3")
    from_dropdown = dcc.Dropdown(options=country_years, id="from", value=INITIAL_FROM_VALUE, multi=False)
    from_div = html.Div([dbc.Label("From", html_for="from"), from_dropdown], className="mb-3")
    floating_filter = dbc.Form([country_div, from_div], className="p-4 border rounded bg-light position-sticky shadow", style={"bottom": "10rem", "width": "60%", "left": "calc(50vw - 30%)", "zIndex": Z_INDEX_FILTER})

    return html.Div([app_header, world_map_section, country_detail_section, scatter_plot_section, heatmap_section, floating_filter], className="p-4")

def create_country_card(title, value, rank, total_number_of_ranks):
    """
    Returns a customized bootstrap Card specific for a selected country 

        Parameters:
            title (str): The title for the bootstrap card (e.g Life Ladder)
            value (float): The value which should be shown (e.g 4.2)
            rank (int): The rank for the country (e.g 1)
            total_numbers_of_ranks (int): The total available number of ranks (e.g 142)

        Returns:
            card (dbc.Card): A customized bootstrap Card containing specific information about a country
    """
    # The entire value is quite verbose. In order to improve readability we only show the value with a precision of two after the decimal point.
    # See: https://stackoverflow.com/questions/8885663/how-to-format-a-floating-number-to-fixed-width-in-python
    card = dbc.Card(dbc.CardBody([html.H6(title, className="card-title"), html.H4(f"{value:4.2f}"), html.P([f"Ranked ", html.B(rank), f" out of {total_number_of_ranks} in the World"])]), style={"width": "12rem", "height": "12rem", "float": "left", "margin": "2rem 2rem 2rem 0"})
    return card

def get_correlation_category(corr_factor):
    """
    Returns a correlation category (negligible, weak, moderate, strong, very strong) and if it is positive or not.

        Parameters:
            corr_factor (float): The correlation value itself

        Returns:
            positive (bool): Tells if the correlation value is positive or not.
            category (str): Tells to which category this value belongs (negligible, weak, moderate, strong, very strong)
    """
    # Implemented with reference to: https://medium.com/brdata/correlation-straight-to-the-point-e692ab601f4c
    positive = corr_factor >= 0
    abs_corr_factor = abs(corr_factor)

    if abs_corr_factor <= 0.3:
        return (positive, "negligible")

    if abs_corr_factor <= 0.5:
        return (positive, "weak")

    if abs_corr_factor <= 0.7:
        return (positive, "moderate")

    if abs_corr_factor <= 0.9:
        return (positive, "strong")

    return (positive, "very strong")

def get_simplified_correlation_explanation(corr_factor, first_feature, second_feature, country_name):
    """
    Returns a simplified more "human understandable" explanation for a correlation between two features 
        Parameters:
            corr_factor (float): The correlation value itself
            first_feature (str): The first feature for the correlation
            second_feature (str): The second feature for the correlation
            country_name (str): The name of the country

        Returns:
            human_readable_explanation (str): A more human readable version in order to understand the correlation between two features
    """
    positive, corr_category = get_correlation_category(corr_factor)

    if corr_category == "negligible": 
        return f"The Correlation is negligibale. Therefore no real assumption can be made between {first_feature} and {second_feature}"
    
    if corr_category == "weak": 
        return f"The Correlation is weak. Therefore no real assumption can be made between {first_feature} and {second_feature}"

    if corr_category == "moderate": 
        if positive:
            return f"The Correlation is moderate: The higher {first_feature} the higher is {second_feature} in {country_name}"
        return f"The Correlation is moderate: The higher {first_feature} the lower is {second_feature} in {country_name}"

    if corr_category == "strong": 
        if positive:
            return f"The Correlation is strong: The higher {first_feature} the higher is {second_feature} in {country_name}"
        return f"The Correlation is strong: The higher {first_feature} the lower is {second_feature} in {country_name}"
    
    # Very Strong Correlation 
    if positive:
        return f"The Correlation is very strong: The higher {first_feature} the higher is {second_feature} in {country_name}"
    return f"The Correlation is very strong: The higher {first_feature} the lower is {second_feature} in {country_name}"

# Load Dataset and initial layout
df = prepare_dataset()
country_names = get_country_names(df)
country_years = get_country_years(df)
app.layout = prepare_layout()

@app.callback(Output("country_detail_overlay", "children"), Output("country_detail_overlay", "style"), Output("country_detail_title", "children"), Output("country_detail_container", "children"), Input("selected_country", "value"), Input("from", "value"))
def generate_country_detail(selected_country, from_value):
    if selected_country == None and from_value == None:
        return "No country and year selected", OVERLAY_SHOWN_STYLE, "", [] 
    elif selected_country == None:
        return "No country selected", OVERLAY_SHOWN_STYLE, "", [] 
    elif from_value == None:
        return "No year selected", OVERLAY_SHOWN_STYLE, "", [] 

    dff = df.copy()
    dff_country = dff[(dff["country_name"] == selected_country) & (dff["year"] == int(from_value))]
    if dff_country.empty:
        return f"No data found for {selected_country} in Year {from_value}", OVERLAY_SHOWN_STYLE, "", [] 

    country_detail = [create_country_card(feature_human_readable, dff_country[feature].values[0], dff_country[f"{feature}_rank"].values[0], dff_country["total_number_of_ranks"].values[0]) for (feature_human_readable, feature) in zip(FEATURES_HUMAN_READABLE, FEATURES_IN_DATA)]
    country_detail_title = f"General Information about {selected_country} for Year {from_value}"
    return "", OVERLAY_HIDDEN_STYLE, country_detail_title, country_detail 


@app.callback(Output("simplified_explanation_overlay", "children"), Output("simplified_explanation_overlay", "style"), Output("simplified_explanation_container", "children"), Input("selected_country", "value"), Input("first_feature", "value"), Input("second_feature", "value"))
def generate_simplified_explanation_detail(selected_country, first_feature, second_feature):
    if selected_country == None:
        return "No country selected", OVERLAY_SHOWN_STYLE, [] 

    first_feature_data = FEATURES_DICT.get(first_feature, None)
    second_feature_data = FEATURES_DICT.get(second_feature, None)

    if first_feature_data == None or second_feature_data == None:
        return f"Select two features to compare", OVERLAY_SHOWN_STYLE, []

    dff = df.copy()
    dff_country = dff[(dff["country_name"] == selected_country)]

    if dff_country.empty:
        return f"No data found for {selected_country}", OVERLAY_SHOWN_STYLE, [] 

    corr_value = dff_country[first_feature_data].corr(dff_country[second_feature_data])
    simplified_explanation = get_simplified_correlation_explanation(corr_value, first_feature, second_feature, selected_country)
    simplified_card = dbc.Card(dbc.CardBody([html.H6(simplified_explanation)]), className="p-2 my-3")

    positive, corr_category = get_correlation_category(corr_value)
    scientific_corr_label = ""
    match corr_category:
        case "negligible":
            scientific_corr_label = "Negligible Significance"
        case "weak":
            scientific_corr_label = "Weak Significance"
        case "moderate":
            scientific_corr_label = "Moderate Significance"
        case "strong":
           scientific_corr_label = "Strong Significance"
        case _:
            scientific_corr_label = "Very Strong Signifiance"

    scientific_explanation = ""

    if positive:
        scientific_explanation = "A positive correlation means that if one value increases so does the other one."
    else:
        scientific_explanation = "A negative correlation means that if one value increases the other decreases."

    scientific_card = dbc.Card(dbc.CardBody([dbc.Badge(scientific_corr_label, color="primary", className="my-2"), html.H6(f"Significance: {corr_value:4.2f}", className="card-title"), html.P(scientific_explanation)]), className="p-2 my-3")
    return "", OVERLAY_HIDDEN_STYLE, [simplified_card, scientific_card]

@app.callback(Output("heatmap_overlay", "children"), Output("heatmap_overlay", "style"), Output("correlation_overview_title", "children"), Output("heatmap", "figure"), Input("selected_country", "value"))
def update_heatmap(selected_country):
    # Implemented with reference to: https://plotly.com/python/heatmaps/
    if selected_country == None:
        return "No country selected", OVERLAY_SHOWN_STYLE, "", None 

    dff = df.copy()
    dff_country = dff[(dff["country_name"] == selected_country)]
    if dff_country.empty:
        return f"No data found for {selected_country}", OVERLAY_SHOWN_STYLE, "", None 

    columns = FEATURES_HUMAN_READABLE 
    dff_country = dff_country[FEATURES_IN_DATA]
    correlation = dff_country.corr(numeric_only=True)

    # Round correlation numbers so that they do not have some many decimal places
    # See https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.round.html
    correlation = correlation.round(2)

    heatmap = px.imshow(correlation, x=columns, y=columns, aspect="auto", text_auto=True, color_continuous_scale=px.colors.sequential.Blues)
    heatmap.update_xaxes(side="top")
    heatmap_title = f"Correlation Information about {selected_country}"
    return "", OVERLAY_HIDDEN_STYLE, heatmap_title, heatmap 

@app.callback(Output("scatter_plot_overlay", "children"), Output("scatter_plot_overlay", "style"), Output("features_title", "children"), Output("scatter_plot", "figure"), Input("selected_country", "value"), Input("first_feature", "value"), Input("second_feature", "value"))
def update_scatter_plot(selected_country, first_feature, second_feature):
    if selected_country == None:
        return "No country selected", OVERLAY_SHOWN_STYLE, "", None 
    
    first_feature_data = FEATURES_DICT.get(first_feature, None)
    second_feature_data = FEATURES_DICT.get(second_feature, None)

    if first_feature_data == None or second_feature_data == None:
        return f"Please choose at least two features", OVERLAY_SHOWN_STYLE, "", None

    dff = df.copy()
    dff_country = dff[(dff["country_name"] == selected_country)]
    if dff_country.empty:
        return f"No data found for {selected_country}", OVERLAY_SHOWN_STYLE, "", None 

    # Implemented with reference to:
    # - https://plotly.com/python/text-and-annotations/
    # - https://plotly.com/python/linear-fits/
    scatter_plot = px.scatter(dff_country, x=first_feature_data, y=second_feature_data, text="year", trendline="ols")
    scatter_plot.update_traces(textposition='top center')
    scatter_title = f"Comparing {first_feature} and {second_feature} for {selected_country}"
    return "", OVERLAY_HIDDEN_STYLE, scatter_title, scatter_plot

if __name__ == '__main__':
    app.run_server(debug=True)
