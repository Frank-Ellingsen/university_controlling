# Veileder: Koble Power BI Desktop til DuckDB («The DuckDB Bridge»)

Denne veilederen beskriver hvordan du etablerer en direkte tilkobling (**bro**) mellom **Power BI Desktop** og den lokale analytiske databasen **DuckDB** (`university_analytics.duckdb`) på denne maskinen.

---

## 1. Arkitektur & Fordeler for Project Controlling

```
+------------------------------------------+
|  data/*.csv (Transaksjoner & Budsjett)   |
+------------------------------------------+
                     |  (scripts/build_duckdb.py)
                     v
+------------------------------------------+
|      DuckDB (university_analytics.duckdb)       |
|  - Kolonneorientert OLAP-motor (C++)     |
|  - Analytiske views (Avvik, EVM, SRS)   |
+------------------------------------------+
                     |
                     |  Python / DuckDB Connector
                     v
+------------------------------------------+
|        Power Query (M Engine)            |
|  - DuckDBDatabasePath parameter          |
|  - fnDuckDBQuery() funksjon              |
+------------------------------------------+
                     |
                     v
+------------------------------------------+
|    Power BI Desktop (VertiPaq Engine)    |
|  - Interaktive Tufte-dashboards          |
|  - Rask ad-hoc slicing & DAX             |
+------------------------------------------+
```

### Hvorfor bruke DuckDB-broen fremfor rå CSV?
1. **Lynhurtig forhåndsbehandling**: DuckDB kjører komplekse koblinger (joins), vindusfunksjoner og avstemminger i minnet på under 10 millisekunder.
2. **Én sannhetskilde (Single Source of Truth)**: Logikken for budsjettavvik, EVM og kontohierarki defineres én gang i DuckDB SQL-views og deles sømløst mellom Python-skript, tester og Power BI.
3. **Mindre minnebruk i Power BI**: I stedet for å laste 10 separate råtabeller og gjøre tunge Power Query merges, importeres ferdig berikede analytiske tabeller.

---

## 2. Forutsetninger på denne maskinen

