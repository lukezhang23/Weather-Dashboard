import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from geopy.geocoders import Nominatim
import os
import certifi

os.environ['SSL_CERT_FILE'] = certifi.where()

# Input field to type a city name
city_input = st.text_input("City:", value="Columbus")

# Geocode the City
geolocator = Nominatim(user_agent=email)
location = geolocator.geocode(city_input)

# Find correct weather station in API
headers = {"User-Agent" : email}
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

# Streamlit Display

st.title("Sample Weather Dashboard")
st.line_chart(chart_data, x_label="Date", y_label="Temperature")
