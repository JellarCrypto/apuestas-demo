# data_ingest.py
"""
Módulo para ingesta de datos desde API-Football (v3).
Usa la clave definida en la variable de entorno API_FOOTBALL_KEY.
"""
import os
import requests
# Leer la API Key de la variable de entorno
API_KEY = os.getenv("API_FOOTBALL_KEY")
if not API_KEY:
    raise ValueError(
        "Falta la API_KEY de API-Football.\n"
        "Define API_FOOTBALL_KEY en la variable de entorno antes de usar."
    )
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {
    "x-apisports-key": API_KEY,
    "Accept": "application/json"
}
def _get(endpoint: str, params: dict = None) -> list:
    """
    Llama al endpoint de API-Football y devuelve la parte 'response'.
    """
    url = f"{BASE_URL}{endpoint}"
    response = requests.get(url, headers=HEADERS, params=params or {})
    response.raise_for_status()
    data = response.json()
    if data.get("errors"):
        raise ValueError(f"Error API-Football: {data['errors']}")
    return data.get("response", [])
def fetch_upcoming_fixtures(league_id: int, season: int = None) -> list:
    """
    Obtiene los próximos fixtures para una liga y temporada dada.
    :param league_id: ID de la liga en API-Football
    :param season: Año de la temporada (e.g., 2024). Opcional.
    :return: Lista de fixtures (response JSON).
    """
    params = {"league": league_id}
    if season is not None:
        params["season"] = season
    return _get("/fixtures", params)
def fetch_odds_for_fixture(fixture_id: int, bookmaker: str = None) -> list:
    """
    Obtiene cuotas para un fixture específico.
    :param fixture_id: ID del partido
    :param bookmaker: Nombre interno del bookmaker (opcional)
    :return: Lista de ofertas de cuotas (response JSON).
    """
    params = {"fixture": fixture_id}
    if bookmaker:
        params["bookmaker"] = bookmaker
    return _get("/odds", params)
