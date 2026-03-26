import requests
from rdflib import OWL, Graph, Literal, URIRef

# Endpoint SPARQL Wikidata
SPARQL_URL = "https://query.wikidata.org/sparql"

# Charger KB alignée
g = Graph()
g.parse("movies_kb_aligned.ttl", format="turtle")

# Requête 1-hop
def get_triples(qid):
    query = f"""
    SELECT ?p ?o WHERE {{
      wd:{qid} ?p ?o .
    }}
    """

    headers = {
        "User-Agent": "MovieProjectESILV/1.0 (https://github.com/fatou26/Projet-web-dataming-semantic; fatou-esilv)",
        "Accept": "application/sparql-results+json"
    }
    response = requests.get(SPARQL_URL, params={"query": query}, headers=headers)
    
    data = response.json()

    triples = []
    for item in data["results"]["bindings"]:
        p = item["p"]["value"]
        o = item["o"]["value"]
        triples.append((p, o))

    return triples

# Récupérer QIDs depuis ton fichier alignement
aligned_entities = [str(s).split("/")[-1] for s in g.subjects(predicate=URIRef("http://www.w3.org/2002/07/owl#sameAs"))]

aligned_entities = []
for s, o in g.subject_objects(OWL.sameAs):
    qid = str(o).split("/")[-1]
    aligned_entities.append((qid))

# Expansion
for qid in aligned_entities:
    print(f"Expansion de {qid}")
    triples = get_triples(qid)

    subject = URIRef(f"http://www.wikidata.org/entity/{qid}")

    for p, o in triples:
        obj = URIRef(o) if o.startswith("http://") or o.startswith("https://") else Literal(o)
        g.add((subject, URIRef(p), obj))

# Sauvegarde
g.serialize("movies_kb_expanded.nt", format="nt", encoding="utf-8")

print(f"Expansion terminée : {len(g)} triplets")