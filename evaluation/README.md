# SQL Evaluation Framework (sql_eval)

## Overview
The sql_eval framework is a tool to evaluate the performance of SQL query generation systems. It compares generated SQL queries against predefined “gold” SQL queries to measure accuracy. The evaluation approach is flexible, considering variations in valid SQL representations while maintaining robust comparison metrics.

## Key Features
1.	**Handling Flexible Gold Queries:
- Gold queries can include `{}` braces to represent acceptable variations of columns in SELECT and GROUP BY clauses.
- These allow flexibility in evaluation without enforcing strict syntactic matching.
  
2.	**Comparison Metrics:
- Exact Match: True if the generated query’s result matches the gold query’s result exactly.
- Subset Match: True if the gold query’s result is a subset of the generated query’s result, allowing leniency for additional information.
  
3.	**Handling Query Execution Errors:
- Queries that cannot execute (e.g., due to syntax errors or invalid operations) return empty results, which affect the comparison.
  
4.	**Normalization:
- DataFrames resulting from queries are normalized by removing duplicates, sorting columns and rows, and ensuring unique column names for fair comparison.

## Evaluation Approach
1. **Handling {} in Gold Queries
Gold queries may include {} braces to indicate acceptable column combinations, especially in SELECT and GROUP BY clauses. For example:
```sql
SELECT {student.name, student.id}, COUNT(*) FROM student GROUP BY {};
```
This flexibility allows the system to:
- Expand all possible combinations of columns in {}.
- Execute each expanded query against the database.
- Compare the results with the generated query’s result.

2. **Comparison Metrics
- Exact Match
  
The generated query’s result must match the gold query’s result exactly in terms of values and order (if applicable).
- Subset Match 
  - The gold query’s result is checked to be a subset of the generated query’s result.
  - Useful when the generated query includes additional, valid columns or rows that do not conflict with the gold query’s intent.
  
3. **Query Execution
- Handling Query Errors

If a query fails to execute (e.g., due to syntax errors, data type errors, division by zero), it is handled gracefully by returning an empty DataFrame. Such cases typically result in both exact_match and subset_match being False.
- Gold Query Execution
  - Gold queries are expanded into all possible minimal queries based on {} combinations.
  - Each expanded query is executed, and results are normalized for comparison.
 