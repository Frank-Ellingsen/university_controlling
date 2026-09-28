"""
Comprehensive Builder for HHU-Rapport.pbip
Populates the TMDL Semantic Model and PBIR Report from all CSV files in C:\\Users\\frank\\Desktop\\UIA2\\HHU
Following Edward Tufte Data-Ink Ratio standards and Frank Ellingsen's Project Controlling guidelines.
"""
import os
import shutil
import uuid
import json
import re

HHU_DIR = r"c:\Users\frank\Desktop\UIA2\HHU"
PBIP_FILE = os.path.join(HHU_DIR, "HHU-Rapport.pbip")
SEMANTIC_DIR = os.path.join(HHU_DIR, "HHU-Rapport.SemanticModel", "definition")
REPORT_DIR = os.path.join(HHU_DIR, "HHU-Rapport.Report")
THEME_SOURCE = r"c:\Users\frank\Desktop\UIA2\powerbi\themes\tufte_minimalist_theme.json"

def gen_guid():
    return str(uuid.uuid4())

def fill_guids(text):
    while "[[GUID]]" in text:
        text = text.replace("[[GUID]]", gen_guid(), 1)
    return text

def ensure_directories():
    os.makedirs(os.path.join(SEMANTIC_DIR, "tables"), exist_ok=True)
    os.makedirs(os.path.join(SEMANTIC_DIR, "roles"), exist_ok=True)
    os.makedirs(os.path.join(SEMANTIC_DIR, "cultures"), exist_ok=True)
    os.makedirs(os.path.join(REPORT_DIR, "StaticResources", "RegisteredResources"), exist_ok=True)
    os.makedirs(os.path.join(REPORT_DIR, "definition", "pages"), exist_ok=True)

def setup_fact_students_csv():
    target_csv = os.path.join(HHU_DIR, "FactStudents.csv")
    source_csv = os.path.join(HHU_DIR, "FactStudents_2027.csv")
    if not os.path.exists(target_csv) and os.path.exists(source_csv):
        shutil.copy2(source_csv, target_csv)
        print("Created FactStudents.csv from FactStudents_2027.csv")

