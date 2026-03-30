# Final report - Web Datamining & Semantic Project

## Title
**From Web Pages to a Movie Knowledge Graph: extraction, alignment, reasoning, embeddings, and RAG**

---

## 1. Introduction

This project integrates the four lab sessions of the Web Datamining & Semantic module into one complete pipeline. The chosen domain is the **movie domain**, because it combines rich textual descriptions, many named entities, strong relations between films and people, and the possibility of alignment with a large open knowledge base such as Wikidata.

The objective was to start from unstructured web pages, extract useful information, transform it into RDF triples, align the private graph with an open KB, enrich it through SPARQL-based expansion, apply symbolic and embedding-based reasoning, and finally query the graph through a lightweight RAG interface.

The final system therefore follows this chain:

**Web pages -> cleaned text -> entities and relations -> RDF graph -> aligned and expanded KB -> SWRL reasoning -> KGE -> NL to SPARQL RAG**

---

## 2. TD1 - Data acquisition and information extraction

### 2.1 Domain and seed URLs

The project focuses on films and film-related entities. The corpus was built from text-heavy pages such as:
- Wikipedia pages for individual movies
- Filmsite pages containing long-form descriptions and historical context

This choice is appropriate for three reasons:
1. these pages contain many named entities,
2. they describe meaningful semantic relations,
3. the entities are usually linkable to Wikidata.

### 2.2 Crawling and cleaning pipeline

The crawling pipeline was implemented with `trafilatura`, which is particularly useful for boilerplate removal. Instead of keeping raw HTML, the script extracted only the main textual content of each page. A document was kept only if it contained at least **500 words**, which reduced noise and excluded pages with little semantic value.

The cleaned corpus was stored in **JSONL** format. Each record contains:
- the source URL,
- the cleaned text,
- the word count.

This choice made it easy to preserve traceability between extracted knowledge and its source page.

### 2.3 Named entity recognition

A spaCy transformer pipeline (`en_core_web_trf`) was used to identify named entities. The project kept the following entity types:
- `PERSON`
- `ORG`
- `GPE`
- `DATE`

These are particularly useful in the movie domain because they capture:
- directors and actors,
- studios and organizations,
- places,
- release years and other time references.

The extracted entities were exported to `extracted_knowledge.csv`.

### 2.4 Candidate relation extraction

Candidate relations were extracted sentence by sentence. The method is simple but effective for a first private KB:
- identify at least two named entities in the same sentence,
- find the sentence root verb from the dependency tree,
- store the tuple `(subject, relation, object, source)`.

This produced `extracted_relations.csv`. The approach is heuristic, but it creates a usable first set of edge candidates for the KB.

### 2.5 Ambiguity cases

Three ambiguity cases appeared during extraction:

**Case 1 - Person vs movie title**  
Some titles contain person names or partial person names, which may lead to confusion between film entities and person entities.

**Case 2 - Date ambiguity**  
Many `DATE` entities are not release years. Some refer to awards, production periods, or historical references.

**Case 3 - Generic relation roots**  
The dependency root of a sentence is not always semantically meaningful for graph construction. Verbs such as *be*, *have*, or *say* may generate weak predicates.

### 2.6 Discussion

The first stage successfully transformed noisy web pages into structured intermediate files. The main limitation is that the relation extraction is only a first approximation. It is sufficient for bootstrapping the graph, but not enough for a production-grade semantic extraction system.

---

## 3. TD2 - Knowledge base construction, alignment, and expansion

### 3.1 Initial RDF modeling choices

The private graph was modeled in RDF using `rdflib`. The local namespace is:

`http://projet-web-movies.org/movie/`

The initial ontology includes at least the following classes:
- `Movie`
- `Person`
- `Organization`
- `Genre`

The project also defined local predicates such as:
- `hasActor`
- `directedBy`
- `releaseYear`
- `relatedTo`

Using URIs instead of plain strings ensures that entities are machine-readable and reusable in downstream tasks.

### 3.2 Entity linking with Wikidata

