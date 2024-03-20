import json
import copy
from bnf import DrugEncoder
from tqdm import tqdm

file = open("data.json")
data = json.load(file)
filtered_data = []

for i in tqdm(data):
	curr = copy.deepcopy(i)
	curr["side_effects"]["common"] = curr["side_effects"]["common"].lower()
	curr["side_effects"]["uncommon"] = curr["side_effects"]["uncommon"].lower()
	curr["side_effects"]["rare"] = curr["side_effects"]["rare"].lower()
	curr["side_effects"]["unknown_frequency"] = curr["side_effects"]["unknown_frequency"].lower()

	filtered_data.append(curr)

with open('data_filtered.json', 'w') as f:
	json.dump(filtered_data, f, cls=DrugEncoder)