from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import json

# Initial values 
INITIAL_COUNTRY_NAME = "Switzerland"
INITIAL_FROM_VALUE = "2020"
INITIAL_FIRST_FEATURE = "Life Ladder"
INITIAL_SECOND_FEATURE = "Generosity"

# Initial centered country on the mapbox based choropleth map (Switzerland)
INITIAL_CENTERED_COUNTRY = {"lat": 46.8182, "lon": 8.2275}

HEIGHT_CHOROPLETH_MAP = 950

# Will be displayed in the Dropdowns in a more human readable form
FEATURES_HUMAN_READABLE = ["Life Ladder", "Log GDP", "Social Support", "Life Expectancy", "Freedom to Make Life Choices", "Generosity", "Perception of Corruption", "Positive Affect", "Negative Affect"]

# Taken from:
# - https://happiness-report.s3.amazonaws.com/2023/WHR+23.pdf
# - https://worldhappiness.report/faq/#:~:text=This%20is%20called%20the%20Cantril,for%20the%20years%202020%2D2022.
FEATURES_EXPLANATION = [
        "Life Ladder is a ladder, with the best possible life for them being a 10 and the worst possible life being a 0.", # Life Ladder
        "Gross Domestic Product, or how much each country produces, divided by the number of people in the country. GDP per capita gives information about the size of the economy and how the economy is performing.", # Log GDP 
        "Social support, or having someone to count on in times of trouble. 'If you were in trouble, do you have relatives or friends you can count on to help you whenever you need them, or not?'", # Social Support
        "More than life expectancy, how is your physical and mental health? Mental health is a key component of subjective well-being and is also a risk factor for future physical health and longevity. Mental health influences and drives a number of individual choices, behaviours,and outcomes.", #Life Expectancy
        "'Are you satisfied or dissatisfied with your freedom to choose what you do with your life?' This also includes Human Rights. Inherent to all human beings, regardless of race, sex, nationality, ethnicity, language, religion, or any other status. Human rights include the right to life and liberty, freedom from slavery and torture, freedom of opinion and expression, the right to work and education, and many more. Everyone is entitled to these rights without discrimination.", # Freedom to Make Life Choices
        "'Have you donated money to a charity in the past month?' A clear marker for a sense of positive community engagement and a central way that humans connect with each other. Research shows that in all cultures, starting in early childhood, people are drawn to behaviours which benefit other people.", # Generosity
        "'Is corruption widespread throughout the government or not' and 'Is corruption widespread within businesses or not?' Do people trust their governments and have trust in the benevolence of others?", #Perception of Corruption
        "Positive affect is given by the average of individual yes or no answers about three emotions: laughter, enjoyment, and interest", #Positive Affect
        "Negative affect is given by the average of individual yes or no answers about three emotions: worry, sadness, and anger." # Negative Affect
        ]

# Actual feature names used in the data, note that the order must be the same as the human readable definition above.
FEATURES_IN_DATA = ["life_ladder", "log_gdp", "social_support", "life_expectancy", "freedom", "generosity", "corruption", "positive_affect", "negative_affect"]

# Dictionary to quickly lookup the actual feature names for the data given a human readable feature name
FEATURES_DICT = {feature_human_readable: feature_in_data for (feature_human_readable, feature_in_data) in zip(FEATURES_HUMAN_READABLE, FEATURES_IN_DATA)}

# Dictionary to define labels for axis etc.
FEATURES_LABELS= {feature_in_data: feature_human_readable for (feature_human_readable, feature_in_data) in zip(FEATURES_HUMAN_READABLE, FEATURES_IN_DATA)}
# Add an aditional entry for country_name
FEATURES_LABELS["country_name"] = "Country Name"


# Dictionary to look up explanations for various features
FEATURES_EXPLANATION_DICT = {feature_human_readable: feature_explanation for (feature_human_readable, feature_explanation) in zip(FEATURES_HUMAN_READABLE, FEATURES_EXPLANATION)}

