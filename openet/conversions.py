import math


def mass_to_volume(m,den):
    """
    Convert a mass flow from 'Kg/s' to MBPD (thousand barrels per day)
    """
    
    mf = m*60*60*24 # Kg/s -> Kg/day
    mf = mf/den #Kg/day -> m3/day
    mf = mf*6.289811 #CMD -> BPD
    mf = mf/1000 #BPD -> MBPD
    
    #print(m,'Kg/s', MW,'g/mol', mf,'MMSCFD')
    
    return (mf)

def mass_to_molar(m,MW):
    """
    Convert a mass flow from 'Kg/s' to MMSCFD (thousand thousand standard cubic feet per day)
    given the following assumptions for standard conditions:

    Temperature - 15 C
    Pressure - 1 ATM
    """
    
    mf = m*60*60 # Kg/s -> Kg/hr
    mf = mf/MW #Kg/hr -> Kgmole/hr
    mf = mf*22.414 #22.414 Nm3 per kmole Normal Volume occupies 22.414 [L/mol] [m3/kmol] [m3/kgmol]
    mf = mf*((273+15)/273) #STP = 15oC, NTP 0oC: conversion from normal (0 C) to standard (15 C)
    mf = mf*(3.282**3) # meters cubic to feet cubic
    #mf = mf*24 # Scf/hr -> cf/day
    mf = mf/1e3 #SCFH -> MSCFH
    
    #print(m,'Kg/s', MW,'g/mol', mf,'MMSCFD')
    
    return (mf)