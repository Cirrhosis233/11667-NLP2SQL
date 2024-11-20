from datasets import load_dataset

# Specify the folder to save the dataset
save_folder = "./datasets/"

# Load and save the dataset
dataset = load_dataset("b-mc2/sql-create-context", cache_dir=save_folder)