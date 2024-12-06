import requests
import tkinter as tk
from tkinter import *
from tkinter import ttk
from io import StringIO
import csv
import pandas as pd

# Configuration des compteurs
compteurs = [
    {"nom": "Compteur Grid", "ip": "10.151.50.6", "offset": 0, "last_index": None,"timestamp":[],"energy":[]},
    {"nom": "Compteur PV", "ip": "10.151.50.7", "offset": 0, "last_index": None,"timestamp":[],"energy":[]},
    {"nom": "Compteur Serge", "ip": "10.151.50.8", "offset": 0, "last_index": None,"timestamp":[],"energy":[]},
    {"nom": "Compteur MPA", "ip": "10.151.50.9", "offset": 19751, "last_index": None,"timestamp":[],"energy":[]},
    {"nom": "Compteur Commun", "ip": "10.151.50.10", "offset": -1, "last_index": None,"timestamp":[],"energy":[]},
]

# Récupérer l'index actuel d'un compteur
def fetch_last_index(ip):
    """Envoie une requête pour récupérer le dernier index du compteur."""
    url = f"http://{ip}/data/?last=1"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        if "text/csv" in response.headers.get("Content-Type", ""):
            csv_reader = csv.reader(StringIO(response.text), delimiter=";")
            next(csv_reader)  # Skip header
            last_row = next(csv_reader)
            index = int(last_row[1])
            return index
        else:
            print(f"Réponse inattendue pour le compteur {ip}.")
            return None
    except Exception as e:
        print(f"Erreur lors de la connexion au compteur {ip}: {e}")
        return None

# Afficher les index des compteurs
def afficher_index():
    """Affiche les index actuels des 5 compteurs."""
    for compteur in compteurs:
        index = fetch_last_index(compteur["ip"])
        if index is not None:
            compteur["last_index"] = index  # Stocke l'index récupéré
            index_label[compteur["nom"]].config(text=f"Index : {index}")
        else:
            index_label[compteur["nom"]].config(text="Index : Erreur")

# Récupérer les données à partir d'un index donné
def fetch_data_from_index():
    """Récupère les données à partir d'un index donné jusqu'au dernier index."""
    try:
        base_index = int(index_entry.get())  # Récupère l'index entré
    except ValueError:
        print("Veuillez entrer un index valide.")
        return

    # Récupérer les données pour chaque compteur
    for compteur in compteurs:
        if compteur["last_index"] is None:
            data_label[compteur["nom"]].config(text="Données : Erreur (index inconnu)")
            continue

        # Calcul de l'index cible
        start_index = base_index + compteur["offset"]
        end_index = compteur["last_index"]

        url = f"http://{compteur['ip']}/data/?from={start_index}&to={end_index}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            if "text/csv" in response.headers.get("Content-Type", ""):
                csv_reader = csv.reader(StringIO(response.text), delimiter=";")
                next(csv_reader)  # Skip header
                rows = []
                # Lire et stocker les données dans les listes
                for row in csv_reader:
                    print(row[4]);
                    compteur["timestamp"].append(row[0])  # Timestamp
                    compteur["energy"].append(row[4])  # Active Energy
                    rows.append(row);                
                if rows:
                    data_label[compteur["nom"]].config(text=f"Données récupérées : {len(rows)} entrées")
                else:
                    data_label[compteur["nom"]].config(text="Données : Aucune")
                    
                    
            else:
                data_label[compteur["nom"]].config(text="Données : Erreur")
        except Exception as e:
            print(f"Erreur lors de la récupération des données pour {compteur['nom']}: {e}")
            data_label[compteur["nom"]].config(text="Données : Erreur")
            
            
def toExcel():
    gridIn=[]
    gridOut=[]
    pvRestant=[]
    pv = compteurs[1]["energy"]
    mpa = compteurs[3]["energy"]
    sda = compteurs[2]["energy"]
    commun = compteurs[4]["energy"]
    
    for element in compteurs[0]["energy"]:
        if element >= 0:
            gridIn.append(element);
            gridOut.append(0);
        else :
            gridIn.append(0);
            gridOut.append(-element);
            
    for i, power in enumerate(compteurs[1]["energy"]):
        pvRestant.append(power - gridOut[i])
            
    data = {
        "Timestamp": compteurs[0]["timestamp"],
        "Grid In": gridIn,
        "Grid Out": gridOut,
        "PV": pv,
        "PV Restant": pv_restant,
        "MPA": mpa,
        "SDA": sda,
        "Commun": commun,
    }

    df = pd.DataFrame(data)

    # Ajout d'une ligne "Total" à la fin
    totals = {
        "Timestamp": "Total",
        "Grid In": sum(grid_in),
        "Grid Out": sum(grid_out),
        "PV": sum(pv),
        "PV Restant": sum(pv_restant),
        "MPA": sum(mpa),
        "SDA": sum(sda),
        "Commun": sum(commun),
    }

    df = pd.concat([df, pd.DataFrame([totals])], ignore_index=True)

    # Écriture dans un fichier Excel
    df.to_excel("compteurs.xlsx", index=False)

    print("Les données ont été écrites dans 'compteurs.xlsx'.")
    
    
# Fonction main
def run():
    fetch_data_from_index();
    print(compteurs[0]["timestamp"]);
    toExcel()
    
# Interface graphique
window = tk.Tk()
window.title("Gestion des compteurs")
window.geometry("600x500")

# Titre
title_label = tk.Label(window, text="Gestion des Compteurs", font=("Helvetica", 16))
title_label.pack(pady=10)

# Section affichage des index
index_frame = tk.Frame(window)
index_frame.pack(pady=10)
index_label = {}
for compteur in compteurs:
    frame = tk.Frame(index_frame)
    frame.pack(pady=5)
    tk.Label(frame, text=f"{compteur['nom']} : ").pack(side=tk.LEFT)
    index_label[compteur["nom"]] = tk.Label(frame, text="Index : Non récupéré")
    index_label[compteur["nom"]].pack(side=tk.LEFT)

# Bouton pour récupérer les index
fetch_index_button = tk.Button(window, text="Récupérer les index", command=afficher_index)
fetch_index_button.pack(pady=10)

# Section pour entrer un index et récupérer les données
entry_frame = tk.Frame(window)
entry_frame.pack(pady=10)
tk.Label(entry_frame, text="Entrer un index de début pour comteur Grid : ").pack(side=tk.LEFT)
index_entry = tk.Entry(entry_frame)
index_entry.pack(side=tk.LEFT)

fetch_data_button = tk.Button(window, text="Récupérer les données", command=run)
fetch_data_button.pack(pady=10)

# Affichage des données
data_frame = tk.Frame(window)
data_frame.pack(pady=10)
data_label = {}
for compteur in compteurs:
    frame = tk.Frame(data_frame)
    frame.pack(pady=5)
    tk.Label(frame, text=f"{compteur['nom']} : ").pack(side=tk.LEFT)
    data_label[compteur["nom"]] = tk.Label(frame, text="Données : Non récupérées")
    data_label[compteur["nom"]].pack(side=tk.LEFT)

# Lancer l'application
window.mainloop()
