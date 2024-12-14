import requests
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from io import StringIO
import csv
import pandas as pd


def toExcel():
    #Données
    gridIn=[0,70,140,210]
    gridOut=[0,0,0,0]
    pv = [0,0,0,0]
    mpa = [0,30,70,90]
    sda = [0,30,50,90]
    commun = [0,10,20,30]
    

    
    
    """#Passage des données dans les list
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
        gridOut.append(f)"""
        
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
        #"Timestamp": compteurs[0]["timestamp"],
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

toExcel();
    