import requests
import csv
from io import StringIO
from datetime import datetime, timedelta
import pytz
import tkinter as tk
from tkinter import *
from tkcalendar import Calendar

# Variables globales
startDate = None
endDate = None
date1 = []
energy1 = []
date2 = []
energy2 = []
# Configuration
mpa_ip = "10.151.50.9"
grid_ip = "10.151.50.6"

###################################################################################
def fetch_csv_data_with_range(meter_ip, from_index, to_index):
    """Récupère un fichier CSV avec une plage d'indices."""
    url = f"http://{meter_ip}/data/?from={from_index}&to={to_index}"
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

def parse_csv_data(csv_content, date, energy):
    """Analyse et affiche les données du fichier CSV."""
    # Convertit le contenu brut en un objet type fichier
    csv_reader = csv.reader(StringIO(csv_content), delimiter=";")
    
    # Lire l'en-tête
    header = next(csv_reader)

    # Lire et stocker les données dans les listes
    for row in csv_reader:
        date.append(row[0])  # Timestamp
        energy.append(row[4])  # Active Energy
    date.reverse()
    energy.reverse()

# Récupérer l'index actuel avec ?last=1
def fetch_last_data(meter_ip):
    """Récupère la dernière donnée pour obtenir l'index et le timestamp."""
    url = f"http://{meter_ip}/data/?last=1"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Vérifie les erreurs HTTP

        if "text/csv" in response.headers.get("Content-Type", ""):
            # Lecture du CSV
            csv_reader = csv.reader(StringIO(response.text), delimiter=";")
            next(csv_reader)  # Skip header
            
            # Extraire les données de la dernière ligne
            last_row = next(csv_reader)
            timestamp = last_row[0]
            current_index = int(last_row[1])
            return timestamp, current_index
        else:
            print("La réponse ne contient pas un fichier CSV valide.")
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la connexion au compteur : {e}")
    return None, None

