import csv
import json

def parse_csv_to_json(csv_file_path, json_file_path):
    data = []
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            entry = {
                "question": row["question"],
                "answer": row["query"],
                "db_name": row["db_name"],
                "query_category": row["query_category"],
                "instructions": row.get("instructions", "").strip(),
                "full_instructions": row.get("full_instructions", "").strip()
            }
            data.append(entry)
    
    # Write the JSON data to file
    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

csv_file_path = "instruct_advanced_postgres.csv"  
json_file_path = "output.json"  

parse_csv_to_json(csv_file_path, json_file_path)

print(f"JSON file has been created at: {json_file_path}")