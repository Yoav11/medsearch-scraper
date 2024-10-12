import json
import re

# Load data.json and extract drug names
with open('data.json', 'r') as json_file:
    data_json = json.load(json_file)

# Function to extract potential suffixes from drug names
def extract_suffixes(drug_names):
    suffixes = set()
    
    for entry in drug_names:
        drug_name = entry['name']
        # Split the drug name into words
        words = drug_name.lower().split()
        
        # Consider the last word as a potential suffix
        if len(words) > 1:  # Skip single-word names
            potential_suffix = words[-1]
            suffixes.add(potential_suffix)

            # Check for common patterns (like "hydrochloride", "sodium", etc.)
            # Here we can add some basic cleaning to strip out unwanted characters
            cleaned_suffix = re.sub(r'[^\w\s]', '', potential_suffix)  # Remove punctuation
            if cleaned_suffix:  # Avoid empty suffixes
                suffixes.add(cleaned_suffix)

    return suffixes

# Extract suffixes
unique_suffixes = extract_suffixes(data_json)

# Print the unique suffixes found as a comma-delimited string
comma_delimited_suffixes = '", "'.join(unique_suffixes)
print("Unique Suffixes Found:")
print(comma_delimited_suffixes)
