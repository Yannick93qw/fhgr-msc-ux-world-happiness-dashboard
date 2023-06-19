import pandas as pd

# Because we use the built in Choropleth Map we need to provide the Country as a 3 letter ISO notation.
# See "Using Built-in Country and state Geometry: https://plotly.com/python/choropleth-maps/
# In order to do this we use the pycountry library.
import pycountry

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
    return list(set(data["Country Name"])) 

def remove_countries(data):
    for country_name in REMOVED_COUNTRY_NAMES:
        data.drop(data[data['Country Name'] == country_name].index, inplace = True)
    return data

def correct_country_names(data):
    data = data.replace(CORRECTED_COUNTRY_NAMES)
    return data

if __name__ == "__main__":
    df  = pd.read_csv("./data.csv", encoding="utf-8")
    df = remove_countries(df)
    df = correct_country_names(df)

    # Create a new column for the short hand country code
    df["Country Code"] = df.apply(lambda x: get_short_country_code(x["Country Name"]), axis=1)

    # Write out cleaned data
    df.to_csv("./data_cleaned.csv")
