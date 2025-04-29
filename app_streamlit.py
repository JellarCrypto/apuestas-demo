# app_streamlit.py
"""
Web App con Streamlit para análisis de apuestas deportivas.
Deploy gratuito en Streamlit Cloud.
"""
import os
import streamlit as st
from data_ingest import fetch_upcoming_fixtures, fetch_odds_for_fixture
from app import calcular_probabilidades_desde_cuotas

st.set_page_config(page_title="Apuestas Deportivas", layout="centered")
st.title("Análisis de Apuestas Deportivas")

st.sidebar.header("Ajustes API")
api_key = st.sidebar.text_input("API-Football Key", type="password")
if api_key:
    os.environ["API_FOOTBALL_KEY"] = api_key

st.markdown("## Selecciona Partido")
league_id = 2  # Champions League
season = 2024

try:
    fixtures = fetch_upcoming_fixtures(league_id, season)
except Exception as e:
    st.error(f"Error al obtener fixtures: {e}")
    st.stop()

psg_fixtures = [
    f for f in fixtures
    if "Paris Saint-Germain" in (
        f.get("teams", {}).get("home", {}).get("name"),
        f.get("teams", {}).get("away", {}).get("name")
    )
]
if not psg_fixtures:
    st.warning("No se encontró partido de PSG.")
    st.stop()

fixture = psg_fixtures[0]
fix = fixture.get("fixture", {})
home = fixture.get("teams", {}).get("home", {}).get("name")
away = fixture.get("teams", {}).get("away", {}).get("name")
date = fix.get("date")
fixture_id = fix.get("id")

st.markdown(f"### Partido: {home} vs {away}\nFecha: {date}")

try:
    odds_data = fetch_odds_for_fixture(fixture_id)
except Exception as e:
    st.error(f"Error al obtener cuotas: {e}")
    st.stop()

odds_1x2 = []
for offer in odds_data:
    for bet in offer.get("bets", []):
        if bet.get("name") in ["Match Winner", "1X2"]:
            values = bet.get("values", [])
            mapping = {v.get("value"): v.get("odd") for v in values}
            if all(k in mapping for k in [home, "Draw", away]):
                cuota_l = mapping[home]
                cuota_e = mapping["Draw"]
                cuota_v = mapping[away]
                probs = calcular_probabilidades_desde_cuotas(cuota_l, cuota_e, cuota_v)
                for nombre, prob, cuota in [
                    (home, probs[0], cuota_l),
                    ("Empate", probs[1], cuota_e),
                    (away, probs[2], cuota_v)
                ]:
                    ve = prob * cuota - 1
                    if prob >= 0.8:
                        odds_1x2.append((nombre, prob, cuota, ve))

odds_sorted = sorted(odds_1x2, key=lambda x: x[1], reverse=True)[:3]
if not odds_sorted:
    st.info("No hay apuestas con probabilidad >= 80% en 1X2.")
else:
    st.markdown("## Top 3 apuestas con ≥80% de probabilidad")
    for nombre, prob, cuota, ve in odds_sorted:
        st.write(f"**{nombre}**: Probabilidad={prob*100:.1f}%, Cuota={cuota}, Valor Esperado={ve:.2f}")

st.markdown("---")
st.write("Demo creada con Streamlit. Ajusta la API Key y parámetros según necesites.")