Z_INDEX_OVERLAY = 2
Z_INDEX_FILTER = 3

# Styles which should be applied to the overlays depending if they are shown or not.
OVERLAY_SHOWN_STYLE = {"top": 0, "left": 0, "bottom": 0, "width": "99%", "zIndex": Z_INDEX_OVERLAY, "display": "flex"}
OVERLAY_HIDDEN_STYLE = {"top": 0, "left": 0, "bottom": 0, "width": "99%", "zIndex": Z_INDEX_OVERLAY, "display": "none"}

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Msc FHGR - World Happiness Dashboard"
server = app.server


def get_ranking_explanation(feature_human_readable):
    """
    Returns an explanation of how to interpret a certain ranking

    Parameters:
        feature_human_readable (str): The feature for which the ranking should be explained (e.g Life Ladder) 
        Returns:
            An explanation if a lower or higher ranking is better.
    """
    match feature_human_readable:
        case "Life Ladder":
            return "Higher is better"
        case "Log GDP":
            return "Higher is better"
        case "Social Support":
            return "Higher is better"
        case "Life Expectancy":
            return "Higher is better"
        case "Freedom to Make Life Choices":
            return "Higher is better"
        case "Generosity":
            return "Higher is better"
        case "Positive Affect":
            return "Higher is better"
        case "Perception of Corruption":
            return "Lower is better"
        case "Negative Affect":
            return "Lower is better"
        case _:
            return ""

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
    # - https://towardsdatascience.com/how-to-create-outstanding-custom-choropleth-maps-with-plotly-and-dash-49ac918a5f05
    dff = df.copy()

    # Geojson was generated with: https://geojson-maps.ash.ms/
    with open("./custom.geo.json") as f:
        geo_world = json.load(f)

    hover_data = {"country_name": True, "life_ladder": True, "year": True, "country_code_iso": False}

    # We need to map a property inside the geojson to the actual iso code of our country.
    # Luckily this can easily by done via featureidkey, see "Indexing by GeoJSON Properties" on https://plotly.com/python/mapbox-county-choropleth/
    fig = px.choropleth_mapbox(
            dff,
            geojson=geo_world,
            featureidkey="properties.iso_a3",
            mapbox_style="open-street-map", 
            locations="country_code_iso",
            color="life_ladder",
            center=INITIAL_CENTERED_COUNTRY,
            animation_frame="year",
            hover_name="country_name",
            hover_data=hover_data,
            color_continuous_scale=px.colors.sequential.Blues,
            zoom=5)
    fig.update_layout(
            height=HEIGHT_CHOROPLETH_MAP,
            margin={"r":0,"t":0,"l":0,"b":0},
            geo=dict(showframe=False))
    return fig

