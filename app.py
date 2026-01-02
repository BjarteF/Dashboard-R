import streamlit as st
import pandas as pd

# --- KONFIGURASJON ---
st.set_page_config(page_title="Salgsdashboard", layout="wide")

# --- DATA URL ---
# Her skal du lime inn lenken til ditt Google Sheet.
# Husk: Hvis lenken slutter på "edit?usp=sharing", må du endre det til "export?format=csv"
# For nå bruker vi en test-lenke slik at appen ikke krasjer før du legger inn din egen.
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRk_qYVfO8eO_O7oX4j8GkMv_aQn_wXW_rZk-2jX_x_yZ_w/pub?output=csv" 

# --- LASTE DATA ---
@st.cache_data(ttl=600)  # Cacher data i 10 minutter for hastighet
def load_data(url):
    try:
        # Leser CSV direkte fra URL
        df = pd.read_csv(url)
        
        # Prøver å konvertere 'Dato' kolonnen hvis den finnes
        # Hvis du kaller kolonnen noe annet enn 'Dato' i Excel, må du endre navnet her
        if 'Dato' in df.columns:
            df['Dato'] = pd.to_datetime(df['Dato'], errors='coerce')
            df = df.sort_values(by='Dato', ascending=False)
            
        return df
    except Exception as e:
        return None

df = load_data(SHEET_URL)

# --- DASHBOARD VISNING ---
st.title("📊 Ukentlig Salgsdashboard")

if df is not None:
    # 1. Vis bekreftelse på at data er lastet
    st.success(f"Data hentet vellykket! Viser {len(df)} rader.")

    # 2. Vis KPI-er (Eksempel - tilpass kolonnenavnene dine senere)
    col1, col2, col3 = st.columns(3)
    
    # Sjekker om kolonnene finnes før vi viser tall, for å unngå krasj
    if 'Omsetning' in df.columns:
        total_omsetning = df['Omsetning'].sum()
        col1.metric("Total Omsetning", f"{total_omsetning:,.0f} kr")
    else:
        col1.warning("Finner ikke kolonnen 'Omsetning'")

    if 'Antall' in df.columns:
        total_salg = df['Antall'].sum()
        col2.metric("Totalt Antall Salg", total_salg)
    
    # 3. Vis Datatabell
    st.subheader("Siste salgsdata")
    st.dataframe(df, use_container_width=True)

else:
    st.error("Kunne ikke laste data. Sjekk at Google Sheet-lenken er riktig og at arket er delt offentlig (eller som CSV).")
    st.info("Tips: Sjekk at du har endret URL-en i koden til din egen Google Sheet lenke.")
