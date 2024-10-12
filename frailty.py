import pandas as pd
import json
import numpy as np

# Load the first CSV file (heading, drugs, text, stop or start)
file1_path = 'frailty.csv'  # Replace with the path to your first CSV file
df1 = pd.read_csv(file1_path)

# Load the second CSV file (drug, score)
file2_path = 'frailty_score.csv'  # Replace with the path to your second CSV file
df2 = pd.read_csv(file2_path)

# Load the drug name mapping
file3_path = 'drug_name_mapping.csv'  # Replace with the path to your first CSV file
df3 = pd.read_csv(file3_path)

# Replace NaN values with empty strings in both dataframes
df1 = df1.replace({np.nan: ''})
df2 = df2.replace({np.nan: 0})  # Assuming missing scores should be treated as 0
df3 = df3.replace({np.nan: ""})

def get_bnf_name(drug):
    f = drug + ","
    g = "," + drug + ","
    h = drug + ","
    rows = df3[
            (df3["stopp_or_acb_name"].str.startswith(f)) 
            | (df3["stopp_or_acb_name"].str.contains(g)) 
            | (df3["stopp_or_acb_name"].str.endswith(h)) 
            | (df3["stopp_or_acb_name"] == drug)]
    if (len(rows) > 1):
        raise(drug, " has multiple bnf names!")
    elif len(rows) == 0:
        print(drug, " has no bnf name :(")
        return drug
    return rows.iloc[0]["bnf_name"]

# Initialize a dictionary to store the result
result = {}

# Iterate through each row in the first CSV
for _, row in df1.iterrows():
    # Skip rows where 'drugs' or 'stop or start' columns are empty
    if not row['drugs'].strip() or not row['stop or start'].strip():
        continue
    
    # Split the drugs column by commas and strip any whitespace
    drugs = [get_bnf_name(drug.strip().lower()).title() for drug in row['drugs'].split(',') if drug.strip()]
    
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
    drug = get_bnf_name(row['drug'].strip().lower()).title()
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
    
# Load the existing JSON (with name and frailty object)
with open('data.json', 'r') as existing_file:
    existing_data = json.load(existing_file)

# Load the combined JSON (with stop, start, and score)
with open('frailty.json', 'r') as combined_file:
    combined_data = json.load(combined_file)

# Update the "frailty" object for each drug in the existing data
for drug_name, frailty_data in combined_data.items():
    found = False
    for drug_entry in existing_data:
        if drug_name == drug_entry.get('name'):
            drug_entry['frailty'] = frailty_data
            found = True
            break
    if not found:
        print(drug_name, " was not found and is now added!")
        existing_data.append({
            "name": drug_name,
            "frailty": frailty_data
        })
        

# Optionally, write the updated JSON back to a file
with open('data_updated.json', 'w') as output_file:
    json.dump(existing_data, output_file, separators=(',', ':'))
