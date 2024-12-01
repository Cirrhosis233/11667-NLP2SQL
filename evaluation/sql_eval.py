# References:
# https://github.com/defog-ai/sql-eval/blob/main/eval/eval.py
# https://github.com/defog-ai/sql-eval/blob/main/tests/local_db_tests.py

import json
import pandas as pd
from sqlalchemy import create_engine
from typing import Dict, Tuple, List
import itertools
import re
import collections

LIKE_PATTERN = r"LIKE[\s\S]*'"


def deduplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure column names in DataFrame are unique.
    SQL queries may result in DataFrames with duplicate column names (e.g., after JOIN operations), which may cause errors during comparison.
    """
    cols = df.columns.tolist()
    if len(cols) != len(set(cols)):
        duplicates = [item for item, count in collections.Counter(cols).items() if count > 1]
        for dup in duplicates:
            indices = [i for i, x in enumerate(cols) if x == dup]
            for i in indices:
                cols[i] = f"{dup}_{i}"
        df.columns = cols
    return df


def normalize_table(
    df: pd.DataFrame, query_category: str, question: str, sql: str = None
) -> pd.DataFrame:
    """
    Normalizes a dataframe by:
    1. Removing duplicate rows.
    2. Ensuring unique column names.
    3. Sorting columns in alphabetical order.
    4. Sorting rows based on ordering criteria (e.g., ORDER BY or inferred intent from the question).
    5. Resetting the index.

    Args:
        df (pd.DataFrame): Input DataFrame to normalize.
        query_category (str): Category of the query (e.g., 'order_by').
        question (str): Natural language question corresponding to the query.
        sql (str, optional): SQL query used for ordering reference.

    Returns:
        pd.DataFrame: Normalized DataFrame.
    """
    # Remove duplicate rows
    df = df.drop_duplicates()

    # Ensure unique column names
    df = deduplicate_columns(df)

    # Sort columns in alphabetical order
    sorted_df = df.reindex(sorted(df.columns), axis=1)

    # Determine if ordering is required
    has_order_by = False
    order_by_columns = []
    ascending = True  # Default sort direction is ascending

    # Check for ordering intent from the question or query_category
    if query_category == "order_by" or re.search(r"\b(order|sort|arrange)\b", question, re.IGNORECASE):
        has_order_by = True

    # Parse ORDER BY clause from the SQL query (if provided)
    if sql:
        order_by_match = re.search(r"ORDER BY[\s\S]*?(?=LIMIT|$)", sql, re.IGNORECASE)
        if order_by_match:
            order_by_clause = order_by_match.group(0)
            # Extract column names and sort directions
            column_pattern = r"([\w\.]+)(?:\s+(ASC|DESC))?"
            for col_match in re.finditer(column_pattern, order_by_clause):
                column = col_match.group(1).split('.')[-1]  # Handle qualified names (e.g., table.column)
                direction = col_match.group(2)
                order_by_columns.append(column)
                if direction and direction.upper() == "DESC":
                    ascending = False

    # Apply sorting if ordering is required
    if has_order_by and order_by_columns:
        # Validate that all ORDER BY columns exist in the DataFrame
        order_by_columns = [col for col in order_by_columns if col in sorted_df.columns]
        remaining_columns = [col for col in sorted_df.columns if col not in order_by_columns]

        # Sort DataFrame by ORDER BY columns, followed by remaining columns
        sorted_df = sorted_df.sort_values(by=order_by_columns + remaining_columns, ascending=ascending)

    elif not has_order_by:
        # Default sorting: lexicographically by all columns
        sorted_df = sorted_df.sort_values(by=list(sorted_df.columns))

    # Reset the index
    sorted_df = sorted_df.reset_index(drop=True)

    return sorted_df

def get_all_minimal_queries(query: str) -> List[str]:
    """
    Expand a query with `{}` braces into all possible permutations of column combinations.
    The gold queries often use {} to represent acceptable variations of column combinations (e.g., SELECT {id, name}).
    - Handles `SELECT` and `GROUP BY` dynamically.
    - Supports multiple semicolon-separated queries.

    Args:
        query (str): SQL query containing `{}` braces.

    Returns:
        List[str]: List of expanded SQL queries.
    """
    queries = query.split(";")  # Split multiple queries by semicolon
    result_queries = []

    for query in queries:
        query = query.strip()
        if not query:
            continue  # Skip empty queries

        start, end = query.find("{"), query.find("}")
        if start == -1 or end == -1:
            result_queries.append(query)  # No `{}`, add query as-is
            continue

        # Extract columns within `{}` and generate all combinations
        column_options = query[start + 1:end].split(",")
        column_combinations = list(
            itertools.chain.from_iterable(
                itertools.combinations(column_options, r)
                for r in range(1, len(column_options) + 1)
            )
        )

        # Generate queries for each combination of columns
        for column_tuple in column_combinations:
            column_str = ", ".join(column_tuple)  # Format columns as comma-separated
            new_query = query[:start] + column_str + query[end + 1:]

            # Dynamically handle `GROUP BY {}` if present
            if "GROUP BY {}" in new_query:
                new_query = new_query.replace("GROUP BY {}", f"GROUP BY {column_str}")

            result_queries.append(new_query)

    return result_queries


def query_postgres_db(db_name: str, db_creds: Dict, query: str) -> pd.DataFrame:
    """
    Executes a query on a PostgreSQL database and returns the result as a DataFrame.
    """
    db_url = f"postgresql://{db_creds['user']}:{db_creds['password']}@{db_creds['host']}:{db_creds['port']}/{db_name}"
    engine = create_engine(db_url)
    try:
        escaped_query = re.sub(LIKE_PATTERN, lambda match: match.group(0).replace("%", "%%"), query, flags=re.IGNORECASE)
        result_df = pd.read_sql_query(escaped_query, con=engine)
        return result_df
    except Exception as e:
        print(f"Error executing query: {query}")
        print(f"Error: {e}")
        return pd.DataFrame()
    finally:
        engine.dispose()


def compare_query_results(gold_query: str, generated_query: str, db_name: str, db_creds: Dict, query_category: str, question: str) -> Tuple[bool, bool]:
    """
    Compares the results of gold and generated queries.
    Returns (exact_match, subset_match).
    """
    gold_queries = get_all_minimal_queries(gold_query)

    # Execute the generated query
    generated_result = query_postgres_db(db_name, db_creds, generated_query)
    if generated_result.empty:
        print("Generated query returned no results.")
        return False, False

    # Normalize the generated result
    generated_result = normalize_table(generated_result, query_category=query_category, question=question, sql=generated_query)
    print("\nGenerated Query Results (Normalized):")
    print(generated_result)
    
    exact_match = False
    subset_match = False

    for query in gold_queries:
        gold_result = query_postgres_db(db_name, db_creds, query)
        if gold_result.empty:
            continue

        gold_result = normalize_table(generated_result, query_category=query_category, question=question, sql=query)
        print("\nGold Query Results (Normalized):")
        print(gold_result)

        # Align columns for comparison
        common_columns = list(set(gold_result.columns) & set(generated_result.columns))
        if not common_columns:
            # print("No common columns between gold and generated results.")
            continue

        gold_aligned = gold_result[common_columns]
        generated_aligned = generated_result[common_columns]

        # Check for exact match
        if gold_aligned.equals(generated_aligned):
            return True, True

        # Check if gold is a subset of generated
        subset_match = all(
            gold_aligned[col].isin(generated_aligned[col]).all() for col in gold_aligned.columns
        )

    return exact_match, subset_match

def process_json_file(json_file: str, db_creds: Dict):
    """
    Processes the JSON file, executes queries, and compares the results.
    Accuracy is calculated as the fraction of rows where either exact match or subset match is True.
    """
    with open(json_file, "r") as f:
        data = json.load(f)
    
    i = 0
    total_count = 0  
    match_count = 0  

    for entry in data:
        db_name = entry["db_name"]
        gold_query = entry["answer"]
        category = entry["query_category"]
        generated_query = entry.get("generation")
        question = entry['question']

        print(f"Processing {i}th question: {question} on database: {db_name}")

        if not generated_query:
            print("No generated query available.")
            total_count += 1
            continue
        
        print(f"Generation: {generated_query}\n")
        exact_match, subset_match = compare_query_results(gold_query, generated_query, db_name, db_creds, category, question)

        print(f"{i}: Exact Match: {exact_match}, Subset Match: {subset_match}\n\n")
        i += 1
        total_count += 1
        if exact_match or subset_match:
            match_count += 1
    
    accuracy = (match_count / total_count) * 100 if total_count > 0 else 0
    print(f"Processed {total_count} rows.")
    print(f"Matched {match_count} rows.")
    print(f"Accuracy: {accuracy:.3f}%")


if __name__ == "__main__":
    # Database credentials
    db_creds = {
        "host": "localhost",
        "port": 5432,
        "user": "postgres",
        "password": "postgres"
    }

    # json_file_path = "/Users/yufeizhao/Desktop/11667MiniProject/11667-NLP2SQL/evaluation/sql_eval_dataset_20.json"
    # json_file_path = "/Users/yufeizhao/Desktop/11667MiniProject/11667-NLP2SQL/evaluation/sql_eval_dataset_1.json"
    
    json_file_path = "/Users/yufeizhao/Desktop/11667MiniProject/11667-NLP2SQL/inference_output/prompt_v4/deepseek_v0/eval_train_deepseek_inference_comma.json"

    process_json_file(json_file_path, db_creds)