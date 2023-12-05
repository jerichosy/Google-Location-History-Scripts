import json
import math

# Function to calculate distance between two points using Haversine formula
def haversine_distance(lat1, lon1, lat2, lon2):
    """This is an accurate implementation of the Haversine formula to calculate the
    distance between two points on a sphere given their longitudes and latitudes."""

    # Earth radius in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine calculation
    a = math.sin(delta_phi / 2.0)**2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

# Load JSON data (assuming it's stored in a file named 'Records.json' in the current directory)
FILENAME = 'Records.json'
with open(FILENAME, 'r') as file:
    print(f"{FILENAME} found, loading...")
    data = json.load(file)

# Prompt user for latitude, longitude, and radius
user_lat = float(input("Please enter latitude: "))
user_long = float(input("Please enter longitude: "))
radius_km = float(input("Please enter radius in kilometers: "))

for location in data['locations']:
    # Convert E7 format to standard latitude and longitude
    try:
        location_lat = location['latitudeE7'] / 1e7
        location_long = location['longitudeE7'] / 1e7
    except KeyError:
        # Skip locations that don't have latitude and longitude
        # print(location)
        continue

    # Calculate distance from user's location
    distance = haversine_distance(user_lat, user_long, location_lat, location_long)

    # If the location is within the specified radius, print it
    if distance <= radius_km:
        # print(f"Distance from user: {distance} km")
        print(f"Location within {radius_km} km: lat={location_lat}, long={location_long}, timestamp={location['timestamp']}")
