# app_streamlit.py
"""
Web App con Streamlit para análisis de apuestas deportivas.
Pide la API Key en el sidebar y muestra las 3 mejores apuestas 1X2 con ≥80% de probabilidad.
"""
import os
import streamlit as st

# ── PEDIR LA API KEY EN EL SIDEBAR ────────────────────────────────────────────
st.set_page_config(page_title="Apuestas Deportivas", layout="centered")
st.sidebar.header("Ajustes API")
api_key = st.sidebar.text_input("API-Football Key", type="password")
if not api_key:
    st.sidebar.error("🔑 Introduce tu API Key para continuar")
    st.stop()
os.environ["API_FOOTBALL_KEY"] = api_key

# ── IMPORTS QUE DEPENDEN DE LA API KEY ────────────────────────────────────────
from data_ingest import fetch_upcoming_fixtures, fetch_odds_for_fixture
from app import calcular_probabilidades_desde_cuotas

# ── LOGO / TÍTULO DE PÁGINA ──────────────────────────────────────────────────
st.title("Análisis de Apuestas Deportivas")

# ── SELECCIÓN DE PARTIDO PSG (Champions League 2024) ─────────────────────────
st.markdown("## Selecciona Partido")
league_id = 2   # Champions League
season = 2024

try:
    fixtures = fetch_upcoming_fixtures(league_id, season)
except Exception as e:
    st.error(f"Error al obtener fixtures: {e}")
    st.stop()

psg_fixtures = []
for f in fixtures:
    home = f["teams"]["home"]["name"]
    away = f["teams"]["away"]["name"]
    if "Paris Saint-Germain" in (home, away):
        psg_fixtures.append(f)

if not psg_fixtures:
    st.warning("No se encontró partido de PSG para Champions League 2024.")
    st.stop()

fixture = psg_fixtures[0]
fix = fixture["fixture"]
home = fixture["teams"]["home"]["name"]
away = fixture["teams"]["away"]["name"]
date = fix["date"]
fixture_id = fix["id"]

st.markdown(f"### Partido: **{home} vs {away}**\n**Fecha:** {date}")

# ── CÁLCULO DE APUESTAS 1X2 CON PROB ≥80% ──────────────────────────────────
try:
    odds_data = fetch_odds_for_fixture(fixture_id)
except Exception as e:
    st.error(f"Error al obtener cuotas: {e}")
    st.stop()

odds_1x2 = []
for offer in odds_data:
    for bet in offer.get("bets", []):
        if bet.get("name") in ["Match Winner", "1X2"]:
            for val in bet.get("values", []):
                key = val["value"]
                odd = val["odd"]
                # Guardamos en un dict para luego procesar
                mapping = {v["value"]: v["odd"] for v in bet["values"]}
            if home in mapping and "Draw" in mapping and away in mapping:
                cL, cE, cV = mapping[home], mapping["Draw"], mapping[away]
                probs = calcular_probabilidades_desde_cuotas(cL, cE, cV)
                for nombre, prob, cuota in [
                    (home, probs[0], cL),
                    ("Empate", probs[1], cE),
                    (away, probs[2], cV)
                ]:
                    ve = prob * cuota - 1
                    if prob >= 0.8:
                        odds_1x2.append((nombre, prob, cuota, ve))

if not odds_1x2:
    st.info("No hay apuestas con probabilidad ≥80% en 1X2 para este partido.")
else:
    st.markdown("## Top 3 apuestas con ≥80% de probabilidad")
    for nombre, prob, cuota, ve in sorted(odds_1x2, key=lambda x: x[1], reverse=True)[:3]:
        st.write(f"**{nombre}**: Prob={prob*100:.1f}% | Cuota={cuota} | VE={ve:.2f}")

st.markdown("---")
st.write("Demo creada con Streamlit. Ajusta la API Key y parámetros según necesites.")