def parse_dax_measures():
    md_path = os.path.join(HHU_DIR, "DAX_Measures_UiA_HHU_2026_2027.md")
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()

    sections = re.split(r'##\s+\d+\.\s+', text)
    measures = []
    
    for s in sections[1:]:
        lines = s.strip().split('\n')
        header = lines[0]
        folder_match = re.search(r'\(`([^`]+)`\)', header)
        folder = folder_match.group(1) if folder_match else header
        
        code_blocks = re.findall(r'```dax\s*(.*?)\s*```', s, re.DOTALL)
        for block in code_blocks:
            chunks = re.split(r'(?=\/\/\s*\d+\.\s+)', block.strip())
            for chunk in chunks:
                chunk = chunk.strip()
                if not chunk: continue
                clines = chunk.split('\n')
                desc = clines[0].lstrip('/ ').strip()
                rest = '\n'.join(clines[1:]).strip()
                
                eq_idx = rest.find('=')
                if eq_idx != -1:
                    mname = rest[:eq_idx].strip()
                    expr = rest[eq_idx+1:].strip()
                    
                    # determine formatString
                    format_str = "#,##0"
                    if "%" in mname or "Andel" in mname or "grad" in mname:
                        format_str = "0.0%"
                    elif "CPI" in mname or "SPI" in mname:
                        format_str = "0.00"
                    elif "Hex" in mname or "Status" in mname or "Subtitle" in mname or "Badge" in mname:
                        format_str = None
                    elif "NOK" in mname or "Belop" in mname or "YTD" in mname or "EAC" in mname or "BAC" in mname or "VAC" in mname or "Inntekt" in mname or "Kostnad" in mname or "Resultat" in mname:
                        format_str = "#,##0"
                    elif "Årsverk" in mname or "SPE60" in mname:
                        format_str = "#,##0.0"
                    
                    measures.append({
                        'name': mname,
                        'desc': desc,
                        'folder': folder,
                        'expr': expr,
                        'formatString': format_str
                    })
    
    # Incorporate executive measures from pbi_dashboard_gudie_skill.md & storytelling-with-data-pbi-skill-v3.md
    extra_measures = [
        {
            'name': 'Revenue Variance Indicator',
            'desc': 'Dynamisk budsjettavvik-indikator for inntektskort',
            'folder': '_08 RAG & Design',
            'expr': (
                'VAR Budget = [Årsbudsjett (BAC)]\n'
                'VAR Forecast = [Forecast LE (EAC)]\n'
                'VAR Diff = Forecast - Budget\n'
                'VAR Pct = DIVIDE(Diff, Budget, 0)\n'
                'VAR BudgetMNOK = DIVIDE(Budget, IF(Budget > 1000000, 1000000, 1), 0)\n'
                'RETURN\n'
                '"Budsjett: " & FORMAT(BudgetMNOK, "#,##0.0") & " MNOK | " &\n'
                'IF(Diff >= 0, "▲ +" & FORMAT(Pct, "0.0%"), "▼ " & FORMAT(Pct, "0.0%"))'
            ),
            'formatString': None
        },
        {
            'name': 'Net Result Status Text',
            'desc': 'Status- og avvikstekst for nettoresultat',
            'folder': '_08 RAG & Design',
            'expr': (
                'VAR YTDResult = DIVIDE([Actual YTD], IF(ABS([Actual YTD]) > 1000000, 1000000, 1), 0)\n'
                'VAR HelarVAC = DIVIDE([Sluttavvik (VAC)], IF(ABS([Sluttavvik (VAC)]) > 1000000, 1000000, 1), 0)\n'
                'RETURN\n'
                '"Helårsavvik: " & FORMAT(HelarVAC, "+#,##0.0;-#,##0.0;0.0") & " MNOK | YTD: " & FORMAT(YTDResult, "#,##0.0") & " MNOK"'
            ),
            'formatString': None
        },
        {
            'name': 'Staffing Card Subtitle',
            'desc': 'UF/TA fordeling og lønnsandel for bemanningskort',
            'folder': '_05 Staffing & FTE',
            'expr': (
                'VAR UF = [Faglige Årsverk (UF)]\n'
                'VAR TA = [Teknisk-Admin Årsverk (TA)]\n'
                'VAR LonnPct = [Lønnsandel %]\n'
                'RETURN\n'
                'FORMAT(UF, "#0") & " UF / " & FORMAT(TA, "#0") & " TA | Lønnsandel: " & FORMAT(LonnPct, "0.0%")'
            ),
            'formatString': None
        },
        {
            'name': 'Student KPI Subtitle',
            'desc': 'Studiepoeng og studenttetthet for studentkort',
            'folder': '_06 Utdanning & SPE60',
            'expr': (
                'VAR SPE = [Avlagte SPE60]\n'
                'VAR Ratio = [Studenter pr UF-Årsverk]\n'
                'RETURN\n'
                'FORMAT(SPE, "#,##0") & " SPE60 | " & FORMAT(Ratio, "0.0") & " Studenter/UF-ÅV"'
            ),
            'formatString': None
        },
        {
            'name': 'Faculty Bar Color',
            'desc': 'Tufte RAG-fargekode for instituttstolper',
            'folder': '_08 RAG & Design',
            'expr': 'IF([Sluttavvik (VAC)] >= 0, "#10b981", "#ef4444")',
            'formatString': None
        },
        {
            'name': 'Cumulative Actual & Forecast',
            'desc': 'Akkumulerte faktiske kostnader og Q4-prognose',
            'folder': '_02 Forecast & LE',
            'expr': (
                'VAR MaxDate = MAX(\'DimDate\'[Dato])\n'
                'RETURN\n'
                'CALCULATE(\n'
                '    [Forecast LE (EAC)],\n'
                '    \'DimDate\'[Dato] <= MaxDate,\n'
                '    ALLSELECTED(\'DimDate\')\n'
                ')'
            ),
            'formatString': '#,##0'
        },
        {
            'name': 'Cumulative Budget',
            'desc': 'Akkumulert periodisert årsbudsjett',
            'folder': '_02 Forecast & LE',
            'expr': (
                'VAR MaxDate = MAX(\'DimDate\'[Dato])\n'
                'RETURN\n'
                'CALCULATE(\n'
                '    [Årsbudsjett (BAC)],\n'
                '    \'DimDate\'[Dato] <= MaxDate,\n'
                '    ALLSELECTED(\'DimDate\')\n'
                ')'
            ),
            'formatString': '#,##0'
        },
        {
            'name': 'KPI Card Border Color',
            'desc': 'Dynamisk kantlinjefarge basert på VAC % terskler',
            'folder': '_08 RAG & Design',
            'expr': (
                'SWITCH(\n'
                '    TRUE(),\n'
                '    [VAC %] < -0.05, "#EF4444",\n'
                '    [VAC %] < 0.00, "#F59E0B",\n'
                '    "#10B981"\n'
                ')'
            ),
            'formatString': None
        },
        {
            'name': 'Faktiske & Prognostiserte Driftskostnader',
            'desc': 'Månedlige kostnader (M01-M09 faktiske, M10-M12 prognose) i MNOK',
            'folder': '_01 Accounting',
            'expr': (
                'VAR CutoffMonth = 9\n'
                'VAR CurrentMonth = MAX(\'DimDate\'[MaanedNummer])\n'
                'VAR ActualAmount = CALCULATE(SUM(\'FactGL\'[Belop_signert]), \'FactGL\'[Bokforingstype] = "Actual", \'DimAccountHierarchy\'[Kontotype] = "Kostnad")\n'
                'VAR ForecastAmount = CALCULATE(SUM(\'FactGL\'[Belop_signert]), \'FactGL\'[Bokforingstype] = "Forecast", \'DimAccountHierarchy\'[Kontotype] = "Kostnad")\n'
                'VAR Amount = IF(CurrentMonth <= CutoffMonth, ActualAmount, ForecastAmount)\n'
                'RETURN\n'
                'DIVIDE(Amount, 1000000, 0)'
            ),
            'formatString': '#,##0.0'
        },
        {
            'name': 'Månedlig Budsjett MNOK',
            'desc': 'Periodisert månedlig driftsbudsjett i MNOK',
            'folder': '_01 Accounting',
            'expr': (
                'VAR Bud = CALCULATE(SUM(\'FactBudget\'[BudsjettBelop]), \'DimAccountHierarchy\'[Kontotype] = "Kostnad")\n'
                'RETURN\n'
                'DIVIDE(Bud, 1000000, 0)'
            ),
            'formatString': '#,##0.0'
        },
        {
            'name': 'Budsjett MNOK',
            'desc': 'Driftsbudsjett i MNOK',
            'folder': '_01 Accounting',
            'expr': (
                'VAR Bud = CALCULATE(SUM(\'FactBudget\'[BudsjettBelop]), \'DimAccountHierarchy\'[Kontotype] = "Kostnad")\n'
                'RETURN\n'
                'DIVIDE(Bud, 1000000, 0)'
            ),
            'formatString': '#,##0.0'
        },
        {
            'name': 'Total Inntekt MNOK',
            'desc': 'Samlet inntekt / bevilget ramme i MNOK',
            'folder': '_01 Accounting',
            'expr': (
                'VAR InntektGL = CALCULATE(SUM(\'FactGL\'[Belop_signert]), \'DimAccountHierarchy\'[Kontotype] = "Inntekt")\n'
                'VAR InntektBud = CALCULATE(SUM(\'FactBudget\'[BudsjettBelop]), \'DimAccountHierarchy\'[Kontotype] = "Inntekt")\n'
                'VAR Ramme = [HHU 2026 Vedtatt Årsbudsjett]\n'
                'VAR Res = COALESCE(InntektGL, InntektBud, Ramme, 0)\n'
                'RETURN\n'
                'DIVIDE(Res, IF(Res > 1000, 1000000, 1), 0)'
            ),
            'formatString': '#,##0.0'
        },
        {
            'name': 'Actual/FC Lønn',
            'desc': 'Helårsprognose for lønnskostnader i MNOK',
            'folder': '_02 Forecast & LE',
            'expr': (
                'VAR Lonn = CALCULATE([Forecast LE (EAC)], \'DimAccountHierarchy\'[Nivaa1_Navn] = "Lønnskostnad")\n'
                'RETURN\n'
                'DIVIDE(Lonn, IF(ABS(Lonn) > 1000, 1000000, 1), 0)'
            ),
            'formatString': '#,##0.0'
        },
        {
            'name': 'Actual/FC Drift',
            'desc': 'Helårsprognose for andre driftskostnader i MNOK',
            'folder': '_02 Forecast & LE',
            'expr': (
                'VAR Drift = CALCULATE([Forecast LE (EAC)], \'DimAccountHierarchy\'[Nivaa1_Navn] IN {"Annen driftskostnad", "Andre driftskostnader"})\n'
                'RETURN\n'
                'DIVIDE(Drift, IF(ABS(Drift) > 1000, 1000000, 1), 0)'
            ),
            'formatString': '#,##0.0'
        },
        {
            'name': 'Actual/FC Capex',
            'desc': 'Helårsprognose for investeringer / utstyr i MNOK',
            'folder': '_02 Forecast & LE',
            'expr': (
                'VAR Capex = CALCULATE([Forecast LE (EAC)], \'DimAccountHierarchy\'[Kontotype] = "Investeringer" || \'DimAccountHierarchy\'[Nivaa1_Navn] = "Investeringer")\n'
                'RETURN\n'
                'DIVIDE(COALESCE(Capex, 0), IF(ABS(COALESCE(Capex, 0)) > 1000, 1000000, 1), 0)'
            ),
            'formatString': '#,##0.0'
        },
        {
            'name': 'Sluttavvik (VAC) MNOK',
            'desc': 'Sluttavvik (VAC) skalert til MNOK',
            'folder': '_02 Forecast & LE',
            'expr': 'DIVIDE([Sluttavvik (VAC)], 1000000, 0)',
            'formatString': '#,##0.0'
        },
        {
            'name': 'Forecast RAG Status',
            'desc': 'Evaluering av helårsavvik med RAG trafikklys-symboler',
            'folder': '_08 RAG & Design',
            'expr': (
                'VAR Vac = [Sluttavvik (VAC)]\n'
                'VAR VacPct = [VAC %]\n'
                'RETURN\n'
                'SWITCH(\n'
                '    TRUE(),\n'
                '    Vac >= 0, "🟢 Planmessig",\n'
                '    VacPct >= -0.05, "🟡 Moderat avvik",\n'
                '    "🔴 Vesentlig avvik"\n'
                ')'
            ),
            'formatString': None
        },
        {
            'name': 'Diagnose og Drivere',
            'desc': 'Tekstlig analyse av økonomiske drivere per institutt',
            'folder': '_08 RAG & Design',
            'expr': (
                'VAR Org = SELECTEDVALUE(\'DimOrganization\'[OrgKode])\n'
                'RETURN\n'
                'SWITCH(\n'
                '    Org,\n'
                '    "K10000", "HHU Fakultetsadministrasjon & Felles: T001 administrativ ansettelsesstopp. AACSB akkrediteringskostnad. Ramme 14,0 MNOK.",\n'
                '    "K11000", "Institutt for ledelse og innovasjon: Høy SPE-produksjon. KD Kat 1 sats. T003 EVU-ekspansjon pågår. Ramme 38,5 MNOK.",\n'
                '    "K12000", "Institutt for rettsvitenskap: Stabil drift. Rettsvitenskap. Lav vakansgrad. Ramme 29,25 MNOK.",\n'
                '    "K13000", "Institutt for økonomi: Høy studenttetthet (23,3 stud/UF). T002 faglige årsverk. Ramme 48,40 MNOK.",\n'
                '    "Handelshøyskolen ved UiA har en samlet vedtatt ramme på 130,15 MNOK med balansert drift og kontrollert lønnsandel."\n'
                ')'
            ),
            'formatString': None
        },
        {
            'name': 'YoY Growth RAG Status',
            'desc': 'RAG evaluering av årlig inntektsvekst',
            'folder': '_08 RAG & Design',
            'expr': (
                'VAR YoYPct = [Actual YoY %]\n'
                'RETURN\n'
                'SWITCH(\n'
                '    TRUE(),\n'
                '    YoYPct >= 0.03, "🟢 Sterk vekst (>= +3%)",\n'
                '    YoYPct >= -0.02, "🟡 Stabil / Flat (-2% til +3%)",\n'
                '    "🔴 Svekket inntekt (< -2%)"\n'
                ')'
            ),
            'formatString': None
        },
        {
            'name': 'EVM RAG Status',
            'desc': 'EVM kostnadseffektivitet status',
            'folder': '_04 EVM',
            'expr': (
                'VAR CPIVal = [CPI]\n'
                'RETURN\n'
                'SWITCH(\n'
                '    TRUE(),\n'
                '    CPIVal >= 1.00, "🟢 God effektivitet (CPI >= 1.0)",\n'
                '    CPIVal >= 0.90, "🟡 Moderat avvik (CPI 0.90-0.99)",\n'
                '    "🔴 Kritisk overskridelse (CPI < 0.90)"\n'
                ')'
            ),
            'formatString': None
        },
        {
            'name': 'EVM CPI RAG Hex',
            'desc': 'Hex fargekode for CPI',
            'folder': '_04 EVM',
            'expr': (
                'VAR CPIVal = [CPI]\n'
                'RETURN\n'
                'IF(CPIVal >= 1.00, "#10b981", IF(CPIVal >= 0.90, "#f59e0b", "#ef4444"))'
            ),
            'formatString': None
        }
    ]
    
    existing_names = {m['name'] for m in measures}
    for em in extra_measures:
        if em['name'] not in existing_names:
            measures.append(em)
            
    return measures

