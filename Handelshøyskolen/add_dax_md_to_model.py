"""
Script to fully integrate DAX.md into the Power BI semantic model and report:
1. Creates DimDAXLibrary.csv (50 parsed measures with metadata, formulas, and notes)
2. Creates DimDAXDoc.csv (verbatim markdown lines for document viewing)
3. Generates DimDAXLibrary.tmdl and DimDAXDoc.tmdl in semantic model tables
4. Updates model.tmdl to reference the new tables
5. Updates _Measures.tmdl to include all 50 DAX.md measures with exact folder mapping and descriptions
6. Adds a 5th PBIR page: page_dax_library with interactive Tufte-styled DAX library browser
7. Updates pages.json to register the new page
"""
import os
import re
import csv
import json
import uuid

BASE_DIR = r"c:\Users\frank\Desktop\UIA2\Handelshøyskolen"
SEMANTIC_DIR = os.path.join(BASE_DIR, "Controller-Handelshøyskolen.SemanticModel", "definition")
TABLES_DIR = os.path.join(SEMANTIC_DIR, "tables")
REPORT_DIR = os.path.join(BASE_DIR, "Controller-Handelshøyskolen.Report", "definition")
PAGES_DIR = os.path.join(REPORT_DIR, "pages")

def gen_guid():
    return str(uuid.uuid4())

def fill_guids(text):
    while "[[GUID]]" in text:
        text = text.replace("[[GUID]]", gen_guid(), 1)
    return text

def parse_dax_md():
    with open(os.path.join(BASE_DIR, "DAX.md"), "r", encoding="utf-8") as f:
        text = f.read()

    folder_mapping = [
        (1, 5, '_01 Accounting', 'Core Accounting & YTD Measures', 'Actual YTD summerer bokførte hovedboksbevegelser frem til 30. september (1 072,1 MNOK inntekt / 1 092,0 MNOK kostnader for UiA).'),
        (6, 10, '_02 Forecast & LE', 'Rolling Forecasts & Year-End Estimates', 'Samlet helårsprognose (Forecast LE / EAC) utgjør 1 433,0 MNOK inntekt mot 1 444,0 MNOK kostnader. Netto helårsavvik (VAC) på -11,0 MNOK dekkes av oppsparte reserver i tråd med Note 15 og Rundskriv F-05-20.'),
        (11, 17, '_03 Temporal YoY & MoM', 'Temporal Baseline Comparisons', 'Temporære sammenligningslinjer (YoY og MoM) sikrer at ledelsen evaluerer driftsmomentum parallelt med faste årsbudsjetter.'),
        (18, 23, '_04 EVM', 'Earned Value Management', 'Ved T3-avskjæring er UiAs CPI 0,95 (5% kostnadsoverskridelse) og SPI 0,92 (8% fremdriftsforsinkelse).'),
        (24, 29, '_05 Staffing & FTE', 'Staffing & Capacity KPIs', 'Lønnskostnader utgjør 65,4% av totale driftskostnader ved UiA (944,0 MNOK), marginalt over sektornormens øvre terskel på 65,0%.'),
        (30, 35, '_06 Utdanning & SPE60', 'Student Production & KD 2025 Model', 'Under KDs 2025-finansieringsmodell gir Kategori 1 en sats på 54 550 NOK pr 60 SPE. Satsen gjelder marginale volumendringer.'),
        (36, 40, '_07 Action Tracker', 'Restructuring & Action Tracker', 'FactAction kobler omstillingstiltak (f.eks. administrativ ansettelsesstopp T001/T002) direkte til regnskapskonti og prognoseavvik.'),
        (41, 44, '_08 RAG & Design', 'RAG Formatting & Dynamic Design', 'Bruk av myke bakgrunnsfyll (#ECFDF5, #FFFBEB, #FEF2F2) forhindrer blendende neonfarger og følger Edward Tuftes data-ink prinsipper.'),
        (45, 50, '_09 HHU Measures', 'Handelshøyskolen ved UiA Spesifikt', 'Handelshøyskolen (HHU) leverer et positivt netto driftsresultat på +2,2 MNOK. Høy student-til-faglig ratio (22,3) kombinert med KD Kat 1 krever aktiv controller-oppfølging.')
    ]

    def get_folder_info(nr):
        for start, end, code, title, note in folder_mapping:
            if start <= nr <= end:
                return code, title, note
        return '_00 Other', 'General', ''

    measure_regex = re.compile(
        r'//\s*(\d+)\.\s*([^\n\r]+)\r?\n(.*?)(?=\n//|\nNote:|\nFolder |\nSpecial Sub-Folder:|\nImplementation |\Z)',
        re.DOTALL
    )

    rows = []
    for m in measure_regex.finditer(text):
        nr = int(m.group(1))
        header = m.group(2).strip()
        body = m.group(3).strip()
        
        eq_idx = body.find('=')
        if eq_idx != -1:
            name = body[:eq_idx].strip()
            expr = body[eq_idx+1:].strip()
        else:
            name = header
            expr = body
            
        code, title, note = get_folder_info(nr)
        clean_dax = re.sub(r'\s+', ' ', body)
        
        rows.append({
            'MeasureNr': nr,
            'Folder': code,
            'FolderTitle': title,
            'MeasureName': name,
            'HeaderDescription': header,
            'DAXFormula': clean_dax,
            'DAXCode': body,
            'ControllingNote': note
        })

    return rows

