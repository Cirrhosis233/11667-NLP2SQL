### Task
Translate the user’s question into SQL using the database schema: [QUESTION]{user_question}[/QUESTION]. 

### Instructions
- Use the database schema to ensure the SQL query references valid table and column names.
- Always end the SQL query with a semicolon ;.
- If the question cannot be answered using the given schema, return 'I do not know' instead of attempting to guess.
- Do not include explanations or comments in the output; provide only the SQL query.
- Construct a well-formatted SQL query that adheres to standard Postgres SQL syntax.
  
### Database Schema
The query will run on a database with the following schema:
{table_metadata_string}

### Answer
Given the database schema, here is the SQL query that answers [QUESTION]{user_question}[/QUESTION]
[SQL]