# Project audit - current state, missing parts, and priorities

## 1. What was already done well

Your project is **substantially advanced**. After inspecting the repository, the following deliverables are already present:

- TD1 outputs:
  - `crawler_output.jsonl`
  - `extracted_knowledge.csv`
  - `extracted_relations.csv`
- TD2 outputs:
  - `kg_artifacts/movies_kb.ttl`
  - `kg_artifacts/movies_kb_aligned.ttl`
  - `alignment_table.csv`
  - `kg_artifacts/predicate_alignment.ttl`
  - `kg_artifacts/movies_kb_expanded.nt`
- TD3 outputs:
  - `train.txt`, `valid.txt`, `test.txt`
  - trained PyKEEN models for **TransE** and **ComplEx**
  - `kge_performance_comparison.png`

This means the project already covers the **core pipeline**, and the raw material is strong enough for a good final grade.

## 2. Main weaknesses detected

### A. Repository structure was not aligned with the grading guide
The original repository stored almost everything in notebooks and did not expose a clean executable structure under `src/`.
This is a grading risk because the guide explicitly asks for:
- code per module,
- reproducibility,
- README with running instructions,
- clean repository organization.

### B. README was almost empty
The original README only contained a title and one sentence.
That would likely lose points on:
- reproducibility,
- clarity,
- GitHub quality.

### C. Reasoning part was missing as a proper script
The grading guide expects:
- one SWRL rule on `family.owl`,
- one rule on your own KB.

Your notebooks did not expose that part as a final runnable deliverable.

### D. RAG part was missing as a final integrated module
The grading guide expects:
- schema summary,
- NL to SPARQL generation,
- self-repair loop,
- baseline vs RAG comparison,
- demo screenshot.

Your repository did not yet contain a dedicated `src/rag/` implementation.

### E. Some methodology sections remained implicit
Several important decisions existed in notebooks, but were not documented clearly enough:
- why the movie domain was chosen,
- why URI-only triples were kept for KGE,
- why controlled predicate expansion was necessary,
- how alignment confidence was computed,
- what the main limitations are.

## 3. Quantitative state of the current KB

From the current expanded graph:

- **Triples**: 31419
- **Entities**: 14646
- **Distinct predicates**: 2567

This is enough to demonstrate the full pipeline, but the predicate count is unusually large for a movie-focused KG. That strongly suggests the SPARQL expansion brought in a lot of Wikidata-specific properties, which may introduce noise.

## 4. KGE results already available

### TransE
- MRR: 0.0907
- Hits@1: 0.0429
- Hits@3: 0.1000
- Hits@10: 0.1829

### ComplEx
- MRR: 0.0010
- Hits@1: 0.0000
- Hits@3: 0.0000
- Hits@10: 0.0000

Interpretation:
- In the saved results, **TransE clearly outperforms ComplEx**.
- This is perfectly acceptable academically, but the report must explain it.
- The current comparison chart in the original notebook uses placeholder values and should not be presented as if it came directly from the model outputs.

## 5. Priority order to finish properly

### Priority 1 - Make the repository submission-ready
Done in this completed package:
- modular scripts under `src/`
- filled `README.md`
- `requirements.txt`

### Priority 2 - Finalize reasoning
Done in this completed package:
- `src/reason/reasoning.py`

### Priority 3 - Finalize RAG
Done in this completed package:
- `src/rag/rag_cli.py`

### Priority 4 - Final report
Draft included:
- `reports/final_report.md`

## 6. What still requires execution on your machine before submission

To claim the project is fully reproducible, you should still run these scripts locally and keep the generated outputs:

1. `python src/reason/reasoning.py`
2. `python src/rag/rag_cli.py --question "Who acted in Inception?"`
3. optionally regenerate the metric plot with `python src/kge/train_kge.py`

## 7. Honest grading estimate

### Original repository
Likely around **14/20 to 16/20**
because the pipeline existed but the packaging, reasoning, RAG, and documentation were incomplete.

### Completed package delivered here
Potentially **18/20 to 20/20**
if you:
- run the reasoning script,
- run the RAG demo,
- add 1 or 2 screenshots in the report,
- submit the cleaned repository instead of the raw notebook-only version.
