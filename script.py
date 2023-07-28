import csv
import json
import os
import sys

def read_json_to_csv(input_file_path, output_file_path):
    # Check if the input file exists
    if not os.path.exists(input_file_path):
        print(f"Error: Input file '{input_file_path}' not found.")
        return

    # Determine the file extension to handle different input file types
    file_extension = os.path.splitext(input_file_path)[1].lower()

    if file_extension == '.json':
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
    else:
        print(f"Error: Unsupported file type '{file_extension}'. Only JSON files are supported.")

# This function is not used here, but you can keep it if you need to call it separately
def convert_to_csv(input_file_path, output_file_path):
    read_json_to_csv(input_file_path, output_file_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py input_file_path")
    else:
        input_file_path = sys.argv[1]
        output_file_path = os.path.join('static', 'output', 'output.csv')
        read_json_to_csv(input_file_path, output_file_path)