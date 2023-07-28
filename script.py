import csv
import json
import os

input_file_path = os.path.join('static', 'input', 'data.json')
output_file_path = os.path.join('static', 'output', 'output.csv')

# Load the JSON data from the file
with open(input_file_path, 'r') as file:
    data = json.load(file)

# Extract the "reqid" and "rationale" fields for each entry
csv_data = [['reqid', 'rationale']]
for entry in data:
    reqid = entry.get('reqid', '')
    rationale = entry.get('rationale', '')
    csv_data.append([reqid, rationale])

# Save the extracted data as a CSV file
with open(output_file_path, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(csv_data)

print("CSV file has been created successfully.")