import requests
import csv

def fetch_csv_data(meter_ip, last_entries):
    """Récupère un fichier CSV avec les dernières entrées."""
    url = f"http://{meter_ip}/data/?last={last_entries}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Vérifie les erreurs HTTP

        # Vérifie si la réponse contient un fichier CSV
        if "text/csv" in response.headers.get("Content-Type", ""):
            return response.text  # Retourne le contenu brut du CSV
        else:
            print("La réponse ne contient pas de fichier CSV.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la connexion au compteur : {e}")
    return None

def parse_csv_data(csv_content):
    """Analyse et affiche les données du fichier CSV."""
    csv_reader = csv.reader(csv_content.splitlines(), delimiter=";")
    for row in csv_reader:
        print(row)  # Affiche chaque ligne du CSV

# Configuration
meter_ip = "10.151.50.9"  # Remplacez par l'IP du compteur
last_entries = 30  # Nombre d'entrées à récupérer

# Étape 1 : Récupérer le fichier CSV
csv_data = fetch_csv_data(meter_ip, last_entries)

# Étape 2 : Lire et afficher les données si le CSV est valide
if csv_data:
    parse_csv_data(csv_data)
else:
    print("Aucune donnée CSV récupérée.")
