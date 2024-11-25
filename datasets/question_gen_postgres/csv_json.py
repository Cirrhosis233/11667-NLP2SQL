import csv
import json

def csv_to_json(csv_file_path, json_file_path):
    data = []
    
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        
        for row in csv_reader:
            # Construct a dictionary for each row
            entry = {
                "question": row["question"],
                "answer": row["query"],
                "context": row["db_name"],
                "query_category": row["query_category"]
            }
            # Add instructions if they exist
            if "instructions" in row and row["instructions"].strip():
                entry["instructions"] = row["instructions"]
            
            data.append(entry)
    
    # Write to a JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

# Specify the input CSV file and output JSON file paths
csv_file_path = "questions_gen_postgres_copy.csv"  # Replace with your input CSV file path
json_file_path = "output.json"  # Replace with your desired output JSON file path

# Convert the CSV to JSON
csv_to_json(csv_file_path, json_file_path)

print(f"JSON file has been created at: {json_file_path}")