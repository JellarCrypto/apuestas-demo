# app.py
"""
CLI para análisis de apuestas deportivas.
Incluye ingestión de datos desde API-Football y análisis de apuestas.
"""
import os
import argparse
import sys

from data_ingest import (
    fetch_upcoming_fixtures,
    fetch_odds_for_fixture
)
from typing import Optional

def calcular_probabilidades_desde_cuotas(cuota_local: float, cuota_empate: float, cuota_visitante: float):
    """
    Calcula probabilidades implícitas normalizadas a partir de cuotas 1X2.
    """
    prob_local = 1 / cuota_local
    prob_empate = 1 / cuota_empate
    prob_visitante = 1 / cuota_visitante

    total = prob_local + prob_empate + prob_visitante
    prob_local /= total
    prob_empate /= total
    prob_visitante /= total

    return prob_local, prob_empate, prob_visitante

def analizar_mas_de_2_5_goles(
    goles_local: float,
    goles_visitante: float,
    porcentaje_over25: float,
    cuota: float,
    bajas_ofensivas: bool = False
):
    """
    Evalúa apuesta de más de 2.5 goles usando valor esperado.
    """
    prob_media = (goles_local + goles_visitante) / 2
    prob = porcentaje_over25 / 100

    if prob_media > 1.8:
        prob += 0.05
    if bajas_ofensivas:
        prob -= 0.07

    prob = max(0, min(prob, 1))
    ve = prob * cuota - 1

    return prob, ve

def analizar_btts(
    pct_local: float,
    pct_visitante: float,
    cuota: float,
    baja_goleadores: bool = False,
    defensa_fuerte: bool = False
):
    """
    Evalúa apuesta "Both Teams To Score" (BTTS) usando valor esperado.
    """
    prob = ((pct_local + pct_visitante) / 2) / 100

    if baja_goleadores:
        prob -= 0.07
    if defensa_fuerte:
        prob -= 0.05
    else:
        prob += 0.03

    prob = max(0, min(prob, 1))
    ve = prob * cuota - 1

    return prob, ve

def analizar_resultado_1x2(
    prob_local: float,
    prob_empate: float,
    prob_visitante: float,
    cuota_local: float,
    cuota_empate: float,
    cuota_visitante: float
):
    """
    Evalúa apuestas 1X2 para cada resultado y calcula valor esperado.
    """
    resultados = []
    for nombre, prob, cuota in [
        ("Local", prob_local, cuota_local),
        ("Empate", prob_empate, cuota_empate),
        ("Visitante", prob_visitante, cuota_visitante)
    ]:
        ve = prob * cuota - 1
        resultados.append((nombre, prob, cuota, ve))
    return resultados

def main():
    parser = argparse.ArgumentParser(
        description="Herramienta CLI de análisis de apuestas deportivas"
    )
    subparsers = parser.add_subparsers(dest="comando", required=True)

    # Subcomando: over 2.5
    over = subparsers.add_parser("over", help="Análisis Over 2.5 goles")
    over.add_argument("--goles_local", type=float, required=True)
    over.add_argument("--goles_visitante", type=float, required=True)
    over.add_argument("--porcentaje_over25", type=float, required=True)
    over.add_argument("--cuota", type=float, required=True)
    over.add_argument("--bajas_ofensivas", action="store_true")

    # Subcomando: btts
    btts = subparsers.add_parser("btts", help="Análisis Ambos Equipos Marcan")
    btts.add_argument("--pct_local", type=float, required=True)
    btts.add_argument("--pct_visitante", type=float, required=True)
    btts.add_argument("--cuota", type=float, required=True)
    btts.add_argument("--baja_goleadores", action="store_true")
    btts.add_argument("--defensa_fuerte", action="store_true")

    # Subcomando: resultado 1X2
    res = subparsers.add_parser("resultado", help="Análisis 1X2")
    res.add_argument("--cuota_local", type=float, required=True)
    res.add_argument("--cuota_empate", type=float, required=True)
    res.add_argument("--cuota_visitante", type=float, required=True)

    # Subcomando: fixtures
    fixtures = subparsers.add_parser("fixtures", help="Listar próximos fixtures de una liga")
    fixtures.add_argument("--league_id", type=int, required=True)
    fixtures.add_argument("--season", type=int)

    # Subcomando: odds
    odds = subparsers.add_parser("odds", help="Mostrar cuotas para un fixture específico")
    odds.add_argument("--fixture_id", type=int, required=True)
    odds.add_argument("--bookmaker", type=str)

    args = parser.parse_args()

    if args.comando == "over":
        prob, ve = analizar_mas_de_2_5_goles(
            args.goles_local, args.goles_visitante,
            args.porcentaje_over25, args.cuota, args.bajas_ofensivas
        )
        print(f"Over 2.5: Probabilidad={prob*100:.1f}% | Valor Esperado={ve:.2f}")

    elif args.comando == "btts":
        prob, ve = analizar_btts(
            args.pct_local, args.pct_visitante,
            args.cuota, args.baja_goleadores, args.defensa_fuerte
        )
        print(f"BTTS: Probabilidad={prob*100:.1f}% | Valor Esperado={ve:.2f}")

    elif args.comando == "resultado":
        probs = calcular_probabilidades_desde_cuotas(
            args.cuota_local, args.cuota_empate, args.cuota_visitante
        )
        resultados = analizar_resultado_1x2(
            *probs,
            args.cuota_local, args.cuota_empate, args.cuota_visitante
        )
        for nombre, prob, cuota, ve in resultados:
            print(f"{nombre}: Prob={prob*100:.1f}% | Cuota={cuota} | VE={ve:.2f}")

    elif args.comando == "fixtures":
        fixtures_list = fetch_upcoming_fixtures(
            args.league_id, args.season
        )
        if not fixtures_list:
            print("No se encontraron fixtures.")
            sys.exit()
        for f in fixtures_list:
            fix = f.get("fixture", {})
            teams = f.get("teams", {})
            home = teams.get("home", {}).get("name")
            away = teams.get("away", {}).get("name")
            date = fix.get("date")
            fid = fix.get("id")
            print(f"{fid}: {home} vs {away} @ {date}")

    elif args.comando == "odds":
        odds_list = fetch_odds_for_fixture(
            args.fixture_id, args.bookmaker
        )
        if not odds_list:
            print("No se encontraron cuotas para el fixture.")
            sys.exit()
        for offer in odds_list:
            book = offer.get("bookmaker", {}).get("name")
            print(f"Bookmaker: {book}")
            for bet in offer.get("bets", []):
                if bet.get("name") in ["Match Winner", "1X2"]:
                    print(f"  Mercado: {bet.get('name')}")
                    for val in bet.get("values", []):
                        print(f"    {val.get('value')}: {val.get('odd')}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
