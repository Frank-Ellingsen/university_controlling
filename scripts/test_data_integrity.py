"""
Automatisk integritets- og referansetest for UiA Controlling datasett.
Tester primær-/fremmednøkler, manglende verdier og matematiske formler (EVM).

Kjøres i CI/CD pipeline (GitHub Actions) eller lokalt med:
    python -m unittest scripts/test_data_integrity.py
"""

import unittest
import duckdb
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

class TestDataIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.con = duckdb.connect(database=":memory:")
        tables = [
            "DimAccountHierarchy", "DimDate", "DimForecastVersion",
            "DimOrganization", "FactBudget", "FactEVM", "FactFTE",
            "FactFacultyKPI", "FactGL", "FactStudents"
        ]
        for t in tables:
            csv_path = DATA_DIR / f"{t}.csv"
            cls.con.execute(f"CREATE TABLE {t} AS SELECT * FROM read_csv_auto('{csv_path.as_posix()}', delim=';', header=true);")

    def test_org_kode_referential_integrity(self):
        """Alle OrgKode i faktatabeller må finnes i DimOrganization."""
        facts = ["FactGL", "FactBudget", "FactFTE", "FactFacultyKPI", "FactStudents"]
        for f in facts:
            missing = self.con.execute(f"""
                SELECT DISTINCT f.OrgKode 
                FROM {f} f 
                LEFT JOIN DimOrganization o ON f.OrgKode = o.OrgKode 
                WHERE o.OrgKode IS NULL;
            """).fetchall()
            self.assertEqual(len(missing), 0, f"Ugyldig OrgKode funnet i {f}: {missing}")

    def test_dato_nokkel_referential_integrity(self):
        """Alle DatoNokkel i tidsbaserte faktatabeller må finnes i DimDate."""
        facts = ["FactGL", "FactBudget", "FactFTE", "FactEVM"]
        for f in facts:
            missing = self.con.execute(f"""
                SELECT DISTINCT f.DatoNokkel 
                FROM {f} f 
                LEFT JOIN DimDate d ON f.DatoNokkel = d.DatoNokkel 
                WHERE d.DatoNokkel IS NULL;
            """).fetchall()
            self.assertEqual(len(missing), 0, f"Ugyldig DatoNokkel funnet i {f}: {missing}")

    def test_account_referential_integrity(self):
        """Alle Konto i FactGL og FactBudget må finnes i DimAccountHierarchy."""
        for f in ["FactGL", "FactBudget"]:
            missing = self.con.execute(f"""
                SELECT DISTINCT f.Konto 
                FROM {f} f 
                LEFT JOIN DimAccountHierarchy a ON f.Konto = a.Konto 
                WHERE a.Konto IS NULL;
            """).fetchall()
            self.assertEqual(len(missing), 0, f"Ugyldig Konto funnet i {f}: {missing}")

    def test_versjon_kode_referential_integrity(self):
        """Alle VersjonKode i FactGL, FactBudget og FactFTE må finnes i DimForecastVersion."""
        for f in ["FactGL", "FactBudget", "FactFTE"]:
            missing = self.con.execute(f"""
                SELECT DISTINCT f.VersjonKode 
                FROM {f} f 
                LEFT JOIN DimForecastVersion v ON f.VersjonKode = v.VersjonKode 
                WHERE v.VersjonKode IS NULL;
            """).fetchall()
            self.assertEqual(len(missing), 0, f"Ugyldig VersjonKode funnet i {f}: {missing}")

    def test_evm_cpi_spi_consistency(self):
        """EVM-indekser CPI og SPI må tilsvare EV/AC og EV/PV."""
        rows = self.con.execute("""
            SELECT 
                DatoNokkel,
                Cost_Performance_Index_CPI,
                Earned_Value_EV_MNOK / Actual_Cost_AC_MNOK as calc_cpi,
                Schedule_Performance_Index_SPI,
                Earned_Value_EV_MNOK / Planned_Value_PV_MNOK as calc_spi
            FROM FactEVM;
        """).fetchall()
        for r in rows:
            dato, rep_cpi, calc_cpi, rep_spi, calc_spi = r
            self.assertAlmostEqual(rep_cpi, calc_cpi, places=2, msg=f"CPI mismatch i {dato}")
            self.assertAlmostEqual(rep_spi, calc_spi, places=2, msg=f"SPI mismatch i {dato}")

    def test_no_negative_fte(self):
        """Faktisk årsverk og budsjetterte årsverk kan ikke være negative."""
        neg = self.con.execute("""
            SELECT COUNT(*) 
            FROM FactFTE 
            WHERE Aarsverk_Faktisk < 0 OR Aarsverk_Budsjett < 0;
        """).fetchone()[0]
        self.assertEqual(neg, 0, "Funnet negative årsverk i FactFTE")

if __name__ == "__main__":
    unittest.main()