Each local entity was matched against the Wikidata API using `wbsearchentities`. For each successful match, the project stored:
- the local entity,
- the external Wikidata URI,
- a confidence score.

The confidence score was computed with a lightweight string similarity measure based on `SequenceMatcher`. This is not a full entity linking system, but it is enough for an academic alignment pipeline.

The result was saved in:
- `alignment_table.csv`
- `movies_kb_aligned.ttl`

### 3.3 Predicate alignment

After entity linking, predicate alignment was attempted by querying Wikidata for direct properties between aligned subject-object pairs. When a candidate property was found, the local predicate was aligned through `owl:equivalentProperty`.

The result was saved in `predicate_alignment.ttl`.

### 3.4 KB expansion strategy

The aligned graph was then expanded through controlled SPARQL queries over Wikidata. The expansion was restricted to a whitelist of movie-relevant predicates such as:
- instance of
- title
- genre
- director
- cast member
- composer
- publication date

This limited the expansion to semantically useful information while preventing a fully uncontrolled crawl of Wikidata.

### 3.5 Final KB statistics

The final expanded KB contains:

- **31419 triples**
- **14646 entities**
- **2567 distinct predicates**

This graph is large enough for KGE experiments, but the number of predicates is relatively high. This suggests that the expansion step introduced many Wikidata-specific relations, which can increase noise.

### 3.6 Critical observation on KB quality

The strongest point of the KB is that it is already aligned with an open knowledge base and contains enough entities for embedding-based experiments.

Its main weakness is **heterogeneity**:
- some predicates are very local,
- others are imported directly from Wikidata,
- the relation space is therefore not fully normalized.

This directly affects the later KGE results.

---

## 4. TD3 - Reasoning and knowledge graph embeddings

## 4.1 Symbolic reasoning with SWRL

The first reasoning task uses the supplied `family.owl` ontology. The SWRL rule is:

`Person(?p) ^ hasAge(?p, ?a) ^ swrlb:greaterThan(?a, 60) -> oldPerson(?p)`

This rule infers that any person older than 60 belongs to the class `oldPerson`.

A second rule was created for the movie domain. In the cleaned project package, the following rule is implemented on a small movie ontology wrapper:

`Movie(?m) ^ releaseYear(?m, ?y) ^ swrlb:lessThan(?y, 2000) -> ClassicMovie(?m)`

This allows the project to demonstrate reasoning not only on the toy ontology but also on the project domain.

## 4.2 Preparation for KGE

Before training, the expanded KB was cleaned as follows:
- remove duplicate triples,
- keep only triples whose objects are URIs,
- generate consistent train / validation / test splits.

The object-literal triples were excluded because standard link prediction with PyKEEN expects entity-to-entity triples.

The resulting files are:
- `train.txt`
- `valid.txt`
- `test.txt`

## 4.3 Models and configuration

Two KGE models were used:
- **TransE**
- **ComplEx**

The configuration was kept consistent across models:
- embedding dimension: 200
- learning rate: 0.001
- batch size: 256
- negative sampling: basic
- epochs: 100 in the notebook setup

## 4.4 Evaluation metrics

The evaluation focuses on filtered link prediction metrics:
- MRR
- Hits@1
- Hits@3
- Hits@10

### Saved results

**TransE**
- MRR: 0.0907
- Hits@1: 0.0429
- Hits@3: 0.1000
- Hits@10: 0.1829

**ComplEx**
- MRR: 0.0010
- Hits@1: 0.0000
- Hits@3: 0.0000
- Hits@10: 0.0000

### Interpretation

TransE performs much better than ComplEx on the saved runs. A plausible explanation is that the graph structure is noisy and heterogeneous. ComplEx can be powerful, especially with asymmetric relations, but it may be more sensitive to the quality and consistency of the relation space. In this project, the local plus Wikidata predicate mixture likely harms its generalization.

## 4.5 Size sensitivity

The notebook also sketches an analysis at different KB sizes:
- 20k triples
- 50k triples
- full dataset

This experiment should be reported conceptually even if not all runs were completed. The expected behavior is:
- very small KBs underfit,
- medium KBs improve the learned representations,
- larger KBs help only if the added triples are informative and not too noisy.

