import streamlit as st
import pandas as pd

# --- KONFIGURASJON ---
st.set_page_config(page_title="Økologisk Mat - Salgsdashboard", layout="wide", page_icon="🥦")

# --- DIN DATA LINK ---
# HUSK: Lim inn din CSV-link her!
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSOlsbymJKHivZ-UEbhBrOhWsKZu927JCVCqLbn2cYDcEFoAxyMOkNghXqwuTmf33Zb1Tgse4NXTYwM/pub?output=csv" 

# --- LASTE DATA ---
@st.cache_data(ttl=600)
def load_data(url):
    try:
        df = pd.read_csv(url)
        
        # 1. Vi må sikre at 'Uke'-kolonnen finnes og bruke den som index (X-akse)
        # Vi sjekker både 'Uke' og 'uke' for sikkerhets skyld
        if 'Uke' in df.columns:
            df = df.set_index('Uke')
        elif 'uke' in df.columns:
            df = df.set_index('uke')
        else:
            st.error("Fant ikke kolonnen 'Uke'. Sjekk stavemåten i Google Sheet (Rad 1).")
            return None

        # 2. Vi konverterer alt til tall (i tilfelle du har skrevet 'kr' eller mellomrom i cellene)
        # Dette fjerner alt som ikke er tall, slik at grafene virker
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        return df
    except Exception as e:
        st.error(f"Feil under lasting av data: {e}")
        return None

# Sjekk om brukeren har oppdatert linken
if "DIN_CSV_LINK_HER" in SHEET_URL:
    st.warning("⚠️ Du må lime inn CSV-linken din i koden på GitHub (linje 10).")
    df = None
else:
    df = load_data(SHEET_URL)

# --- DASHBOARDET ---
if df is not None:
    st.title("🥦 Økologisk Mat - Salgsoversikt")

    # Finn nåværende år (Det siste årstallet i kolonnene dine)
    # Vi antar at kolonnene heter '2024', '2025' osv.
    alle_år = [col for col in df.columns if col.isdigit()] # Finner kolonner som er tall
    alle_år.sort() # Sorterer så nyeste år er sist
    
    if alle_år:
        current_year = alle_år[-1] # F.eks "2026"
        last_year = alle_år[-2] if len(alle_år) > 1 else None # F.eks "2025"
        
        # --- NØKKELTALL (KPI) ---
        # Vi finner siste uke som faktisk har omsetning i år
        valid_data_current = df[current_year].dropna() # Fjerner tomme celler
        
        if not valid_data_current.empty:
            siste_uke = valid_data_current.index[-1] # Siste ukenummer
            siste_salg = valid_data_current.iloc[-1] # Salget den uken
            
            col1, col2, col3 = st.columns(3)
            
            # KPI 1: Salg denne uken
            col1.metric(f"Salg Uke {siste_uke} ({current_year})", f"{siste_salg:,.0f} kr")
            
            # KPI 2: Sammenligning med fjoråret samme uke
            if last_year:
                salg_fjoråret = df.loc[siste_uke, last_year]
                diff = siste_salg - salg_fjoråret
                col2.metric(f"Mot samme uke {last_year}", f"{salg_fjoråret:,.0f} kr", f"{diff:,.0f} kr")
            
            # KPI 3: Totalsalg hittil i år
            total_i_år = valid_data_current.sum()
            col3.metric(f"Total omsetning {current_year}", f"{total_i_år:,.0f} kr")
    
    st.divider()

    # --- GRAFER ---
    
    # 1. Hovedgraf: Sammenligning av år
    st.subheader("📈 Salgstrend: År mot År")
    st.markdown("Her ser du hvordan årets salg (linjene) ligger an sammenlignet med tidligere år.")
    
    # Streamlit er smart: Hvis vi gir den en tabell med år som kolonner, tegner den en linje for hvert år automatisk.
    st.line_chart(df[alle_år])

    # 2. Tabell
    with st.expander("Se alle tallene"):
        st.dataframe(df.sort_index(ascending=False)) # Sorterer så uke 52 er øverst, 1 nederst (eller omvendt)
