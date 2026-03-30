"""TD3 - Knowledge reasoning with rule and Knowledge Graph Embedding (KGE)
Train and evaluate two KGE models with PyKEEN."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import torch
from pykeen.pipeline import pipeline
from pykeen.triples import TriplesFactory

# --- load data---

training = TriplesFactory.from_path("data/intermediate/train.txt")
validation = TriplesFactory.from_path(
    "data/intermediate/valid.txt",
    entity_to_id=training.entity_to_id,
    relation_to_id=training.relation_to_id,
)
testing = TriplesFactory.from_path(
    "data/intermediate/test.txt",
    entity_to_id=training.entity_to_id,
    relation_to_id=training.relation_to_id,
)


# --- train models ---

common = dict(
    training=training,
    validation=validation,
    testing=testing,
    model_kwargs=dict(embedding_dim=200),
    optimizer_kwargs=dict(lr=0.001),
    training_kwargs=dict(num_epochs=50, batch_size=256),
    negative_sampler="basic",
    device="cuda" if torch.cuda.is_available() else "cpu",
)

transe = pipeline(model="TransE", **common)
complex_ = pipeline(model="ComplEx", **common)

transe.save_to_directory("models/results_transe")
complex_.save_to_directory("models/results_complex")


# --- Extraction of metrics ---

def extract_main_metrics(results):
    metric_results = results.metric_results.to_flat_dict()
    return {
        "MRR": metric_results.get("both.realistic.inverse_harmonic_mean_rank", 0.0),
        "Hits@1": metric_results.get("both.realistic.hits_at_1", 0.0),
        "Hits@3": metric_results.get("both.realistic.hits_at_3", 0.0),
        "Hits@10": metric_results.get("both.realistic.hits_at_10", 0.0),
    }

transe_metrics = extract_main_metrics(transe)
complex_metrics = extract_main_metrics(complex_)

print("TransE :", transe_metrics)
print("ComplEx :", complex_metrics)


# --- visuals ---

labels = list(transe_metrics.keys())
x = np.arange(len(labels))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))
bars1 = ax.bar(x - width / 2, [transe_metrics[k] for k in labels], width, label="TransE")
bars2 = ax.bar(x + width / 2, [complex_metrics[k] for k in labels], width, label="ComplEx")

ax.set_title("Filtered link prediction metrics")
ax.set_ylabel("Score")
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

for bars in (bars1, bars2):
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height:.3f}", (bar.get_x() + bar.get_width() / 2, height), ha="center", va="bottom")

fig.tight_layout()
fig.savefig("kge_performance_comparison.png")
print("Graphic : data/kge_performance_comparison.png")


# --- save the metrics  ---

summary = {"TransE": transe_metrics, "ComplEx": complex_metrics}
with open("models/metrics_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)
print("Metrics saved : models/metrics_summary.json")
