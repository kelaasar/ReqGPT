import json
import csv

def json_to_csv(json_path, csv_path):
    with open(json_path, 'r') as json_file:
        data = json.load(json_file)

    with open(csv_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        # Assuming data is a list of dictionaries with the same keys
        csv_writer.writerow(data[0].keys())  # Write header
        for item in data:
            csv_writer.writerow(item.values())
