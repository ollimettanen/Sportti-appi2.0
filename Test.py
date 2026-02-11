import streamlit as st
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# --- Funktiot ---

def laske_kalorit(laji, kesto, rasittavuus, paino=70):
    # MET-arvot: padel hieman koripalloa rauhallisempi
    met_arvot = {
        "sali": 6,
        "juoksu": 9,
        "koripallo": 8,
        "padel": 7,
        "kävely": 3
    }
    met = met_arvot.get(laji.lower(), 5)
    kerroin = 0.8 + (rasittavuus - 1) * 0.15
    kalorikulutus = met * paino * (kesto / 60) * kerroin
    return round(kalorikulutus, 1)

def laske_palautuminen(kesto, rasittavuus):
    palautuminen = kesto * (0.5 + 0.25 * rasittavuus)
    return round(palautuminen, 1)

def tallenna_treeni(treeni):
    tiedosto = "treenit.json"
    data = []
    if os.path.exists(tiedosto):
        with open(tiedosto, "r") as f:
            data = json.load(f)
    data.append(treeni)
    with open(tiedosto, "w") as f:
        json.dump(data, f, indent=4)

def lue_treenit():
    tiedosto = "treenit.json"
    if os.path.exists(tiedosto):
        with open(tiedosto, "r") as f:
            return json.load(f)
    return []

# --- Streamlit käyttöliittymä ---

st.title("Henkilökohtainen urheilusovellus v3")

# Käyttäjän syötteet
laji = st.selectbox("Valitse liikuntalaji", ["sali", "juoksu", "koripallo", "padel", "kävely"])
kesto = st.number_input("Kesto minuutteina", min_value=5, max_value=300, value=30)
rasittavuus = st.slider("Kuinka rankka 1-5", min_value=1, max_value=5, value=3)
paino = st.number_input("Painosi kg", min_value=30, max_value=200, value=70)

if st.button("Tallenna treeni"):
    kalorit = laske_kalorit(laji, kesto, rasittavuus, paino)
    palautuminen = laske_palautuminen(kesto, rasittavuus)
    
    treeni = {
        "pvm": datetime.now().strftime("%Y-%m-%d"),
        "laji": laji,
        "kesto": kesto,
        "rasittavuus": rasittavuus,
        "paino": paino,
        "kalorit": kalorit,
        "palautuminen": palautuminen
    }
    tallenna_treeni(treeni)
    
    st.success(f"Treeni tallennettu! Kalorit: {kalorit} kcal, palautuminen: {palautuminen} min")

# Näytä historia
st.subheader("Treenihistoria")
treenit = lue_treenit()
if treenit:
    df = pd.DataFrame(treenit)
    st.dataframe(df)

    # Muunna pvm datetimeksi
    df['pvm'] = pd.to_datetime(df['pvm'])

    # Viikkoyhteenvedot
    st.subheader("Viikon yhteenvedot")
    viikko = df[df['pvm'] >= datetime.now() - timedelta(days=7)]
    if not viikko.empty:
        st.write(viikko.groupby('laji')[['kalorit','rasittavuus']].sum())
    
    # Kuukausiyhteenvedot
    st.subheader("Kuukauden yhteenvedot")
    kuukausi = df[df['pvm'] >= datetime.now() - timedelta(days=30)]
    if not kuukausi.empty:
        st.write(kuukausi.groupby('laji')[['kalorit','rasittavuus']].sum())

    # Graafit: viikko
    st.subheader("Kalorikulutus viimeisen viikon treeneissä")
    plt.figure(figsize=(8,4))
    plt.plot(viikko['pvm'], viikko['kalorit'], marker='o')
    plt.title("Viikon kalorikulutus")
    plt.xlabel("Päivämäärä")
    plt.ylabel("Kalorit")
    plt.xticks(rotation=45)
    st.pyplot(plt)

    st.subheader("Rasittavuus viimeisen viikon treeneissä")
    plt.figure(figsize=(8,4))
    plt.plot(viikko['pvm'], viikko['rasittavuus'], marker='o', color='orange')
    plt.title("Viikon rasittavuus")
    plt.xlabel("Päivämäärä")
    plt.ylabel("Rasittavuus (1-5)")
    plt.xticks(rotation=45)
    st.pyplot(plt)

else:
    st.write("Ei tallennettuja treenejä vielä.")
