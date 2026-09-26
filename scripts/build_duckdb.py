"""
Bygger lokal analytisk database (DuckDB) for UiA Controlling.
Leser alle CSV-filer fra data/ og oppretter relasjonstabeller samt
optimaliserte analytiske visninger (views) for rask ad-hoc analyse og BI-støtte.

Forfatter: Frank Ellingsen (Project Controller)
"""

import sys
import duckdb
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_FILE = BASE_DIR / "uia_analytics.duckdb"

def build_database():
    print("=" * 80)
    print(f"BYGGER ANALYTISK DUCKDB DATABASE: {DB_FILE.name}")
    print("=" * 80)
    
    con = duckdb.connect(database=str(DB_FILE))
    
    # 1. Tabelliste
    csv_tables = {
        "DimAccountHierarchy": "DimAccountHierarchy.csv",
        "DimDate": "DimDate.csv",
        "DimForecastVersion": "DimForecastVersion.csv",
        "DimOrganization": "DimOrganization.csv",
        "DimKPI": "DimKPI.csv",
        "FactBudget": "FactBudget.csv",
        "FactEVM": "FactEVM.csv",
        "FactFTE": "FactFTE.csv",
        "FactFacultyKPI": "FactFacultyKPI.csv",
        "FactGL": "FactGL.csv",
        "FactStudents": "FactStudents.csv"
    }
    
    print("\n[1/3] Importerer CSV-filer til basistabeller...")
    for table_name, file_name in csv_tables.items():
        csv_path = DATA_DIR / file_name
        if not csv_path.exists():
            print(f"  [FEIL] Fant ikke {csv_path}")
            continue
        
        con.execute(f"DROP TABLE IF EXISTS {table_name};")
        con.execute(f"""
            CREATE TABLE {table_name} AS 
            SELECT * FROM read_csv_auto('{csv_path.as_posix()}', delim=';', header=true);
        """)
        row_count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"  - {table_name:<22}: {row_count:>5} rader importert")

    # 2. Opprett analytiske visninger (views)
    print("\n[2/3] Oppretter analytiske visninger (Views)...")

    # View 1: v_ytd_regnskap
    con.execute("""
        CREATE OR REPLACE VIEW v_ytd_regnskap AS
        SELECT 
            g.DatoNokkel,
            d.Dato,
            d.MaanedNavn,
            d.Kvartal,
            g.OrgKode,
            o.Enhet,
            o.Kortnavn as FakultetKort,
            g.Konto,
            g.Kontonavn,
            a.Nivaa1_Navn as Kontoklasse,
            a.Nivaa2_Navn as Kontogruppe,
            a.SRS_regnskapslinje,
            g.Artstype,
            g.Kategori,
            g.Belop_MNOK,
            g.Belop_signert_MNOK,
            g.VersjonKode
        FROM FactGL g
        LEFT JOIN DimOrganization o ON g.OrgKode = o.OrgKode
        LEFT JOIN DimAccountHierarchy a ON g.Konto = a.Konto
        LEFT JOIN DimDate d ON g.DatoNokkel = d.DatoNokkel;
    """)
    print("  - v_ytd_regnskap opprettet")

    # View 2: v_avvik_budsjett_actual
    con.execute("""
        CREATE OR REPLACE VIEW v_avvik_budsjett_actual AS
        WITH Actuals AS (
            SELECT 
                OrgKode,
                Konto,
                SUM(Belop_signert_MNOK) as Actual_Signert_MNOK
            FROM FactGL
            WHERE VersjonKode = 'ACTUAL_YTD_SEP2026'
            GROUP BY OrgKode, Konto
        ),
        Budget AS (
            SELECT 
                b.OrgKode,
                b.Konto,
                SUM(b.Budsjett_signert_MNOK) as Budsjett_YTD_Signert_MNOK
            FROM FactBudget b
            JOIN DimDate d ON b.DatoNokkel = d.DatoNokkel
            WHERE d.StatusPr30Sep = 'Actual'
            GROUP BY b.OrgKode, b.Konto
        )
        SELECT 
            COALESCE(a.OrgKode, b.OrgKode) as OrgKode,
            o.Enhet,
            o.Kortnavn as Fakultet,
            COALESCE(a.Konto, b.Konto) as Konto,
            acc.Kontonavn,
            acc.Nivaa1_Navn as Kontoklasse,
            ROUND(COALESCE(a.Actual_Signert_MNOK, 0), 3) as Actual_YTD_MNOK,
            ROUND(COALESCE(b.Budsjett_YTD_Signert_MNOK, 0), 3) as Budsjett_YTD_MNOK,
            ROUND(COALESCE(a.Actual_Signert_MNOK, 0) - COALESCE(b.Budsjett_YTD_Signert_MNOK, 0), 3) as Avvik_YTD_MNOK,
            CASE 
                WHEN COALESCE(b.Budsjett_YTD_Signert_MNOK, 0) != 0 
                THEN ROUND(((COALESCE(a.Actual_Signert_MNOK, 0) - COALESCE(b.Budsjett_YTD_Signert_MNOK, 0)) / ABS(b.Budsjett_YTD_Signert_MNOK)) * 100, 2)
                ELSE 0 
            END as Avvik_YTD_Pct
        FROM Actuals a
        FULL OUTER JOIN Budget b ON a.OrgKode = b.OrgKode AND a.Konto = b.Konto
        LEFT JOIN DimOrganization o ON COALESCE(a.OrgKode, b.OrgKode) = o.OrgKode
        LEFT JOIN DimAccountHierarchy acc ON COALESCE(a.Konto, b.Konto) = acc.Konto;
    """)
    print("  - v_avvik_budsjett_actual opprettet")

    # View 3: v_evm_sammendrag
    con.execute("""
        CREATE OR REPLACE VIEW v_evm_sammendrag AS
        SELECT 
            e.DatoNokkel,
            d.MaanedNavn,
            d.Kvartal,
            e.OrgKode,
            o.Kortnavn as Enhet,
            e.Planned_Value_PV_MNOK as PV,
            e.Earned_Value_EV_MNOK as EV,
            e.Actual_Cost_AC_MNOK as AC,
            e.Budget_At_Completion_BAC_MNOK as BAC,
            e.Estimate_At_Completion_EAC_MNOK as EAC,
            e.Estimate_To_Complete_ETC_MNOK as ETC,
            e.Cost_Performance_Index_CPI as CPI,
            e.Schedule_Performance_Index_SPI as SPI,
            e.Variance_At_Completion_VAC_MNOK as VAC,
            ROUND(e.Earned_Value_EV_MNOK - e.Actual_Cost_AC_MNOK, 2) as Cost_Variance_CV,
            ROUND(e.Earned_Value_EV_MNOK - e.Planned_Value_PV_MNOK, 2) as Schedule_Variance_SV
        FROM FactEVM e
        LEFT JOIN DimOrganization o ON e.OrgKode = o.OrgKode
        LEFT JOIN DimDate d ON e.DatoNokkel = d.DatoNokkel;
    """)
    print("  - v_evm_sammendrag opprettet")

    # 3. Kjøre en testspørring
    print("\n[3/3] Kjører sjekkspørring på opprettede visninger...")
    sample = con.execute("""
        SELECT 
            Fakultet, 
            ROUND(SUM(Actual_YTD_MNOK), 2) as Actual_Netto_MNOK, 
            ROUND(SUM(Budsjett_YTD_MNOK), 2) as Budsjett_Netto_MNOK,
            ROUND(SUM(Avvik_YTD_MNOK), 2) as Avvik_Netto_MNOK
        FROM v_avvik_budsjett_actual
        GROUP BY Fakultet
        ORDER BY Fakultet;
    """).fetchall()
    
    for row in sample:
        fak, act, bud, avv = row
        print(f"  {fak:<8}: Actual={act:>7.2f} MNOK | Budsjett={bud:>7.2f} MNOK | Avvik={avv:>7.2f} MNOK")
        
    con.close()
    print("\n" + "=" * 80)
    print(f"DATABASE BYGGET VELLYKKET: {DB_FILE.name}")
    print("=" * 80)

if __name__ == "__main__":
    build_database()
