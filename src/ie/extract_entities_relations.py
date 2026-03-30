"""TD1 - From the Unstructured Web to Structured Entities

Phase 2 : Information Extraction 
In this phase, we will extract entities and relations from the cleaned text obtained in Phase 1.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import spacy

nlp = spacy.load("en_core_web_trf")

extracted_data = []
relations = []

with open('data/intermediate/crawler_output.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        doc_data = json.loads(line)
        text = doc_data["text"]
        url = doc_data["url"]

        doc = nlp(text)

        for ent in doc.ents:
            if ent.label_ in ["PERSON", "ORG", "GPE", "DATE"]:
                extracted_data.append({
                    "entity": ent.text,
                    "label": ent.label_,
                    "source": url
                })

        for sent in doc.sents:
            ents = [ent for ent in sent.ents]

            if len(ents) >= 2:
                for token in sent:
                    if token.dep_ == "ROOT":
                        relations.append({
                            "subject": ents[0].text,
                            "relation": token.lemma_,
                            "object": ents[1].text,
                            "source": url
                        })

print(f"Saved {len(extracted_data)} entities to {"extracted_knowledge.csv"}")
df = pd.DataFrame(extracted_data).drop_duplicates()
df.to_csv('data/intermediate/extracted_knowledge.csv', index=False)
print("Fichier extracted_knowledge.csv généré avec succès.")

print(f"Saved {len(relations)} relations to {"extracted_relations.csv"}")
relations_df = pd.DataFrame(relations).drop_duplicates()
relations_df.to_csv('data/intermediate/extracted_relations.csv', index=False)
print("Fichier extracted_relations.csv généré avec succès.")

    