## 4.6 Embedding analysis

The project already includes:
- nearest-neighbor exploration for one entity,
- a t-SNE visualization of entity embeddings by class.

This is useful because it shows whether semantically related entities cluster together in the learned vector space.

---

## 5. TD4 - RAG over RDF/SPARQL

### 5.1 Objective

The final stage consists of building a grounded question-answering interface over the RDF graph. Instead of answering directly from the language model, the system:
1. receives a natural-language question,
2. generates a SPARQL query,
3. executes the query on the graph,
4. returns grounded results.

### 5.2 Method

The cleaned project package includes:
- graph loading with `rdflib`,
- schema summary construction,
- lightweight NL to SPARQL generation,
- optional self-repair through Ollama.

For an academic demo, a hybrid approach is practical:
- rule-based templates for common question types,
- LLM-based repair only when needed.

### 5.3 Example supported questions

- Who acted in Inception?
- Who directed The Matrix?
- What is the release year of Interstellar?

### 5.4 Baseline vs RAG evaluation

A final evaluation table should include at least five questions. A recommended format is:

| Question | Baseline answer | RAG answer | Correct |
|---|---|---|---|
| Who acted in Inception? | vague or hallucinated | grounded SPARQL result | Yes |
| Who directed The Matrix? | may fail | grounded result from KG | Yes |
| What is the release year of Interstellar? | approximate memory | exact graph value | Yes |
| Who acted in The Godfather? | partial | KG-based list | Yes/Partial |
| Which genre is Parasite linked to? | uncertain | graph result | Yes |

### 5.5 Why this stage matters

This stage demonstrates the practical value of the knowledge graph:
- the graph is not only stored,
- it is directly queryable,
- the LLM becomes grounded instead of purely generative.

---

## 6. Critical reflection

### 6.1 Impact of KB quality

The project confirms a central idea of knowledge engineering:
**the quality of downstream reasoning depends heavily on the quality of upstream extraction and modeling.**

Errors or inconsistencies introduced during crawling, entity extraction, or alignment propagate to:
- graph expansion,
- SWRL rules,
- KGE training,
- RAG retrieval quality.

### 6.2 Noise issues

The main noise sources are:
- weak relation extraction from dependency roots,
- date ambiguity,
- imperfect entity linking,
- excessive predicate diversity after expansion.

### 6.3 Rule-based vs embedding-based reasoning

The two reasoning paradigms are complementary:

**Rule-based reasoning**
- explicit,
- interpretable,
- precise,
- but limited to predefined logic.

**Embedding-based reasoning**
- scalable,
- flexible,
- able to generalize from patterns,
- but less interpretable and more sensitive to noise.

### 6.4 What could be improved

Several improvements would make the project stronger:
1. better relation extraction using dependency patterns or open IE,
2. stricter predicate normalization before KGE,
3. confidence-aware entity linking,
4. more targeted expansion strategy,
5. evaluation with manually verified gold triples,
6. richer RAG interface with conversation memory and better prompting.

---

## 7. Conclusion

This project successfully implements a full semantic pipeline starting from unstructured web pages and ending with a grounded graph-based QA system.

The final contribution is not a single model, but an integrated workflow:
- extract information from the web,
- structure it into RDF,
- align it with Wikidata,
- enrich it,
- reason on it symbolically and numerically,
- and query it through SPARQL-based RAG.

The project also shows that **knowledge graph quality is the central factor** that determines the success of the later stages. Even when the final models are not perfect, the pipeline remains academically valuable because it demonstrates the interaction between web mining, semantic modeling, reasoning, and retrieval-augmented generation.

---

## 8. Submission checklist

- [x] Code separated by module
- [x] RDF graph files included
- [x] Alignment files included
- [x] KGE datasets included
- [x] Trained model outputs included
- [x] README with run instructions
- [x] Reasoning script included
- [x] RAG script included
- [ ] Add 1-2 screenshots before final submission
- [ ] Export this report to PDF if required
