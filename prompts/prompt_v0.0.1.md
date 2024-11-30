### Task
You are an advanced SQL generation model. Your task is to convert the following user question into a valid SQL query using the provided database schema. Ensure that the generated query:
- Accurately answers the user’s question.
- Adheres to standard Postgres SQL syntax.
- References the correct table and column names based on the schema.

### User Question: 
[QUESTION]{user_question}[/QUESTION]

### Database Schema:
{table_metadata_string}

### Answer:
Provide only the SQL query that answers the question.
