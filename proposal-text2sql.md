### **1. Task Description and Motivation**

**Task:** The selected task is Text-to-SQL, where the goal is to translate natural language questions into executable SQL queries. This task is crucial for automating data retrieval from structured databases based on human-like language queries, making database access more accessible for users without SQL knowledge.

**Motivation:** This task is significant for developing intuitive database interfaces, enabling non-experts to interact with data systems easily. The task requires language models to effectively interpret natural language, map it to SQL syntax, and correctly refer to database schema elements like table names and columns, which is a challenging yet essential capability in the natural language processing (NLP) field.

### **2. Data Description**

**Dataset:** The dataset, “sql-create-context,” is derived from WikiSQL and Spider and includes 78,577 examples of natural language queries, SQL CREATE TABLE statements, and SQL queries as answers. This dataset is tailored to reduce hallucination in Text-to-SQL models by providing the context of table creation statements. The dataset structure prevents unnecessary token usage and avoids exposure to sensitive information by grounding the queries in schema-level context instead of actual data.

- **Splits:** For this project, I’ll partition the dataset into train, dev, and test splits in a 70-15-15 ratio, ensuring that each set reflects the distribution of table types and complexity of queries.
- Example Data Instance:
  - **Question:** "Please show the themes of competitions with host cities having populations larger than 1000."
  - **Context:** `CREATE TABLE city (City_ID VARCHAR, Population INTEGER); CREATE TABLE farm_competition (Theme VARCHAR, Host_city_ID VARCHAR)`
  - **Answer:** `SELECT T2.Theme FROM city AS T1 JOIN farm_competition AS T2 ON T1.City_ID = T2.Host_city_ID WHERE T1.Population > 1000`

### **3. Ethical Considerations**

Ethical concerns for this project primarily involve the possibility of introducing biases during model training, especially if the SQL queries or data structure patterns are unbalanced across various schema types. Additionally, if the model is applied in a production environment, there is a risk that erroneous queries may retrieve incorrect or unauthorized data. Thus, careful monitoring and dataset curation will be essential to mitigate these risks.

### **4. Formulation of Training Data**

**Task Formulation:** The Text-to-SQL task here will be set up as a text generation problem. For **fine-tuning**, the model will receive a natural language question along with the corresponding CREATE TABLE context and generate the SQL answer as output. During **in-context learning**, prompts will include a few-shot example format with prior examples of questions, contexts, and SQL outputs to help the model generate accurate responses without extensive finetuning.

- Example Input/Target Pair:
  - **Input (Question + Context):** "Please show the themes of competitions with host cities having populations larger than 1000." + "CREATE TABLE city (City_ID VARCHAR, Population INTEGER); CREATE TABLE farm_competition (Theme VARCHAR, Host_city_ID VARCHAR)"
  - **Target (SQL Query):** `SELECT T2.Theme FROM city AS T1 JOIN farm_competition AS T2 ON T1.City_ID = T2.Host_city_ID WHERE T1.Population > 1000`

### **5. Method for Evaluation**

**Metrics:** Performance will be measured using execution accuracy (whether the generated SQL matches the expected answer) and string match accuracy. Both logits and generated sequences will be analyzed against the ground truth. Execution accuracy is particularly important since it directly evaluates the query's correctness, while string match accuracy helps identify syntactical precision. These metrics were chosen based on prior work demonstrating their effectiveness in SQL query generation evaluation.

**Exact Match Accuracy:** Measures exact matches; score ranges 0-100%.

**Token-Level Edit Distance:** Measures closeness to reference; lower scores indicate better performance.

**Column and Table Coverage:** Evaluates correct schema usage; score ranges 0-100%.

**BLEU Score:** Measures n-gram overlap; higher BLEU indicates closer match.

**F1 Score for Named Entity Accuracy:** Measures correct inclusion of named entities; score ranges 0-100%.

**SQL Syntax Validity:** Checks syntactical correctness; score ranges 0-100%.



