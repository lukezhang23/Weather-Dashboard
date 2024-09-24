import geojson
import pprint as pp
import geopandas as gpd

with open('hourly.geojson', 'r') as file:
    geojson_data = geojson.load(file)

# Now, let's print the GeoJSON data to understand its structure
pp.pprint(dict(geojson_data))
print(type(geojson_data))

# Load the GeoJSON file into a GeoDataFrame
gdf = gpd.read_file('hourly.geojson')

# If you just want a standard pandas DataFrame (and not GeoDataFrame), you can convert:
df = gdf.drop(columns='geometry')  # Drop the geometry column if needed

gdf