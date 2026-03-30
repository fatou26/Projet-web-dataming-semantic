"""TD4 - Retrieval-Augmented Generation (RAG) with RDF/SPARQL and a Local Small LLM

For the last lab, we build a LLM chatbot augmented by he knowledge base. For this, we : 
- loads the RDF graph
- builds a schema summary
- converts a small set of natural-language questions into SPARQL templates
- optional Ollama-based self-repair for unsupported/failing queries
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import requests
from rdflib import Graph

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "gemma:2b"

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "gemma:2b"
CODE_BLOCK_RE = re.compile(r"```(?:sparql)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)


# --- Fonctions utilitaires ---

def ask_ollama(prompt, model=DEFAULT_MODEL):
    payload = {"model": model, "prompt": prompt, "stream": False}
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.ConnectionError:
        return "[Ollama non disponible : le serveur local n'est pas démarré. Lancez Ollama avec 'ollama serve' puis 'ollama pull gemma:2b'.]"
    except requests.exceptions.RequestException as e:
        return f"[Erreur Ollama : {e}]"


def extract_sparql(text):
    m = CODE_BLOCK_RE.search(text)
    if m:
        return m.group(1).strip()
    return text.strip()

def normalize_entity(text):
    text = text.strip()
    text = re.sub(r"[^\w\s-]", "", text)   
    text = text.replace(" ", "_")
    return text


def rule_based_nl_to_sparql(question):
    q = question.lower().strip()
    if "actors" in q or "acted in" in q:
        m = re.search(r"(?:in|of)\s+(.+)$", question, re.IGNORECASE)
        if not m:
            return None
        movie = normalize_entity(m.group(1))
        return f"""
        PREFIX ex: <http://projet-web-movies.org/movie/>
        SELECT ?actor WHERE {{
            ex:{movie} ex:hasActor ?actor .
        }} LIMIT 20
        """
    if "directed" in q and ("who" in q or "director" in q):
        m = re.search(r"(?:of|for)\s+(.+)$", question, re.IGNORECASE)
        if not m:
            return None
        movie = m.group(1).strip().replace(" ", "_")
        return f"""
        PREFIX ex: <http://projet-web-movies.org/movie/>
        SELECT ?director WHERE {{
            ex:{movie} ex:directedBy ?director .
        }} LIMIT 10
        """
    if "release year" in q or "when was" in q:
        m = re.search(r"(?:was|of)\s+(.+)$", question, re.IGNORECASE)
        if not m:
            return None
        movie = m.group(1).strip().replace(" ", "_")
        return f"""
        PREFIX ex: <http://projet-web-movies.org/movie/>
        SELECT ?year WHERE {{
            ex:{movie} ex:releaseYear ?year .
        }} LIMIT 10
        """
    return None


# --- Chargement du graphe ---

g = Graph()
g.parse("kg_artifacts/movies_kb_expanded.nt", format="nt")
print(f"Graphe chargé : {len(g)} triplets")


# --- Construction du schema summary ---

predicates = sorted({str(p) for _, p, _ in g})[:50]
classes = sorted({str(o) for _, p, o in g if str(p) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"})[:40]
samples = [(str(s), str(p), str(o)) for s, p, o in list(g)[:20]]

pred_lines = "\n".join(f"- {p}" for p in predicates)
cls_lines = "\n".join(f"- {c}" for c in classes)
sample_lines = "\n".join(f"- {s} {p} {o}" for s, p, o in samples)

schema_summary = f"""
# Prédicats
{pred_lines}

# Classes
{cls_lines}

# Triplets exemples
{sample_lines}
""".strip()


# --- Boucle de questions ---

while True:
    question = input("\nQuestion (ou 'quit') : ").strip()
    if question.lower() == "quit":
        break

    # Baseline sans RAG
    print("\n--- Baseline (sans RAG) ---")
    baseline = ask_ollama(f"Answer the following question as best as you can:\n\n{question}")
    print(baseline)

    # Génération SPARQL
    print("\n--- RAG avec génération SPARQL ---")

    sparql = rule_based_nl_to_sparql(question)

    if sparql is None:
        prompt = f"""You are a SPARQL generator. Convert the QUESTION into a valid SPARQL 1.1 SELECT query.
Use ONLY the IRIs visible in the SCHEMA SUMMARY. Return ONLY the SPARQL query in a sparql code block.

SCHEMA SUMMARY:
{schema_summary}

QUESTION:
{question}
"""
        sparql = extract_sparql(ask_ollama(prompt))

    try:
        rows = list(g.query(sparql))
        answers = [tuple(map(str, row)) for row in rows]
        repaired = False
    except Exception as e:
        print(f"Erreur SPARQL, tentative de réparation : {e}")
        repair_prompt = f"""The previous SPARQL failed. Return a corrected SPARQL 1.1 SELECT query in a sparql code block.

SCHEMA SUMMARY:
{schema_summary}

QUESTION:
{question}

BAD SPARQL:
{sparql}

ERROR:
{e}
"""
        sparql = extract_sparql(ask_ollama(repair_prompt))
        try:
            rows = list(g.query(sparql))
            answers = [tuple(map(str, row)) for row in rows]
            repaired = True
        except Exception as e2:
            answers = []
            repaired = True
            print(f"Réparation échouée : {e2}")

    print(f"\n[Requête SPARQL utilisée]\n{sparql}")
    print(f"[Réparée ?] {repaired}")
    if answers:
        for row in answers[:20]:
            print(" | ".join(row))
        if len(answers) > 20:
            print(f"... ({len(answers)} résultats au total)")
    else:
        print("[Aucun résultat]")