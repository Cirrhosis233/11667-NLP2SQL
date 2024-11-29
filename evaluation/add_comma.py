input_file = "/Users/yufeizhao/Desktop/11667MiniProject/11667-NLP2SQL/inference_output/prompt_v3/codellama_v4/eval_train_codellama_inference.json"  # Replace with your file name
output_file = "/Users/yufeizhao/Desktop/11667MiniProject/11667-NLP2SQL/inference_output/prompt_v3/codellama_v4/eval_train_codellama_inference_comma.json"  # Replace with desired output file name

def fix_json(input_file: str, output_file: str):
    """
    Fixes the JSON file by adding commas between objects and formatting it as a proper JSON array.
    """
    with open(input_file, "r") as infile:
        lines = infile.readlines()
    
    # Add commas between lines and format as a JSON array
    with open(output_file, "w") as outfile:
        outfile.write("[\n")  # Start of JSON array
        for i, line in enumerate(lines):
            line = line.strip()  # Remove any extra spaces
            if not line:
                continue  # Skip empty lines
            outfile.write(line)
            if i < len(lines) - 1:
                outfile.write(",\n")  # Add comma after each object except the last
        outfile.write("\n]")  # End of JSON array

    print(f"Fixed JSON written to {output_file}")

# Run the function
fix_json(input_file, output_file)