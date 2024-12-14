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
    gridIn=[0,70,140,210,210,210,210,230,250,270,300,300,300,300]
    gridOut=[0,0,0,0,0,0,0,0,0,0,0,20,40,60]
    pv = [0,0,0,0,70,140,210,290,370,450,500,620,740,860]
    mpa = [0,30,70,90,120,160,180,220,240,300,370,410,470,490]
    sda = [0,30,50,90,120,140,180,220,280,300,300,340,360,420]
    commun = [0,10,20,30,40,50,60,80,100,120,130,150,170,190]
    

    
    
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
    
    pvMPATh = [0] * len(gridIn)
    pvSDATh = [0] * len(gridIn)
    gridMPATh = [0] * len(gridIn)
    gridSDATh = [0] * len(gridIn)
    surplusMPATh = [0] * len(gridIn)
    surplusSDATh = [0] * len(gridIn)
    
    pvFinalMPA= [0] * len(gridIn)
    pvFinalSDA= [0] * len(gridIn)
    gridFinalMPA= [0] * len(gridIn)
    gridFinalSDA= [0] * len(gridIn)
    
    #Compte
    SDAaMPA=0.0
    MPAaSDA=0.0
    
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
        consoInTotal = deltaPV[i]+deltaGridIn[i]-deltaGridOut[i]
        consoMPAFinal[i] = (deltaMPA[i]/consoOutTotalTh)*consoInTotal+0.5*(deltaCommun[i]/consoOutTotalTh)*consoInTotal
        consoSDAFinal[i] = (deltaSDA[i]/consoOutTotalTh)*consoInTotal+0.5*(deltaCommun[i]/consoOutTotalTh)*consoInTotal
        
        #Calcul théorique
        pvMPATh[i] = pvRestant[i]/2
        pvSDATh[i] = pvRestant[i]/2
        gridMPATh[i] = consoMPAFinal[i]-pvMPATh[i]
        gridSDATh[i] = consoSDAFinal[i]-pvSDATh[i]
        
        #Calcul surplus
        if(gridMPATh[i]>=0):
            surplusMPATh[i] =0
        else :
            surplusMPATh[i] = gridMPATh[i]*-1
        
        if(gridSDATh[i]>=0):
            surplusSDATh[i] =0
        else :
            surplusSDATh[i] = gridSDATh[i]*-1
        
        #Calcul valeurs finales
        pvFinalMPA[i] = pvMPATh[i]-surplusMPATh[i]+surplusSDATh[i]
        pvFinalSDA[i] = pvSDATh[i]-surplusSDATh[i]+surplusMPATh[i]
        
        gridFinalMPA[i] = consoMPAFinal[i]-pvFinalMPA[i]
        gridFinalSDA[i] = consoSDAFinal[i]-pvFinalSDA[i]
    
    #Compte
    if sum(pvFinalMPA) > sum(pvFinalSDA):
        MPAaSDA = sum(pvFinalMPA) -(sum(pvRestant)/2)
        SDAaMPA = 0.0
    elif sum(pvFinalMPA) < sum(pvFinalSDA):
        SDAaMPA = sum(pvFinalSDA) -(sum(pvRestant)/2)
        MPAaSDA = 0.0
    else :
        SDAaMPA = 0.0
        MPAaSDA = 0.0
                
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
        " " : None,
        "PV Théorique MPA" : pvMPATh,
        "PV Théorique SDA" : pvSDATh,
        "Grid Théorique MPA" : gridMPATh,
        "Grid Théorique SDA" : gridSDATh,
        "Surplus MPA" : surplusMPATh,
        "Surplus SDA" : surplusSDATh,
        "  " : None,
        "PV Final MPA" :pvFinalMPA,
        "Grid Final MPA" :gridFinalMPA,
        "   " : None,
        "PV Final SDA" :pvFinalSDA,
        "Grid Final SDA" :gridFinalSDA,
    }

    df = pd.DataFrame(data)

    # Ajout d'une ligne "Total" à la fin
    totals = {
        #"Timestamp": "Total",
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
        " " : "",
        "PV Théorique MPA" : sum(pvMPATh),
        "PV Théorique SDA" : sum(pvSDATh),
        "Grid Théorique MPA" : "",
        "Grid Théorique SDA" : "",
        "Surplus MPA" : "",
        "Surplus SDA" : "",
        "  " : "",
        "PV Final MPA" : sum(pvFinalMPA),
        "Grid Final MPA" :sum(gridFinalMPA),
        "   " : "",
        "PV Final SDA" :sum(pvFinalSDA),
        "Grid Final SDA" :sum(gridFinalSDA),
    }

    df = pd.concat([df, pd.DataFrame([totals])], ignore_index=True)
    
    # Ajouter plusieurs lignes vides
    empty_rows = pd.DataFrame([[""] * len(df.columns)] * 2, columns=df.columns)
    df = pd.concat([df, empty_rows], ignore_index=True)
    
    # Ajout d'une ligne "Total global" à la fin
    total = {
        #"Timestamp": "Total",
        "Grid In": "",
        "Delta Grid In": "",
        "Grid Out": "",
        "Delta Grid Out": "",
        "PV": "",
        "Delta PV": "",
        "PV Restant": "",
        "MPA": "",
        "Delta MPA": "",
        "SDA": "",
        "Delta SDA": "",
        "Commun": "",
        "Delta Commun": "",
        "" :"",
        "Conso Total MPA" : "",
        "Conso Total SDA" : "",
        " " : "",
        "PV Théorique MPA" : "",
        "PV Théorique SDA" : "",
        "Grid Théorique MPA" : "",
        "Grid Théorique SDA" : "",
        "Surplus MPA" : "",
        "Surplus SDA" : "",
        "  " : "Total PV",
        "PV Final MPA" : sum(pvFinalMPA)+sum(pvFinalSDA),
        "Grid Final MPA" :"Total Grid",
        "   " : sum(gridFinalMPA)+sum(gridFinalSDA),
        "PV Final SDA" :"",
        "Grid Final SDA" :"",
    }

    df = pd.concat([df, pd.DataFrame([total])], ignore_index=True)
    
    # Ajout d'une ligne "Résumé" à la fin
    resume = {
        #"Timestamp": "Total",
        "Grid In": "Oiken achète",
        "Delta Grid In": sum(deltaGridOut),
        "Grid Out": "SDA doit à Oiken",
        "Delta Grid Out": sum(gridFinalSDA),
        "PV": "MPA doit à Oiken",
        "Delta PV": sum(gridFinalMPA),
        "PV Restant": "MPA doit à SDA",
        "MPA": MPAaSDA,
        "Delta MPA": "SDA doit a MPA",
        "SDA": SDAaMPA,
        "Delta SDA": "",
        "Commun": "",
        "Delta Commun": "",
        "" :"",
        "Conso Total MPA" : "",
        "Conso Total SDA" : "",
        " " : "",
        "PV Théorique MPA" : "",
        "PV Théorique SDA" : "",
        "Grid Théorique MPA" : "",
        "Grid Théorique SDA" : "",
        "Surplus MPA" : "",
        "Surplus SDA" : "",
        "  " : "",
        "PV Final MPA" : "",
        "Grid Final MPA" :"",
        "   " : "",
        "PV Final SDA" :"",
        "Grid Final SDA" :"",
    }

    df = pd.concat([df, pd.DataFrame([resume])], ignore_index=True)

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
    