def build_measures_tmdl(measures):
    lines = [
        "table _Measures",
        "\tlineageTag: [[GUID]]",
        ""
    ]
    
    for m in measures:
        desc = m['desc'].replace('"', '""')
        lines.append(f"\t/// {desc}")
        lines.append(f"\tmeasure '{m['name']}' =")
        
        # indent each line of the expression with 3 tabs
        expr_lines = m['expr'].split('\n')
        for el in expr_lines:
            lines.append(f"\t\t\t{el}")
            
        if m['formatString']:
            lines.append(f"\t\tformatString: {m['formatString']}")
        lines.append(f"\t\tdisplayFolder: {m['folder']}")
        lines.append("\t\tlineageTag: [[GUID]]")
        lines.append("")
        
    lines.extend([
        "\tcolumn RowId",
        "\t\tdataType: int64",
        "\t\tisHidden",
        "\t\tformatString: 0",
        "\t\tlineageTag: [[GUID]]",
        "\t\tsummarizeBy: none",
        "\t\tsourceColumn: RowId",
        "",
        "\t\tannotation SummarizationSetBy = Automatic",
        "",
        "\tpartition _Measures = m",
        "\t\tmode: import",
        "\t\tsource =",
        "\t\t\t\tlet",
        "\t\t\t\t    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText(\"i45WMlSKjQUA\", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type nullable text) meta [Serialized.Text = true]) in type table [RowId = _t]),",
        "\t\t\t\t    #\"Changed Type\" = Table.TransformColumnTypes(Source,{{\"RowId\", Int64.Type}}, \"en-US\")",
        "\t\t\t\tin",
        "\t\t\t\t    #\"Changed Type\"",
        "",
        "\tannotation PBI_ResultType = Table",
        ""
    ])
    return fill_guids("\n".join(lines))