def prepare_layout():
    """
    Sets up the layout of the dashboard
    """
    # Header 
    app_header = dbc.Row([html.H1("World Happiness Dashboard")], className="my-2")

    # World Map and associated Country Detail information
    choropleth_map = generate_world_map()
    world_map = html.Div([html.H4("Life Ladder Overview"), dcc.Graph(figure=choropleth_map)])
    country_detail = html.Div([html.H5(id="country_detail_overlay", className="justify-content-center align-items-center position-absolute bg-white", style=OVERLAY_HIDDEN_STYLE), html.Div(id="country_detail_container", style={"maxHeight": HEIGHT_CHOROPLETH_MAP, "overflowY": "auto"})], className="position-relative", style={"minHeight": HEIGHT_CHOROPLETH_MAP})

    country_detail_section = html.Div([html.H4(id="country_detail_title"), country_detail])
    world_map_section = dbc.Row([dbc.Col([world_map], className="col-md-8 col-sm-12"), dbc.Col([country_detail_section], className="col-md-4 col-sm-12")], className="my-2")

    # Parallel Coordinate System
    parallel_coordinate_system_section = dbc.Row([html.H4(id="parallel_coordinate_system_title"), dbc.Form([dbc.Label("Select multiple Features", html_for="parallel_coordinate_system_features"), dcc.Dropdown(options=FEATURES_HUMAN_READABLE, id="parallel_coordinate_system_features", value=FEATURES_HUMAN_READABLE, multi=True)]),html.Div([html.H5(id="parallel_coordinate_system_overlay", className="justify-content-center align-items-center position-absolute bg-white"), dcc.Graph(id="parallel_coordinate_system")], className="position-relative", style={"minHeight": 250})])

    # Top 5 countries bar chart
    top_5_countries_detail = html.Div([html.H5(id="top_5_countries_overlay", className="justify-content-center align-items-center position-absolute bg-white", style=OVERLAY_HIDDEN_STYLE), dcc.Graph(id="top_5_countries_bar_chart")], className="position-relative", style={"minHeight": 250}) 
    top_5_countries_feature_dropdown = dcc.Dropdown(options=FEATURES_HUMAN_READABLE, id="top_5_countries_feature", value=INITIAL_FIRST_FEATURE, multi=False)
    top_5_countries_section = html.Div([html.H4(id="top_5_countries_title"), dbc.Form([dbc.Label("Select a Feature", html_for="top_5_countries_feature"), top_5_countries_feature_dropdown]), top_5_countries_detail])

    # Scatter Plot and in a nutshell explanations
    first_feature_dropdown = dcc.Dropdown(options=FEATURES_HUMAN_READABLE, id="first_feature", value=INITIAL_FIRST_FEATURE, multi=False)
    second_feature_dropdown = dcc.Dropdown(options=FEATURES_HUMAN_READABLE, id="second_feature", value=INITIAL_SECOND_FEATURE, multi=False)
    first_feature_div = html.Div([dbc.Label("First Feature", html_for="first_feature"), first_feature_dropdown], className="mb-3")
    second_feature_div = html.Div([dbc.Label("Second Feature", html_for="second_feature"), second_feature_dropdown], className="mb-3")
    features = dbc.Form([html.H5("Select two features"), first_feature_div, second_feature_div])
    simplified_explanation = html.Div([html.H5("In a nuthsell"), html.H5(id="simplified_explanation_overlay", className="justify-content-center align-items-center position-absolute bg-white", style=OVERLAY_HIDDEN_STYLE), html.Div(id="simplified_explanation_container")], className="position-relative", style={"minHeight": 250})
    scatter_plot = html.Div([html.H5("In a graph"), html.H5(id="scatter_plot_overlay", className="justify-content-center align-items-center position-absolute bg-white", style=OVERLAY_HIDDEN_STYLE), dcc.Graph(id="scatter_plot")], className="position-relative", style={"minHeight": 250})
    scatter_plot_section = dbc.Row([html.H4(id="features_title"), dbc.Col([features], className="col-lg-2 col-md-12"), dbc.Col([simplified_explanation], className="col-lg-3 col-md-12"), dbc.Col([scatter_plot], className="col-lg-7 col-md-12")], className="my-2")

    # Heatmap
    heatmap_section = dbc.Row([html.H4(id="correlation_overview_title"), html.Div([html.H5(id="heatmap_overlay", className="justify-content-center align-items-center position-absolute bg-white", style=OVERLAY_HIDDEN_STYLE), dcc.Graph(id="heatmap")], className="my-2 position-relative")]) 

    # Filter
    country_dropdown = dcc.Dropdown(options=country_names, value=INITIAL_COUNTRY_NAME, id='selected_country', multi=False)
    country_div = html.Div([dbc.Label("Select country", html_for="selected_country"), country_dropdown], className="mb-3")
    year_dropdown= dcc.Dropdown(options=country_years, id="year", value=INITIAL_FROM_VALUE, multi=False)
    year_div= html.Div([dbc.Label("Year", html_for="year"), year_dropdown], className="mb-3")
    floating_filter = dbc.Form([country_div, year_div], className="p-4 border rounded bg-light position-sticky shadow", style={"bottom": "11rem", "width": "36rem", "left": "calc(50vw - 18rem)", "zIndex": Z_INDEX_FILTER})

    return html.Div([app_header, world_map_section, parallel_coordinate_system_section, top_5_countries_section, scatter_plot_section, heatmap_section, floating_filter], className="p-4")