def generate_csv_files(rows):
    # 1. DimDAXLibrary.csv
    csv_path = os.path.join(BASE_DIR, "DimDAXLibrary.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['MeasureNr', 'Folder', 'FolderTitle', 'MeasureName', 'HeaderDescription', 'DAXFormula', 'DAXCode', 'ControllingNote'])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {csv_path} with {len(rows)} measures.")

    # 2. DimDAXDoc.csv
    with open(os.path.join(BASE_DIR, "DAX.md"), "r", encoding="utf-8") as f:
        doc_lines = f.readlines()
    doc_csv_path = os.path.join(BASE_DIR, "DimDAXDoc.csv")
    with open(doc_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['LineNr', 'LineContent'])
        for i, line in enumerate(doc_lines, 1):
            writer.writerow([i, line.rstrip('\r\n')])
    print(f"Generated {doc_csv_path} with {len(doc_lines)} lines.")

def generate_tmdl_tables():
    # 1. DimDAXLibrary.tmdl
    tmdl_lib = """table DimDAXLibrary
\tlineageTag: [[GUID]]

\tcolumn MeasureNr
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: MeasureNr
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Folder
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Folder
\t\tannotation SummarizationSetBy = Automatic

\tcolumn FolderTitle
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: FolderTitle
\t\tannotation SummarizationSetBy = Automatic

\tcolumn MeasureName
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: MeasureName
\t\tannotation SummarizationSetBy = Automatic

\tcolumn HeaderDescription
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: HeaderDescription
\t\tannotation SummarizationSetBy = Automatic

\tcolumn DAXFormula
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: DAXFormula
\t\tannotation SummarizationSetBy = Automatic

\tcolumn DAXCode
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: DAXCode
\t\tannotation SummarizationSetBy = Automatic

\tcolumn ControllingNote
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: ControllingNote
\t\tannotation SummarizationSetBy = Automatic

\tpartition DimDAXLibrary = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\Handelshøyskolen\\DimDAXLibrary.csv"),[Delimiter=",", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"MeasureNr", Int64.Type}, {"Folder", type text}, {"FolderTitle", type text}, {"MeasureName", type text}, {"HeaderDescription", type text}, {"DAXFormula", type text}, {"DAXCode", type text}, {"ControllingNote", type text}})
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(TABLES_DIR, "DimDAXLibrary.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(tmdl_lib))
    print("Created DimDAXLibrary.tmdl")

    # 2. DimDAXDoc.tmdl
    tmdl_doc = """table DimDAXDoc
