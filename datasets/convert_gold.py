import json
import itertools


def get_first_valid_combination(query: str) -> str:
    """
    Replace `{}` placeholders in the query with the first valid combination of columns.
    """
    start, end = query.find("{"), query.find("}")
    if start == -1 or end == -1:
        return query  # No `{}` placeholders, return as is

    column_options = query[start + 1:end].split(",")
    if not column_options:
        return query  # Empty `{}`, return as is

    # Select the first valid combination (all columns)
    column_str = ", ".join(col.strip() for col in column_options)
    updated_query = query[:start] + column_str + query[end + 1:]

    # Replace `GROUP BY {}` if it exists
    updated_query = updated_query.replace("GROUP BY {}", f"GROUP BY {column_str}")
    return updated_query


def update_gold_queries(input_file: str, output_file: str):
    """
    Update the `answer` field in the JSON file by replacing `{}` with valid combinations.
    """
    with open(input_file, "r") as infile:
        data = json.load(infile)

    for entry in data:
        if "answer" in entry:
            entry["answer"] = get_first_valid_combination(entry["answer"])

    with open(output_file, "w") as outfile:
        json.dump(data, outfile, indent=4)

    print(f"Updated queries saved to {output_file}")


input_file = "sql_eval_dataset.json"  
output_file = "sql_eval_dataset_executable_gold.json"  

# Run the update script
update_gold_queries(input_file, output_file)