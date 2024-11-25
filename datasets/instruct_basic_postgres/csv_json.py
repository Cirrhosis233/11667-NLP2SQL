import csv
import json
from collections import OrderedDict

def csv_to_json_reordered(csv_file_path, json_file_path):
    data = []

    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            # Construct a dictionary for each row with reordered keys
            entry = OrderedDict({
                "question": row["question"],
                "answer": row["query"],
                "context": row["db_name"],
                "query_category": row["query_category"]
            })
            data.append(entry)

    # Write the reordered data to a JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    print(f"JSON file with reordered keys has been created at: {json_file_path}")

# Specify the input CSV file and output JSON file paths
csv_file_path = "instruct_basic_postgres.csv"  # Replace with your input CSV file path
json_file_path = "output.json"  # Replace with your desired output JSON file path

# Convert the CSV to JSON with reordered keys
csv_to_json_reordered(csv_file_path, json_file_path)