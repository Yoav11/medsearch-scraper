import pandas as pd
import json
import numpy as np

# Load the first CSV file (heading, drugs, text, stop or start)
file1_path = 'frailty.csv'  # Replace with the path to your first CSV file
df1 = pd.read_csv(file1_path)

# Load the second CSV file (drug, score)
file2_path = 'frailty_score.csv'  # Replace with the path to your second CSV file
df2 = pd.read_csv(file2_path)

# Replace NaN values with empty strings in both dataframes
df1 = df1.replace({np.nan: ''})
df2 = df2.replace({np.nan: 0})  # Assuming missing scores should be treated as 0

# Initialize a dictionary to store the result
result = {}

# Iterate through each row in the first CSV
for _, row in df1.iterrows():
    # Skip rows where 'drugs' or 'stop or start' columns are empty
    if not row['drugs'].strip() or not row['stop or start'].strip():
        continue
    
    # Split the drugs column by commas and strip any whitespace
    drugs = [drug.strip() for drug in row['drugs'].split(',') if drug.strip()]
    
    # Check whether the action is "stop" or "start"
    action = row['stop or start'].strip().lower()
    
    # Skip if action is neither "stop" nor "start"
    if action not in ['stop', 'start']:
        continue
    
    # For each drug in the list
    for drug in drugs:
        if drug not in result:
            result[drug] = {'stop': [], 'start': [], 'score': 0}
        
        # Add the heading and text to the corresponding action list
        if row['heading'].strip() and row['text'].strip():
            result[drug][action].append({row['heading']: row['text']})

# Now, iterate through the second CSV (drug, score) and add the score to the respective drugs
for _, row in df2.iterrows():
    drug = row['drug'].strip()
    score = row['score']
    
    # If the drug already exists in the result, update its score
    if drug in result:
        result[drug]['score'] = score
    # If the drug is not in result, add it with an empty stop/start and assign the score
    else:
        result[drug] = {'stop': [], 'start': [], 'score': score}

# Convert the result to a JSON string
json_result = json.dumps(result, indent=4)

# Optionally, write the JSON to a file
with open('frailty.json', 'w') as json_file:
    json_file.write(json_result)
    
import json

# Load the existing JSON (with name and frailty object)
with open('data.json', 'r') as existing_file:
    existing_data = json.load(existing_file)

# Load the combined JSON (with stop, start, and score)
with open('frailty.json', 'r') as combined_file:
    combined_data = json.load(combined_file)

# Create a set of drug names from the existing JSON for quick lookup
existing_drug_names = {entry['name'] for entry in existing_data}

# Initialize a list to store the drugs that meet the criteria
new_drugs_with_score = []

# Iterate through the combined JSON to find drugs with score > 0
for drug, data in combined_data.items():
    if data['score'] > 0 and drug not in existing_drug_names:
        new_drugs_with_score.append(drug)

# Print the resulting list of new drugs with a score greater than 0
print("Drugs with a score greater than 0 that do not appear in the existing JSON:")
print(new_drugs_with_score)
