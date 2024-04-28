from requests import Session
from bs4 import BeautifulSoup
from tqdm import tqdm

from typing import Dict, List

class SideEffectsInformation:
	def __init__(self, text: str, title: str="", header: str="", frequency: str="", route: str=""):
		self.title = title
		self.text = text
		self.header = header
		self.frequency = frequency
		self.route = route
	
	def __repr__(self):
		return self.title

class Drug:
	def __init__(self, name):
		self.name = name
		self.side_effects: List[SideEffectsInformation] = []

	def __repr__(self):
		return (self.name + ", side_effects: " + self.side_effects)
	
	def has_side_effects(self):
		return not self.side_effects.empty()

class BnfScraper:
	def __init__(self, session: Session):
		self.session = session
		self.base_url = "https://bnf.nice.org.uk"
		self.drug_endpoint = "drugs"

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
			title = i.findChildren("span")[-1].get_text()
			title = title if "Side-effects" not in title else ""
			side_effects_texts = i.find_next_sibling("div").findChildren("p")
			for j in side_effects_texts:
				side_effect = SideEffectsInformation(j.get_text().lower())
				previous_tag = j.find_previous_sibling().name
				if j.find_previous_sibling('h3'):
					side_effect.header = j.find_previous_sibling('h3').get_text()
				if previous_tag in ['h4', 'h5'] and j.find_previous_sibling('h4'):
					side_effect.frequency = j.find_previous_sibling('h4').get_text()
				if previous_tag in ['h5'] and j.find_previous_sibling('h5'):
					side_effect.route = j.find_previous_sibling('h5').get_text()
				side_effect.title = title
				drug.side_effects.append(side_effect)

		return drug

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
			name = i.get_text()
			if 'with' not in name.lower():
				out[i.get_text()] = i.get('href')

		return out

