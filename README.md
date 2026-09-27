# University – Prosjekt- og Virksomhetscontrolling 2026 YTD

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue?logo=python)](https://www.python.org/)
[![DuckDB](https://img.shields.io/badge/DuckDB-1.5.3-yellow?logo=duckdb)](https://duckdb.org/)
[![Power BI](https://img.shields.io/badge/Power%20BI-PBIP%20Developer%20Mode-F2C811?logo=powerbi)](https://powerbi.microsoft.com/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)](https://www.docker.com/)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-brightgreen?logo=githubactions)](.github/workflows/ci.yml)
[![Design](https://img.shields.io/badge/Standard-Edward%20Tufte%20Data--Ink-darkgreen)](docs/reporting_standard_tufte.md)

---

## 1. Prosjektoversikt

Dette repositoriet samler og standardiserer controlling, virksomhetsstyring og prosjektøkonomi for **University** for regnskapsåret 2026 YTD (per 30. september 2026).

Prosjektet er bygget med moderne, versjonskontrollert BI-arkitektur (**Power BI Project - PBIP**) i kombinasjon med **DuckDB** for lokal-først dataanalyse, containerisert kjøremiljø (**Docker / DevContainer**), og helautomatisert kvalitetssikring i **GitHub Actions**.

### Sentrale Forretningsområder & Regelverk
* **Statlige Regnskapsstandarder (SRS)**: Praktisk etterlevelse av SRS 1 (virksomhetsregnskap), SRS 9 (oppdragsaktivitet & tapskontrakter), SRS 10 (bidragsaktivitet med motsatt sammenstilling) og SRS 17 (aktivering og avskrivning av anleggsmidler).
* **KD Finansieringsmodell 2025**: Beregning av åpen resultatramme for studiepoeng (SPE60) fordelt på 3 nye satser (Kategori 1: 54 550 NOK, Kategori 2: 81 800 NOK, Kategori 3: 190 900 NOK), under hensyn til marginalitetsprinsippet.
* **5 %-regelen for Ubrukte Midler (Rundskriv F-05-20)**: Automatisk avsetningskontroll på konto 2080 opp mot årlig rammetildeling for å sikre rettidig tiltaksplanlegging for styret og Note 15.
* **BOA Prosjektcontrolling & TDI-kalkyle**: Oppfølging av Bidrags- og Oppdragsfinansiert Aktivitet etter Total Dekning av Inntekter (Tid, Direkte kostnader, Indirekte kostnader/overhead).
* **Earned Value Management (EVM)**: Portefølje- og prosjektstyring med måling av fremdrift og kostnadseffektivitet ($PV, EV, AC, CPI, SPI, EAC, ETC, VAC$).
* **Edward Tufte Data-Ink Ratio**: Minimalistisk visualisering uten unødig grafisk støy for maksimal beslutningsstøtte.

---

## 2. Katalogstruktur (Repository Architecture)

```
c:\Users\frank\Desktop\UIA2\
│
├── .devcontainer/                       # VS Code Dev Containers konfigurasjon
│   └── devcontainer.json
│
├── .github/                             # GitHub Actions CI/CD workflows
│   └── workflows/
│       └── ci.yml                       # Automatisk testsuite, DuckDB-validering & PBIP-sjekk
│
├── .env.example                         # Mal for miljøvariabler (Gemini, OpenAI, Claude, Ollama)
├── .gitattributes                       # Git linjeskiftnormalisering & PBIP TMDL/JSON-regler
├── .gitignore                           # Ekskluderer PBI-cache, DuckDB, venv, secrets og OS-støy
├── .dockerignore                         # Bygg-ekskluderinger for Docker
├── Dockerfile                           # Container med Python 3.12, DuckDB, Pandas og Pytest
├── docker-compose.yml                   # Orkestrering med bind-mounts og Ollama-integrasjon
│
├── University-project-2026YTD.pbip             # Power BI Project (dobbeltklikk for å åpne i Desktop)
├── University-project-2026YTD.Report/          # Rapportdefinisjon (visuals, sider, tema)
├── University-project-2026YTD.SemanticModel/   # Semantisk modell i TMDL-format (Fabric Git-kompatibel)
│
├── data/                                # Rensede semikolondelilte CSV-datasett for BI & SQL
│   ├── DimAccountHierarchy.csv          # Kontoplanhierarki (Nivå 1-4, SRS-regnskapslinjer)
│   ├── DimDate.csv                      # Datotabell (Måned, Kvartal, Status Actual vs Forecast)
│   ├── DimForecastVersion.csv           # Versjonsstyring (BUD2026, ACTUAL_YTD_SEP2026, FC_Q4_2026)
│   ├── DimOrganization.csv             # Organisasjonsstruktur (Fakulteter og fellestjenester)
│   ├── FactBudget.csv                   # Vedtatt årsbudsjett 2026
│   ├── FactEVM.csv                      # Earned Value Management tidsserier
│   ├── FactFTE.csv                      # Bemanningsdata og årsverk (UF vs TA, vakanser)
│   ├── FactFacultyKPI.csv               # Aggregerte nøkkeltall per fakultet
│   ├── FactGL.csv                       # Hovedbokstransaksjoner YTD og estimert Q4
│   ├── FactStudents.csv                 # Studenttall, SPE60 og KD-kategorier
│   ├── Relationships.csv                # Dokumentasjon av relasjoner og kardinalitet
│   └── raw/
│       └── standard-kontoplan-2025...   # Offisielt Finansdepartementets vedlegg R-102 (Excel)
│
├── powerbi/                             # Power BI utviklingsressurser
│   ├── dax/
│   │   ├── measures.dax                 # 25 ferdigformulerte DAX-måltall fordelt på mapper
│   │   └── dax_guide.md                 # Detaljert måltallsbeskrivelse og implementasjonssteg
│   ├── powerquery/
│   │   ├── import_all_tables.m          # Power Query M-skript med dynamisk DataFolder-parameter
│   │   ├── duckdb_bridge.m              # Power Query M DuckDB-bro for direkte SQL-spørringer
│   │   └── Account_Hierarchy_PowerBI.md # Veileder for denormalisering av kontoplanhierarki
│   ├── themes/
│   │   └── tufte_minimalist_theme.json  # Eget Edward Tufte minimalist-tema for Power BI
│   └── archive/
│       └── University-rapport-2026YTD.pbix     # Sikkerhetskopiert opprinnelig PBIX
│
├── references/                          # Faglige veiledere, regelverk og pensum (jf. overall.md)
│   ├── veileder_kontroll_og_rapportering_university.md
│   ├── kd_finansieringsmodell_2025.md
│   ├── statlige_regnskapsstandarder_srs.md
│   ├── boa_tdi_modell.md
│   ├── femprosent_regelen_og_note15.md
│   ├── controller_kompetansekart.md
│   ├── university-2026-mocup-nøkkeltall.md
│   ├── university_styrenotat.md
│   ├── rapp_akk.md
│   ├── curriculum/                      # Læreplaner og ordliste for controller-opplæring
│   └── pdf/                             # Offisielle PDF-kilder (Årsrapport, SRS-notater, Kontoplan)
│
├── docs/                                # Prosjektdokumentasjon og arkitektur
│   ├── architecture/                    # Flytdiagrammer og use-case beskrivelser
│   ├── duckdb_powerbi_bridge_guide.md   # Veileder for Power BI Desktop -> DuckDB Bridge
│   └── reporting_standard_tufte.md      # Edward Tufte Data-Ink standard for styre- og ledermøter
│
├── scripts/                             # Python-automatisering og DuckDB analyse
│   ├── verify_reporting_rules.py        # Kjører kontroller for 5%-regel, SRS, EVM og KD-modell
│   ├── build_duckdb.py                  # Bygger lokal database university_analytics.duckdb med visninger
│   ├── duckdb_pbi_bridge.py             # Validerings- og spørrehjelper for Power BI DuckDB-bro
│   └── test_data_integrity.py           # Pytest/Unittest-suite for fremmednøkler og datakvalitet
│
├── overall.md                           # Overordnet faglig rammeverk og kompetanseveileder
└── README.md                            # Hoveddokumentasjon for repositoriet
```

---

## 3. Komme i Gang med Power BI Project (`University-project-2026YTD.pbip`)

Power BI Desktop støtter nå Git-integrert utviklermodus via filformatet `.pbip`. Dette muliggjør ren tekstbasert versjonskontroll (TMDL og JSON) uten binære flettestridigheter.

### 3.1 Åpne prosjektet
1. Dobbeltklikk på [`University-project-2026YTD.pbip`](./University-project-2026YTD.pbip) direkte i prosjektets rotmappe.
2. Power BI Desktop vil åpne rapporten og laste inn den semantiske modellen fra undermappene:
   * `University-project-2026YTD.Report/`
   * `University-project-2026YTD.SemanticModel/`

### 3.2 Importere data via Power Query
Hvis tabellene skal oppdateres fra CSV-filene:
1. I Power BI Desktop, klikk på **Transform Data** (Power Query).
2. Opprett parameteren `DataFolder` og pek den til `...\data\` (se ferdig M-kode i [`powerbi/powerquery/import_all_tables.m`](powerbi/powerquery/import_all_tables.m)).
3. Last inn tabellene med korrekte datatyper.

### 3.3 Opprette DAX-måltall
1. Opprett en måltallstabell `_Measures` (Home > Enter Data).
2. Kopier inn måltallene fra [`powerbi/dax/measures.dax`](powerbi/dax/measures.dax). Måltallene er organisert i logiske visningsmapper:
   * `_01 Regnskap & YTD`
   * `_02 Prognose & EAC`
   * `_03 EVM`
   * `_04 Bemanning & FTE`
   * `_05 Utdanning`
   * `_06 RAG & Design`

### 3.4 Aktivere Edward Tufte-temaet
1. Gå til **View > Themes > Browse for themes**.
2. Velg [`powerbi/themes/tufte_minimalist_theme.json`](powerbi/themes/tufte_minimalist_theme.json).
3. Rapporten oppdateres med nøytrale farger, ingen skygger, ingen vertikale tabellinjer og selektiv RAG-fargeheving.

---

## 4. Lokal Analyse med DuckDB og Python

For rask datautforsking og automatisert regnskapskontroll uten behov for å starte Power BI:

### 4.1 Kjør forretningsregelvalidering
```bash
python scripts/verify_reporting_rules.py
```
Dette skriptet verifiserer:
1. Innlasting av alle faktatabeller og dimensjoner.
2. 5 %-regelen for ubenyttede bevilgningsmidler (F-05-20) per organisasjonsenhet.
3. SRS 10 motsatt sammenstilling for BOA/tilskuddsinntekter.
4. EVM-beregninger ($CPI, SPI, VAC$).
5. Bemanningsfordeling (UF vs. TA årsverk, mål > 50 % faglig).
6. KD 2025 studiepoengberegninger etter nye satser.

### 4.2 Bygg lokal analytisk database
```bash
python scripts/build_duckdb.py
```
Oppretter databasen `university_analytics.duckdb` med tre ferdige analytiske visninger:
* `v_ytd_regnskap`: Komplett transaksjonsbilde koblet mot dimensjoner.
* `v_avvik_budsjett_actual`: Automatisk avviksberegning i MNOK og prosent.
* `v_evm_sammendrag`: Månedlig EVM-oversikt med kostnads- og tidsavvik.

### 4.3 Kjør dataintegritetstester
```bash
python -m unittest scripts/test_data_integrity.py
```

### 4.4 Koble Power BI Desktop til DuckDB (The DuckDB Bridge)
For å utnytte DuckDBs lynraske OLAP-beregninger direkte i Power BI Desktop uten å gå via CSV-filer:
1. **Verifiser tilkoblingen**:
   ```bash
   python scripts/duckdb_pbi_bridge.py
   ```
2. **Bruk Power Query M-modulen**:
   * Åpne [`powerbi/powerquery/duckdb_bridge.m`](powerbi/powerquery/duckdb_bridge.m) for ferdig M-kode.
   * Se komplett oppsettveileder i [`docs/duckdb_powerbi_bridge_guide.md`](docs/duckdb_powerbi_bridge_guide.md).
   * Importer ferdige visninger som `v_avvik_budsjett_actual`, `v_evm_sammendrag` og `v_ytd_regnskap` direkte inn i modellen via Power BI Python Scripting.

---

## 5. Containerisering (Docker & DevContainer)

### 5.1 Kjøre med Docker Compose
Prosjektet inneholder full containerisering med støtte for tilkobling til lokal **Ollama** eller **LM Studio** på vertsmaskinen:

```bash
# Bygg og kjør validering
docker compose up --build

# Kjør interaktivt skall for utvikling
docker compose run --rm controller-shell
```

### 5.2 Utvikling i VS Code Dev Container
1. Installer utvidelsen **Dev Containers** i VS Code.
2. Trykk `Ctrl+Shift+P` (eller `F1`) og velg:
   `Dev Containers: Reopen in Container`
3. Miljøet settes opp automatisk med Python 3.12, DuckDB, testverktøy og anbefalte utvidelser.

---

## 6. GitHub CI/CD Pipeline

Filen [`.github/workflows/ci.yml`](.github/workflows/ci.yml) kjører automatiske kvalitetssjekker ved hver `push` og `pull_request`:
* **Matrix-testing**: Validerer mot Python 3.11 og 3.12.
* **Dataintegritet**: Kjører referansesjekker på alle fremmednøkler mellom fakta- og dimensjonstabeller.
* **Forretningslogikk**: Kjører `verify_reporting_rules.py`.
* **Databasebygging**: Sikrer at DuckDB-visninger opprettes feilfritt.
* **PBIP-validering**: Bekrefter integriteten til Power BI prosjektfiler og mapper.

---

## 7. Edward Tufte Data-Ink Standard

Prosjektet følger Edward Tuftes prinsipper for visuell datakommunikasjon:
1. **Fjern "Chartjunk"**: Ingen 3D-elementer, ingen skygger, ingen tunge rammer.
2. **Tabellrenslighet**: Ingen vertikale rutenettlinjer. Kun lette horisontale skillelinjer.
3. **Muted Palette**: Hovedsakelig skifer- og koksgrå nyanser. Rød (`#EF4444`) og gul (`#F59E0B`) benyttes utelukkende for å indikere vesentlige avvik (> 5 % eller 2–5 %).
4. **Direkte Merking**: S-kurver og tidsserier merkes direkte på kurven fremfor å bruke separate fargetegnforklaringer.
5. **Talljustering**: Tekst venstrejusteres, tall høyrejusteres, og desimaler flukter vertikalt.

Les full standard i [`docs/reporting_standard_tufte.md`](docs/reporting_standard_tufte.md).

---

## 8. Forfatter & Faglig Kontekst

* **Forfatter**: Frank Ellingsen
* **Rolle**: Senior Financial Controller & BI-spesialist / Project Controller
* **Kontekst**: University / Statlig sektor / Prosjekt- og virksomhetsstyring
