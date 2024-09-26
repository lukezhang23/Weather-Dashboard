import requests
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates

# Pull data off API
response = requests.get("https://api.weather.gov/gridpoints/LWX/97,71").json()

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

# Plot the line chart
plt.plot(valid_times, tempList, marker='o')

# Format the x-axis to display dates nicely
plt.gcf().autofmt_xdate()  # Auto-rotate dates for better readability
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))  # Custom date format

# Display the plot
plt.tight_layout()
plt.show()
