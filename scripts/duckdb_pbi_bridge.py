"""
DuckDB to Power BI Desktop Bridge Helper
----------------------------------------
Gir verifisering og standardiserte spørringer for å koble Power BI Desktop
opp mot den lokale DuckDB-analysedatabasen (uia_analytics.duckdb) via Python M-skript.

Forfatter: Frank Ellingsen (Project Controller)
"""

import sys
import duckdb
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "uia_analytics.duckdb"

def get_duckdb_connection(db_path: str = None, read_only: bool = True):
    path = db_path or str(DEFAULT_DB_PATH)
    return duckdb.connect(database=path, read_only=read_only)

def query_to_dataframe(sql: str, db_path: str = None) -> pd.DataFrame:
    """Kjører en SQL-spørring mot DuckDB og returnerer en pandas DataFrame."""
    con = get_duckdb_connection(db_path, read_only=True)
    try:
        return con.execute(sql).df()
    finally:
        con.close()

def get_available_views_and_tables(db_path: str = None) -> dict:
    """Lister alle tilgjengelige tabeller og visninger med radantall."""
    con = get_duckdb_connection(db_path, read_only=True)
    try:
        tables = con.execute("SHOW TABLES;").fetchall()
        result = {}
        for (table_name,) in tables:
            count = con.execute(f"SELECT COUNT(*) FROM {table_name};").fetchone()[0]
            result[table_name] = count
        return result
    finally:
        con.close()

def verify_bridge():
    """Validerer at databasen eksisterer og at nøkkelviews er klare for Power BI."""
    print("=" * 80)
    print("TESTER DUCKDB -> POWER BI DESKTOP PYTHON BRIDGE")
    print("=" * 80)
    
    if not DEFAULT_DB_PATH.exists():
        print(f"[FEIL] Fant ikke databasen: {DEFAULT_DB_PATH}")
        sys.exit(1)
        
    print(f"[OK] Databasefil funnet: {DEFAULT_DB_PATH}")
    print(f"[OK] DuckDB Versjon: {duckdb.__version__}")
    print(f"[OK] Pandas Versjon: {pd.__version__}\n")
    
    tables = get_available_views_and_tables()
    print(f"Fant {len(tables)} tabeller/visninger i uia_analytics.duckdb:")
    for name, cnt in sorted(tables.items()):
        prefix = "  [VIEW ]" if name.startswith("v_") else "  [TABLE]"
        print(f"{prefix} {name:<26}: {cnt:>6} rader")
        
    print("\n[TEST] Henter 3 rader fra v_avvik_budsjett_actual for Power BI test:")
    sample = query_to_dataframe("SELECT Fakultet, Kontonavn, Actual_YTD_MNOK, Budsjett_YTD_MNOK, Avvik_YTD_MNOK FROM v_avvik_budsjett_actual LIMIT 3")
    print(sample.to_string(index=False))
    
    print("\n" + "=" * 80)
    print("BRIDGE-VERIFISERING VELLYKKET: KLAR FOR BRUK I POWER BI DESKTOP")
    print("=" * 80)

if __name__ == "__main__":
    verify_bridge()
