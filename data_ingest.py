# data_ingest.py
"""
Módulo para ingesta de datos desde API-Football (v3).
Usa la clave configurada en Streamlit Cloud (st.secrets) o variable de entorno.
"""
import os
import requests

# Intentamos leer la clave desde st.secrets si estamos en Streamlit Cloud
try:
    import streamlit as st
    API_KEY = st.secrets.get("API_FOOTBALL_KEY")
except Exception:
    API_KEY = None

# Si no vino por st.secrets, la tomamos de la variable de entorno local
if not API_KEY:
    API_KEY = os.getenv("API_FOOTBALL_KEY")

if not API_KEY:
    raise ValueError(
        "Falta la API_KEY de API-Football.\n"
        "Define API_FOOTBALL_KEY en Secrets de Streamlit Cloud o como variable de entorno."
    )

BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {
    "x-apisports-key": API_KEY,
    "Accept": "application/json"
}

def _get(endpoint: str, params: dict = None) -> dict:
    url = f"{BASE_URL}{endpoint}"
    resp = requests.get(url, headers=HEADERS, params=params or {})
    resp.raise_for_status()
    data = resp.json()
    if data.get("errors"):
        raise ValueError(f"Error API-Football: {data['errors']}")
    return data.get("response", {})

def fetch_upcoming_fixtures(league_id: int, season: int = None) -> list:
    params = {"league": league_id}
    if season:
        params["season"] = season
    return _get("/fixtures", params)

def fetch_odds_for_fixture(fixture_id: int, bookmaker: str = None) -> list:
    params = {"fixture": fixture_id}
    if bookmaker:
        params["bookmaker"] = bookmaker
    return _get("/odds", params)

