import requests

# Utilise ton profil comme convenu pour le User-Agent [cite: 117]
headers = {
    "User-Agent": "MovieProjectESILV/1.0 (https://github.com/fatou26/Projet-web-dataming-semantic; fatou-esilv)"
}

def search_wikidata_correct(entity_name):
    # L'URL correcte pour la recherche (Action API)
    url = "https://www.wikidata.org/w/api.php"
    
    params = {
        "action": "wbsearchentities",
        "search": entity_name,
        "language": "en",
        "format": "json",
        "limit": 1
    }
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("search"):
            result = data["search"][0]
            # Retourne l'ID (ex: Q1591) et le label pour ton tableau d'alignement [cite: 198]
            return result['id'], result['label']
    
    return None, None

# Test avec Edward Norton
qid, label = search_wikidata_correct("Edward Norton")
print(f"Résultat : {qid} ({label})")