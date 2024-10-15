import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import os
import certifi
import urllib.parse

os.environ['SSL_CERT_FILE'] = certifi.where()


class Location:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude


def geocode_city(city):
    # Special case handling for "Morrill Tower"
    if city.lower() == "morrill tower":
        return Location(40.0002, -83.0220)

    # Make the request to Geoapify
    parsed_city = urllib.parse.quote(city)
    geoapify_url = f'https://api.geoapify.com/v1/geocode/search?text={parsed_city}&apiKey={st.secrets["geoapifyKey"]}'
    geocode_response = requests.get(geoapify_url).json()

    # Extract latitude and longitude from the response
    found_latitude = geocode_response["features"][0]["properties"]["lat"]
    found_longitude = geocode_response["features"][0]["properties"]["lon"]

    return Location(found_latitude, found_longitude)


# Function to parse the ISO date-time string and ignore the duration part
def parse_iso8601_time(iso_time_str):
    # Split the string by '/' and take the first part (before '/PT1H')
    time_str = iso_time_str.split('/')[0]

    # Parse the time string to a datetime object
    return datetime.fromisoformat(time_str)


# Input field to type a city name
city_input = st.text_input("Location:", value="Morrill Tower")

# Geocode the city
location = geocode_city(city_input)

# Find correct weather station in API
headers = {"User-Agent": st.secrets["email"]}
locationResponse = requests.get(f'https://api.weather.gov/points/{location.latitude},{location.longitude}',
                                headers=headers).json()
gridpointsURL = locationResponse["properties"]["forecastGridData"]

# Pull data off API
response = requests.get(gridpointsURL).json()

# Create subset of temperatures
temps = response["properties"]["temperature"]["values"]

# Create time and temperature lists
timeList = []
for x in temps:
    timeList.append(x["validTime"])
tempList = []
for x in temps:
    fahrenheit = (x["value"] * 1.8) + 32
    tempList.append(fahrenheit)

# Convert timeList to valid_times
valid_times = []
for i in timeList:
    valid_times.append(parse_iso8601_time(i))

# Dataframe of temp vs time
chart_data = pd.DataFrame(tempList,
                          valid_times)

# Creating dataframe for map
mapData = pd.DataFrame({
    'lat': [location.latitude],
    'lon': [location.longitude]
})

# Streamlit Display
st.title("Weather Forecast")
st.map(mapData, size=0)
st.line_chart(chart_data, x_label="Date", y_label="Temperature")
st.markdown('Powered by [Geoapify](https://www.geoapify.com/)')
