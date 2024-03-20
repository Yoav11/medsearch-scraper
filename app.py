import requests
from bnf import BnfScraper
import json
from bnf import DrugEncoder

scraper = BnfScraper(requests.session())


#drugs = scraper.scrape()
#with open('data.json', 'w') as f:
#	json.dump(drugs, f, cls=DrugEncoder)

#with open('data_sample.json', 'w') as f:
#	json.dump(drugs[:10], f, cls=DrugEncoder)


drugs = input("what drug does the patient use ? (comma separated list)").split(",")
symptoms = input("what symptom does the patient have ?")


def build_query():
	query = f"(name: {drugs[0]}"
	for i in drugs[1:]:
		query += " || " 
		query += f"name: {i}" 
	query += f") && side_effects.common: {symptoms}"
	return query
result = requests.get("http://localhost:8983/solr/drugs/query", json={
	"query": build_query()
})

response = result.json()["response"]	
print("possible drugs that caused this:")
for i in response["docs"]:
	print(i["name"])