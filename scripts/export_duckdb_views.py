"""
Export analytical views from uia_analytics.duckdb to CSV files in data/
This allows Power BI Desktop to load without requiring Python.Execute
or Native Database Query security permissions.
"""
import os
import duckdb

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "uia_analytics.duckdb")
DATA_DIR = os.path.join(BASE_DIR, "data")

VIEWS = {
    "DuckDB_v_avvik_budsjett_actual.csv": "v_avvik_budsjett_actual",
    "DuckDB_v_evm_sammendrag.csv": "v_evm_sammendrag",
    "DuckDB_v_ytd_regnskap.csv": "v_ytd_regnskap"
}

def export_views():
    if not os.path.exists(DB_PATH):
        print(f"Error: DuckDB database not found at {DB_PATH}")
        return

    con = duckdb.connect(DB_PATH, read_only=True)
    for csv_name, view in VIEWS.items():
        csv_path = os.path.join(DATA_DIR, csv_name)
        df = con.execute(f"SELECT * FROM {view}").df()
        df.to_csv(csv_path, sep=";", index=False, encoding="utf-8")
        print(f"[OK] Exported {csv_name}: {len(df)} rows, {len(df.columns)} columns")
    con.close()
    print("All DuckDB analytical views successfully exported to data/")

if __name__ == "__main__":
    export_views()
