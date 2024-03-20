from requests import Session
from bs4 import BeautifulSoup
from tqdm import tqdm
from json import JSONEncoder

from typing import Dict, List

class SideEffects:
	def __init__(self, common: str="", uncommon: str="", rare: str="", unknown_frequency: str=""):
		self.common = common
		self.uncommon = uncommon
		self.rare = rare
		self.unknown_frequency = unknown_frequency

class Drug:
	def __init__(self, name):
		self.name = name
		self.side_effects = SideEffects()

	def __repr__(self):
		return (self.name + "\n\tCommon: " + self.side_effects.common
		+ "\n\tUncommon: " + self.side_effects.uncommon
		+ "\n\tRare: " + self.side_effects.rare
		+ "\n\tUnknown Frequency: " + self.side_effects.unknown_frequency
		)

class DrugEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

class BnfScraper:
	def __init__(self, session: Session):
		self.session = session
		self.base_url = "https://bnf.nice.org.uk"
		self.drug_endpoint = "drugs"
		self.headers = set()

	def scrape(self) -> List[Drug]:
		drugs = self.get_drugs()
		out = []
		for [drug_name, drug_link] in tqdm(drugs.items()):
			out.append(self.build_drug_profile(drug_name, drug_link))
		return out
	
	def build_drug_profile(self, drug_name: str, endpoint: str) -> Drug:
		drug_page = self.session.get(f"{self.base_url}/{endpoint}", headers={
			"User-Agent": 'Bot'
		})
		soup = BeautifulSoup(drug_page.content, "html.parser")

		def side_effects_section(tag):
			return tag.name == "h3" and tag.has_attr("id") and "side-effects" in tag.get("id")
		
		side_effects = soup.find_all(side_effects_section)
		drug = Drug(drug_name)
		if side_effects == []:
			return drug
		
		for i in side_effects:
			side_effects_texts = i.find_next_sibling("div").findChildren("p")
			for j in side_effects_texts:
				header = j.find_previous_sibling()
				self.populate_side_effect_section(drug, header.get_text(), j.get_text())

		return drug
	
	def populate_side_effect_section(self, drug: Drug, header: str, content: str):
		if header == "Common or very common":
			drug.side_effects.common += content + "; "
		elif header == "Uncommon":
			drug.side_effects.uncommon += content + "; "
		elif header == "Rare or very rare":
			drug.side_effects.rare += content + "; "
		elif header == "Frequency not known":
			drug.side_effects.unknown_frequency += content + "; "
		return

	def get_drugs(self) -> Dict[str, str]:
		landing_page = self.session.get(f"{self.base_url}/{self.drug_endpoint}", headers={
			"User-Agent": 'Bot'
		})
		soup = BeautifulSoup(landing_page.content, "html.parser")

		def custom_selector(tag):
			excluded_set = ("Drugs", "switch to BNFC")
			return tag.name == "a" and tag.has_attr("href") and "/drugs/" in tag.get("href") and tag.get_text() not in excluded_set
		result = soup.find_all(custom_selector)

		out = {}
		for i in result:
			out[i.get_text()] = i.get('href')

		return out

