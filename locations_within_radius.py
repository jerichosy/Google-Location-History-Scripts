import argparse
import json
import math
from datetime import datetime

import pytz

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Process locations within a certain radius and adjust timestamps for a timezone.")
parser.add_argument('-tz', '--timezone', help='Timezone to convert the timestamp to, e.g., "Asia/Manila".', default="")
args = parser.parse_args()

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

# Function to convert timestamp to a different timezone and make it human-readable
def convert_timestamp(time_string, timezone_name):
    # Try parsing the timestamp with and without milliseconds
    for fmt in ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"]:
        try:
            utc_time = datetime.strptime(time_string, fmt)
        except ValueError:
            continue
        else:
            break
    else:
        raise ValueError(f"time data '{time_string}' does not match format with or without milliseconds")

    utc_time = utc_time.replace(tzinfo=pytz.utc)
    target_timezone = pytz.timezone(timezone_name)
    local_time = utc_time.astimezone(target_timezone)
    return local_time.strftime("%Y-%m-%d %H:%M:%S %Z (%A)")

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
        if args.timezone:
            # Convert the timestamp
            try:
                human_readable_timestamp = convert_timestamp(location['timestamp'], args.timezone)
            except Exception as e:
                print(f"Error converting timestamp: {e}")
                human_readable_timestamp = 'N/A'
        else:
            human_readable_timestamp = location['timestamp']

        print(f"Location within {radius_km} km: lat={location_lat}, long={location_long}, timestamp={human_readable_timestamp}")
