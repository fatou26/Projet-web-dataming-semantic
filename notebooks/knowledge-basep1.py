from rdflib import Graph, Namespace, Literal, RDF, OWL

# Création du graphe
g = Graph()

# Namespace
EX = Namespace("http://projet-web-movies.org/movie/")
g.bind("ex", EX)

# Classes
Person = EX.Person
Movie = EX.Movie
Genre = EX.Genre

# Relations
directedBy = EX.directedBy
hasActor = EX.hasActor
hasGenre = EX.hasGenre
releaseYear = EX.releaseYear
profession = EX.profession

# Données (films, réalisateurs, acteurs)
movies_data = [
    ("Inception", "ChristopherNolan", ["LeonardoDiCaprio", "JosephGordonLevitt"], "SciFi", 2010),
    ("Interstellar", "ChristopherNolan", ["MatthewMcConaughey", "AnneHathaway"], "SciFi", 2014),
    ("TheDarkKnight", "ChristopherNolan", ["ChristianBale", "HeathLedger"], "Action", 2008),
    ("Titanic", "JamesCameron", ["LeonardoDiCaprio", "KateWinslet"], "Romance", 1997),
    ("Avatar", "JamesCameron", ["SamWorthington", "ZoeSaldana"], "SciFi", 2009),
    ("Gladiator", "RidleyScott", ["RussellCrowe", "JoaquinPhoenix"], "Action", 2000),
    ("TheMartian", "RidleyScott", ["MattDamon"], "SciFi", 2015),
    ("Dunkirk", "ChristopherNolan", ["TomHardy", "CillianMurphy"], "War", 2017),
    ("TheRevenant", "AlejandroInarritu", ["LeonardoDiCaprio"], "Drama", 2015),
    ("FightClub", "DavidFincher", ["BradPitt", "EdwardNorton"], "Drama", 1999),
    ("PulpFiction", "QuentinTarantino", ["JohnTravolta", "SamuelLJackson"], "Crime", 1994),
    ("TheGodFather", "FrancisFordCoppola", ["MarlonBrando", "AlPacino"], "Crime", 1972),
    ("12AngryMen", "SidneyLumet", ["HenryFonda", "LeeCobb"], "Drama", 1957),
    ("ToyStory", "JohnLasseter", ["TomHanks", "TimAllen"], "Animation", 1995),
    ("Parasite", "BongJoonHo", ["SongKangHo", "LeeSunKyun"], "Thriller", 2019)
]

# Ajout des triplets
for title, director, actors, genre, year in movies_data:
    movie_uri = EX[title]
    director_uri = EX[director]
    genre_uri = EX[genre]

    # Types
    g.add((movie_uri, RDF.type, Movie))
    g.add((director_uri, RDF.type, Person))
    g.add((genre_uri, RDF.type, Genre))

    # Relations principales
    g.add((movie_uri, directedBy, director_uri))
    g.add((movie_uri, hasGenre, genre_uri))
    g.add((movie_uri, releaseYear, Literal(year)))

    # Acteurs
    for actor in actors:
        actor_uri = EX[actor]
        g.add((actor_uri, RDF.type, Person))
        g.add((movie_uri, hasActor, actor_uri))
        g.add((actor_uri, profession, Literal("Actor")))

    # Profession réalisateur
    g.add((director_uri, profession, Literal("Director")))

# Export
g.serialize("movies_kb.ttl", format="turtle")

print("KB générée avec succès : movies_kb.ttl")
print(f"Nombre de triplets : {len(g)}")


alignments = {
    "Inception": "Q43361",
    "Interstellar": "Q13417189",
    "TheDarkKnight": "Q163872",
    "Titanic": "Q44578",
    "Avatar": "Q48416",
    "ChristopherNolan": "Q25191",
    "JamesCameron": "Q38111"
}

WD = Namespace("http://www.wikidata.org/entity/")

for entity, qid in alignments.items():
    g.add((EX[entity], OWL.sameAs, WD[qid]))

g.serialize("movies_kb_aligned.ttl", format="turtle")

print("✅ Alignement ajouté !")