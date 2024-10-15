import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import os
import certifi
import urllib.parse

os.environ['SSL_CERT_FILE'] = certifi.where()

# Input field to type a city name
city_input = st.text_input("Location:", value="Morrill Tower")

# Geocode the City
parsedCity = urllib.parse.quote(city_input)
geoapifyUrl = f'https://api.geoapify.com/v1/geocode/search?text={parsedCity}&apiKey={st.secrets["geoapifyKey"]}'
geocodeResponse = requests.get(geoapifyUrl).json()
latitude = geocodeResponse["features"][0]["properties"]["lat"]
longitude = geocodeResponse["features"][0]["properties"]["lon"]

# Find correct weather station in API
headers = {"User-Agent": st.secrets["email"]}
locationResponse = requests.get(f'https://api.weather.gov/points/{latitude},{longitude}',
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


# Function to parse the ISO date-time string and ignore the duration part
def parse_iso8601_time(iso_time_str):
    # Split the string by '/' and take the first part (before '/PT1H')
    time_str = iso_time_str.split('/')[0]

    # Parse the time string to a datetime object
    return datetime.fromisoformat(time_str)


# Convert timeList to valid_times
valid_times = []
for i in timeList:
    valid_times.append(parse_iso8601_time(i))

# Dataframe of temp vs time
chart_data = pd.DataFrame(tempList,
                          valid_times)

# Creating dataframe for map
mapData = pd.DataFrame({
    'lat': [latitude],
    'lon': [longitude]
})

# Streamlit Display
st.title("Weather Forecast")
st.map(mapData, size=0)
st.line_chart(chart_data, x_label="Date", y_label="Temperature")
