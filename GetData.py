import requests
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from io import StringIO
import csv
import pandas as pd

# Configuration des compteurs
compteurs = [
    {"nom": "Compteur Grid", "ip": "10.151.50.6", "offset": 0, "last_index": None,"timestamp":[],"energy":[], "energy_export": []},
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
                    # Gestion de energy_export uniquement pour Compteur Grid
                    if compteur["nom"] == "Compteur Grid":
                        energy = int(row[6])
                        compteur["energy_export"].append(energy)
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
    #Données
    gridIn=[]
    gridOut=[]
    pv = []
    mpa = []
    sda = []
    commun = []
    

    
    
    #Passage des données dans les list
    for a in compteurs[1]["energy"]:
        pv.append(int(a))
    for b in compteurs[3]["energy"]:
        mpa.append(int(b))
    for c in compteurs[2]["energy"]:
        sda.append(int(c))
    for d in compteurs[4]["energy"]:
        commun.append(int(d))
    for e in compteurs[0]["energy"]:
        gridIn.append(int(e))
    for f in compteurs[0]["energy_export"]:
        gridOut.append(f)
        
    #Colonne calculée
    deltaGridIn = [0] * len(gridIn)
    deltaGridOut = [0] * len(gridOut)
    deltaPV = [0] * len(pv)
    deltaMPA = [0] * len(mpa)
    deltaSDA = [0] * len(sda)
    deltaCommun = [0] * len(commun)
    pvRestant = [0] * len(pv)
    
    consoMPAFinal = [0] * len(gridIn)
    consoSDAFinal = [0] * len(gridIn)
    
    #Calcul
    for i in range(1,len(gridIn),1):
        deltaGridIn[i] = gridIn[i]-gridIn[i-1]
        deltaGridOut[i] = gridOut[i]-gridOut[i-1]
        deltaPV[i]= pv[i]-pv[i-1]
        deltaMPA[i] = mpa[i]-mpa[i-1]
        deltaSDA[i] = sda[i]-sda[i-1]
        deltaCommun[i] = commun[i]-commun[i-1]
        
        #Calcul PV Restant
        pvRestant[i] =deltaPV[i]-deltaGridOut[i]
        
        #Calcul pourcentage de conso total pour chacun
        consoOutTotalTh = deltaMPA[i]+deltaSDA[i]+deltaCommun[i]
        consoInTotal = deltaPV[i]+deltaGridIn[i]
        consoMPAFinal[i] = (deltaMPA[i]/consoOutTotalTh)*consoInTotal+0.5*(deltaCommun[i]/consoOutTotalTh)*consoInTotal
        consoSDAFinal[i] = (deltaSDA[i]/consoOutTotalTh)*consoInTotal+0.5*(deltaCommun[i]/consoOutTotalTh)*consoInTotal
        
                
    #Création du fichier excel         
    data = {
        "Timestamp": compteurs[0]["timestamp"],
        "Grid In": gridIn,
        "Delta Grid In": deltaGridIn,
        "Grid Out": gridOut,
        "Delta Grid Out": deltaGridOut,
        "PV": pv,
        "Delta PV": deltaPV,
        "PV Restant": pvRestant,
        "MPA": mpa,
        "Delta MPA": deltaMPA,
        "SDA": sda,
        "Delta SDA": deltaSDA,
        "Commun": commun,
        "Delta Commun": deltaCommun,
        "" : None,
        "Conso Total MPA" : consoMPAFinal,
        "Conso Total SDA" : consoSDAFinal,
        
        
    }

    df = pd.DataFrame(data)

    # Ajout d'une ligne "Total" à la fin
    totals = {
        "Timestamp": "Total",
        "Grid In": "",
        "Delta Grid In": sum(deltaGridIn),
        "Grid Out": "",
        "Delta Grid Out": sum(deltaGridOut),
        "PV": "",
        "Delta PV": sum(deltaPV),
        "PV Restant": sum(pvRestant),
        "MPA": "",
        "Delta MPA": sum(deltaMPA),
        "SDA": "",
        "Delta SDA": sum(deltaSDA),
        "Commun": "",
        "Delta Commun": sum(deltaCommun),
        "" :"",
        "Conso Total MPA" : sum(consoMPAFinal),
        "Conso Total SDA" : sum(consoSDAFinal),
    }

    df = pd.concat([df, pd.DataFrame([totals])], ignore_index=True)

    # Boîte de dialogue pour choisir l'emplacement du fichier
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",  # Extension par défaut
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],  # Types de fichiers autorisés
        title="Enregistrer sous"  # Titre de la fenêtre
    )

    # Vérifiez si un chemin a été sélectionné
    if file_path:
        df.to_excel(file_path, index=False)  # Enregistrement du fichier Excel
        print(f"Les données ont été écrites dans '{file_path}'.")
    else:
        print("Enregistrement annulé par l'utilisateur.")
    
    
# Fonction main
def run():
    fetch_data_from_index();
    print(compteurs[0]["timestamp"]);
    toExcel()
    
# Interface graphique
window = tk.Tk()
window.title("Gestion des compteurs")
window.geometry("600x800")

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
tk.Label(entry_frame, text="Entrer un index de début pour compteur Grid : ").pack(side=tk.LEFT)
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