# Calcul des indices à partir de la plage horaire UTC
def calculate_from_to_indices(start_date, end_date, current_timestamp, current_index):
    """
    Calcule les indices `from` et `to` en fonction des dates exactes, en corrigeant l'ordre des indices
    pour garantir que la plage horaire est correcte.
    """
    # Convertir les dates de début et de fin en datetime UTC
    start_dt_utc = datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, tzinfo=pytz.UTC)
    end_dt_utc = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=45, second=0, tzinfo=pytz.UTC)

    # Convertir le timestamp actuel en datetime UTC
    current_dt_utc = datetime.strptime(current_timestamp, '%Y-%m-%dT%H:%M:%S%z')

    # Calculer les intervalles de 15 minutes
    print("soustraction utc : ")
    print(current_dt_utc - start_dt_utc)
    print("en s : ")
    print((current_dt_utc - start_dt_utc).total_seconds())
    print("divison : ")
    print(int((current_dt_utc - start_dt_utc).total_seconds() // (15 * 60)))
    print("soustraction utc : ")
    print(current_dt_utc - end_dt_utc)
    print("en s : ")
    print((current_dt_utc - end_dt_utc).total_seconds())
    print("divison : ")
    print(int((current_dt_utc - end_dt_utc).total_seconds() // (15 * 60)))
    
    intervals_since_start = int((current_dt_utc - start_dt_utc).total_seconds() // (15 * 60))
    intervals_since_end = int((current_dt_utc - end_dt_utc).total_seconds() // (15 * 60))

    # Calculer les indices
    from_index = current_index - intervals_since_start
    to_index = current_index - intervals_since_end

    # Vérifications et affichage pour débogage
    print(f"Start UTC: {start_dt_utc}, End UTC: {end_dt_utc}")
    print(f"Current timestamp: {current_dt_utc}, Current index: {current_index}")
    print(f"Intervals since start: {intervals_since_start}, Intervals since end: {intervals_since_end}")
    print(f"Calculated indices - From: {from_index}, To: {to_index}")

    return from_index, to_index



# Fonction pour récupérer les données pour une plage d'indices donnée
def fetch_csv_data_with_range(meter_ip, from_index, to_index):
    """Récupère un fichier CSV avec une plage d'indices."""
    url = f"http://{meter_ip}/data/?from={from_index}&to={to_index}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Vérifie les erreurs HTTP

        if "text/csv" in response.headers.get("Content-Type", ""):
            return response.text  # Retourne le contenu brut du CSV
        else:
            print("La réponse ne contient pas de fichier CSV.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la connexion au compteur : {e}")
    return None

# Lancer le traitement
def run():
    global startDate, endDate
    if startDate and endDate:
        print(f"Récupération des données entre {startDate} et {endDate}...")

        # Étape 1 : Récupérer l'index actuel et le timestamp
        current_timestamp, current_index = fetch_last_data(mpa_ip)
        if current_timestamp and current_index:
            print(f"Index actuel : {current_index}, Timestamp actuel : {current_timestamp}")

            # Étape 2 : Calculer les indices `from` et `to` pour une plage horaire donnée
            from_index, to_index = calculate_from_to_indices(startDate, endDate, current_timestamp, current_index)
            print(f"Indices calculés : from={from_index}, to={to_index}")

            # Étape 3 : Récupérer les données pour la plage d'indices
            csv_data = fetch_csv_data_with_range(mpa_ip, from_index, to_index)
            if csv_data:
                parse_csv_data(csv_data, date1, energy1)
                print("Données MPA :", date1, energy1)
            else:
                print("Erreur lors de la récupération des données.")
        else:
            print("Impossible de récupérer l'index actuel et le timestamp.")
    else:
        print("Veuillez définir les dates de début et de fin.")


#####################################################################################
# Interface graphique
window = Tk()
window.title("Acquisition des compteurs")
window.geometry("400x400")

title = tk.Label(text="Acquisition des compteurs")
title.pack()

# Ajout du calendrier
cal = Calendar(window, selectmode='day', year=2024, month=11, day=30)
cal.pack(pady=20)

# Définir les dates de début et de fin
def setGrad_date():
    global startDate, endDate
    if startDate is None:
        # Convertir au format attendu
        startDate = datetime.strptime(cal.get_date(), '%m/%d/%y').strftime('%Y-%m-%d')
        print(f"Date de début définie : {startDate}")
    else:
        # Convertir au format attendu
        endDate = datetime.strptime(cal.get_date(), '%m/%d/%y').strftime('%Y-%m-%d')
        print(f"Date de fin définie : {endDate}")

# Lancer la collecte de données
def run():
    global startDate, endDate
    if startDate and endDate:
        print(f"Récupération des données entre {startDate} et {endDate}...")

        # Étape 1 : Récupérer l'index actuel et le timestamp
        current_timestamp, current_index = fetch_last_data(mpa_ip)
        if current_timestamp and current_index:
            print(f"Index actuel : {current_index}, Timestamp actuel : {current_timestamp}")

            # Étape 2 : Calculer les indices `from` et `to` pour une plage horaire donnée
            from_index, to_index = calculate_from_to_indices(startDate, endDate, current_timestamp, current_index)
            print(f"Indices calculés : from={from_index}, to={to_index}")

            # Étape 3 : Récupérer les données pour la plage d'indices
            csv_data = fetch_csv_data_with_range(mpa_ip, from_index, to_index)
            if csv_data:
                parse_csv_data(csv_data, date1, energy1)
                print("Données MPA :", date1, energy1)
            else:
                print("Erreur lors de la récupération des données.")
        else:
            print("Impossible de récupérer l'index actuel et le timestamp.")
    else:
        print("Veuillez définir les dates de début et de fin.")



# Boutons pour définir les dates et lancer le traitement
Button(window, text="Set Date", command=setGrad_date).pack(pady=10)
Button(window, text="Run", command=run).pack(pady=10)

#####################################################################################
# Lancement de l'interface graphique
window.mainloop()
