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

def add_iso_specific_country_columns(data):
    # Make a name column for iso specific notation  based on the current country_name
    data["country_name_iso"] = data["country_name"]
    data["country_name_iso"] = data["country_name_iso"].replace(CORRECTED_COUNTRY_NAMES)

    # Make a country code column for iso specific notation.
    data["country_code_iso"] = data.apply(lambda x: get_short_country_code(x["country_name_iso"]), axis=1)
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

def get_total_number_of_ranks(data, year):
    return len(data[data["year"] == year])

def calculate_country_ranking(data, country_name, year, feature):
    # Compare all countries in the same year
    data = data[(data["year"] == year)]
    # Extract country name and its associated feature (e.g Life Ladder)
    data = data[["country_name", feature]]
    # Create a dictionary which associates a country name with the given feature (e.g <feature_value>: <country_name>)
    feature_table = data.to_dict()["country_name"]
    # Sort them in descending order by the feature value note that this is now a list of tuple pairs
    result = sorted(feature_table.items(), key=lambda x:x[0], reverse=True)
    # Now all we have to do is get the index + 1 (because 0 based)  where the country name matches and we have our ranking
    rank = [index + 1 for (index, (feature_value, country)) in enumerate(result) if country == country_name][0]
    # Currently this would be terrible for performance at runtime as we build up the dictionary etc. for each for. But because we pre calulate the result and simply lookup the precalculated result at runtime it is fine. 
    return rank 

def precalculate_country_ranking(data):
    data["total_number_of_ranks"] = data.apply(lambda x: get_total_number_of_ranks(data, x["year"]), axis=1)
    data["life_ladder_rank"] = data.apply(lambda x: calculate_country_ranking(data, x["country_name"], x["year"], "life_ladder"), axis=1)
    data["log_gdp_rank"] = data.apply(lambda x: calculate_country_ranking(data, x["country_name"], x["year"], "log_gdp"), axis=1)
    data["social_support_rank"] = data.apply(lambda x: calculate_country_ranking(data, x["country_name"], x["year"], "social_support"), axis=1)
    data["life_expectancy_rank"] = data.apply(lambda x: calculate_country_ranking(data, x["country_name"], x["year"], "life_expectancy"), axis=1)
    data["freedom_rank"] = data.apply(lambda x: calculate_country_ranking(data, x["country_name"], x["year"], "freedom"), axis=1)
    data["generosity_rank"] = data.apply(lambda x: calculate_country_ranking(data, x["country_name"], x["year"], "generosity"), axis=1)
    data["corruption_rank"] = data.apply(lambda x: calculate_country_ranking(data, x["country_name"], x["year"], "corruption"), axis=1)
    data["positive_affect_rank"] = data.apply(lambda x: calculate_country_ranking(data, x["country_name"], x["year"], "positive_affect"), axis=1)
    data["negative_affect_rank"] = data.apply(lambda x: calculate_country_ranking(data, x["country_name"], x["year"], "negative_affect"), axis=1)
    data["confidence_in_government_rank"] = data.apply(lambda x: calculate_country_ranking(data, x["country_name"], x["year"], "confidence_in_government"), axis=1)
    return data

if __name__ == "__main__":
    df  = pd.read_csv("./data.csv", encoding="utf-8")
    df = remove_columns(df)
    df = rename_columns(df)
    df = remove_countries(df)
    df = add_iso_specific_country_columns(df)
    df = fill_in_missing_values(df)

    # Precalculate ranking for countries so that we do not have to do this at runtime...
    df = precalculate_country_ranking(df)
    
    # Write out cleaned data and drop index
    df.to_csv("./data_cleaned.csv", index=False)