def generate_country_card(feature_human_readable, feature, df_country):
    """
    Returns a customized bootstrap Card specific for a selected country 

        Parameters:
            feature_human_readable (str): The feature in human readable form (e.g Life Ladder)
            feature (str): The feature in the data set (e.g life_ladder)
            df_country (pd.DataFrame): The dataframe for the specific country

        Returns:
            card (dbc.Card): A customized bootstrap Card containing specific information about a country
    """
    feature_explanation = FEATURES_EXPLANATION_DICT.get(feature_human_readable, "")
    ranking_explanation = get_ranking_explanation(feature_human_readable)
    rank = df_country[f"{feature}_rank"].values[0] 
    total_number_of_ranks = df_country["total_number_of_ranks"].values[0]
    value = df_country[feature].values[0]

    # The entire value is quite verbose. In order to improve readability we only show the value with a precision of two after the decimal point.
    # See: https://stackoverflow.com/questions/8885663/how-to-format-a-floating-number-to-fixed-width-in-python
    card = dbc.Card(dbc.CardBody([html.H5(feature_human_readable, className="card-title"), html.P(ranking_explanation, className="card-subtitle mb-2 text-muted"), html.P(feature_explanation), html.H3(dbc.Badge(f"Ranked {rank}", color="primary", className="p-2")), html.P(f"out of {total_number_of_ranks}", className="text-muted"), html.B(f"Value: {value:4.2f}")]), className="my-2")
    return card

def get_correlation_category(corr_factor):
    """
    Returns a correlation category (negligible, weak, moderate, strong, very strong) and if it is positive or not.

        Parameters:
            corr_factor (float): The correlation value itself

        Returns:
            is_positive (bool): Tells if the correlation value is positive or not.
            category (str): Tells to which category this value belongs (negligible, weak, moderate, strong, very strong)
    """
    # Implemented with reference to: https://medium.com/brdata/correlation-straight-to-the-point-e692ab601f4c
    is_positive = corr_factor >= 0
    abs_corr_factor = abs(corr_factor)
    if abs_corr_factor <= 0.3:
        return (is_positive, "negligible")

    if abs_corr_factor <= 0.5:
        return (is_positive, "weak")

    if abs_corr_factor <= 0.7:
        return (is_positive, "moderate")

    if abs_corr_factor <= 0.9:
        return (is_positive, "strong")

    return (is_positive, "very strong")

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
    is_positive, corr_category = get_correlation_category(corr_factor)

    if corr_category == "negligible": 
        return f"The Correlation is negligibale. Therefore no real assumption can be made between {first_feature} and {second_feature}"

    if corr_category == "weak": 
        return f"The Correlation is weak. Therefore no real assumption can be made between {first_feature} and {second_feature}"

    if corr_category == "moderate": 
        if is_positive:
            return f"The Correlation is moderate: The higher {first_feature} the higher is {second_feature} in {country_name}"
        return f"The Correlation is moderate: The higher {first_feature} the lower is {second_feature} in {country_name}"

    if corr_category == "strong": 
        if is_positive:
            return f"The Correlation is strong: The higher {first_feature} the higher is {second_feature} in {country_name}"
        return f"The Correlation is strong: The higher {first_feature} the lower is {second_feature} in {country_name}"

    # Very Strong Correlation 
    if is_positive:
        return f"The Correlation is very strong: The higher {first_feature} the higher is {second_feature} in {country_name}"
    return f"The Correlation is very strong: The higher {first_feature} the lower is {second_feature} in {country_name}"

