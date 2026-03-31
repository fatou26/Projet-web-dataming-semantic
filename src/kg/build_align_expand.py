"""TD2 - Knowledge Base Construction,Alignment, and Expansion

In this lab, we construct a KB from the extracted entities and relations, align it with Wikidata, and expand it with additional facts.
We did that in four steps :
1- Build the initial KB
2- Entity linking with open knowledge Bases
3- Predicate alignment
4- KB expansion with SPARQL queries
"""
# Load libraries
from __future__ import annotations
import argparse
import csv
import re
import time
import urllib.parse
from difflib import SequenceMatcher
from pathlib import Path
import pandas as pd
import requests
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import OWL, RDFS, XSD
from SPARQLWrapper import JSON, SPARQLWrapper

# We define here the namespaces and constants
EX = Namespace("http://projet-web-movies.org/movie/")
WD = Namespace("http://www.wikidata.org/entity/")
SPARQL_URL = "https://query.wikidata.org/sparql"
USER_AGENT = "MovieProjectESILV/1.0 (https://github.com/fatou26/Projet-web-dataming-semantic; fatou-esilv)"

YEAR_RE = re.compile(r"\b(1[89]\d\d|20\d\d)\b")

# A function to  clean entity names 
def clean_uri(text):
    text = str(text).replace(" ", "_").replace(",", "").replace("(", "").replace(")", "")
    return urllib.parse.quote(text, safe="_-.")

# A function to compute string similarity for entity alignment
def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()



# load the extracted entities and relations from the previous phase (the output of the information extraction)
df_ent = pd.read_csv('data/intermediate/extracted_knowledge.csv')
df_rel = pd.read_csv('data/intermediate/extracted_relations.csv')

# -Build the intial graph with the extracted entities and relations, and save it in Turtle format
g = Graph()
g.bind("ex", EX)
g.bind("owl", OWL)

Movie = EX.Movie
Person = EX.Person
Organization = EX.Organization
Genre = EX.Genre

directedBy = EX.directedBy
hasActor = EX.hasActor
releaseYear = EX.releaseYear
relatedTo = EX.relatedTo

g.add((Movie, RDF.type, RDFS.Class))
g.add((Person, RDF.type, RDFS.Class))
g.add((Organization, RDF.type, RDFS.Class))
g.add((Genre, RDF.type, RDFS.Class))

for source, group in df_rel.groupby("source"):
    candidate_titles = set(group["subject"].tolist())
    years = [m.group(1) for obj in group["object"].astype(str) for m in [YEAR_RE.search(obj)] if m]
    year = years[0] if years else None

    for title in candidate_titles:
        movie_uri = EX[clean_uri(title)]
        g.add((movie_uri, RDF.type, Movie))
        if year:
            g.add((movie_uri, releaseYear, Literal(int(year), datatype=XSD.gYear)))

        source_people = set(df_ent[(df_ent["source"] == source) & (df_ent["label"] == "PERSON")]["entity"])
        for person_name in source_people:
            person_uri = EX[clean_uri(person_name)]
            g.add((person_uri, RDF.type, Person))
            g.add((movie_uri, hasActor, person_uri))
            g.add((movie_uri, relatedTo, person_uri))

# We save the initial graph in Turtle format. This file will be used in the next steps for alignment and expansion.
g.serialize("kg_artifacts/movies_kb.ttl", format="turtle")
print("Fichier movies_kb.ttl généré avec succès.")


# The third phase, we aligned entities with Wikidata 

# we create a fonction to check if Wikidata is reachable, to avoid making unnecessary requests 
# if the service is down. Because we will make many requests to Wikidata for entity and predicate alignment, 
# we want to ensure that the service is available before proceeding. If Wikidata is unreachable, 
# we skip the alignment and expansion steps and save the initial KB as the final output.

def _wikidata_available():
    try:
        r = requests.get(
            "https://www.wikidata.org/w/api.php",
            params={"action": "query", "format": "json"},
            headers={"User-Agent": USER_AGENT},
            timeout=10,
        )
        return r.status_code == 200
    except Exception:
        return False


# This function search for an entity name in Wikidata and return the best matching QID along with
#  a confidence score based on string similarity.

def search_wikidata(entity_name):
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "search": entity_name,
        "language": "en",
        "format": "json",
        "limit": 1,
    }
    try:
        response = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=30)
        data = response.json()
    except Exception as e:
        print(f"Warning: could not reach Wikidata for '{entity_name}': {e}")
        return None
    if not data.get("search"):
        return None
    result = data["search"][0]
    return {
        "entity": entity_name,
        "wikidata_id": result["id"],
        "confidence": round(similarity(entity_name, result.get("label", "")), 2),
    }


rows = []

if not _wikidata_available():
    print("Warning: Wikidata is unreachable. Skipping entity alignment, predicate alignment, and expansion.")
    g.serialize("kg_artifacts/movies_kb_aligned.ttl", format="turtle")
    print("Fichier movies_kb_aligned.ttl généré avec succès (sans alignement).")
    import sys; sys.exit(0)

