# data_ingest.py
"""
Módulo para ingesta de datos desde API-Football (v3)
Incluye funciones para obtener fixtures, cuotas y estadísticas básicas.
"""
import os
import requests
from typing import Dict, Any, List

# Configuración de la API
API_KEY = os.getenv("API_FOOTBALL_KEY", "TU_API_KEY_AQUI")
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {
    "x-apisports-key": API_KEY,
    "Accept": "application/json"
}

def _get(endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Llama al endpoint especificado con parámetros y devuelve el JSON.
    """
    url = f"{BASE_URL}{endpoint}"
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    data = response.json()
    if data.get("errors"):
        raise ValueError(f"Error API-Football: {data['errors']}")
    return data.get("response", {})

def fetch_upcoming_fixtures(league_id: int, season: int = None) -> List[Dict[str, Any]]:
    """
    Obtiene los próximos fixtures para una liga y temporada dada.
    """
    params = {"league": league_id}
    if season:
        params["season"] = season
    return _get("/fixtures", params)

def fetch_odds_for_fixture(fixture_id: int, bookmaker: str = None) -> List[Dict[str, Any]]:
    """
    Obtiene cuotas para un fixture específico.
    """
    params = {"fixture": fixture_id}
    if bookmaker:
        params["bookmaker"] = bookmaker
    return _get("/odds", params)

def fetch_team_statistics(team_id: int, league_id: int, season: int) -> Dict[str, Any]:
    """
    Obtiene estadísticas de un equipo en una liga y temporada.
    """
    params = {"team": team_id, "league": league_id, "season": season}
    return _get("/teams/statistics", params)
