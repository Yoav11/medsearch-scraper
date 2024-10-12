import csv
import json
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from tqdm import tqdm  # Progress bar

# Load the frailty.csv and extract the drugs (comma-separated)
frailty_df = pd.read_csv('frailty.csv')
frailty_drugs = set(frailty_df['drugs'].dropna().str.split(',').explode().str.strip().str.replace(r'[^\w\s]', '', regex=True).str.lower())

# Load the frailty_score.csv and extract the drug names
frailty_score_df = pd.read_csv('frailty_score.csv')
frailty_score_drugs = set(frailty_score_df['drug'].dropna().str.strip().str.replace(r'[^\w\s]', '', regex=True).str.lower())

# Combine drug names from frailty.csv and frailty_score.csv
all_csv_drugs = frailty_drugs.union(frailty_score_drugs)
print(all_csv_drugs)

# Load data.json and extract the drug names (in the "name" field)
with open('data.json', 'r') as json_file:
    data_json = json.load(json_file)

# Normalize the drug names from data.json
existing_drugs = {entry['name'].lower(): entry['name'] for entry in data_json}

# Common suffixes to strip for matching
suffixes = ["soft", "valproate", "paraffincontaining", "ranelate", "hexacetonide", "sulfonate", "adsorbed)", "maleate", "nitrite", "hydrate", "oil", "salmon", "(rabbit)", "salicylate", "nitrate", "phenylbutyrate", "vaccines", "3350", "oilcontaining", "cilexetil", "glargine", "gamma1b", "a", "butylbromide", "adjuvanted)", "furoate", "tartrate", "rabbit", "ii", "dipropionate", "drug", "husk", "cromoglicate", "hydrochloride", "activated", "etexilate", "aspart", "copper", "feredetate", "derisomaltose", "dextran", "calcium", "sinensis", "fosamil", "antitoxin", "propionate", "glycerophosphate", "inactivated", "products", "recombinant", "erbumine", "oxybate", "dihydrochloride", "(adsorbed)", "immunoglobulin", "pegol", "adsorbed", "disoproxil", "clodronate", "400", "detemir", "acetate", "lactate", "hexahydrate", "beta1a", "potassium", "(unfractionated)", "edetate", "alfa", "bicarbonate", "ureacontaining", "mofetil", "etabonate", "(inactivated)", "inhibitor", "extract", "insulin", "succinate", "tocopherol", "tar", "permanganate", "antibody", "hydrobromide", "lispro", "subsalicylate", "citrate", "plasma", "trinitrate", "hippurate", "trometamol", "isetionate", "supplements", "antiserum", "mononitrate", "(equine)", "teoclate", "beta-1a", "derivative", "hormone", "sulfate", "fluoride", "paraffin", "glulisine", "besilate", "ointments", "oxyhydroxide", "benzoate", "aspartate", "medoxomil", "benzylpenicillin", "live", "equine", "hyaluronate", "gluconate", "pranobex", "degludec", "(recombinant)", "dinitrate", "(live)", "bromide", "(salmon)", "trisilicate", "misoprostol", "oxalate", "(13c)", "chloride", "sodium", "oxide", "mebutate", "enantate", "carboxymaltose", "adjuvanted", "esters", "drug]", "undecanoate", "solution", "marboxil", "protein", "(copper)", "ethyl", "aminobenzoate", "dipivoxil", "13c", "complex", "thiosulfate", "mesilate", "hydroxide", "peroxide", "maltol", "cyclosilicate", "antimicrobial-containing", "sulfadiazine", "fumarate", "acetonide", "alafenamide", "urea-containing", "delta", "beta", "zeta", "paraffin-containing", "decanoate", "nicotinate", "disodium", "oatmeal-containing", "oatmealcontaining", "vaccine", "butyrate", "unfractionated", "picosulfate", "alcohol", "monohydrate", "sucrose", "wort", "antimicrobialcontaining", "gamma-1b", "embonate", "oil-containing", "d", "phosphate", "nitroprusside", "acid", "arginine", "b", "arginate", "carbonate", "feeds"]

def strip_suffix(drug_name):
    for suffix in suffixes:
        if drug_name.endswith(suffix):
            return drug_name[:-len(suffix)].strip()
    return drug_name

def find_best_match(bnf_drugs, csv_drug, threshold=80):
	best_score = -1
	match = None
	for bnf_drug in bnf_drugs:
		stripped_bnf_drug = strip_suffix(bnf_drug.lower())
		if (csv_drug == bnf_drug):
			return bnf_drug
		elif strip_suffix(csv_drug) == stripped_bnf_drug:
			best_score = 101
			match = bnf_drug
		score = fuzz.token_sort_ratio(stripped_bnf_drug, strip_suffix(csv_drug))
		if score > threshold and score > best_score:
			#print("matched!", csv_drug, "with", bnf_drug)
			match = bnf_drug
		
	return match

# Initialize list to store the results
results = {
    normalized_bnf_drug: [] for normalized_bnf_drug in existing_drugs
}

results["Not found"] = []

with tqdm(total=len(all_csv_drugs), desc="Processing drugs") as pbar:
    for csv_drug in all_csv_drugs:
        best_match = find_best_match(existing_drugs.keys(), csv_drug)
        if best_match is None:
            results["Not found"].append(csv_drug)
            pbar.update(1)
        else:
             results[best_match].append(csv_drug)

results_array = []
for key, value in results.items():
	results_array.append({
          "bnf_name": key,
          "american_name": ",".join(value)
	})
print(results_array)

# Write the results to a new CSV file
with open('drug_name_mapping.csv', 'w', newline='') as output_file:
    writer = csv.DictWriter(output_file, fieldnames=['bnf_name', 'american_name'])
    writer.writeheader()
    writer.writerows(results_array)

print("CSV file 'drug_name_mapping.csv' has been created successfully.")
