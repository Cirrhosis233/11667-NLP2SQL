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
    It measures the differences based on logical units (tokens) like keywords, table names, column names, operators, and so on.
    Edit distance is a measure of how many changes (insertions, deletions, or substitutions) are needed to transform one sequence into another. In this context:
	•	Insertions: Adding a missing token in the generated SQL.
	•	Deletions: Removing an extra token in the generated SQL.
	•	Substitutions: Replacing one token with another to make the SQL statements match.
    Examples:
    - Deletion:
	•	Gold SQL: SELECT name, age FROM students
	•	Generated SQL: SELECT name FROM students
	•	Edit Distance: 1 (One missing token: age)
	- Substitution:
	•	Gold SQL: SELECT name FROM students
	•	Generated SQL: SELECT name FROM teachers
	•	Edit Distance: 1 (One token difference: students vs. teachers)
    - Complex Difference:
	•	Gold SQL: SELECT name, age FROM students WHERE age > 18
	•	Generated SQL: SELECT name FROM students WHERE age < 18
	•	Edit Distance: 3
	•	Token changes: age removed, > replaced with <, and age added after SELECT.
    """
    # Convert the sql string to a list of tokens
    tokens1 = tokenize_sql(sql1)
    tokens2 = tokenize_sql(sql2)
    matcher = SequenceMatcher(None, tokens1, tokens2)
    """
    Example: 
    seq1 = ["SELECT", "name", ",", "age", "FROM", "students", "WHERE", "age", ">", "18"]
    seq2 = ["SELECT", "name", "FROM", "students", "WHERE", "age", "<", "18"]
    matcher.get_matching_blocks(): 
    [Match(a=0, b=0, size=2), Match(a=4, b=2, size=3), Match(a=8, b=6, size=1), Match(a=10, b=8, size=0)]
    """
    # Calculate edit distance based on unmatched tokens
    total_tokens = len(tokens1) + len(tokens2)
    unmatched = total_tokens - 2 * sum(block.size for block in matcher.get_matching_blocks())
    return unmatched

def evaluate_edit_distance(data, skip_penalty_multiplier=3):
    """
    Evaluate token-level edit distance for SQL generation accuracy.
    """
    total = len(data)
    total_edit_distance = 0
    # i = 0
    skipped_queries = 0

    for item in data:
        # print(f"{i}")
        golden_sql = standardize_sql(item["answer"])
        generated_sql = standardize_sql(item["generation"])
        if not generated_sql:
            # If generated_sql is empty, log it and assign maximum penalty
            # print(f"Warning: Empty generated SQL for query index {i}")
            skipped_queries += 1
            total_edit_distance += skip_penalty_multiplier * len(tokenize_sql(golden_sql))
            # i += 1
            continue

        # Calculate token-level edit distance
        edit_distance = token_level_edit_distance(golden_sql, generated_sql)
        total_edit_distance += edit_distance
        # i += 1

    # Average edit distance
    avg_edit_distance = total_edit_distance / total if total > 0 else 0
    return total, total_edit_distance, avg_edit_distance, skipped_queries

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
    total, total_edit_distance, avg_edit_distance, empty_gen = evaluate_edit_distance(data)

    print(f"File: {file_path}")
    print(f"Total Queries: {total}")
    print(f"Total Distance: {total_edit_distance}")
    print(f"Skipped Count (empty generation): {empty_gen}")
    print(f"Average Token-Level Edit Distance: {avg_edit_distance:.2f}")

if __name__ == "__main__":
    main()