# Load Dataset and initial layout
df = prepare_dataset()
country_names = get_country_names(df)
country_years = get_country_years(df)
app.layout = prepare_layout()

@app.callback(Output("country_detail_overlay", "children"), Output("country_detail_overlay", "style"), Output("country_detail_title", "children"), Output("country_detail_container", "children"), Input("selected_country", "value"), Input("year", "value"))
def update_country_detail(selected_country, year):
    country_detail_title = "General Information"
    if selected_country == None and year == None:
        return "No country and year selected", OVERLAY_SHOWN_STYLE, country_detail_title, [] 
    elif selected_country == None:
        return "No country selected", OVERLAY_SHOWN_STYLE, country_detail_title, [] 
    elif year == None:
        return "No year selected", OVERLAY_SHOWN_STYLE, country_detail_title, [] 

    dff = df.copy()
    dff_country = dff[(dff["country_name"] == selected_country) & (dff["year"] == int(year))]
    if dff_country.empty:
        return f"No data found for {selected_country} in Year {year}", OVERLAY_SHOWN_STYLE, country_detail_title, [] 

    country_detail = [generate_country_card(feature_human_readable, feature, dff_country) for (feature_human_readable, feature) in zip(FEATURES_HUMAN_READABLE, FEATURES_IN_DATA)]
    country_detail_title = f"General Information about {selected_country} for Year {year}"
    return "", OVERLAY_HIDDEN_STYLE, country_detail_title, country_detail 


@app.callback(Output("top_5_countries_title", "children"), Output("top_5_countries_overlay", "children"), Output("top_5_countries_overlay", "style"), Output("top_5_countries_bar_chart", "figure"), Input("year", "value"), Input("top_5_countries_feature", "value"))
def update_top_5_countries(year, feature):
    title = "Top 5 Countries"
    if year == None:
        return title, f"No Year selected", OVERLAY_SHOWN_STYLE,  px.bar()

    feature_data = FEATURES_DICT.get(feature, None)

    if feature_data == None:
        return title, "Please select a feature", OVERLAY_SHOWN_STYLE, px.bar()

    title = f"Top 5 Countries for {feature} in Year {year}"
    dff = df.copy()

    # First get all data in the same year
    dff = dff[dff["year"] == int(year)]

    # Then sort by the desired feature (e.g life ladder) and take the first 5.
    dff = dff.sort_values(by=feature_data, ascending=False)
    dff_top_5 = dff.head(5)
    return title, "", OVERLAY_HIDDEN_STYLE, px.bar(dff_top_5, x=feature_data, y="country_name", orientation="h", labels=FEATURES_LABELS)

@app.callback(Output("parallel_coordinate_system_title", "children"), Output("parallel_coordinate_system_overlay", "children"), Output("parallel_coordinate_system_overlay", "style"), Output("parallel_coordinate_system", "figure"), Input("year", "value"), Input("parallel_coordinate_system_features", "value"))
def update_parallel_coordinate_system(year, features_human_readable):
    # Implemented with reference to: https://plotly.com/python/parallel-coordinates-plot/
    title = f"Compare Features across all Countries"

    if year == None:
        return title, f"No Year selected", OVERLAY_SHOWN_STYLE, px.parallel_coordinates(pd.DataFrame())

    if features_human_readable == None or len(features_human_readable) < 2:
        return title, f"Please select at least two features", OVERLAY_SHOWN_STYLE, px.parallel_coordinates(pd.DataFrame())

    dff = df.copy()
    dff = dff[dff["year"] == int(year)]
    title =  f"Compare Features across all Countries in Year {year}"
    dimensions = [FEATURES_DICT.get(feature_human_readable, "") for feature_human_readable in features_human_readable]
    parallel_coordinates = px.parallel_coordinates(dff, color="life_ladder", dimensions=dimensions, color_continuous_scale=px.colors.sequential.Blues, labels=FEATURES_LABELS)

    return title, "", OVERLAY_HIDDEN_STYLE, parallel_coordinates

