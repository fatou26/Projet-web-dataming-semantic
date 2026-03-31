"""TD3 -  Knowledge reasoning with rule and Knowledge Graph Embedding (KGE)

The objectif of this lab is to Reasoning with SWRL. 
We will apply SWRL rules on a family ontology and on our movie KB to infer new facts.

Part A:
    Apply a SWRL rule on family.owl: 
    Find the oldPerson instances based on the hasAge property:
    Person(?p) ^ hasAge(?p, ?a) ^ swrlb:greaterThan(?a, 60) -> oldPerson(?p)

Part B:
    Apply a movie-specific rule on a small ontology wrapper:
    Find the movies release before 2000:
    Movie(?m) ^ releaseYear(?m, ?y) ^ swrlb:lessThan(?y, 2000) -> ClassicMovie(?m)

"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from owlready2 import DataProperty, FunctionalProperty, ObjectProperty, Thing, get_ontology

# On the family.owl

onto_family = get_ontology(str(Path("data/family.owl").resolve())).load()

# --- Part A: Person(?p) ^ age(?p, ?a) ^ ?a > 60 -> oldPerson(?p) ---
with onto_family:
    class oldPerson(Thing):
        pass

for person in onto_family.Person.instances():
    age_val = getattr(person, "age", None)
    # age may be stored as a list or a scalar depending on the ontology
    if isinstance(age_val, list):
        age_val = age_val[0] if age_val else None
    if age_val is not None and age_val > 60:
        if onto_family.oldPerson not in person.is_a:
            person.is_a.append(onto_family.oldPerson)

family_old = [ind.name for ind in onto_family.oldPerson.instances()]
print("Family oldPerson instances :", family_old)


# --- Part B: Movie(?m) ^ releaseYear(?m, ?y) ^ ?y < 2000 -> ClassicMovie(?m) ---
onto_movies = get_ontology("http://projet-web-movies.org/ontology.owl")

with onto_movies:
    class Movie(Thing):
        pass
    class ClassicMovie(Movie):
        pass
    class releaseYear(DataProperty, FunctionalProperty):
        domain = [Movie]
        range = [int]

df = pd.read_csv("data/intermediate/extracted_relations.csv")

created = {}
for _, row in df.iterrows():
    subject = str(row["subject"]).strip().replace(" ", "_").replace("-", "_")
    obj = str(row["object"]).strip()
    if not subject or not obj.isdigit():
        continue
    year = int(obj)
    if year < 1800 or year > 2035:
        continue
    if subject not in created:
        created[subject] = Movie(subject, namespace=onto_movies)
    created[subject].releaseYear = year

# Apply rule: releaseYear < 2000 -> ClassicMovie
for movie in onto_movies.Movie.instances():
    year = movie.releaseYear
    if year is not None and year < 2000:
        if onto_movies.ClassicMovie not in movie.is_a:
            movie.is_a.append(onto_movies.ClassicMovie)

movie_classics = [ind.name for ind in onto_movies.ClassicMovie.instances()]
print("ClassicMovie instances :", movie_classics[:20])

# This program applies SWRL-like reasoning on two ontologies: a family ontology and a movie ontology.
# In the family ontology, it identifies individuals who are older than 60 and classifies them as oldPerson. 
# In the movie ontology, it identifies movies released before the year 2000 and classifies them as ClassicMovie.