import pandas as pd

# Because we use the built in Choropleth Map we need to provide the Country as a 3 letter ISO notation.
# See "Using Built-in Country and state Geometry: https://plotly.com/python/choropleth-maps/
# In order to do this we use the pycountry library.
import pycountry

RENAMED_COLUMNS = {
    "Country Name": "country_name",
    "Year": "year",
    "Life Ladder": "life_ladder",
    "Log GDP Per Capita": "log_gdp",
    "Social Support": "social_support",
    "Healthy Life Expectancy At Birth": "life_expectancy",
    "Freedom To Make Life Choices": "freedom",
    "Generosity": "generosity",
    "Perceptions Of Corruption": "corruption",
    "Positive Affect": "positive_affect",
    "Negative Affect": "negative_affect",
    "Confidence In National Government": "confidence_in_government"
}

REMOVED_COLUMNS = ["Regional Indicator"]


# There are some country names that pycountry is unable to resolve. Therefore we rename these countries accordingly.
# Source: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3
CORRECTED_COUNTRY_NAMES = {
    "Hong Kong S.A.R. of China": "Hong Kong",
    "Taiwan Province of China": "Taiwan, Province of China",
    "State of Palestine": "Palestine, State of",
    "Turkiye": "Turkey",
    "South Korea": "Korea, Republic of",
    "Laos": "Lao People's Democratic Republic",
    "Moldova": "Moldova, Republic of",
    "Syria": "Syrian Arab Republic",
    "Tanzania": "Tanzania, United Republic of",
    "Vietnam": "Viet Nam",
    "Congo (Brazzaville)": "Congo",
    "Congo (Kinshasa)": "Congo, The Democratic Republic of the",
    "Venezuela": "Venezuela, Bolivarian Republic of",
    "Bolivia": "Bolivia, Plurinational State of",
    "Russia": "Russian Federation",
    "Iran": "Iran, Islamic Republic of",
    "Somaliland region": "Somalia"
}

# There are also some names that simply do not have a valid country code (according to wikipedia)
REMOVED_COUNTRY_NAMES = ["Kosovo", "Ivory Coast"]

def get_short_country_code(country_name):
    country = pycountry.countries.get(name=country_name)
    if country == None:
       return None 
    return country.alpha_3 

def get_country_names(data):
    return list(set(data["country_name"])) 

def remove_countries(data):
    for country_name in REMOVED_COUNTRY_NAMES:
        data.drop(data[data['country_name'] == country_name].index, inplace = True)
    return data

def correct_country_names(data):
    # Make a name column for iso specific notation  based on the current country_name
    data["country_name_iso"] = data["country_name"]
    data["country_name_iso"] = data["country_name_iso"].replace(CORRECTED_COUNTRY_NAMES)
    return data

def rename_columns(data):
    data = data.rename(columns=RENAMED_COLUMNS)
    return data

def remove_columns(data):
    data = data.drop(columns=REMOVED_COLUMNS)
    return data

def fill_in_missing_values(data):
    # Some rows do have missing values we try to fill those in by interpolating
    # Implemented with reference to: https://www.makeuseof.com/fill-missing-data-with-pandas/
    data.interpolate(method ='linear', limit_direction ='forward', inplace=True)
    return data

if __name__ == "__main__":
    df  = pd.read_csv("./data.csv", encoding="utf-8")
    df = remove_columns(df)
    df = rename_columns(df)
    df = correct_country_names(df)
    df = remove_countries(df)

    # Create a new column for the short hand country code
    df["country_code_iso"] = df.apply(lambda x: get_short_country_code(x["country_name_iso"]), axis=1)
    
    df = fill_in_missing_values(df)

    # Write out cleaned data
    df.to_csv("./data_cleaned.csv")
