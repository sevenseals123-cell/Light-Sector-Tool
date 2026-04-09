import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

st.set_page_config(page_title="NWM - Pointe NEGRI Sector Tool", layout="wide")

st.title("⚓ Application de Pilotage - Pointe NEGRI (NWM)")
st.caption("Basé sur la Note de Calcul GISMAN 25-2879 - Rev D")

# --- MODULE 1 : CALCUL DE PORTÉE (Section 3 du doc) ---
st.sidebar.header("📏 Calcul de Portée (AISM)")
ho = st.sidebar.number_input("Hauteur de l'œil (ho) en m", value=25.0) # 
Hm = st.sidebar.number_input("Plan focal du feu (Hm) en m", value=51.2) # 

# Formule AISM du document : Rg = 2.03 * (sqrt(ho) + sqrt(Hm))
rg = 2.03 * (np.sqrt(ho) + np.sqrt(Hm)) # 

st.sidebar.metric("Portée Géographique (Rg)", f"{rg:.1f} NM")
st.sidebar.write(f"Note: Portée nominale requise: 12 NM") # [cite: 35]

# --- MODULE 2 : SECTEURS D'OCCLUSION (Section 4.1 du doc) ---
st.header("🚫 Analyse des Secteurs d'Occlusion")

# Données extraites du tableau de la page 4 
occlusions_predefinies = [
    {"Label": "Bâtiment 1", "Amplitude": 13.21, "Distance": 0.54, "Couleur": "orange"},
    {"Label": "Bâtiment 2 (Marine Royale)", "Amplitude": 4.83, "Distance": 0.52, "Couleur": "red"},
    {"Label": "Radar MR", "Amplitude": 0.95, "Distance": 1.01, "Couleur": "blue"}
]

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Configuration des Secteurs")
    # On permet à l'utilisateur de positionner ces secteurs sur le compas
    secteurs_pilote = []
    for occ in occlusions_predefinies:
        st.write(f"**{occ['Label']}** (Étude: {occ['Amplitude']}°)")
        centre = st.number_input(f"Relèvement central pour {occ['Label']} (°)", 0.0, 360.0, key=occ['Label'])
        
        secteurs_pilote.append({
            "debut": (centre - occ['Amplitude']/2) % 360,
            "fin": (centre + occ['Amplitude']/2) % 360,
            "couleur": occ['Couleur'],
            "label": occ['Label']
        })

with col2:
    # Visualisation Radar
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(6,6))
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)

    for s in secteurs_pilote:
        start_rad = np.radians(s['debut'])
        end_rad = np.radians(s['fin'])
        width = (end_rad - start_rad) % (2 * np.pi)
        ax.bar(start_rad, 1, width=width, color=s['couleur'], alpha=0.6, align='edge', label=s['label'])

    ax.set_yticklabels([])
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    st.pyplot(fig)

# --- MODULE 3 : COORDONNÉES DES ZONES (Section 4.2) ---
st.divider()
st.subheader("📍 Coordonnées des Zones d'Occlusion (Estimation)")
# [cite: 72, 74, 76, 79, 82, 84, 85, 86]
data_coords = {
    "Zone": ["Zone B", "Zone B", "Zone B", "Zone B", "Zone R", "Zone R", "Zone R", "Zone R"],
    "Point": ["OCC 4", "OCC 1", "OCC 2", "OCC 3", "OCC rad1", "OCC rad2", "OCC rad3", "OCC rad4"],
    "Latitude": ["35°17'04.91\"N", "35°17'29.12\"N", "35°17'21.14\"N", "35°17'03.31\"N", "35°17'26.11\"N", "35°17'50.37\"N", "35°17'49.35\"N", "35°17'25.49\"N"],
    "Longitude": ["3°08'02.44\"W", "3°08'13.78\"W", "3°08'28.41\"W", "3°08'05.91\"W", "3°08'19.26\"W", "3°08'36.71\"W", "3°08'38.87\"W", "3°08'20.42\"W"]
}
st.table(pd.DataFrame(data_coords))
st.warning("⚠️ Les coordonnées sont estimées. GISMAN recommande des relevés in-situ[cite: 99].")