@app.callback(Output("simplified_explanation_overlay", "children"), Output("simplified_explanation_overlay", "style"), Output("simplified_explanation_container", "children"), Input("selected_country", "value"), Input("first_feature", "value"), Input("second_feature", "value"))
def udpate_simplified_explanation_detail(selected_country, first_feature, second_feature):
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

    # There are some countries like Maldives which only have one single value.
    # A correlation based on a single value is not really possible...
    if len(dff_country.index) <= 1:
        return f"Insufficient number of data in order to caluclate a meaningful correlation", OVERLAY_SHOWN_STYLE, []

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
    heatmap_title = "Correlation Information"
    if selected_country == None:
        return "No country selected", OVERLAY_SHOWN_STYLE, heatmap_title, px.imshow(pd.DataFrame()) 

    dff = df.copy()
    dff_country = dff[(dff["country_name"] == selected_country)]
    if dff_country.empty:
        return f"No data found for {selected_country}", OVERLAY_SHOWN_STYLE, heatmap_title, px.imshow(pd.DataFrame()) 

    columns = FEATURES_HUMAN_READABLE 
    dff_country = dff_country[FEATURES_IN_DATA]
    correlation = dff_country.corr(numeric_only=True)

    # There are some countries like Maldives which only have one single value.
    # A correlation based on a single value is not really possible...
    if len(dff_country.index) <= 1:
        return f"Insufficient number of data in order to caluclate a meaningful correlation", OVERLAY_SHOWN_STYLE, heatmap_title, px.imshow(pd.DataFrame())

    # Round correlation numbers so that they do not have some many decimal places
    # See https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.round.html
    correlation = correlation.round(2)

    heatmap = px.imshow(correlation, x=columns, y=columns, aspect="auto", text_auto=True, color_continuous_scale=px.colors.sequential.Blues, labels=FEATURES_LABELS)
    heatmap.update_xaxes(side="top")
    heatmap_title = f"Correlation Information about {selected_country}"
    return "", OVERLAY_HIDDEN_STYLE, heatmap_title, heatmap 

@app.callback(Output("scatter_plot_overlay", "children"), Output("scatter_plot_overlay", "style"), Output("features_title", "children"), Output("scatter_plot", "figure"), Input("selected_country", "value"), Input("first_feature", "value"), Input("second_feature", "value"))
def update_scatter_plot(selected_country, first_feature, second_feature):
    scatter_title = f"Comparing Features"
    if selected_country == None:
        return "No country selected", OVERLAY_SHOWN_STYLE, scatter_title, px.scatter() 

    first_feature_data = FEATURES_DICT.get(first_feature, None)
    second_feature_data = FEATURES_DICT.get(second_feature, None)

    if first_feature_data == None or second_feature_data == None:
        return f"Please choose at least two features", OVERLAY_SHOWN_STYLE, scatter_title, px.scatter() 

    dff = df.copy()
    dff_country = dff[(dff["country_name"] == selected_country)]
    if dff_country.empty:
        return f"No data found for {selected_country}", OVERLAY_SHOWN_STYLE, scatter_title, px.scatter() 

    # Implemented with reference to:
    # - https://plotly.com/python/text-and-annotations/
    # - https://plotly.com/python/linear-fits/
    scatter_plot = px.scatter(dff_country, x=first_feature_data, y=second_feature_data, text="year", trendline="ols", labels=FEATURES_LABELS)
    scatter_plot.update_traces(textposition='top center')
    scatter_title = f"Comparing {first_feature} and {second_feature} for {selected_country}"
    return "", OVERLAY_HIDDEN_STYLE, scatter_title, scatter_plot

if __name__ == '__main__':
    app.run_server(debug=True)
