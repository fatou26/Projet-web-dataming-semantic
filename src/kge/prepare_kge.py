"""TD3 - Knowledge reasoning with rule and Knowledge Graph Embedding (KGE)

Phase 1 : Knowledge Graph Embedding
In this phase, we prepare cleaned train/valid/test splits for knowledge graph embedding.
We must implement two embedding models
"""
# Load libraries
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from rdflib import Graph, URIRef
from sklearn.model_selection import train_test_split


# --- Load the graph---

g = Graph()
g.parse("kg_artifacts/movies_kb_expanded.nt", format="nt")

triples = []
relations = set()
entities = set()

for s, p, o in g:
    if isinstance(o, URIRef):
        triples.append([str(s), str(p), str(o)])
        relations.add(str(p))
        entities.add(str(o))
    entities.add(str(s))
df = pd.DataFrame(triples, columns=["subject", "predicate", "object"]).drop_duplicates()
print(df)
print(f"Triples after cleaning : {len(df)}")
print(f"Relations : {len(relations)} | Entities : {len(entities)}")
# Here we verify if the graph has the correct format (subject, predicate, object) and if there are any duplicates.
#  We also count the number of unique relations and entities in the graph.
#  This is important to ensure that the data is clean and ready for the next steps of splitting and embedding.

# --- Split train / valid / test ---

train_df, temp = train_test_split(df, test_size=0.2, random_state=42)

train_entities = set(train_df["subject"]).union(set(train_df["object"]))
temp = temp[temp["subject"].isin(train_entities) & temp["object"].isin(train_entities)]

valid_df, test_df = train_test_split(temp, test_size=0.5, random_state=42)


# Output 
train_df.to_csv("data/intermediate/train.txt", sep="\t", header=False, index=False)
valid_df.to_csv("data/intermediate/valid.txt", sep="\t", header=False, index=False)
test_df.to_csv("data/intermediate/test.txt", sep="\t", header=False, index=False)

print(f"Train : {len(train_df)} | Valid : {len(valid_df)} | Test : {len(test_df)}")