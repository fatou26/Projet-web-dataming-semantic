# Web Datamining & Semantic Project - Movie Knowledge Graph

Ce dêpot rassemble l'ensemble des fichiers réalisés durant le projet inclus dans le module Web datamining & semantic. Ce read-me vous permettra d'avoir les instructions pour lancer une pipeline complète pour la création et l'exploitation d'un graphe de connaissancé dans le domaine du cinéma.


## Repository structure

```text
.
├── data/
│   ├── family.owl
│   └── intermediate/
│       ├── crawler_output.jsonl
│       ├── extracted_knowledge.csv
│       ├── extracted_relations.csv
│       ├── train.txt
│       ├── valid.txt
│       ├── test.txt
│       └── kge_performance_comparison.png
├── kg_artifacts/
│   ├── movies_kb.ttl
│   ├── movies_kb_aligned.ttl
│   ├── movies_kb_expanded.nt
│   └── predicate_alignment.ttl
├── models/
│   ├── results_transe/
│   ├── results_complex/
│   └── 
├── reports/
│   └── final_report.pdf
└── src/
    ├── crawl/
    ├── ie/
    ├── kg/
    ├── reason/
    ├── kge/
    └── rag/
```

---

## Installation
Pour garantir le bon fonctionnement des scripts, il est nécessaire de configurer l'environnement de travil sur python (cela peut être avec un environmment vituel), et de télécharger les dépendances. 

```bash
python -m venv .venv
pip install -r requirements.txt
python -m spacy download en_core_web_trf
```

For TD4, install **Ollama** locally and run a small model such as:

```bash
ollama run gemma:2b
```

---

## How to run each module

Pour mener à bien ce projet, il est nécessaire de suivre un fil conducteur et donc de lancer les scripts avec un certain ordre. 

### TD1 - From the Unstructured Web to Structured Entities

#### Crawl and clean the corpus

```bash
python src/crawl/crawl_and_clean.py --output data/intermediate/crawler_output.jsonl
```

#### Extract entities and candidate relations

```bash
python src/ie/extract_entities_relations.py   
```

### TD2 - Knowledge Base Construction, Alignment, and Expansion

#### Build, align, and expand the knowledge graph

```bash
python src/kg/build_align_expand.py
```

### TD3 - Knowledge reasoning with rule and Knowledge Graph Embedding (KGE)

#### Prepare KGE splits

```bash
python src/kge/prepare_kge.py 
```

#### - Train KGE models

```bash
python src/kge/train_kge.py 
```

#### - Run rule-based reasoning

```bash
python src/reason/reasoning.py
```

### TD4 - Augmented Generation (RAG) with RDF/SPARQL and a Local Small LLM

```bash
python src/rag/rag_cli.py --graph kg_artifacts/movies_kb_expanded.nt --question "Who acted in Inception?"
```

---

## Hardware requirements

- Internet access for Wikidata alignment and expansion
- Optional GPU for KGE training
- Local Ollama runtime for the RAG demo

---
