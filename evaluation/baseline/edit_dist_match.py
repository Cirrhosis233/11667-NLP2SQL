import json
import sqlparse
import argparse
import os
from difflib import SequenceMatcher

def standardize_sql(sql):
    """
    Standardize the SQL statement to remove formatting differences.
    """
    # Format SQL for standardization using sqlparse
    parsed = sqlparse.format(sql, keyword_case='upper', identifier_case='lower', strip_comments=True, reindent=True)
    return parsed.strip()

def tokenize_sql(sql):
    """
    Tokenize the SQL statement for edit distance calculation.
    """
    tokens = sqlparse.parse(sql)[0].tokens
    return [str(token).strip() for token in tokens if str(token).strip()]

def token_level_edit_distance(sql1, sql2):
    """
    Calculate token-level edit distance between two SQL statements.
    """
    # Convert the sql string to a list of tokens
    tokens1 = tokenize_sql(sql1)
    tokens2 = tokenize_sql(sql2)
    matcher = SequenceMatcher(None, tokens1, tokens2)
    # Calculate edit distance based on unmatched tokens
    total_tokens = len(tokens1) + len(tokens2)
    unmatched = total_tokens - 2 * sum(block.size for block in matcher.get_matching_blocks())
    return unmatched

def evaluate_edit_distance(data):
    """
    Evaluate token-level edit distance for SQL generation accuracy.
    """
    total = len(data)
    total_edit_distance = 0

    for item in data:
        golden_sql = standardize_sql(item["answer"])
        generated_sql = standardize_sql(item["generation"])

        # Calculate token-level edit distance
        edit_distance = token_level_edit_distance(golden_sql, generated_sql)
        total_edit_distance += edit_distance

    # Average edit distance
    avg_edit_distance = total_edit_distance / total if total > 0 else 0
    return total, total_edit_distance, avg_edit_distance

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Evaluate SQL generation using token-level edit distance.")
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

    # Evaluate token-level edit distance
    total, total_edit_distance, avg_edit_distance = evaluate_edit_distance(data)

    print(f"File: {file_path}")
    print(f"Total Queries: {total}")
    print(f"Total Distance: {total_edit_distance}")
    print(f"Average Token-Level Edit Distance: {avg_edit_distance:.2f}")

if __name__ == "__main__":
    main()