import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Configuration de la page
st.set_page_config(page_title="Maritime Sector Light Tool", layout="wide")

st.title("⚓ Déterminateur de Secteurs de Feu Portuaire")
st.markdown("""
Cette application permet de définir les secteurs d'un feu à partir des points d'occlusion 
relevés par rapport au **Nord Vrai**.
""")

# --- BARRE LATÉRALE : CONFIGURATION ---
st.sidebar.header("Paramètres du Feu")
nom_feu = st.sidebar.text_input("Nom du fanal / balise", "Feu de Jetée")
incertitude = st.sidebar.slider("Zone de pénombre (degrés)", 0.0, 5.0, 0.5)
mode_vue = st.sidebar.radio("Relèvements saisis depuis :", 
                             ["Le navire (vers le feu)", "Le feu (vers le large)"])

# --- CORPS DE L'APPLICATION ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Saisie des secteurs")
    nb_secteurs = st.number_input("Nombre de secteurs à définir", 1, 6, 3)
    
    secteurs_data = []
    couleurs_map = {"Blanc": "yellow", "Rouge": "red", "Vert": "green", "Obscurci": "gray"}

    for i in range(nb_secteurs):
        st.write(f"**Secteur {i+1}**")
        c1, c2, c3 = st.columns(3)
        with c1:
            debut = st.number_input(f"Début (°)", 0.0, 360.0, key=f"d{i}")
        with c2:
            fin = st.number_input(f"Fin (°)", 0.0, 360.0, key=f"f{i}")
        with c3:
            coul = st.selectbox("Couleur", list(couleurs_map.keys()), key=f"c{i}")
        
        # Conversion si saisie depuis le navire
        if mode_vue == "Le navire (vers le feu)":
            d_calc = (debut + 180) % 360
            f_calc = (fin + 180) % 360
        else:
            d_calc, f_calc = debut, fin

        secteurs_data.append({
            "debut": d_calc,
            "fin": f_calc,
            "couleur": couleurs_map[coul],
            "label": coul
        })

with col2:
    st.subheader("Visualisation Radar (Vue du ciel)")
    
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(6,6))
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1) # Sens horaire

    for s in secteurs_data:
        start_rad = np.radians(s['debut'])
        end_rad = np.radians(s['fin'])
        
        # Gestion du passage par le Nord (360/0)
        if end_rad < start_rad:
            width = (2 * np.pi - start_rad) + end_rad
        else:
            width = end_rad - start_rad
            
        # Dessin du secteur
        ax.bar(start_rad, 1, width=width, color=s['couleur'], 
               alpha=0.5, align='edge', edgecolor='black', label=s['label'])
        
        # Dessin de la pénombre (incertitude)
        pen_rad = np.radians(incertitude)
        ax.bar(start_rad - pen_rad/2, 1, width=pen_rad, color='black', alpha=0.2, align='edge')
        ax.bar(end_rad - pen_rad/2, 1, width=pen_rad, color='black', alpha=0.2, align='edge')

    ax.set_yticklabels([]) # Cacher les cercles de distance
    ax.set_xticks(np.radians(np.arange(0, 360, 45)))
    ax.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])
    
    st.pyplot(fig)

# --- TABLEAU RÉCAPITULATIF ---
st.divider()
st.subheader("Tableau de bord des secteurs (Relèvements Vrais)")
res_data = []
for s in secteurs_data:
    arc = (s['fin'] - s['debut']) % 360
    res_data.append({
        "Secteur": s['label'],
        "De (Nv)": f"{s['debut']:.1f}°",
        "À (Nv)": f"{s['fin']:.1f}°",
        "Amplitude": f"{arc:.1f}°"
    })

st.table(res_data)

st.info(f"Note : Les points d'occlusion incluent une marge de pénombre de ±{incertitude}°.")
