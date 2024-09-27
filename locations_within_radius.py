import argparse
import json
import math
from collections import defaultdict
from datetime import datetime, timedelta

import pytz

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Process locations within a certain radius and adjust timestamps for a timezone.")
parser.add_argument('-tz', '--timezone', help='Timezone to convert the timestamp to, e.g., Asia/Manila')
parser.add_argument('--perday', action='store_true', help='Print the first and last location instances for each day')
args = parser.parse_args()

# Check if perday is True but timezone is not set
if args.perday and not args.timezone:
    parser.error("--perday requires --timezone to be set.")

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

# Function to convert timestamp to a different timezone and return a datetime object
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

    # Test case for when timestamp fails to convert
    # raise ValueError(f"Test when timestamp fails to convert")

    utc_time = utc_time.replace(tzinfo=pytz.utc)
    target_timezone = pytz.timezone(timezone_name)
    return utc_time.astimezone(target_timezone)

# Function to get the difference in hours between two timestamps
def get_hours_difference(start, end):
    fmt = "%Y-%m-%d %H:%M:%S %Z (%A)"
    start_dt = datetime.strptime(start, fmt)
    end_dt = datetime.strptime(end, fmt)
    return (end_dt - start_dt).total_seconds() / 3600

# Load JSON data (assuming it's stored in a file named 'Records.json' in the current directory)
FILENAME = 'Records.json'
with open(FILENAME, 'r') as file:
    print(f"{FILENAME} found, loading...")
    data = json.load(file)

# Prompt user for latitude, longitude, and radius
user_lat, user_long = map(float, input("Please enter latitude and longitude (comma separated): ").split(","))
radius_km = float(input("Please enter radius in kilometers: "))

# Create a dictionary to store lists of locations for each date
daily_locations = defaultdict(list)

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

    # If the location is within the specified radius, process it
    if distance <= radius_km:
        # When timezone is provided, only the datetime objects are stored and processed
        if args.timezone:
            # Convert the timestamp to a datetime object
            try:
                location_datetime = convert_timestamp(location['timestamp'], args.timezone)
                local_date = location_datetime.strftime("%Y-%m-%d %H:%M:%S %Z (%A)")
                # Add location to its corresponding date's list
                day = local_date.split()[0]  # key for daily_locations dictionary
                daily_locations[day].append((distance, location_datetime, location_lat, location_long))
            except Exception as e:
                print(f"Error converting and processing timestamp: {e}")
                # Set to 'N/A' because we don't want to skip any location instance (the lat/long will be useful for debugging)
                # and we want to be explicit, so we don't accidentally use the wrong timestamp
                local_date = 'N/A'
        else:
            local_date = location['timestamp']

        # If not in first/last mode, print every location
        if not args.perday:
            print(f"Location within {radius_km} km: lat={location_lat}, long={location_long}, timestamp={local_date}")

time_differences = {}  # Store time differences for each date

# If in first/last mode, process the dictionary to print the first and last location for each day
if args.perday:
    for date, locations in daily_locations.items():
        first = locations[0]
        last = locations[-1]

        # Print the first (and last if different) location instance
        for location in [first, (last if first != last else None)]:
            if location is not None:
                _, location_datetime, lat, long = location
                print(f"Location within {radius_km} km: lat={lat}, long={long}, timestamp={location_datetime.strftime('%Y-%m-%d %H:%M:%S %Z (%A)')}")

        # Calculate the time difference between the first and last location for this date
        if first != last:
            time_diff = (last[1] - first[1]).total_seconds() / 3600
            print(f"Time spent in vicinity: {time_diff:.2f} hours")
            time_differences[date] = time_diff

        print()

# At the end, print the top days with the longest time spent in vicinity
if time_differences:
    time_differences = sorted(time_differences.items(), key=lambda x: x[1], reverse=True)

    # top = min(15, len(time_differences))  # print top days
    top = len(time_differences) // 4  # print top days

    # print top longest
    print(f"Top {top} longest time spent in vicinity:")
    for date, hours in time_differences[:top]:
        print(f"{date}: {hours:.2f} hours")