\tlineageTag: [[GUID]]

\tcolumn LineNr
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: LineNr
\t\tannotation SummarizationSetBy = Automatic

\tcolumn LineContent
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: LineContent
\t\tannotation SummarizationSetBy = Automatic

\tpartition DimDAXDoc = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\Handelshøyskolen\\DimDAXDoc.csv"),[Delimiter=",", Columns=2, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"LineNr", Int64.Type}, {"LineContent", type text}})
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(TABLES_DIR, "DimDAXDoc.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(tmdl_doc))
    print("Created DimDAXDoc.tmdl")

def update_model_tmdl():
    model_path = os.path.join(SEMANTIC_DIR, "model.tmdl")
    with open(model_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "ref table DimDAXLibrary" not in content:
        content = content.replace("ref table _Measures", "ref table _Measures\nref table DimDAXLibrary\nref table DimDAXDoc")
        content = content.replace('"_Measures"]', '"_Measures","DimDAXLibrary","DimDAXDoc"]')
        with open(model_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Updated model.tmdl with DimDAXLibrary and DimDAXDoc.")

def update_measures_tmdl(rows):
    # We will build a unified _Measures.tmdl that includes:
    # 1. All 50 measures from DAX.md with their exact names, formulas, folders, and descriptions
    # 2. All auxiliary measures needed by existing report visuals (e.g., Forecast LE Inntekt, etc.)
    
    # Map from DAX.md
    dax_by_name = {r['MeasureName']: r for r in rows}
    
    measures_code = """table _Measures
\tlineageTag: [[GUID]]

"""
    # 1. Define all 50 DAX.md measures
    for r in rows:
        m_name = r['MeasureName']
        m_folder = r['Folder']
        m_desc = r['HeaderDescription'].replace('"', '\\"')
        m_note = r['ControllingNote'].replace('"', '\\"')
        
        # Determine format string
        fmt = "#,##0.0"
        if "%" in m_name:
            fmt = "0.0%"
        elif m_name in ["CPI", "SPI", "TCPI"]:
            fmt = "0.00"
        elif "NOK" in m_name or "Sats" in m_name:
            fmt = "#,##0 kr"
        elif m_name in ["Registrerte Studenter", "Avlagte SPE60"]:
            fmt = "#,##0"
        elif m_name in ["Studenter pr UF-Årsverk", "Enhetskostnad pr SPE60"]:
            fmt = "#,##0.0"
        elif "Color" in m_name or "Status" in m_name or "Subtitle" in m_name:
            fmt = None
            
        # Format the DAX body
        body = r['DAXCode']
        # remove MeasureName = from body
        if "=" in body:
            body = body.split("=", 1)[1].strip()
            
        # Indent body with 3 tabs
        indented_lines = ["\t\t\t" + l for l in body.splitlines()]
        indented_body = "\n".join(indented_lines)
        
        measures_code += f"\t/// {m_desc}\n"
        measures_code += f"\tmeasure '{m_name}' =\n{indented_body}\n"
        if fmt:
            measures_code += f"\t\tformatString: {fmt}\n"
        measures_code += f"\t\tdisplayFolder: {m_folder}\n"
        measures_code += f'\t\tdescription: "{m_desc} | {m_note}"\n'
        measures_code += f"\t\tlineageTag: [[GUID]]\n\n"

    # 2. Auxiliary measures for report continuity
    auxiliary_measures = [
        ("Actual YTD Inntekt", "CALCULATE(SUM('FactGL'[Belop_signert]), 'DimAccountHierarchy'[Kontotype] = \"Inntekt\", 'DimDate'[ErActualYTD] = TRUE())", "#,##0.0", "_01 Accounting", "Bokført inntekt YTD"),
        ("Actual YTD Kostnad", "CALCULATE(SUM('FactGL'[Belop_signert]), 'DimAccountHierarchy'[Kontotype] = \"Kostnad\", 'DimDate'[ErActualYTD] = TRUE())", "#,##0.0", "_01 Accounting", "Bokført kostnad YTD"),
        ("Budsjett YTD Inntekt", "CALCULATE(SUM('FactBudget'[BudsjettBelop]), 'DimAccountHierarchy'[Kontotype] = \"Inntekt\", 'DimDate'[ErActualYTD] = TRUE())", "#,##0.0", "_01 Accounting", "Periodisert budsjett inntekt YTD"),
        ("Budsjett YTD Kostnad", "CALCULATE(SUM('FactBudget'[BudsjettBelop]), 'DimAccountHierarchy'[Kontotype] = \"Kostnad\", 'DimDate'[ErActualYTD] = TRUE())", "#,##0.0", "_01 Accounting", "Periodisert budsjett kostnad YTD"),
        ("Actual PY Inntekt", "CALCULATE([Actual YTD Inntekt], SAMEPERIODLASTYEAR('DimDate'[Dato]))", "#,##0.0", "_03 Temporal YoY & MoM", "Fjorårsinntekt YTD"),
        ("Forecast Q4 Inntekt", "CALCULATE(SUM('FactGL'[Belop_signert]), 'DimAccountHierarchy'[Kontotype] = \"Inntekt\", 'DimDate'[ErActualYTD] = FALSE())", "#,##0.0", "_02 Forecast & LE", "Prognostisert inntekt Q4"),
        ("Forecast Q4 Kostnad", "CALCULATE(SUM('FactGL'[Belop_signert]), 'DimAccountHierarchy'[Kontotype] = \"Kostnad\", 'DimDate'[ErActualYTD] = FALSE())", "#,##0.0", "_02 Forecast & LE", "Prognostisert kostnad Q4"),
        ("Forecast LE Inntekt", "CALCULATE(SUM('FactGL'[Belop_signert]), 'DimAccountHierarchy'[Kontotype] = \"Inntekt\")", "#,##0.0", "_02 Forecast & LE", "Total helårsprognose inntekt"),
        ("Forecast LE Kostnad", "CALCULATE(SUM('FactGL'[Belop_signert]), 'DimAccountHierarchy'[Kontotype] = \"Kostnad\")", "#,##0.0", "_02 Forecast & LE", "Total helårsprognose kostnad"),
        ("Total Inntekt MNOK", "[Forecast LE Inntekt]", "#,##0.0", "_02 Forecast & LE", "Total inntekt helårsprognose"),
        ("Total Kostnad MNOK", "[Forecast LE Kostnad]", "#,##0.0", "_02 Forecast & LE", "Total kostnad helårsprognose"),
        ("Netto Driftsresultat LE", "[Forecast LE Inntekt] - [Forecast LE Kostnad]", "#,##0.0", "_02 Forecast & LE", "Netto driftsresultat helårsprognose"),
        ("Årsbudsjett Inntekt", "CALCULATE(SUM('FactBudget'[BudsjettBelop]), 'DimAccountHierarchy'[Kontotype] = \"Inntekt\")", "#,##0.0", "_02 Forecast & LE", "Vedtatt årsbudsjett inntekt"),
        ("Årsbudsjett Kostnad", "CALCULATE(SUM('FactBudget'[BudsjettBelop]), 'DimAccountHierarchy'[Kontotype] = \"Kostnad\")", "#,##0.0", "_02 Forecast & LE", "Vedtatt årsbudsjett kostnad"),
        ("Netto Driftsresultat Budsjett", "[Årsbudsjett Inntekt] - [Årsbudsjett Kostnad]", "#,##0.0", "_02 Forecast & LE", "Netto driftsresultat vedtatt budsjett"),
        ("HHU Netto Resultat", "[HHU Net Result]", "#,##0.0", "_09 HHU Measures", "Handelshøyskolen netto driftsresultat"),
        ("HHU Total Kostnad", "CALCULATE([Forecast LE Kostnad], 'DimOrganization'[Fakultetsnavn] = \"Handelshøyskolen ved UiA (HHU)\")", "#,##0.0", "_09 HHU Measures", "Handelshøyskolen total kostnad"),
        ("Tiltaksdekning %", "[Tiltak Realiseringsgrad %]", "0.0%", "_07 Action Tracker", "Realisering av omstillingstiltak"),
        ("Gjenstående Tiltakseffekt", "[Forventet Tiltakseffekt] - [Realisert Tiltakseffekt]", "#,##0.00 MNOK", "_07 Action Tracker", "Restavvik tiltak"),
        ("KD Kategori 1 Inntektseffekt", "[Avlagte SPE60] * 54550 / 1000000", "#,##0.0 MNOK", "_06 Utdanning & SPE60", "Beregnet KD Kat 1 inntekt i MNOK"),
        ("HHU AACSB Kostnad", "CALCULATE(SUM('FactGL'[Belop_signert]), 'FactGL'[ProsjektKode] = \"AACSB01\")", "#,##0.000 MNOK", "_09 HHU Measures", "AACSB akkrediteringskostnad"),
        ("HHU EVU001 Avsetning tap", "CALCULATE(SUM('FactGL'[Belop_signert]), 'FactGL'[Konto] = 7790, 'FactGL'[ProsjektKode] = \"EVU001\")", "#,##0.000 MNOK", "_09 HHU Measures", "SRS 9 avsetning for tap på EVU001"),
        ("HHU NFR Frikjøp", "CALCULATE(SUM('FactGL'[Belop_signert]), 'FactGL'[Konto] = 3400, 'FactGL'[ProsjektKode] = \"NFR001\")", "#,##0.000 MNOK", "_09 HHU Measures", "SRS 10 frikjøp NFR001"),
        ("Faculty Bar Color", "IF([Sluttavvik (VAC)] >= 0, \"#10b981\", \"#ef4444\")", None, "_08 RAG & Design", "Farge for avviksstolper"),
        ("KPI Card Border Color", "SWITCH(TRUE(), [VAC %] < -0.05, \"#EF4444\", [VAC %] < 0.00, \"#F59E0B\", \"#10B981\")", None, "_08 RAG & Design", "Kantfarge for KPI-kort"),
        ("Net Result Status Text", "VAR YTDResult = [Actual YTD] VAR HelarVAC = [Sluttavvik (VAC)] RETURN \"Helårsavvik: \" & FORMAT(HelarVAC, \"+#,##0.0;-#,##0.0;0.0\") & \" MNOK | YTD: \" & FORMAT(YTDResult, \"#,##0.0\") & \" MNOK\"", None, "_08 RAG & Design", "Statuslinje resultat"),
        ("Revenue Variance Indicator", "VAR Budget = [Årsbudsjett (BAC)] VAR Forecast = [Forecast LE (EAC)] VAR Diff = Forecast - Budget VAR Pct = DIVIDE(Diff, Budget, 0) RETURN \"Budsjett: \" & FORMAT(Budget, \"#,##0.0\") & \" MNOK | \" & IF(Diff >= 0, \"▲ +\" & FORMAT(Pct, \"0.0%\"), \"▼ \" & FORMAT(Pct, \"0.0%\"))", None, "_08 RAG & Design", "Statuslinje inntekt"),
        ("Forecast RAG Status", "VAR Vac = [Sluttavvik (VAC)] VAR VacPct = [VAC %] RETURN SWITCH(TRUE(), Vac >= 0, \"🟢 Planmessig\", VacPct >= -0.05, \"🟡 Moderat avvik\", \"🔴 Vesentlig avvik\")", None, "_08 RAG & Design", "Prognosestatus"),
        ("Actual/FC Lønn", "CALCULATE(SUM('FactGL'[Belop_signert]), 'DimAccountHierarchy'[Nivaa1_Navn] = \"Lønnskostnad\")", "#,##0.0", "_02 Forecast & LE", "Lønnskostnad helår"),
        ("Actual/FC Drift", "CALCULATE(SUM('FactGL'[Belop_signert]), 'DimAccountHierarchy'[Nivaa1_Navn] IN {\"Annen driftskostnad\", \"Andre driftskostnader\"})", "#,##0.0", "_02 Forecast & LE", "Driftskostnad helår"),
        ("Actual/FC Capex", "CALCULATE(SUM('FactGL'[Belop_signert]), 'DimAccountHierarchy'[Kontotype] = \"Investeringer\")", "#,##0.0", "_02 Forecast & LE", "Capex helår"),
        ("Faktiske & Prognostiserte Driftskostnader", "CALCULATE(SUM('FactGL'[Belop_signert]), 'DimAccountHierarchy'[Kontotype] = \"Kostnad\")", "#,##0.0", "_02 Forecast & LE", "Samlede driftskostnader"),
        ("Cost Variance (CV)", "[Earned Value (EV)] - [Actual Cost (AC)]", "#,##0.0", "_04 EVM", "Kostnadsavvik EVM"),
        ("Schedule Variance (SV)", "[Earned Value (EV)] - [Planned Value (PV)]", "#,##0.0", "_04 EVM", "Fremdriftsavvik EVM"),
        ("TCPI", "DIVIDE([Årsbudsjett (BAC)] - [Earned Value (EV)], [Årsbudsjett (BAC)] - [Actual Cost (AC)], 1)", "0.00", "_04 EVM", "To-Complete Performance Index"),
        ("EAC (EVM)", "DIVIDE([Årsbudsjett (BAC)], [CPI], [Årsbudsjett (BAC)])", "#,##0.0", "_04 EVM", "EVM beregnet EAC"),
        ("VAC (EVM)", "[Årsbudsjett (BAC)] - [EAC (EVM)]", "#,##0.0", "_04 EVM", "EVM beregnet VAC"),
        ("Diagnose og Drivere", """VAR Org = SELECTEDVALUE('DimOrganization'[OrgKode])
RETURN
SWITCH(
    Org,
    "HHU_I001", "Høy SPE-produksjon (86,7/mnd). KD Kat 1 sats. T003 EVU-ekspansjon pågår.",
    "HHU_I002", "Stabil drift. Rettsvitenskap. 21,3 stud/UF. Lav vakansgrad.",
    "HHU_I003", "Høy studenttetthet (23,3 stud/UF). T002 faglige årsverk omdisponert.",
    "HHU_ADM", "T001 administrativ ansettelsesstopp. AACSB akkrediteringskostnad M03/M09.",
    "TEK_001", "Laboratoriekostnader og IKT-investeringer. Merforbruk -1,9 MNOK.",
    "HEL_001", "Klinisk praksis og turnusavtaler. Merforbruk -5,3 MNOK.",
    "SAM_001", "Mindreforbruk på drift +3,0 MNOK. Frikjøp på samfunnsprosjekter.",
    "HUM_001", "Stabil drift, marginalt avvik -0,3 MNOK.",
    "ADM_001", "Sentral vakansstopp T006. Felles konsulentkutt. Merforbruk -8,7 MNOK.",
    "Handelshøyskolen har et samlet netto overskudd på +2,2 MNOK som bidrar til å dempe universitetets sentrale underskudd."
)""", None, "_08 RAG & Design", "Diagnosetekst pr enhet")
    ]

    for name, expr, fmt, folder, desc in auxiliary_measures:
        # Check if already added
        if name in dax_by_name:
            continue
        indented = "\n".join(["\t\t\t" + l for l in expr.splitlines()])
        measures_code += f"\t/// {desc}\n"
        measures_code += f"\tmeasure '{name}' =\n{indented}\n"
        if fmt:
            measures_code += f"\t\tformatString: {fmt}\n"
        measures_code += f"\t\tdisplayFolder: {folder}\n"
        measures_code += f'\t\tdescription: "{desc}"\n'
        measures_code += f"\t\tlineageTag: [[GUID]]\n\n"

    # End table definition with dummy partition
    measures_code += """\tcolumn Column1
\t\tdataType: string
\t\tisHidden
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Column1
\t\tannotation SummarizationSetBy = Automatic

\tpartition _Measures = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("i44FAA==", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type nullable text) meta [Serialized.Text = true]) in type table [Column1 = _t])
\t\t\t\tin
\t\t\t\t    Source

\tannotation PBI_ResultType = Table
"""
    measures_path = os.path.join(TABLES_DIR, "_Measures.tmdl")
    with open(measures_path, "w", encoding="utf-8") as f:
        f.write(fill_guids(measures_code))
    print(f"Successfully generated updated {measures_path} with all DAX.md measures and documentation!")

def add_pbir_dax_library_page():
    page_folder = os.path.join(PAGES_DIR, "page_dax_library")
    os.makedirs(page_folder, exist_ok=True)
    visuals_folder = os.path.join(page_folder, "visuals")
    os.makedirs(visuals_folder, exist_ok=True)

    page_json = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/1.3.0/schema.json",
        "name": "page_dax_library",
        "displayName": "DAX Målbibliotek (DAX.md)",
        "displayOption": "FitToPage",
        "height": 720,
        "width": 1280
    }
    with open(os.path.join(page_folder, "page.json"), "w", encoding="utf-8") as f:
        json.dump(page_json, f, indent=2)

    # 1. Header Visual
    v_hdr = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.4.0/schema.json",
        "name": "v_dax_header",
        "position": {"x": 20, "y": 15, "width": 1240, "height": 55, "z": 1},
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [
                    {
                        "properties": {
                            "paragraphs": [
                                {
                                    "textRuns": [
                                        {
                                            "value": "UiA Handelshøyskolen — DAX Målbibliotek & Dokumentasjon (DAX.md)\n",
                                            "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "16pt", "color": "#1E293B"}
                                        },
                                        {
                                            "value": "50 produksjonsgrad DAX-mål organisert i 9 mapper | Tufte Data-Ink, 3-30-300 hierarki, KD 2025 modell & SRS 9/10 standard",
                                            "textStyle": {"fontFamily": "Segoe UI", "fontSize": "9pt", "color": "#64748B"}
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }
    with open(os.path.join(visuals_folder, "v_dax_header.json"), "w", encoding="utf-8") as f:
        json.dump(v_hdr, f, indent=2)

    # 2. Slicer for Folders
    v_slicer = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.4.0/schema.json",
        "name": "v_dax_slicer",
        "position": {"x": 20, "y": 78, "width": 280, "height": 625, "z": 2},
        "visual": {
            "visualType": "slicer",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimDAXLibrary"}}, "Property": "Folder"}}, "queryRef": "DimDAXLibrary.Folder"}
                        ]
                    }
                }
            },
            "objects": {
                "general": [{"properties": {"title": {"expr": {"Literal": {"Value": "'Mappevelger (9 Tema)'"}}}}}]
            }
        }
    }
    with open(os.path.join(visuals_folder, "v_dax_slicer.json"), "w", encoding="utf-8") as f:
        json.dump(v_slicer, f, indent=2)

    # 3. Quick KPI Card 1: 50 Mål
    v_kpi1 = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.4.0/schema.json",
        "name": "v_dax_kpi1",
        "position": {"x": 315, "y": 78, "width": 220, "height": 80, "z": 3},
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [
                    {
                        "properties": {
                            "paragraphs": [
                                {
                                    "textRuns": [
                                        {"value": "50 Mål\n", "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "20pt", "color": "#1E293B"}},
                                        {"value": "Fullstendig DAX-bibliotek", "textStyle": {"fontFamily": "Segoe UI", "fontSize": "9pt", "color": "#64748B"}}
                                    ]
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }
    with open(os.path.join(visuals_folder, "v_dax_kpi1.json"), "w", encoding="utf-8") as f:
        json.dump(v_kpi1, f, indent=2)

    # 4. Quick KPI Card 2: 9 Mapper
    v_kpi2 = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.4.0/schema.json",
        "name": "v_dax_kpi2",
        "position": {"x": 550, "y": 78, "width": 220, "height": 80, "z": 4},
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [
                    {
                        "properties": {
                            "paragraphs": [
                                {
                                    "textRuns": [
                                        {"value": "9 Mapper\n", "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "20pt", "color": "#0F766E"}},
                                        {"value": "Tematisk inndeling", "textStyle": {"fontFamily": "Segoe UI", "fontSize": "9pt", "color": "#64748B"}}
                                    ]
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }
    with open(os.path.join(visuals_folder, "v_dax_kpi2.json"), "w", encoding="utf-8") as f:
        json.dump(v_kpi2, f, indent=2)

    # 5. Quick KPI Card 3: Standarder
    v_kpi3 = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.4.0/schema.json",
        "name": "v_dax_kpi3",
        "position": {"x": 785, "y": 78, "width": 475, "height": 80, "z": 5},
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [
                    {
                        "properties": {
                            "paragraphs": [
                                {
                                    "textRuns": [
                                        {"value": "Tufte & KD 2025 Standard\n", "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "16pt", "color": "#1E293B"}},
                                        {"value": "RAG Hex, 3-30-300 hierarki, SRS 9/10, F-05-20 og Note 15", "textStyle": {"fontFamily": "Segoe UI", "fontSize": "9pt", "color": "#64748B"}}
                                    ]
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }
    with open(os.path.join(visuals_folder, "v_dax_kpi3.json"), "w", encoding="utf-8") as f:
        json.dump(v_kpi3, f, indent=2)

    # 6. Hovedtabell over alle DAX-mål
    v_table = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.4.0/schema.json",
        "name": "v_dax_table",
        "position": {"x": 315, "y": 168, "width": 945, "height": 535, "z": 6},
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimDAXLibrary"}}, "Property": "MeasureNr"}}, "queryRef": "DimDAXLibrary.MeasureNr"},
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimDAXLibrary"}}, "Property": "MeasureName"}}, "queryRef": "DimDAXLibrary.MeasureName"},
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimDAXLibrary"}}, "Property": "FolderTitle"}}, "queryRef": "DimDAXLibrary.FolderTitle"},
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimDAXLibrary"}}, "Property": "HeaderDescription"}}, "queryRef": "DimDAXLibrary.HeaderDescription"},
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimDAXLibrary"}}, "Property": "DAXFormula"}}, "queryRef": "DimDAXLibrary.DAXFormula"},
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimDAXLibrary"}}, "Property": "ControllingNote"}}, "queryRef": "DimDAXLibrary.ControllingNote"}
                        ]
                    }
                }
            },
            "objects": {
                "general": [
                    {
                        "properties": {
                            "title": {"expr": {"Literal": {"Value": "'DAX Målspesifikasjon & Formler (DAX.md)'"}}}
                        }
                    }
                ]
            }
        }
    }
    with open(os.path.join(visuals_folder, "v_dax_table.json"), "w", encoding="utf-8") as f:
        json.dump(v_table, f, indent=2)

    # Update pages.json
    pages_json_path = os.path.join(PAGES_DIR, "pages.json")
    with open(pages_json_path, "r", encoding="utf-8") as f:
        pages_meta = json.load(f)

    if "page_dax_library" not in pages_meta["pageOrder"]:
        pages_meta["pageOrder"].append("page_dax_library")
        with open(pages_json_path, "w", encoding="utf-8") as f:
            json.dump(pages_meta, f, indent=2)
        print("Updated pages.json with page_dax_library.")

def main():
    print("Starting integration of DAX.md into Power BI Model & Report...")
    rows = parse_dax_md()
    generate_csv_files(rows)
    generate_tmdl_tables()
    update_model_tmdl()
    update_measures_tmdl(rows)
    add_pbir_dax_library_page()
    print("Integration of DAX.md completed successfully!")

if __name__ == "__main__":
    main()
