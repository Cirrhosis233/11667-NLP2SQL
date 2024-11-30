### Task
You are an advanced text-to-SQL translation model. Your task is to generate valid SQL queries based on a user question and table metadata. The SQL query should correctly address the user’s request while respecting the structure and constraints of the provided table. 

### Input Information: 
The user question is [QUESTION]{user_question}[/QUESTION]. And the query should be based on the following schema:
{table_metadata_string}

### Answer
Given the database schema, here is the SQL query that answers [QUESTION]{user_question}[/QUESTION]
[SQL]