entities = set()
for s, _, o in g:
    entities.add(s)
    if isinstance(o, URIRef) and str(o).startswith(str(EX)):
        entities.add(o)

for entity in sorted(entities, key=str):
    local_name = str(entity).split("/")[-1].replace("_", " ")
    result = search_wikidata(local_name)
    if not result:
        continue
    qid = result["wikidata_id"]
    g.add((entity, OWL.sameAs, WD[qid]))
    rows.append((local_name, str(WD[qid]), result["confidence"]))
    time.sleep(0.5)

g.serialize("kg_artifacts/movies_kb_aligned.ttl", format="turtle")
print("Fichier movies_kb_aligned.ttl généré avec succès.")

with open("data/intermediate/alignment_table.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Private Entity", "External URI", "Confidence"])
    writer.writerows(rows)
print("Fichier alignment_table.csv généré avec succès.")


# The fourth phase, we aligned predicates with Wikidata and expand the KB from Wikidata via SPARQL queries.

def query_wikidata_predicates(subj_qid, obj_qid):
    query = f"""
    SELECT ?p WHERE {{
      wd:{subj_qid} ?p wd:{obj_qid} .
      FILTER(STRSTARTS(STR(?p), "http://www.wikidata.org/prop/direct/"))
    }}
    """
    try:
        response = requests.get(
            SPARQL_URL,
            params={"query": query, "format": "json"},
            headers={"User-Agent": USER_AGENT, "Accept": "application/sparql-results+json"},
            timeout=60,
        )
        data = response.json()
    except Exception as e:
        print(f"Warning: predicate query failed for ({subj_qid}, {obj_qid}): {e}")
        return []
    return [r["p"]["value"] for r in data.get("results", {}).get("bindings", [])]


alignment_g = Graph()
alignment_g.bind("owl", OWL)

for s, p, o in g:
    if not isinstance(s, URIRef) or not isinstance(o, URIRef):
        continue
    if p == OWL.sameAs:
        continue
    s_qids = [str(x).split("/")[-1] for x in g.objects(s, OWL.sameAs)]
    o_qids = [str(x).split("/")[-1] for x in g.objects(o, OWL.sameAs)]
    if not s_qids or not o_qids:
        continue
    for cand in query_wikidata_predicates(s_qids[0], o_qids[0]):
        alignment_g.add((p, OWL.equivalentProperty, URIRef(cand)))

alignment_g.serialize("kg_artifacts/predicate_alignment.ttl", format="turtle")
print("Fichier predicate_alignment.ttl généré avec succès.")


# graph expansion with SPARQL queries to Wikidata

def expand_entity(qid):
    sparql = SPARQLWrapper(SPARQL_URL)
    sparql.setReturnFormat(JSON)
    sparql.addCustomHttpHeader("User-Agent", USER_AGENT)
    query = f"""
    SELECT ?item ?p ?o WHERE {{
        VALUES ?item {{ wd:{qid} }}
        VALUES ?p {{
            wdt:P31
            wdt:P1476
            wdt:P136
            wdt:P57
            wdt:P162
            wdt:P577
            wdt:P58
            wdt:P86
            wdt:P161
        }}
        ?item ?p ?o .
    }} LIMIT 500
    """
    sparql.setQuery(query)
    results = sparql.query().convert()
    triples = []
    for r in results["results"]["bindings"]:
        triples.append((r["item"]["value"], r["p"]["value"], r["o"]["value"]))
    return triples


aligned_qids = [str(o).split("/")[-1] for _, o in g.subject_objects(OWL.sameAs)]

for qid in aligned_qids:
    try:
        triples = expand_entity(qid)
    except Exception as e:
        print(f"Erreur pour {qid} : {e}")
        continue
    subject = URIRef(f"http://www.wikidata.org/entity/{qid}")
    for _, p, o in triples:
        obj = URIRef(o) if o.startswith(("http://", "https://")) else Literal(o)
        g.add((subject, URIRef(p), obj))
    time.sleep(1.0)

g.serialize("kg_artifacts/movies_kb_expanded.nt", format="nt")

print(f"Expansion terminée : {len(g)} triplets")

entities = set()

for s, p, o in g:
    entities.add(s)
    if isinstance(o, URIRef):
        entities.add(o)

print("Nombre d'entités :", len(entities))

relations = set()

for s, p, o in g:
    relations.add(p)

print("Nombre de relations :", len(relations))

# This script build a graph about movies from the extracted entities and relations (csv files), align it with Wikidata thanks to the API of Wikidata, 
# and expand it from Wikidata (director, genre, release date, etc.). The final expanded KB is saved in Triples 
# format, and contains 1000+ triples about movies.
# This script also generates intermediate files like the initial KB (movies_kb.ttl), the aligned KB 
# (movies_kb_aligned.ttl), the predicate alignment (predicate_alignment.ttl), and the alignment table 
# (alignment_table.csv) that contains the mapping between our entities and Wikidata QIDs along with confidence scores.
# And the final expanded kb (movies_kb_expanded.nt) will be used in the next phase for knowledge graph embedding.