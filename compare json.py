import os
import json
from collections import Counter

# Define the directory that contains the JSON files
json_directory = '/path/to/json/files'

# Keep track of the values that appear in each file
values = []

# Loop over all files in the JSON directory
for filename in os.listdir(json_directory):
    # Check if the file is a JSON file
    if filename.endswith(".json"):
        # Construct the full path to the JSON file
        json_file = os.path.join(json_directory, filename)

        # Open the JSON file
        with open(json_file, "r") as file:
            # Load the JSON data from the file
            json_data = json.load(file)

            # Loop over all objects in the JSON data
            for obj in json_data.values():
                # Keep track of the values in this object
                values.append(list(obj.values()))

# Flatten the list of values
flattened_values = [value for sublist in values for value in sublist]

# Count the number of times each value appears
value_counts = Counter(flattened_values)

# Get the most common values
most_common_values = value_counts.most_common()

# Print the most common values
# for value, count in most_common_values:
    # print(f"{value}: {count}")

# Write the results to a JSON file
results_file = os.path.join(json_directory, "most_common_values.json")
with open(results_file, "w") as file:
    json.dump(most_common_values, file)