def write_tmdl_semantic_model():
    ensure_directories()
    setup_fact_students_csv()
    
    # 1. database.tmdl
    with open(os.path.join(SEMANTIC_DIR, "database.tmdl"), "w", encoding="utf-8") as f:
        f.write("database\n\tcompatibilityLevel: 1606\n\n")

    # 2. cultures/en-US.tmdl
    with open(os.path.join(SEMANTIC_DIR, "cultures", "en-US.tmdl"), "w", encoding="utf-8") as f:
        f.write("cultureInfo en-US\n\n")

    # 3. model.tmdl
    model_content = """model Model
\tculture: en-US
\tdefaultPowerBIDataSourceVersion: powerBI_V3
\tsourceQueryCulture: en-US
\tvalueFilterBehavior: independent
\tdataAccessOptions
\t\tlegacyRedirects
\t\treturnErrorValuesAsNull

annotation __PBI_TimeIntelligenceEnabled = 1

annotation PBI_ProTooling = ["DevMode","TMDL-Extension"]

annotation PBI_QueryOrder = ["DimAccountHierarchy","DimDate","DimDate_2027","DimForecastVersion","DimOrganization","FactAction","FactAction_2027","FactBudget","FactBudget_2027","FactEVM","FactFTE","FactFTE_2027","FactGL","FactStudents","FactStudents_2027","_Measures"]

ref table DimAccountHierarchy
ref table DimDate
ref table DimDate_2027
ref table DimForecastVersion
ref table DimOrganization
ref table FactAction
ref table FactAction_2027
ref table FactBudget
ref table FactBudget_2027
ref table FactEVM
ref table FactFTE
ref table FactFTE_2027
ref table FactGL
ref table FactStudents
ref table FactStudents_2027
ref table _Measures

ref role Universitetsledelse
ref role Dekan_HHU
ref role Instituttleder_K11000
ref role Instituttleder_K12000
ref role Instituttleder_K13000
ref role Administrasjon_K10000

ref cultureInfo en-US
"""
    with open(os.path.join(SEMANTIC_DIR, "model.tmdl"), "w", encoding="utf-8") as f:
        f.write(model_content)

    # 4. relationships.tmdl
    rel_content = """relationship rel_factgl_dimorg
\tfromColumn: FactGL.OrgKode
\ttoColumn: DimOrganization.OrgKode

relationship rel_factgl_dimacc
\tfromColumn: FactGL.Konto
\ttoColumn: DimAccountHierarchy.Konto

relationship rel_factgl_dimdate
\tfromColumn: FactGL.DatoNokkel
\ttoColumn: DimDate.DatoNokkel

relationship rel_factgl_dimversjon
\tfromColumn: FactGL.VersjonKode
\ttoColumn: DimForecastVersion.VersjonKode

relationship rel_factbudget_dimorg
\tfromColumn: FactBudget.OrgKode
\ttoColumn: DimOrganization.OrgKode

relationship rel_factbudget_dimacc
\tfromColumn: FactBudget.Konto
\ttoColumn: DimAccountHierarchy.Konto

relationship rel_factbudget_dimdate
\tfromColumn: FactBudget.DatoNokkel
\ttoColumn: DimDate.DatoNokkel

relationship rel_factbudget_dimversjon
\tfromColumn: FactBudget.VersjonKode
\ttoColumn: DimForecastVersion.VersjonKode

relationship rel_factfte_dimorg
\tfromColumn: FactFTE.OrgKode
\ttoColumn: DimOrganization.OrgKode

relationship rel_factfte_dimdate
\tfromColumn: FactFTE.DatoNokkel
\ttoColumn: DimDate.DatoNokkel

relationship rel_factstudents_dimorg
\tfromColumn: FactStudents.OrgKode
\ttoColumn: DimOrganization.OrgKode

relationship rel_factevm_dimdate
\tfromColumn: FactEVM.DatoNokkel
\ttoColumn: DimDate.DatoNokkel

relationship rel_factaction_dimorg
\tfromColumn: FactAction.OrgKode
\ttoColumn: DimOrganization.OrgKode

relationship rel_factbudget2027_dimorg
\tfromColumn: FactBudget_2027.OrgKode
\ttoColumn: DimOrganization.OrgKode

relationship rel_factbudget2027_dimacc
\tfromColumn: FactBudget_2027.Konto
\ttoColumn: DimAccountHierarchy.Konto

relationship rel_factbudget2027_dimdate
\tfromColumn: FactBudget_2027.DatoNokkel
\ttoColumn: DimDate_2027.DatoNokkel

relationship rel_factbudget2027_dimversjon
\tfromColumn: FactBudget_2027.VersjonKode
\ttoColumn: DimForecastVersion.VersjonKode

relationship rel_factfte2027_dimorg
\tfromColumn: FactFTE_2027.OrgKode
\ttoColumn: DimOrganization.OrgKode

relationship rel_factfte2027_dimdate
\tfromColumn: FactFTE_2027.DatoNokkel
\ttoColumn: DimDate_2027.DatoNokkel

relationship rel_factstudents2027_dimorg
\tfromColumn: FactStudents_2027.OrgKode
\ttoColumn: DimOrganization.OrgKode

relationship rel_factstudents2027_dimdate
\tfromColumn: FactStudents_2027.DatoNokkel
\ttoColumn: DimDate_2027.DatoNokkel

relationship rel_factaction2027_dimorg
\tfromColumn: FactAction_2027.OrgKode
\ttoColumn: DimOrganization.OrgKode
"""
    with open(os.path.join(SEMANTIC_DIR, "relationships.tmdl"), "w", encoding="utf-8") as f:
        f.write(rel_content)

    # 5. roles
    roles = {
        "Universitetsledelse": "true",
        "Dekan_HHU": "'DimOrganization'[Fakultetsnavn] == \"Handelshøyskolen ved UiA (HHU)\"",
        "Instituttleder_K11000": "'DimOrganization'[OrgKode] == \"K11000\"",
        "Instituttleder_K12000": "'DimOrganization'[OrgKode] == \"K12000\"",
        "Instituttleder_K13000": "'DimOrganization'[OrgKode] == \"K13000\"",
        "Administrasjon_K10000": "'DimOrganization'[OrgKode] == \"K10000\""
    }
    for rname, expr in roles.items():
        r_text = f"""role {rname}
\tmodelPermission: read

\ttablePermission DimOrganization = {expr}

\tannotation PBI_Id = {gen_guid().replace('-', '')}
"""
        with open(os.path.join(SEMANTIC_DIR, "roles", f"{rname}.tmdl"), "w", encoding="utf-8") as f:
            f.write(r_text)

    # 6. Tables
    # Table 1: DimAccountHierarchy
    t_dimacc = """table DimAccountHierarchy
\tlineageTag: [[GUID]]

\tcolumn Konto
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Konto
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Kontonavn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Kontonavn
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Nivaa1_Navn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Nivaa1_Navn
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Kontotype
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Kontotype
\t\tannotation SummarizationSetBy = Automatic

\tcolumn SRS_regnskapslinje
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: SRS_regnskapslinje
\t\tannotation SummarizationSetBy = Automatic

\tpartition DimAccountHierarchy = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\HHU\\DimAccountHierarchy.csv"),[Delimiter=";", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"Konto", Int64.Type}, {"Kontonavn", type text}, {"Nivaa1_Navn", type text}, {"Kontotype", type text}, {"SRS_regnskapslinje", type text}})
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "DimAccountHierarchy.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_dimacc))

    # Table 2: DimDate
    t_dimdate = """table DimDate
\tlineageTag: [[GUID]]
\tdataCategory: Time

\tcolumn DatoNokkel
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: DatoNokkel
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Dato
\t\tdataType: dateTime
\t\tisKey
\t\tformatString: yyyy-MM-dd
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Dato
\t\tannotation SummarizationSetBy = Automatic
\t\tannotation UnderlyingDateTimeDataType = Date

\tcolumn Aar
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Aar
\t\tannotation SummarizationSetBy = Automatic

\tcolumn MaanedNummer
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: MaanedNummer
\t\tannotation SummarizationSetBy = Automatic

\tcolumn MaanedNavn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: MaanedNavn
\t\tsortByColumn: MaanedNummer
\t\tannotation SummarizationSetBy = Automatic

\tcolumn MaanedNavnKort
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: MaanedNavnKort
\t\tsortByColumn: MaanedNummer
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Kvartal
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Kvartal
\t\tannotation SummarizationSetBy = Automatic

\tcolumn ErActualYTD
\t\tdataType: boolean
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: ErActualYTD
\t\tannotation SummarizationSetBy = Automatic

\tcolumn PeriodeBeskrivelse
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: PeriodeBeskrivelse
\t\tannotation SummarizationSetBy = Automatic

\tcolumn PeriodeType
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: PeriodeType
\t\tannotation SummarizationSetBy = Automatic

