import pandas as pd
import json
from collections import defaultdict


class encoder(json.JSONEncoder):
	def default(self, o):
		return o.__dict__
		
df = pd.read_csv('Symptoms.csv')

class Category:
	def __init__(self, key, aliases):
		self.key = key
		self.aliases = aliases

out = defaultdict(set)
for index, row in df.iterrows():
	if not pd.isna(row["Specialty"]):
		out[row["Specialty"]].add(row["Symptom"])
	if not pd.isna(row["Symptom2"]):
		out[row["Symptom2"]].add(row["Symptom"])
	if not pd.isna(row["Anatomy"]):
		out[row["Anatomy"]].add(row["Symptom"])
	if not pd.isna(row["Category 4"]):
		out[row["Category 4"]].add(row["Symptom"])

categories = [Category(key, list(value)) for key, value in out.items()]

with open('categories.json', 'w') as f:
	json.dump(categories, f, cls=encoder)