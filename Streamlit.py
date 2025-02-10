import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import urllib.parse
from enum import Enum


class Status(Enum):
    GOOD = 1
    INVALID_GEOAPIFY_SEARCH = 2
    LOCATION_NOT_FOUND = 3
    NOT_IN_US = 4
    WEATHER_GOV_ERROR = 5


class Location:
    def __init__(self, latitude, longitude, status):
        self.latitude = latitude
        self.longitude = longitude
        self.status = status


class Weather:
    def __init__(self, dataframe, status):
        self.dataframe = dataframe
        self.status = status


@st.cache_data(show_spinner=False, ttl=60)
def get_weather_data(latitude, longitude):
    """
    Fetches temperature data for a given location using the National Weather Service API.
    """
    headers = {"User-Agent": st.secrets["email"]}

    try:
        # Get the forecast grid data URL from the initial location response
        location_response = requests.get(
            f'https://api.weather.gov/points/{latitude},{longitude}',
            headers=headers
        )
        location_response.raise_for_status()
        gridpoints_url = location_response.json()["properties"]["forecastGridData"]

        # Get temperature data from the forecast grid
        response = requests.get(gridpoints_url, headers=headers)
        response.raise_for_status()

    except requests.exceptions.RequestException:
        return Weather(None, Status.WEATHER_GOV_ERROR)

    #Extracting time and temperature (c-->f) to dataframe
    weatherdf = extract_to_df(response.json(), "temperature")

    return Weather(weatherdf, Status.GOOD)


def streamlit_output(coordinates, temps, location_status, weather_status):
    st.title("Weather Forecast")

    # Regular output for good status
    if location_status == Status.GOOD and weather_status == Status.GOOD:
        st.map(coordinates, size=0)
        st.line_chart(temps, x_label="Date", y_label="Temperature")

    # Error outputs for error statuses
    elif location_status == Status.INVALID_GEOAPIFY_SEARCH:
        st.error("Invalid search.")
    elif location_status == Status.LOCATION_NOT_FOUND:
        st.error("Location not found, please try another location. (Geoapify retrieval error)")
    elif location_status == Status.NOT_IN_US:
        st.error("Location not in the United States, please select a different location.")
    elif weather_status == Status.WEATHER_GOV_ERROR:
        st.error("Error, please try another location. If you believe this is a mistake please try again in 1 minute.")
    else:
        st.error("Error, please try another location (Uncaught error)")

    # Geoapify attribution
    st.markdown('Powered by [Geoapify](https://www.geoapify.com/)')


@st.cache_data(show_spinner=False, ttl=43200)
def geocode_city(city):
    # Morrill Tower coordinates
    found_latitude = 40.00007409649716
    found_longitude = -83.0219446815833
    status = Status.GOOD

    # If not Morrill Tower, find coordinates
    if city.lower() != "morrill tower":

        # Make the request to Geoapify
        parsed_city = urllib.parse.quote(city)
        geoapify_url = (f'https://api.geoapify.com/v1/geocode/search?text={parsed_city}&format=json'
                        f'&apiKey={st.secrets["geoapifyKey"]}&bias=countrycode:us')
        geocode_response = requests.get(geoapify_url).json()

        # Check that search is not a bad request
        if "results" not in geocode_response:
            status = Status.INVALID_GEOAPIFY_SEARCH

        # Check that location was found
        elif not geocode_response["results"]:
            status = Status.LOCATION_NOT_FOUND

        else:
            found = False
            i = 0
            while not found and i < len(geocode_response["results"]):
                # Check that location is in United States
                if geocode_response["results"][i]["country_code"] == "us":
                    found_latitude = geocode_response["results"][i]["lat"]
                    found_longitude = geocode_response["results"][i]["lon"]
                    found = True
                i += 1
            if not found:
                status = Status.NOT_IN_US
    return Location(found_latitude, found_longitude, status)


# Function to convert json into a dataframe
def extract_to_df(json, property):

    df = pd.DataFrame(columns=[property])
    values = json["properties"][property]["values"]

    for entry in values:
        start_time, duration = entry["validTime"].split("/")
        start_dt = datetime.fromisoformat(start_time)  # Convert to datetime
        hours = int(duration.replace("PT", "").replace("H", ""))  # Extract duration in hours

        # Add an entry for each hour in the duration
        for hour_offset in range(hours):
            time_entry = [start_dt + timedelta(hours=hour_offset)]
            temp_entry = [(entry["value"] * 1.8) + 32]
            df_entry = pd.DataFrame(temp_entry, index=time_entry, columns=[property])
            if df.empty: # Avoids concatenation of an empty df
                df = df_entry
            else:
                df = pd.concat([df, df_entry])

    return df

# Function to get autocomplete suggestions from geoapify
@st.cache_data(show_spinner=False, ttl=43200)
def get_autocomplete_suggestions(query):
    try:
        response = requests.get("https://api.geoapify.com/v1/geocode/autocomplete?" +
                                f"text={query}&format=json&apiKey={st.secrets["geoapifyKey"]}&bias=countrycode:us").json()
        if response["results"]:
            result = []
            for i in range(len(response["results"])):
                if response["results"][i]["country_code"] == "us":
                    result.append(response["results"][i]["formatted"])
            return result
        else:
            return []
    except Exception as e:
        st.error(f"Error fetching suggestions: {e}")
        return []


def suggestion_trigger():
    if 'selected_suggestion' in st.session_state:
        st.session_state["field_value"] = st.session_state["selected_suggestion"]


def initialize_session_state():
    if "field_value" not in st.session_state:
        st.session_state["field_value"] = "Morrill Tower"
    if "last_typed_value" not in st.session_state:
        st.session_state["last_typed_value"] = st.session_state["field_value"]
    if "suggestions" not in st.session_state:
        st.session_state["suggestions"] = []


initialize_session_state()
# Input field to type a city name
city_input = st.text_input("Location:", value=st.session_state["field_value"])

if city_input != st.session_state["last_typed_value"]:
    st.session_state["last_typed_value"] = city_input
    if city_input == st.session_state["last_typed_value"]:
        st.session_state["suggestions"] = get_autocomplete_suggestions(city_input)
if st.session_state["suggestions"]:
    st.pills("Suggestions", st.session_state["suggestions"], on_change=suggestion_trigger, key="selected_suggestion")

# Make API calls for data
location = geocode_city(city_input)
weather = get_weather_data(location.latitude, location.longitude)

# Creating dataframe from coordinates
coordinatesdf = pd.DataFrame({
    'lat': [location.latitude],
    'lon': [location.longitude]
})

streamlit_output(coordinatesdf, weather.dataframe, location.status, weather.status)
