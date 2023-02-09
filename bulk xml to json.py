import os
import xmltodict

# Define the directory that contains the XML files
xml_directory = '/path/to/xml/files'

# Define the directory to write the JSON files to
json_directory = '/path/to/json/files'

# Loop over all files in the directory
for filename in os.listdir(xml_directory):
    # Check if the file is an XML file
    if filename.endswith(".xml"):
        # Construct the full path to the file
        file_path = os.path.join(xml_directory, filename)

        # Open the XML file
        with open(file_path, "r") as file:
            # Read the XML data from the file
            xml_data = file.read()

        # Parse XML Data
        xml_data2 = xmltodict.parse(xml_data)

        # Convert XML to JSON
        json_data = json.dumps(xml_data2)

        # Construct the full path to the output JSON file
        json_file = os.path.join(json_directory, os.path.splitext(filename)[0] + ".json")

        # Save the JSON data to a file
        with open(json_file, "w") as file:
            file.write(str(json_data))

