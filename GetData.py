import requests

meter_ip = "10.151.50.9"  # Adresse IP du compteur
url = f"http://{meter_ip}/meterdata.json"

try:
    response = requests.get(url, timeout=10)
    print("Statut HTTP :", response.status_code)  # Vérifie le statut HTTP
    print("Contenu brut :", response.text)       # Affiche la réponse brute

    response.raise_for_status()  # Provoque une erreur pour les codes HTTP 4xx ou 5xx

    # Analyse des données JSON
    data = response.json()
    active_power = data.get("p_L123_act_e", "N/A")
    print(f"Puissance active totale : {active_power} kW")

except requests.exceptions.RequestException as e:
    print(f"Erreur lors de la connexion au compteur : {e}")
except ValueError:
    print("Erreur de parsing des données reçues. Contenu incorrect ou vide.")