\tpartition DimDate = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\HHU\\DimDate.csv"),[Delimiter=";", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"DatoNokkel", Int64.Type}, {"Aar", Int64.Type}, {"MaanedNummer", Int64.Type}, {"MaanedNavn", type text}, {"MaanedNavnKort", type text}, {"Kvartal", type text}, {"ErActualYTD", type logical}, {"PeriodeBeskrivelse", type text}}),
\t\t\t\t    #"Added Dato" = Table.AddColumn(#"Changed Type", "Dato", each #date([Aar], [MaanedNummer], 1), type date),
\t\t\t\t    #"Added PeriodeType" = Table.AddColumn(#"Added Dato", "PeriodeType", each [PeriodeBeskrivelse], type text)
\t\t\t\tin
\t\t\t\t    #"Added PeriodeType"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "DimDate.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_dimdate))

    # Table 3: DimDate_2027
    t_dimdate2027 = """table DimDate_2027
\tlineageTag: [[GUID]]
\tdataCategory: Time

\tcolumn DatoNokkel
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: DatoNokkel
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Dato
\t\tdataType: dateTime
\t\tisKey
\t\tformatString: yyyy-MM-dd
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Dato
\t\tannotation SummarizationSetBy = Automatic
\t\tannotation UnderlyingDateTimeDataType = Date

\tcolumn Aar
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Aar
\t\tannotation SummarizationSetBy = Automatic

\tcolumn MaanedNummer
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: MaanedNummer
\t\tannotation SummarizationSetBy = Automatic

\tcolumn MaanedNavn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: MaanedNavn
\t\tsortByColumn: MaanedNummer
\t\tannotation SummarizationSetBy = Automatic

\tcolumn MaanedNavnKort
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: MaanedNavnKort
\t\tsortByColumn: MaanedNummer
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Kvartal
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Kvartal
\t\tannotation SummarizationSetBy = Automatic

\tcolumn ErActualYTD
\t\tdataType: boolean
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: ErActualYTD
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Budsjettaar
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Budsjettaar
\t\tannotation SummarizationSetBy = Automatic

\tpartition DimDate_2027 = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\HHU\\DimDate_2027.csv"),[Delimiter=";", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"DatoNokkel", Int64.Type}, {"Dato", type date}, {"Aar", Int64.Type}, {"MaanedNummer", Int64.Type}, {"MaanedNavn", type text}, {"MaanedNavnKort", type text}, {"Kvartal", type text}, {"ErActualYTD", type logical}, {"Budsjettaar", Int64.Type}})
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "DimDate_2027.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_dimdate2027))

    # Table 4: DimForecastVersion
    t_dimversjon = """table DimForecastVersion
\tlineageTag: [[GUID]]

\tcolumn VersjonKode
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: VersjonKode
\t\tannotation SummarizationSetBy = Automatic

\tcolumn VersjonNavn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: VersjonNavn
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Status
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Status
\t\tannotation SummarizationSetBy = Automatic

\tcolumn SisteOppdatert
\t\tdataType: dateTime
\t\tformatString: yyyy-MM-dd
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: SisteOppdatert
\t\tannotation SummarizationSetBy = Automatic
\t\tannotation UnderlyingDateTimeDataType = Date

\tpartition DimForecastVersion = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\HHU\\DimForecastVersion.csv"),[Delimiter=";", Columns=4, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"VersjonKode", type text}, {"VersjonNavn", type text}, {"Status", type text}, {"SisteOppdatert", type date}})
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "DimForecastVersion.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_dimversjon))

    # Table 5: DimOrganization
    t_dimorg = """table DimOrganization
\tlineageTag: [[GUID]]

\tcolumn OrgKode
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: OrgKode
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Enhetsnavn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Enhetsnavn
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Nivaa1
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Nivaa1
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Nivaa2
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Nivaa2
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Nivaa3
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Nivaa3
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Budsjettansvarlig
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Budsjettansvarlig
\t\tannotation SummarizationSetBy = Automatic

\tcolumn LederTittel
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: LederTittel
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Virksomhetstype
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Virksomhetstype
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Fakultetsnavn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Fakultetsnavn
\t\tannotation SummarizationSetBy = Automatic

\tpartition DimOrganization = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\HHU\\DimOrganization.csv"),[Delimiter=";", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"OrgKode", type text}, {"Enhetsnavn", type text}, {"Nivaa1", type text}, {"Nivaa2", type text}, {"Nivaa3", type text}, {"Budsjettansvarlig", type text}, {"LederTittel", type text}, {"Virksomhetstype", type text}}),
\t\t\t\t    #"Added Fakultetsnavn" = Table.AddColumn(#"Changed Type", "Fakultetsnavn", each [Nivaa2], type text)
\t\t\t\tin
\t\t\t\t    #"Added Fakultetsnavn"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "DimOrganization.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_dimorg))

    # Table 6: FactBudget
    t_factbudget = """table FactBudget
\tlineageTag: [[GUID]]

\tcolumn DatoNokkel
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: DatoNokkel
\t\tannotation SummarizationSetBy = Automatic

\tcolumn OrgKode
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: OrgKode
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Konto
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Konto
\t\tannotation SummarizationSetBy = Automatic

\tcolumn VersjonKode
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: VersjonKode
\t\tannotation SummarizationSetBy = Automatic

\tcolumn BudsjettBelop
\t\tdataType: double
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: BudsjettBelop
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Budsjettansvarsområde
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Budsjettansvarsområde
\t\tannotation SummarizationSetBy = Automatic

\tcolumn BudsjettansvarligLeder
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: BudsjettansvarligLeder
\t\tannotation SummarizationSetBy = Automatic

\tpartition FactBudget = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\HHU\\FactBudget.csv"),[Delimiter=";", Columns=7, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"DatoNokkel", Int64.Type}, {"OrgKode", type text}, {"Konto", Int64.Type}, {"VersjonKode", type text}, {"BudsjettBelop", type number}, {"Budsjettansvarsområde", type text}, {"BudsjettansvarligLeder", type text}})
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "FactBudget.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_factbudget))

    # Table 7: FactBudget_2027
    t_factbudget2027 = """table FactBudget_2027
\tlineageTag: [[GUID]]

\tcolumn BudsjettNokkel
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: BudsjettNokkel
\t\tannotation SummarizationSetBy = Automatic

\tcolumn DatoNokkel
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: DatoNokkel
\t\tannotation SummarizationSetBy = Automatic

\tcolumn OrgKode
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: OrgKode
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Konto
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Konto
\t\tannotation SummarizationSetBy = Automatic

\tcolumn VersjonKode
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: VersjonKode
\t\tannotation SummarizationSetBy = Automatic

\tcolumn BudsjettBelop
\t\tdataType: double
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: BudsjettBelop
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Valuta
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Valuta
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Kommentar
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Kommentar
\t\tannotation SummarizationSetBy = Automatic

\tpartition FactBudget_2027 = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\HHU\\FactBudget_2027.csv"),[Delimiter=";", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"BudsjettNokkel", type text}, {"DatoNokkel", Int64.Type}, {"OrgKode", type text}, {"Konto", Int64.Type}, {"VersjonKode", type text}, {"BudsjettBelop", type number}, {"Valuta", type text}, {"Kommentar", type text}})
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "FactBudget_2027.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_factbudget2027))

    # Table 8: FactGL
    t_factgl = """table FactGL
