import requests
import csv
from io import StringIO
from datetime import datetime
import tkinter as tk

#Variable
date1=[]
energy1=[]
date2=[]
energy2=[]

###################################################################################
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

def parse_csv_data(csv_content,date,energy):
    """Analyse et affiche les données du fichier CSV."""
    # Convertit le contenu brut en un objet type fichier
    csv_reader = csv.reader(StringIO(csv_content), delimiter=";")
    
    # Lire l'en-tête
    header = next(csv_reader)
    #print("Header :", header)

    # Lire et afficher les lignes suivantes
    for row in csv_reader:
        date.append(row[0])
        energy.append(row[4])
    date.reverse()
    energy.reverse()
        
def collectData(meter_ip,numberInput,date,deltaEnergy):
    energy=[]
    csv_file = fetch_csv_data(meter_ip, last_entries)
    parse_csv_data(csv_file,date,energy)
    for i in range(0,len(energy)-1):
        deltaEnergy.append(int(energy[i+1])-int(energy[i]))
       
######################################################################################   
# Configuration
mpa_ip = "10.151.50.9"
grid_ip = "10.151.50.6"
last_entries = 10  # Nombre d'entrées à récupérer

#Récupérer les données
collectData(mpa_ip,last_entries,date1,energy1)
collectData(grid_ip,last_entries,date2,energy2)


#Traitement
print(datetime.now())
print(date1)
print(energy1)
print(date2)
print(energy2)




