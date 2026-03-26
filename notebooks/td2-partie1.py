from owlready2 import *

# 1. Charger l'ontologie à partir du contenu XML (sauvegardé localement)
# Assure-toi que le texte XML est enregistré sous le nom 'family.owl'
onto = get_ontology("family.owl").load()
print(onto)
with onto:
    # Définition de la classe oldPerson demandée par le TP
    class oldPerson(onto.Person):
        pass

    # 2. Application de la règle SWRL
    # "Une personne qui a un âge > 60 est une oldPerson"
    rule = Imp()
    rule.set_as_rule("Person(?p) ^ age(?p, ?a) ^ greaterThan(?a, 60) -> oldPerson(?p)")

# 3. Lancer le raisonneur Pellet (nécessite Java installé)
# Pellet est indispensable pour traiter les règles SWRL
sync_reasoner_pellet(infer_property_values = True, infer_data_property_values = True)

# 4. Afficher les résultats du raisonnement
print("--- Résultats de l'inférence SWRL ---")
old_people = onto.oldPerson.instances()
if not old_people:
    print("Aucune personne âgée trouvée.")
else:
    for p in old_people:
        # On récupère le nom et l'âge via les propriétés de l'ontologie
        name = p.name if p.name else p.name
        age = p.age if p.age else "inconnu"
        print(f"Individu : {p.name} | Âge : {age} -> Classé comme oldPerson")