import json
import sqlparse
import argparse
import os

def standardize_sql(sql):
    """
    Standardize the SQL statement to remove formatting differences.
    """
    # Format SQL for standardization using sqlparse
    parsed = sqlparse.format(sql, keyword_case='upper', identifier_case='lower', strip_comments=True, reindent=True)
    return parsed.strip()

def exact_match_accuracy(data):
    """
    Calculate the exact match accuracy between answer and generation fields in the JSON data.
    """
    total = len(data)
    matches = 0

    for item in data:
        # Extract and standardize the SQL from 'answer' and 'generation'
        answer = standardize_sql(item["answer"])
        generation = standardize_sql(item["generation"])

        # Perform exact match
        if answer == generation:
            matches += 1

    # Calculate accuracy
    accuracy = matches / total if total > 0 else 0
    return matches, total, accuracy

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Evaluate SQL generation accuracy.")
    parser.add_argument("-f", "--file", required=True, help="Path to the JSON file for evaluation.")
    args = parser.parse_args()

    file_path = os.path.join(os.getcwd(), args.file)
    if not os.path.isfile(file_path):
        print(f"Error: File not found at {file_path}")
        return

    # Load the JSON data
    try:
        with open(file_path, 'r') as file:
            data = [json.loads(line) for line in file]
    except Exception as e:
        print(f"Error: Unable to read or parse the JSON file. Details: {e}")
        return

    # Calculate the exact match accuracy
    matches, total, accuracy = exact_match_accuracy(data)

    print(f"File: {file_path}")
    print(f"Total Queries: {total}")
    print(f"Exact Matches: {matches}")
    print(f"Accuracy: {accuracy * 100:.2f}%")

if __name__ == "__main__":
    main()