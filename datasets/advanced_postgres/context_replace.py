import json

def add_context_from_db_name(input_json_file, output_json_file, helper_context_file):
    # Load the input JSON file
    with open(input_json_file, 'r') as infile:
        data = json.load(infile)
    
    # Load the helper context file
    with open(helper_context_file, 'r') as helperfile:
        helper_context = json.load(helperfile)
    
    # Add context values to the data based on db_name
    for entry in data:
        db_name = entry.get("db_name")
        context_key = f"{db_name}_context"
        if db_name and context_key in helper_context:
            entry["context"] = helper_context[context_key]
        else:
            entry["context"] = None
            print(f"Warning: No context found for db_name '{db_name}'.")

    # Save the updated JSON to a new file
    with open(output_json_file, 'w') as outfile:
        json.dump(data, outfile, indent=4)
    
    print(f"Updated JSON file has been created at: {output_json_file}")

input_json_file = "output.json"  
output_json_file = "updated_output.json"  
helper_context_file = "/Users/yufeizhao/Desktop/11667MiniProject/11667-NLP2SQL/datasets/prep.json"  

# Execute the function
add_context_from_db_name(input_json_file, output_json_file, helper_context_file)