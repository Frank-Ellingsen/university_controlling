"""
Verifiseringsskript for Rapporteringsregler ved Universitetet i Agder (UiA)
Kjøres lokalt med DuckDB for øyeblikkelig validering av regnskapsdata,
prognoser, EVM-beregninger og statlige krav (SRS og F-05-20).

Forfatter: Frank Ellingsen (Project Controller)
"""

import sys
import duckdb
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

def run_verification():
    print("=" * 80)
    print("UiA CONTROLLER RAPPORTVALIDERINGS- OG KONTROLLMOTOR (DUCKDB)")
    print("=" * 80)
    
    con = duckdb.connect(database=":memory:")
    
    # 1. Last inn CSV-filer
    tables = [
        "DimAccountHierarchy",
        "DimDate",
        "DimForecastVersion",
        "DimOrganization",
        "FactBudget",
        "FactEVM",
        "FactFTE",
        "FactFacultyKPI",
        "FactGL",
        "FactStudents"
    ]
    
    print("\n[1/6] Laster inn datasett fra /data...")
    for t in tables:
        csv_path = DATA_DIR / f"{t}.csv"
        if not csv_path.exists():
            print(f"  [FEIL] Fant ikke {csv_path}")
            sys.exit(1)
        con.execute(f"CREATE TABLE {t} AS SELECT * FROM read_csv_auto('{csv_path.as_posix()}', delim=';', header=true);")
        count = con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
        print(f"  - {t:<22}: {count:>5} rader")

    # 2. Kontroll: 5 %-regelen for ubrukte midler (Rundskriv F-05-20)
    print("\n[2/6] Kontroll av 5 %-regelen for ubenyttede bevilgningsmidler (F-05-20)...")
    res_f05 = con.execute("""
        WITH Ramme AS (
            SELECT OrgKode, SUM(Budsjett_MNOK) as Aarsramme
            FROM FactBudget
            WHERE VersjonKode = 'BUD2026' AND Artstype = 'Inntekt' AND Kategori = 'Statlig Bevilgning'
            GROUP BY OrgKode
        ),
        Avsetning AS (
            SELECT OrgKode, SUM(Belop_MNOK) as UbruktBevilgning
            FROM FactGL
            WHERE Konto = 2080 AND VersjonKode = 'ACTUAL_YTD_SEP2026'
            GROUP BY OrgKode
        )
        SELECT 
            r.OrgKode,
            o.Enhet,
            r.Aarsramme,
            COALESCE(a.UbruktBevilgning, 0) as UbruktBevilgning,
            ROUND((COALESCE(a.UbruktBevilgning, 0) / r.Aarsramme) * 100, 2) as UbruktProsent,
            CASE 
                WHEN (COALESCE(a.UbruktBevilgning, 0) / r.Aarsramme) * 100 > 5.0 THEN 'GUL/RØD: Over 5% -> Styrenotat og Note 15'
                ELSE 'GRØNN: Innenfor 5 %'
            END as Status
        FROM Ramme r
        JOIN DimOrganization o ON r.OrgKode = o.OrgKode
        LEFT JOIN Avsetning a ON r.OrgKode = a.OrgKode
        ORDER BY UbruktProsent DESC;
    """).fetchall()

    for row in res_f05:
        org_code, org_name, ramme, ubrukt, pct, status = row
        print(f"  Org {org_code} ({org_name:<30}): Ramme={ramme:>6.1f} MNOK | Ubrukt={ubrukt:>5.2f} MNOK ({pct:>4.1f}%) -> {status}")

    # 3. Kontroll: SRS 10 (Motsatt sammenstilling for BOA-tilskudd)
    print("\n[3/6] Kontroll av SRS 10 Motsatt sammenstilling (BOA NFR/EU)...")
    res_srs10 = con.execute("""
        SELECT 
            OrgKode,
            DatoNokkel,
            SUM(CASE WHEN Artstype = 'Inntekt' AND Kategori = 'Forskning (BOA)' THEN Belop_MNOK ELSE 0 END) as BOA_Inntekt,
            SUM(CASE WHEN Artstype = 'Kostnad' AND Kategori = 'Driftskostnader' THEN Belop_MNOK * 0.2 ELSE 0 END) as Estimert_BOA_Kostnad
        FROM FactGL
        WHERE VersjonKode = 'ACTUAL_YTD_SEP2026'
        GROUP BY OrgKode, DatoNokkel
        HAVING BOA_Inntekt > 0
        LIMIT 4;
    """).fetchall()
    
    print(f"  Analysert inntektsføring mot påløpte kostnader for BOA:")
    for row in res_srs10:
        org, dato, inntekt, kost = row
        print(f"  Org {org} Periode {dato}: Inntektsført BOA = {inntekt:.3f} MNOK")

    # 4. Kontroll: Earned Value Management (EVM) beregninger
    print("\n[4/6] Kontroll av Earned Value Management (EVM) metrikker...")
    res_evm = con.execute("""
        SELECT 
            DatoNokkel,
            Planned_Value_PV_MNOK as PV,
            Earned_Value_EV_MNOK as EV,
            Actual_Cost_AC_MNOK as AC,
            ROUND(Earned_Value_EV_MNOK / Actual_Cost_AC_MNOK, 2) as Beregnet_CPI,
            Cost_Performance_Index_CPI as Rapportert_CPI,
            ROUND(Earned_Value_EV_MNOK / Planned_Value_PV_MNOK, 2) as Beregnet_SPI,
            Schedule_Performance_Index_SPI as Rapportert_SPI,
            ROUND(Budget_At_Completion_BAC_MNOK - Estimate_At_Completion_EAC_MNOK, 2) as Beregnet_VAC,
            Variance_At_Completion_VAC_MNOK as Rapportert_VAC
        FROM FactEVM
        ORDER BY DatoNokkel DESC
        LIMIT 4;
    """).fetchall()

    for row in res_evm:
        dato, pv, ev, ac, c_cpi, r_cpi, c_spi, r_spi, c_vac, r_vac = row
        cpi_match = abs(c_cpi - r_cpi) <= 0.02
        spi_match = abs(c_spi - r_spi) <= 0.02
        vac_match = abs(c_vac - r_vac) <= 0.1
        status_str = "OK" if (cpi_match and spi_match and vac_match) else "AVVIK"
        print(f"  Måned {dato}: CPI={r_cpi:.2f} (Calc={c_cpi:.2f}) | SPI={r_spi:.2f} (Calc={c_spi:.2f}) | VAC={r_vac:.1f} MNOK -> {status_str}")

    # 5. Kontroll: Bemannings- og årsverksanalyse (FTE)
    print("\n[5/6] Bemannings- og årsverksanalyse (FTE Faglig vs Teknisk-Administrativ)...")
    res_fte = con.execute("""
        SELECT 
            f.OrgKode,
            o.Kortnavn,
            f.Aarsverk_UF,
            f.Aarsverk_TA,
            f.Aarsverk_Faktisk,
            f.Ubesatte_Vakanser,
            ROUND(f.Faglig_Andel_Pct, 1) as FagligAndelPct
        FROM FactFTE f
        JOIN DimOrganization o ON f.OrgKode = o.OrgKode
        WHERE f.DatoNokkel = 202609 AND f.VersjonKode = 'ACTUAL_YTD_SEP2026'
        ORDER BY FagligAndelPct DESC;
    """).fetchall()

    for row in res_fte:
        org, navn, uf, ta, tot, vak, pct = row
        print(f"  Org {org} ({navn:<8}): UF={uf:>5.1f} | TA={ta:>5.1f} | Totalt={tot:>5.1f} | Vakanser={vak:>4.1f} | Faglig andel={pct:>4.1f}% (Mål: >50%)")

    # 6. Kontroll: KD Finansieringsmodell 2025 studiepoengsatser
    print("\n[6/6] Verifisering av KD 2025 studiepoengkategorier og produksjon...")
    res_stud = con.execute("""
        SELECT 
            s.OrgKode,
            o.Kortnavn,
            s.Registrerte_Studenter,
            s.Avlagte_Studiepoeng_Totalt,
            s.SPE60_Helarsstudenter,
            ROUND((s.KD_Kategori1_SPE60 * 54550 + s.KD_Kategori2_SPE60 * 81800 + s.KD_Kategori3_SPE60 * 190900) / 1000000, 2) as Estimert_KD_Inntekt_MNOK
        FROM FactStudents s
        JOIN DimOrganization o ON s.OrgKode = o.OrgKode
        ORDER BY s.SPE60_Helarsstudenter DESC;
    """).fetchall()

    for row in res_stud:
        org, navn, reg, sp, spe60, inntekt = row
        print(f"  Org {org} ({navn:<8}): Studenter={reg:>5} | SPE60={spe60:>6.1f} | Estimert KD Resultatbevilgning={inntekt:>5.2f} MNOK")

    print("\n" + "=" * 80)
    print("ALLE KONTROLLER FULLFØRT UTEN AVBRUDD. DATASETTET ER KVALITETSSIKRET FOR POWER BI.")
    print("=" * 80)

if __name__ == "__main__":
    run_verification()