\tlineageTag: [[GUID]]

\tcolumn TransaksjonID
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: TransaksjonID
\t\tannotation SummarizationSetBy = Automatic

\tcolumn DatoNokkel
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: DatoNokkel
\t\tannotation SummarizationSetBy = Automatic

\tcolumn OrgKode
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: OrgKode
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Konto
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Konto
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Bokforingstype
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Bokforingstype
\t\tannotation SummarizationSetBy = Automatic

\tcolumn VersjonKode
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: VersjonKode
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Belop_signert
\t\tdataType: double
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Belop_signert
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Budsjettansvarsområde
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Budsjettansvarsområde
\t\tannotation SummarizationSetBy = Automatic

\tcolumn BudsjettansvarligLeder
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: BudsjettansvarligLeder
\t\tannotation SummarizationSetBy = Automatic

\tcolumn ProsjektID
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: ProsjektID
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Avvikstype_Beskrivelse
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Avvikstype_Beskrivelse
\t\tannotation SummarizationSetBy = Automatic

\tpartition FactGL = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\HHU\\FactGL.csv"),[Delimiter=";", Columns=11, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"TransaksjonID", type text}, {"DatoNokkel", Int64.Type}, {"OrgKode", type text}, {"Konto", Int64.Type}, {"Bokforingstype", type text}, {"VersjonKode", type text}, {"Belop_signert", type number}, {"Budsjettansvarsområde", type text}, {"BudsjettansvarligLeder", type text}, {"ProsjektID", type text}, {"Avvikstype_Beskrivelse", type text}})
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "FactGL.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_factgl))

    # Table 9: FactEVM
    t_factevm = """table FactEVM
\tlineageTag: [[GUID]]

\tcolumn DatoNokkel
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: DatoNokkel
\t\tannotation SummarizationSetBy = Automatic

\tcolumn BAC_BudgetAtCompletion
\t\tdataType: double
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: BAC_BudgetAtCompletion
\t\tannotation SummarizationSetBy = Automatic

\tcolumn PlannedValue_PV
\t\tdataType: double
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: PlannedValue_PV
\t\tannotation SummarizationSetBy = Automatic

\tcolumn EarnedValue_EV
\t\tdataType: double
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: EarnedValue_EV
\t\tannotation SummarizationSetBy = Automatic

\tcolumn ActualCost_AC
\t\tdataType: double
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: ActualCost_AC
\t\tannotation SummarizationSetBy = Automatic

\tcolumn EstimateAtCompletion_EAC
\t\tdataType: double
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: EstimateAtCompletion_EAC
\t\tannotation SummarizationSetBy = Automatic

\tcolumn EstimateToComplete_ETC
\t\tdataType: double
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: EstimateToComplete_ETC
\t\tannotation SummarizationSetBy = Automatic

\tcolumn VarianceAtCompletion_VAC
\t\tdataType: double
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: VarianceAtCompletion_VAC
\t\tannotation SummarizationSetBy = Automatic

\tcolumn CostPerformanceIndex_CPI
\t\tdataType: double
\t\tformatString: 0.00
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: average
\t\tsourceColumn: CostPerformanceIndex_CPI
\t\tannotation SummarizationSetBy = Automatic

\tcolumn SchedulePerformanceIndex_SPI
\t\tdataType: double
\t\tformatString: 0.00
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: average
\t\tsourceColumn: SchedulePerformanceIndex_SPI
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Planned_Value_PV_MNOK
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Planned_Value_PV_MNOK
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Earned_Value_EV_MNOK
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Earned_Value_EV_MNOK
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Actual_Cost_AC_MNOK
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Actual_Cost_AC_MNOK
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Budget_At_Completion_BAC_MNOK
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Budget_At_Completion_BAC_MNOK
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Estimate_At_Completion_EAC_MNOK
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Estimate_At_Completion_EAC_MNOK
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Estimate_To_Complete_ETC_MNOK
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Estimate_To_Complete_ETC_MNOK
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Variance_At_Completion_VAC_MNOK
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Variance_At_Completion_VAC_MNOK
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Cost_Performance_Index_CPI
\t\tdataType: double
\t\tformatString: 0.00
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: average
\t\tsourceColumn: Cost_Performance_Index_CPI
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Schedule_Performance_Index_SPI
\t\tdataType: double
\t\tformatString: 0.00
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: average
\t\tsourceColumn: Schedule_Performance_Index_SPI
\t\tannotation SummarizationSetBy = Automatic

\tpartition FactEVM = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\HHU\\FactEVM.csv"),[Delimiter=";", Columns=10, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"DatoNokkel", Int64.Type}, {"BAC_BudgetAtCompletion", type number}, {"PlannedValue_PV", type number}, {"EarnedValue_EV", type number}, {"ActualCost_AC", type number}, {"EstimateAtCompletion_EAC", type number}, {"EstimateToComplete_ETC", type number}, {"VarianceAtCompletion_VAC", type number}, {"CostPerformanceIndex_CPI", type number}, {"SchedulePerformanceIndex_SPI", type number}}),
\t\t\t\t    #"Added PV_MNOK" = Table.AddColumn(#"Changed Type", "Planned_Value_PV_MNOK", each [PlannedValue_PV] / 1000000, type number),
\t\t\t\t    #"Added EV_MNOK" = Table.AddColumn(#"Added PV_MNOK", "Earned_Value_EV_MNOK", each [EarnedValue_EV] / 1000000, type number),
\t\t\t\t    #"Added AC_MNOK" = Table.AddColumn(#"Added EV_MNOK", "Actual_Cost_AC_MNOK", each [ActualCost_AC] / 1000000, type number),
\t\t\t\t    #"Added BAC_MNOK" = Table.AddColumn(#"Added AC_MNOK", "Budget_At_Completion_BAC_MNOK", each [BAC_BudgetAtCompletion] / 1000000, type number),
\t\t\t\t    #"Added EAC_MNOK" = Table.AddColumn(#"Added BAC_MNOK", "Estimate_At_Completion_EAC_MNOK", each [EstimateAtCompletion_EAC] / 1000000, type number),
\t\t\t\t    #"Added ETC_MNOK" = Table.AddColumn(#"Added EAC_MNOK", "Estimate_To_Complete_ETC_MNOK", each [EstimateToComplete_ETC] / 1000000, type number),
\t\t\t\t    #"Added VAC_MNOK" = Table.AddColumn(#"Added ETC_MNOK", "Variance_At_Completion_VAC_MNOK", each [VarianceAtCompletion_VAC] / 1000000, type number),
\t\t\t\t    #"Added CPI" = Table.AddColumn(#"Added VAC_MNOK", "Cost_Performance_Index_CPI", each [CostPerformanceIndex_CPI], type number),
\t\t\t\t    #"Added SPI" = Table.AddColumn(#"Added CPI", "Schedule_Performance_Index_SPI", each [SchedulePerformanceIndex_SPI], type number)
\t\t\t\tin
\t\t\t\t    #"Added SPI"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "FactEVM.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_factevm))

    # Table 10: FactFTE
    t_factfte = """table FactFTE
