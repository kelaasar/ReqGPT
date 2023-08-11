import json
import csv

def json_to_csv(json_path, csv_path):
    with open(json_path, 'r') as json_file:
        data = json.load(json_file)

    with open(csv_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["reqid", "rationale"])  # Write header

        for item in data:
            reqid = item.get("reqid", "")
            rationale = item.get("rationale", "")
            csv_writer.writerow([reqid, rationale])