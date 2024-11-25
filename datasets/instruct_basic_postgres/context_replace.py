import json

def replace_context(input_json_file, output_json_file, helper_context_file):
    # Load the input JSON file
    with open(input_json_file, 'r') as infile:
        data = json.load(infile)
    
    # Load the helper context file
    with open(helper_context_file, 'r') as helperfile:
        helper_context = json.load(helperfile)
    
    # Replace context values
    for entry in data:
        context_key = f"{entry['context']}_context"
        if context_key in helper_context:
            entry['context'] = helper_context[context_key]
    
    # Save the updated JSON to a new file
    with open(output_json_file, 'w') as outfile:
        json.dump(data, outfile, indent=4)
    
    print(f"Updated JSON file has been created at: {output_json_file}")

input_json_file = "output.json"  
output_json_file = "updated_output.json"  
helper_context_file = "/Users/yufeizhao/Desktop/11667MiniProject/11667-NLP2SQL/datasets/prep.json"  

replace_context(input_json_file, output_json_file, helper_context_file)