\tlineageTag: [[GUID]]

\tcolumn DatoNokkel
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: DatoNokkel
\t\tannotation SummarizationSetBy = Automatic

\tcolumn OrgKode
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: OrgKode
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Budsjettansvarsområde
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Budsjettansvarsområde
\t\tannotation SummarizationSetBy = Automatic

\tcolumn BudsjettansvarligLeder
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: BudsjettansvarligLeder
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Stillingstype
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Stillingstype
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Aarsverk
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Aarsverk
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Budsjettert_Aarsverk
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Budsjettert_Aarsverk
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Aarsverk_UF
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Aarsverk_UF
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Aarsverk_TA
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Aarsverk_TA
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Aarsverk_Totalt
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Aarsverk_Totalt
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Vakans_Aarsverk
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Vakans_Aarsverk
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Antall_Ansatte
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Antall_Ansatte
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Vakansgrad_Pct
\t\tdataType: double
\t\tformatString: 0.0%
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: average
\t\tsourceColumn: Vakansgrad_Pct
\t\tannotation SummarizationSetBy = Automatic

\tpartition FactFTE = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\HHU\\FactFTE.csv"),[Delimiter=";", Columns=11, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"DatoNokkel", Int64.Type}, {"OrgKode", type text}, {"Budsjettansvarsområde", type text}, {"BudsjettansvarligLeder", type text}, {"Aarsverk_UF", type number}, {"Aarsverk_TA", type number}, {"Aarsverk_Totalt", type number}, {"Budsjettert_Aarsverk", type number}, {"Vakans_Aarsverk", type number}, {"Antall_Ansatte", Int64.Type}, {"Vakansgrad_Pct", type number}}),
\t\t\t\t    #"Added UF Ratio" = Table.AddColumn(#"Changed Type", "UF_Ratio", each if [Aarsverk_Totalt] = 0 then 0.5 else [Aarsverk_UF] / [Aarsverk_Totalt], type number),
\t\t\t\t    #"UF Table" = Table.AddColumn(Table.AddColumn(Table.AddColumn(#"Added UF Ratio", "Stillingstype", each "UF", type text), "Aarsverk", each [Aarsverk_UF], type number), "Budsjett_ÅV", each [Budsjettert_Aarsverk] * [UF_Ratio], type number),
\t\t\t\t    #"TA Table" = Table.AddColumn(Table.AddColumn(Table.AddColumn(#"Added UF Ratio", "Stillingstype", each "TA", type text), "Aarsverk", each [Aarsverk_TA], type number), "Budsjett_ÅV", each [Budsjettert_Aarsverk] * (1 - [UF_Ratio]), type number),
\t\t\t\t    #"Combined" = Table.Combine({#"UF Table", #"TA Table"}),
\t\t\t\t    #"Removed Columns" = Table.RemoveColumns(#"Combined", {"UF_Ratio", "Budsjettert_Aarsverk"}),
\t\t\t\t    #"Renamed Columns" = Table.RenameColumns(#"Removed Columns", {{"Budsjett_ÅV", "Budsjettert_Aarsverk"}})
\t\t\t\tin
\t\t\t\t    #"Renamed Columns"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "FactFTE.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_factfte))

    # Table 11: FactFTE_2027
    t_factfte2027 = """table FactFTE_2027
\tlineageTag: [[GUID]]

\tcolumn FTENokkel
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: FTENokkel
\t\tannotation SummarizationSetBy = Automatic

\tcolumn DatoNokkel
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: DatoNokkel
\t\tannotation SummarizationSetBy = Automatic

\tcolumn OrgKode
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: OrgKode
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Budsjettert_Aarsverk
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Budsjettert_Aarsverk
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Vakans_Aarsverk
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Vakans_Aarsverk
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Aarsverk_Totalt
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Aarsverk_Totalt
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Aarsverk_UF
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Aarsverk_UF
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Aarsverk_TA
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Aarsverk_TA
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Antall_Ansatte
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Antall_Ansatte
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Maanedlig_Lonnskostnad
\t\tdataType: double
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Maanedlig_Lonnskostnad
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Lennsandel_Pct
\t\tdataType: double
\t\tformatString: 0.0%
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: average
\t\tsourceColumn: Lennsandel_Pct
\t\tannotation SummarizationSetBy = Automatic

\tpartition FactFTE_2027 = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\HHU\\FactFTE_2027.csv"),[Delimiter=";", Columns=11, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"FTENokkel", type text}, {"DatoNokkel", Int64.Type}, {"OrgKode", type text}, {"Budsjettert_Aarsverk", type number}, {"Vakans_Aarsverk", type number}, {"Aarsverk_Totalt", type number}, {"Aarsverk_UF", type number}, {"Aarsverk_TA", type number}, {"Antall_Ansatte", Int64.Type}, {"Maanedlig_Lonnskostnad", type number}, {"Lennsandel_Pct", type number}})
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "FactFTE_2027.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_factfte2027))

    # Table 12: FactAction
    t_factaction = """table FactAction
\tlineageTag: [[GUID]]

\tcolumn TiltakID
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: TiltakID
\t\tannotation SummarizationSetBy = Automatic

\tcolumn OrgKode
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: OrgKode
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Budsjettansvarsområde
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Budsjettansvarsområde
\t\tannotation SummarizationSetBy = Automatic

\tcolumn AnsvarligLeder
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: AnsvarligLeder
\t\tannotation SummarizationSetBy = Automatic

\tcolumn TiltakNavn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: TiltakNavn
\t\tannotation SummarizationSetBy = Automatic

\tcolumn ForventetInnsparingNOK
\t\tdataType: double
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: ForventetInnsparingNOK
\t\tannotation SummarizationSetBy = Automatic

\tcolumn RealisertInnsparingNOK
\t\tdataType: double
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: RealisertInnsparingNOK
\t\tannotation SummarizationSetBy = Automatic

\tcolumn ForventetEffekt
\t\tdataType: double
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: ForventetEffekt
\t\tannotation SummarizationSetBy = Automatic

\tcolumn RealisertEffekt
\t\tdataType: double
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: RealisertEffekt
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Status
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Status
\t\tannotation SummarizationSetBy = Automatic

\tcolumn FristDato
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: FristDato
\t\tannotation SummarizationSetBy = Automatic

