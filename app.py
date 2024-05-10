import requests
from bnf import BnfScraper
from json import JSONEncoder
import json

class DrugEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__
        
scraper = BnfScraper(requests.session())


drugs = scraper.scrape()



print(drugs[0].__dict__)
with open('data.json', 'w') as f:
	json.dump(drugs, f, cls=DrugEncoder)

with open('data_sample.json', 'w') as f:
	json.dump(drugs[:10], f, cls=DrugEncoder)