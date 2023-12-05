import json
from datetime import datetime
from collections import defaultdict

# Open and read the JSON file
with open('Records.json', 'r') as file:
    data = json.load(file)

# Initialize a set to keep track of observed months and years
observed_months = set()

# Loop through the locations
for location in data['locations']:
    # Extract the timestamp and convert it to a datetime object
    timestamp = datetime.fromisoformat(location['timestamp'])

    # Create a tuple of (year, month) and add it to the set
    year_month = (timestamp.year, timestamp.month)
    observed_months.add(year_month)

# Now, generate a set of all (year, month) from 2013 to 2023
all_months = set((year, month) for year in range(2013, datetime.now().year+1) for month in range(1, 13))

# Use set difference to find out what is missing
missing_months = all_months - observed_months

if missing_months:
    print(f"Missing months in dataset: {sorted(missing_months)}")
else:
    print("All months from 2013 to 2023 are present in the dataset.")

# Count missing months per year and total missing months
missing_months_per_year = defaultdict(int)
total_missing_months = 0

# Iterate over the missing months, incrementing the respective counters
for year_month in missing_months:
    year, month = year_month
    missing_months_per_year[year] += 1
    total_missing_months += 1

# Print the tally of missing months per year
for year, count in sorted(missing_months_per_year.items()):
    print(f"Year {year} is missing {count} months.")

# Print the total number of missing months
print(f"Total number of months missing in the dataset: {total_missing_months}")