Alt er allerede installert og verifisert på maskinen:
* **Python**: 3.12 (med `duckdb==1.5.3` og `pandas==3.0.3`).
* **Database**: `C:\Users\frank\Desktop\UIA2\university_analytics.duckdb`.
* **Verifiseringsskript**: [scripts/duckdb_pbi_bridge.py](file:///c:/Users/frank/Desktop/UIA2/scripts/duckdb_pbi_bridge.py).

Kjør verifiseringen i terminalen når som helst:
```bash
python scripts/duckdb_pbi_bridge.py
```

---

## 3. Engangsoppsett i Power BI Desktop

For at Power Query skal kunne kjøre DuckDB-broen:

1. Åpne **Power BI Desktop**.
2. Gå til **File (Fil) > Options and settings (Alternativer og innstillinger) > Options (Alternativer)**.
3. I venstremenyen under *Global*, velg **Python scripting (Python-skripting)**.
4. Sjekk at **Detected Python home directory** er satt til din aktive Python-installasjon (f.eks. `Python312` eller WindowsApps).
5. Klikk **OK**.

---

## 4. Metode 1: Hente data via «Get Data > Python script» (GUI)

Dette er den raskeste måten for ad-hoc analyse:

1. I Power BI Desktop, klikk **Get Data (Hent data) > More... > Other > Python script > Connect**.
2. Lim inn følgende skript i dialogboksen:
   ```python
   import duckdb
   
   db_path = r"C:\Users\frank\Desktop\UIA2\university_analytics.duckdb"
   con = duckdb.connect(db_path, read_only=True)
   
   # Henter de 3 viktigste analytiske visningene
   v_avvik_budsjett_actual = con.execute("SELECT * FROM v_avvik_budsjett_actual").df()
   v_evm_sammendrag        = con.execute("SELECT * FROM v_evm_sammendrag").df()
   v_ytd_regnskap          = con.execute("SELECT * FROM v_ytd_regnskap").df()
   
   con.close()
   ```
3. Klikk **OK**.
4. I **Navigator**-vinduet markerer du tabellene du vil laste inn og klikker **Load** eller **Transform Data**.

---

## 5. Metode 2: Standardisert Power Query M-modul (Anbefalt)

I mappen `powerbi/powerquery/` finner du den komplette M-koden: [duckdb_bridge.m](file:///c:/Users/frank/Desktop/UIA2/powerbi/powerquery/duckdb_bridge.m).

### Slik legger du til en ferdig visning i Power Query:
1. I Power BI Desktop, klikk **Transform Data** for å åpne Power Query Editor.
2. Høyreklikk i spørringspanelet til venstre $\rightarrow$ **New Query > Blank Query**.
3. Klikk **Advanced Editor (Avansert redigering)** på båndet.
4. Erstatt innholdet med M-koden for ønsket spørring fra `duckdb_bridge.m`:

#### Eksempel: Budsjettavvik per Fakultet
```m
let
    DuckDBPath = "C:\Users\frank\Desktop\UIA2\university_analytics.duckdb",
    Source = Python.Execute(
        "import duckdb#(lf)" & 
        "con = duckdb.connect(r'" & DuckDBPath & "', read_only=True)#(lf)" & 
        "df = con.execute('SELECT * FROM v_avvik_budsjett_actual').df()#(lf)" & 
        "con.close()"
    ),
    df_Table = Source{[Name="df"]}[Value],
    #"Changed Type" = Table.TransformColumnTypes(df_Table,{
        {"OrgKode", Int64.Type}, 
        {"Enhet", type text}, 
        {"Fakultet", type text}, 
        {"Konto", Int64.Type}, 
        {"Kontonavn", type text}, 
        {"Kontoklasse", type text}, 
        {"Actual_YTD_MNOK", type number}, 
        {"Budsjett_YTD_MNOK", type number}, 
        {"Avvik_YTD_MNOK", type number}, 
        {"Avvik_YTD_Pct", type number}
    })
in
    #"Changed Type"
```

5. Gi spørringen navnet **DuckDB_AvvikBudsjettActual** og klikk **Close & Apply**.

---

## 6. Tilgjengelige visninger i DuckDB

| Visning / Tabell | Formål for Controlleren | Nøkkelfelter |
| :--- | :--- | :--- |
| **`v_avvik_budsjett_actual`** | Sluttavvik YTD per fakultet og kontoklasse | `OrgKode`, `Fakultet`, `Actual_YTD_MNOK`, `Budsjett_YTD_MNOK`, `Avvik_YTD_MNOK`, `Avvik_YTD_Pct` |
| **`v_evm_sammendrag`** | Portefølje- og prosjektstyring etter EVM | `DatoNokkel`, `PV`, `EV`, `AC`, `BAC`, `EAC`, `ETC`, `CPI`, `SPI`, `VAC`, `CV`, `SV` |
| **`v_ytd_regnskap`** | Detaljert transaksjonsnivå beriket med SRS-linjer | `DatoNokkel`, `OrgKode`, `FakultetKort`, `Konto`, `Kontonavn`, `SRS_regnskapslinje`, `Belop_MNOK` |

---

## 7. Feilsøking & Tips

* **Native Query Warning (Datasikkerhet)**:
  Første gang du kjører et Python-skript i Power BI, kan du få et sikkerhetsvarsel: *"Run script"*. Klikk **Run**.
* **Formula.Firewall (Data Privacy Levels)**:
  Dersom du kombinerer lokale CSV-filer og DuckDB Python-spørringer, kan Power BI vise et personvernvarsel. Løsning: Gå til **File > Options > Current File > Privacy** og sett til **Ignore the Privacy levels and potentially improve performance** for den lokale utviklingsfilen.
* **Oppdatering av data**:
  Når du kjører `python scripts/build_duckdb.py` for å oppdatere databasen med nye månedsfiler, trykker du bare **Refresh** i Power BI Desktop – så oppdateres alle visninger umiddelbart.
