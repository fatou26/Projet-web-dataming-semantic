import requests
from rdflib import Graph, Namespace, URIRef, OWL, RDFS

# Configuration
EX = Namespace("http://projet-web-movies.org/movie/")
WD = Namespace("http://www.wikidata.org/entity/")
WDT = Namespace("http://www.wikidata.org/prop/direct/")
SPARQL_URL = "https://query.wikidata.org/sparql"

def query_wikidata_predicate(subj_qid, obj_qid):
    """Cherche les propriétés existantes entre deux entités sur Wikidata"""
    query = f"""
    SELECT ?p WHERE {{
      wd:{subj_qid} ?p wd:{obj_qid} .
      FILTER(STRSTARTS(STR(?p), "http://www.wikidata.org/prop/direct/"))
    }}
    """
    headers = {
        "User-Agent": "MovieProjectESILV/1.0 (https://github.com/fatou26/Projet-web-dataming-semantic; fatou-esilv)",
        "Accept": "application/sparql-results+json"
    }
    try:
        response = requests.get(SPARQL_URL, params={'query': query, 'format': 'json'}, headers=headers)
        results = response.json()
        return [r['p']['value'] for r in results['results']['bindings']]
    except:
        return []

# Charger ton graphe déjà aligné (celui avec owl:sameAs)
g = Graph()
g.parse("movies_kb_aligned.ttl", format="turtle")

alignment_g = Graph()
alignment_g.bind("owl", OWL)

# Parcourir les triplets pour trouver des correspondances de prédicats
for s, p, o in g:
    # On ne s'intéresse qu'aux relations entre entités (pas les types ou labels)
    if isinstance(s, URIRef) and isinstance(o, URIRef) and p != OWL.sameAs:
        # 1. Récupérer les QIDs de s et o via les liens sameAs existants
        s_qid = list(g.objects(s, OWL.sameAs))
        o_qid = list(g.objects(o, OWL.sameAs))
        
        if s_qid and o_qid:
            s_id = str(s_qid[0]).split("/")[-1]
            o_id = str(o_qid[0]).split("/")[-1]
            
            # 2. Chercher le prédicat sur Wikidata
            candidates = query_wikidata_predicate(s_id, o_id)
            for cand in candidates:
                # 3. Aligner ton prédicat local au prédicat Wikidata
                # On utilise owl:equivalentProperty ou rdfs:subPropertyOf [cite: 246, 248]
                alignment_g.add((p, OWL.equivalentProperty, URIRef(cand)))
                print(f"Alignement Prédicat : {p.split('/')[-1]} ≡ {cand.split('/')[-1]}")

alignment_g.serialize(destination="predicate_alignment.ttl", format="turtle")