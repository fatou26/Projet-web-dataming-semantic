import requests
from rdflib import Graph, Namespace, OWL
import re
import csv

# Charger ta KB existante
g = Graph()
g.parse("movies_kb.ttl", format="turtle")

EX = Namespace("http://projet-web-movies.org/movie/")
WD = Namespace("http://www.wikidata.org/entity/")

# Fonction pour chercher une entité dans Wikidata
def search_wikidata(entity_name):
    url = "https://www.wikidata.org/w/api.php"
    
    params = {
        "action": "wbsearchentities",
        "search": entity_name,
        "language": "en",
        "format": "json",
        "limit": 1
    }
    
    headers = {
    "User-Agent": "MovieProjectESILV/1.0 (https://github.com/fatou26/Projet-web-dataming-semantic; fatou-esilv)"
    }

    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    if data["search"]:
        result = data["search"][0]
        return result['label'],  result['id']
    
    return None, None

# Extraire les entités uniques du graphe
entities = set()

for s, p, o in g:
    if isinstance(s, type(EX["test"])):
        entities.add(s)
    if isinstance(o, type(EX["test"])):
        entities.add(o)

print(f"{len(entities)} entités trouvées")

# Alignement automatique
alignment_results = []

for entity in entities:
    name = entity.split("/")[-1]
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    
    label, qid = search_wikidata(name)
    
    if qid:
        g.add((entity, OWL.sameAs, WD[qid]))
        alignment_results.append((name, str(WD[qid]), 0.99))
        print(f"{name} → {qid} ({label})")
    else:
        print(f"{name} → Aucun résultat")

# Sauvegarde
g.serialize("movies_kb_aligned.ttl", format="turtle")

# Sauvegarde tableau d’alignement
with open("alignment_table.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["Private Entity", "External URI", "Confidence"]) # En-têtes requis 
    writer.writerows(alignment_results)

print("Alignement terminé !")