\tpartition FactAction = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\HHU\\FactAction.csv"),[Delimiter=";", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"TiltakID", type text}, {"OrgKode", type text}, {"Budsjettansvarsområde", type text}, {"AnsvarligLeder", type text}, {"TiltakNavn", type text}, {"ForventetInnsparingNOK", type number}, {"RealisertInnsparingNOK", type number}, {"Status", type text}, {"FristDato", type text}}),
\t\t\t\t    #"Added ForventetEffekt" = Table.AddColumn(#"Changed Type", "ForventetEffekt", each [ForventetInnsparingNOK], type number),
\t\t\t\t    #"Added RealisertEffekt" = Table.AddColumn(#"Added ForventetEffekt", "RealisertEffekt", each [RealisertInnsparingNOK], type number)
\t\t\t\tin
\t\t\t\t    #"Added RealisertEffekt"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "FactAction.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_factaction))

    # Table 13: FactAction_2027
    t_factaction2027 = """table FactAction_2027
\tlineageTag: [[GUID]]

\tcolumn TiltakID
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: TiltakID
\t\tannotation SummarizationSetBy = Automatic

\tcolumn OrgKode
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: OrgKode
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Tiltaksnavn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Tiltaksnavn
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Kategori
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Kategori
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Ansvarlig
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Ansvarlig
\t\tannotation SummarizationSetBy = Automatic

\tcolumn ForventetEffekt
\t\tdataType: double
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: ForventetEffekt
\t\tannotation SummarizationSetBy = Automatic

\tcolumn RealisertEffekt
\t\tdataType: double
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: RealisertEffekt
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Status
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Status
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Beskrivelse
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Beskrivelse
\t\tannotation SummarizationSetBy = Automatic

\tpartition FactAction_2027 = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\HHU\\FactAction_2027.csv"),[Delimiter=";", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"TiltakID", type text}, {"OrgKode", type text}, {"Tiltaksnavn", type text}, {"Kategori", type text}, {"Ansvarlig", type text}, {"ForventetEffekt", type number}, {"RealisertEffekt", type number}, {"Status", type text}, {"Beskrivelse", type text}})
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "FactAction_2027.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_factaction2027))

    # Table 14: FactStudents
    t_factstudents = """table FactStudents
\tlineageTag: [[GUID]]

\tcolumn StudentNokkel
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: StudentNokkel
\t\tannotation SummarizationSetBy = Automatic

\tcolumn DatoNokkel
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: DatoNokkel
\t\tannotation SummarizationSetBy = Automatic

\tcolumn OrgKode
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: OrgKode
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Studieprogram
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Studieprogram
\t\tannotation SummarizationSetBy = Automatic

\tcolumn RegistrerteStudenter
\t\tdataType: int64
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: RegistrerteStudenter
\t\tannotation SummarizationSetBy = Automatic

\tcolumn SPE60_Baseline_2025
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: SPE60_Baseline_2025
\t\tannotation SummarizationSetBy = Automatic

\tcolumn SPE60_Vekst_2025
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: SPE60_Vekst_2025
\t\tannotation SummarizationSetBy = Automatic

\tcolumn SPE60
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: SPE60
\t\tannotation SummarizationSetBy = Automatic

\tcolumn KDKategori
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: KDKategori
\t\tannotation SummarizationSetBy = Automatic

\tcolumn KDSats_NOK
\t\tdataType: double
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: KDSats_NOK
\t\tannotation SummarizationSetBy = Automatic

\tcolumn KD_Marginal_Inntekt_2027
\t\tdataType: double
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: KD_Marginal_Inntekt_2027
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Studenter_pr_UF
\t\tdataType: double
\t\tformatString: 0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: average
\t\tsourceColumn: Studenter_pr_UF
\t\tannotation SummarizationSetBy = Automatic

\tcolumn StudenterPrUF
\t\tdataType: double
\t\tformatString: 0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: average
\t\tsourceColumn: StudenterPrUF
\t\tannotation SummarizationSetBy = Automatic

\tpartition FactStudents = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\HHU\\FactStudents.csv"),[Delimiter=";", Columns=12, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"StudentNokkel", type text}, {"DatoNokkel", Int64.Type}, {"OrgKode", type text}, {"Studieprogram", type text}, {"RegistrerteStudenter", Int64.Type}, {"SPE60_Baseline_2025", type number}, {"SPE60_Vekst_2025", type number}, {"SPE60", type number}, {"KDKategori", type text}, {"KDSats_NOK", type number}, {"KD_Marginal_Inntekt_2027", type number}, {"Studenter_pr_UF", type number}}),
\t\t\t\t    #"Added StudenterPrUF" = Table.AddColumn(#"Changed Type", "StudenterPrUF", each [Studenter_pr_UF], type number)
\t\t\t\tin
\t\t\t\t    #"Added StudenterPrUF"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "FactStudents.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_factstudents))

    # Table 15: FactStudents_2027
    t_factstudents2027 = """table FactStudents_2027
\tlineageTag: [[GUID]]

\tcolumn StudentNokkel
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: StudentNokkel
\t\tannotation SummarizationSetBy = Automatic

\tcolumn DatoNokkel
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: DatoNokkel
\t\tannotation SummarizationSetBy = Automatic

\tcolumn OrgKode
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: OrgKode
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Studieprogram
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Studieprogram
\t\tannotation SummarizationSetBy = Automatic

\tcolumn RegistrerteStudenter
\t\tdataType: int64
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: RegistrerteStudenter
\t\tannotation SummarizationSetBy = Automatic

\tcolumn SPE60_Baseline_2025
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: SPE60_Baseline_2025
\t\tannotation SummarizationSetBy = Automatic

\tcolumn SPE60_Vekst_2025
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: SPE60_Vekst_2025
\t\tannotation SummarizationSetBy = Automatic

\tcolumn SPE60
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: SPE60
\t\tannotation SummarizationSetBy = Automatic

\tcolumn KDKategori
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: KDKategori
\t\tannotation SummarizationSetBy = Automatic

\tcolumn KDSats_NOK
\t\tdataType: double
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: KDSats_NOK
\t\tannotation SummarizationSetBy = Automatic

\tcolumn KD_Marginal_Inntekt_2027
\t\tdataType: double
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: KD_Marginal_Inntekt_2027
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Studenter_pr_UF
\t\tdataType: double
\t\tformatString: 0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: average
\t\tsourceColumn: Studenter_pr_UF
\t\tannotation SummarizationSetBy = Automatic

\tcolumn StudenterPrUF
\t\tdataType: double
\t\tformatString: 0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: average
\t\tsourceColumn: StudenterPrUF
\t\tannotation SummarizationSetBy = Automatic

\tpartition FactStudents_2027 = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\HHU\\FactStudents_2027.csv"),[Delimiter=";", Columns=12, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"StudentNokkel", type text}, {"DatoNokkel", Int64.Type}, {"OrgKode", type text}, {"Studieprogram", type text}, {"RegistrerteStudenter", Int64.Type}, {"SPE60_Baseline_2025", type number}, {"SPE60_Vekst_2025", type number}, {"SPE60", type number}, {"KDKategori", type text}, {"KDSats_NOK", type number}, {"KD_Marginal_Inntekt_2027", type number}, {"Studenter_pr_UF", type number}}),
\t\t\t\t    #"Added StudenterPrUF" = Table.AddColumn(#"Changed Type", "StudenterPrUF", each [Studenter_pr_UF], type number)
\t\t\t\tin
\t\t\t\t    #"Added StudenterPrUF"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "FactStudents_2027.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_factstudents2027))

    # Table 16: _Measures
    measures = parse_dax_measures()
    measures_tmdl = build_measures_tmdl(measures)
    with open(os.path.join(SEMANTIC_DIR, "tables", "_Measures.tmdl"), "w", encoding="utf-8") as f:
        f.write(measures_tmdl)
        
    print(f"Successfully wrote semantic model with 16 tables and {len(measures)} measures.")

if __name__ == "__main__":
    write_tmdl_semantic_model()
