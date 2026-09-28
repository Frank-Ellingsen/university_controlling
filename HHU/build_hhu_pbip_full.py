"""
Orchestrator to update HHU-Rapport.pbip (TMDL Semantic Model + PBIR Report Pages)
with the complete reporting and dashboards from UIA-Handelshøyskolen USE-CASE.xlsx.
"""
import os
import shutil
import uuid
import json
import re
import openpyxl
import pandas as pd

HHU_DIR = r"c:\Users\frank\Desktop\UIA2\HHU"
SEMANTIC_DIR = os.path.join(HHU_DIR, "HHU-Rapport.SemanticModel", "definition")
REPORT_DIR = os.path.join(HHU_DIR, "HHU-Rapport.Report")
PAGES_DIR = os.path.join(REPORT_DIR, "definition", "pages")
EXCEL_PATH = os.path.join(HHU_DIR, "UIA-Handelshøyskolen USE-CASE.xlsx")

def gen_guid():
    return str(uuid.uuid4())

def fill_guids(text):
    while "[[GUID]]" in text:
        text = text.replace("[[GUID]]", gen_guid(), 1)
    return text

def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def export_all_csvs():
    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)

    # 1. FactVarianceDriver
    va = wb['Variance Actions']
    vd_rows = []
    for r in list(va.iter_rows(values_only=True))[10:21]:
        if r[0]:
            vd_rows.append({
                'OrgKode': str(r[0]).strip(),
                'Konto': int(r[1]) if r[1] else 0,
                'Avviksdriver': str(r[2]).strip(),
                'BudsjettBelop': float(r[3]) if r[3] else 0.0,
                'PrognoseLE': float(r[4]) if r[4] else 0.0,
                'AvvikBelop': float(r[5]) if r[5] else 0.0,
                'AvvikProsent': float(r[6]) if r[6] else 0.0,
                'RAG_Status': str(r[7]).strip() if r[7] else ''
            })
    df_vd = pd.DataFrame(vd_rows)
    df_vd.to_csv(os.path.join(HHU_DIR, "FactVarianceDriver.csv"), sep=';', index=False, encoding='utf-8-sig')

    # 2. FactMonthHotspot
    mh_rows = []
    for r in list(va.iter_rows(values_only=True))[10:14]:
        if r[9]:
            mh_rows.append({
                'Maaned': str(r[9]).strip(),
                'AvvikBelop': float(r[10]) if r[10] else 0.0,
                'Forklaring': str(r[11]).strip() if r[11] else ''
            })
    df_mh = pd.DataFrame(mh_rows)
    df_mh.to_csv(os.path.join(HHU_DIR, "FactMonthHotspot.csv"), sep=';', index=False, encoding='utf-8-sig')

    # 3. FactActionPlan
    ap_rows = []
    for r in list(va.iter_rows(values_only=True))[25:30]:
        if r[0]:
            ap_rows.append({
                'Prio': int(r[0]),
                'Omraade': str(r[1]).strip(),
                'Rotaarsak': str(r[2]).strip(),
                'AnbefaltHandling': str(r[3]).strip(),
                'AnsvarligEier': str(r[4]).strip(),
                'FristDato': str(r[5])[:10] if r[5] else '',
                'BruttoGapNOK': float(r[6]) if r[6] else 0.0,
                'ForventetEffektNOK': float(r[7]) if r[7] else 0.0,
                'KPI_Kontrollpunkt': str(r[8]).strip() if r[8] else '',
                'RAG_Status': str(r[9]).strip() if r[9] else '',
                'BeslutningNaa': str(r[10]).strip() if r[10] else '',
                'Oppfoelging': str(r[11]).strip() if r[11] else ''
            })
    df_ap = pd.DataFrame(ap_rows)
    df_ap.to_csv(os.path.join(HHU_DIR, "FactActionPlan.csv"), sep=';', index=False, encoding='utf-8-sig')

    # 4. FactDecisionGate
    bp = wb['Budget Process 2027']
    dg_rows = []
    for r in list(bp.iter_rows(values_only=True))[11:17]:
        if r[0]:
            dg_rows.append({
                'PortNummer': int(r[0]),
                'Periode': str(r[1]).strip() if r[1] else '',
                'Hovedspoersmaal': str(r[2]).strip() if r[2] else '',
                'Aktivitet': str(r[3]).strip() if r[3] else '',
                'Inndata': str(r[4]).strip() if r[4] else '',
                'Ansvarlig': str(r[5]).strip() if r[5] else '',
                'Leveranse': str(r[6]).strip() if r[6] else '',
                'Arena': str(r[7]).strip() if r[7] else '',
                'Status': str(r[8]).strip() if r[8] else '',
                'RAG_Ikon': str(r[9]).strip() if r[9] else '',
                'Kriterier': str(r[10]).strip() if r[10] else '',
                'Forutsetninger': str(r[11]).strip() if r[11] else '',
                'Tiltak': str(r[12]).strip() if r[12] else '',
                'FristDato': str(r[13])[:10] if r[13] else ''
            })
    df_dg = pd.DataFrame(dg_rows)
    df_dg.to_csv(os.path.join(HHU_DIR, "FactDecisionGate.csv"), sep=';', index=False, encoding='utf-8-sig')

    # 5. FactDriverAnalysis
    da_rows = []
    for r in list(bp.iter_rows(values_only=True))[21:27]:
        if r[0]:
            da_rows.append({
                'DriverNavn': str(r[0]).strip(),
                'Mekanisme': str(r[1]).strip() if r[1] else '',
                'Kvantifisering': str(r[2]).strip() if r[2] else '',
                'Helaarseffekt': str(r[3]).strip() if r[3] else '',
                'Risiko': str(r[4]).strip() if r[4] else '',
                'Kontroll': str(r[5]).strip() if r[5] else '',
                'AnsvarligEier': str(r[6]).strip() if r[6] else '',
                'Avstemming': str(r[7]).strip() if r[7] else '',
                'Modellverdi': float(r[8]) if isinstance(r[8], (int, float)) else 0.0,
                'Referanseverdi': float(r[9]) if isinstance(r[9], (int, float)) else 0.0,
                'Differanse': float(r[10]) if isinstance(r[10], (int, float)) else 0.0,
                'RAG_Status': str(r[11]).strip() if r[11] else '',
                'Konklusjon': str(r[12]).strip() if r[12] else ''
            })
    df_da = pd.DataFrame(da_rows)
    df_da.to_csv(os.path.join(HHU_DIR, "FactDriverAnalysis.csv"), sep=';', index=False, encoding='utf-8-sig')

    # 6. FactClosurePlan
    cp_rows = []
    for r in list(bp.iter_rows(values_only=True))[40:46]:
        if r[0]:
            cp_rows.append({
                'Prio': int(r[0]),
                'AvvikRisiko': str(r[1]).strip() if r[1] else '',
                'PaakrevdHandling': str(r[2]).strip() if r[2] else '',
                'AnsvarligEier': str(r[3]).strip() if r[3] else '',
                'FristDato': str(r[4])[:10] if r[4] else '',
                'BevisFerdigkriterium': str(r[5]).strip() if r[5] else '',
                'Konsekvens': str(r[6]).strip() if r[6] else '',
                'RAG_Status': str(r[7]).strip() if r[7] else ''
            })
    df_cp = pd.DataFrame(cp_rows)
    df_cp.to_csv(os.path.join(HHU_DIR, "FactClosurePlan.csv"), sep=';', index=False, encoding='utf-8-sig')

    # 7. FactForecastMethod
    fm = wb['Forecast Methods 2027']
    fm_rows = []
    for r in list(fm.iter_rows(values_only=True))[10:21]:
        if r[0]:
            fm_rows.append({
                'Prio': str(r[0]).strip(),
                'Budsjettpost': str(r[1]).strip() if r[1] else '',
                'KontoTabell': str(r[2]).strip() if r[2] else '',
                'Baseline2027': float(r[3]) if isinstance(r[3], (int, float)) else 0.0,
                'Prognosemetode': str(r[4]).strip() if r[4] else '',
                'DriverInput': str(r[5]).strip() if r[5] else '',
                'OperativBeregning': str(r[6]).strip() if r[6] else '',
                'Oppdateringsfrekvens': str(r[7]).strip() if r[7] else ''
            })
    df_fm = pd.DataFrame(fm_rows)
    df_fm.to_csv(os.path.join(HHU_DIR, "FactForecastMethod.csv"), sep=';', index=False, encoding='utf-8-sig')

    # 8. FactRoutineStep
    rs_rows = []
    for r in list(fm.iter_rows(values_only=True))[26:32]:
        if r[0] is not None and isinstance(r[0], int):
            rs_rows.append({
                'TrinnNummer': int(r[0]),
                'FormelMetode': str(r[1]).strip() if r[1] else '',
                'Forklaring': str(r[2]).strip() if r[2] else '',
                'Kontrollaktivitet': str(r[3]).strip() if r[3] else '',
                'MaanedligTidslinje': f"{r[4] or ''} ({r[5] or ''} | {r[6] or ''} | {r[7] or ''})".strip()
            })
    df_rs = pd.DataFrame(rs_rows)
    df_rs.to_csv(os.path.join(HHU_DIR, "FactRoutineStep.csv"), sep=';', index=False, encoding='utf-8-sig')

    # 9. FactPlan2027Unit
    pr = wb['2027 Plan Report']
    pu_rows = []
    for r in list(pr.iter_rows(values_only=True))[11:15]:
        if r[0]:
            pu_rows.append({
                'OrgKode': str(r[0]).strip(),
                'Enhetsnavn': str(r[1]).strip() if r[1] else '',
                'InntekterNOK': float(r[2]) if r[2] else 0.0,
                'KostnaderNOK': float(r[3]) if r[3] else 0.0,
                'NettoResultatNOK': float(r[4]) if r[4] else 0.0,
                'AarsverkTotalt': float(r[5]) if r[5] else 0.0,
                'UFAarsverk': float(r[6]) if r[6] else 0.0,
                'Studenter': float(r[7]) if r[7] else 0.0,
                'SPE60': float(r[8]) if r[8] else 0.0
            })
    df_pu = pd.DataFrame(pu_rows)
    df_pu.to_csv(os.path.join(HHU_DIR, "FactPlan2027Unit.csv"), sep=';', index=False, encoding='utf-8-sig')

    print("Successfully exported all 9 CSV files from Excel.")

NEW_TABLES_SPEC = {
    'FactVarianceDriver': {
        'csv': r"C:\Users\frank\Desktop\UIA2\HHU\FactVarianceDriver.csv",
        'columns': [
            ('OrgKode', 'string', None, 'none'),
            ('Konto', 'int64', None, 'none'),
            ('Avviksdriver', 'string', None, 'none'),
            ('BudsjettBelop', 'double', '#,##0', 'sum'),
            ('PrognoseLE', 'double', '#,##0', 'sum'),
            ('AvvikBelop', 'double', '#,##0', 'sum'),
            ('AvvikProsent', 'double', '0.0%', 'none'),
            ('RAG_Status', 'string', None, 'none'),
        ]
    },
    'FactMonthHotspot': {
        'csv': r"C:\Users\frank\Desktop\UIA2\HHU\FactMonthHotspot.csv",
        'columns': [
            ('Maaned', 'string', None, 'none'),
            ('AvvikBelop', 'double', '#,##0', 'sum'),
            ('Forklaring', 'string', None, 'none'),
        ]
    },
    'FactActionPlan': {
        'csv': r"C:\Users\frank\Desktop\UIA2\HHU\FactActionPlan.csv",
        'columns': [
            ('Prio', 'int64', '0', 'none'),
            ('Omraade', 'string', None, 'none'),
            ('Rotaarsak', 'string', None, 'none'),
            ('AnbefaltHandling', 'string', None, 'none'),
            ('AnsvarligEier', 'string', None, 'none'),
            ('FristDato', 'string', None, 'none'),
            ('BruttoGapNOK', 'double', '#,##0', 'sum'),
            ('ForventetEffektNOK', 'double', '#,##0', 'sum'),
            ('KPI_Kontrollpunkt', 'string', None, 'none'),
            ('RAG_Status', 'string', None, 'none'),
            ('BeslutningNaa', 'string', None, 'none'),
            ('Oppfoelging', 'string', None, 'none'),
        ]
    },
    'FactDecisionGate': {
        'csv': r"C:\Users\frank\Desktop\UIA2\HHU\FactDecisionGate.csv",
        'columns': [
            ('PortNummer', 'int64', '0', 'none'),
            ('Periode', 'string', None, 'none'),
            ('Hovedspoersmaal', 'string', None, 'none'),
            ('Aktivitet', 'string', None, 'none'),
            ('Inndata', 'string', None, 'none'),
            ('Ansvarlig', 'string', None, 'none'),
            ('Leveranse', 'string', None, 'none'),
            ('Arena', 'string', None, 'none'),
            ('Status', 'string', None, 'none'),
            ('RAG_Ikon', 'string', None, 'none'),
            ('Kriterier', 'string', None, 'none'),
            ('Forutsetninger', 'string', None, 'none'),
            ('Tiltak', 'string', None, 'none'),
            ('FristDato', 'string', None, 'none'),
        ]
    },
    'FactDriverAnalysis': {
        'csv': r"C:\Users\frank\Desktop\UIA2\HHU\FactDriverAnalysis.csv",
        'columns': [
            ('DriverNavn', 'string', None, 'none'),
            ('Mekanisme', 'string', None, 'none'),
            ('Kvantifisering', 'string', None, 'none'),
            ('Helaarseffekt', 'string', None, 'none'),
            ('Risiko', 'string', None, 'none'),
            ('Kontroll', 'string', None, 'none'),
            ('AnsvarligEier', 'string', None, 'none'),
            ('Avstemming', 'string', None, 'none'),
            ('Modellverdi', 'double', '#,##0.0', 'sum'),
            ('Referanseverdi', 'double', '#,##0.0', 'sum'),
            ('Differanse', 'double', '#,##0.0', 'sum'),
            ('RAG_Status', 'string', None, 'none'),
            ('Konklusjon', 'string', None, 'none'),
        ]
    },
    'FactClosurePlan': {
        'csv': r"C:\Users\frank\Desktop\UIA2\HHU\FactClosurePlan.csv",
        'columns': [
            ('Prio', 'int64', '0', 'none'),
            ('AvvikRisiko', 'string', None, 'none'),
            ('PaakrevdHandling', 'string', None, 'none'),
            ('AnsvarligEier', 'string', None, 'none'),
            ('FristDato', 'string', None, 'none'),
            ('BevisFerdigkriterium', 'string', None, 'none'),
            ('Konsekvens', 'string', None, 'none'),
            ('RAG_Status', 'string', None, 'none'),
        ]
    },
    'FactForecastMethod': {
        'csv': r"C:\Users\frank\Desktop\UIA2\HHU\FactForecastMethod.csv",
        'columns': [
            ('Prio', 'string', None, 'none'),
            ('Budsjettpost', 'string', None, 'none'),
            ('KontoTabell', 'string', None, 'none'),
            ('Baseline2027', 'double', '#,##0', 'sum'),
            ('Prognosemetode', 'string', None, 'none'),
            ('DriverInput', 'string', None, 'none'),
            ('OperativBeregning', 'string', None, 'none'),
            ('Oppdateringsfrekvens', 'string', None, 'none'),
        ]
    },
    'FactRoutineStep': {
        'csv': r"C:\Users\frank\Desktop\UIA2\HHU\FactRoutineStep.csv",
        'columns': [
            ('TrinnNummer', 'int64', '0', 'none'),
            ('FormelMetode', 'string', None, 'none'),
            ('Forklaring', 'string', None, 'none'),
            ('Kontrollaktivitet', 'string', None, 'none'),
            ('MaanedligTidslinje', 'string', None, 'none'),
        ]
    },
    'FactPlan2027Unit': {
        'csv': r"C:\Users\frank\Desktop\UIA2\HHU\FactPlan2027Unit.csv",
        'columns': [
            ('OrgKode', 'string', None, 'none'),
            ('Enhetsnavn', 'string', None, 'none'),
            ('InntekterNOK', 'double', '#,##0', 'sum'),
            ('KostnaderNOK', 'double', '#,##0', 'sum'),
            ('NettoResultatNOK', 'double', '#,##0', 'sum'),
            ('AarsverkTotalt', 'double', '0.0', 'sum'),
            ('UFAarsverk', 'double', '0.0', 'sum'),
            ('Studenter', 'double', '#,##0', 'sum'),
            ('SPE60', 'double', '#,##0', 'sum'),
        ]
    }
}

def make_tmdl(table_name, cols_spec, csv_file, delimiter=";"):
    lines = []
    lines.append(f"table {table_name}")
    lines.append(f"\tlineageTag: [[GUID]]\n")
    
    col_transforms = []
    for col_name, col_type, col_format, summarize in cols_spec:
        lines.append(f"\tcolumn {col_name}")
        lines.append(f"\t\tdataType: {col_type}")
        if col_format:
            lines.append(f"\t\tformatString: {col_format}")
        lines.append(f"\t\tlineageTag: [[GUID]]")
        lines.append(f"\t\tsummarizeBy: {summarize}")
        lines.append(f"\t\tsourceColumn: {col_name}\n")
        lines.append(f"\t\tannotation SummarizationSetBy = Automatic\n")
        
        m_type = "type text" if col_type == "string" else ("type number" if col_type == "double" else "Int64.Type")
        col_transforms.append(f'{{"{col_name}", {m_type}}}')
        
    transforms_str = ", ".join(col_transforms)
    lines.append(f"\tpartition {table_name} = m")
    lines.append(f"\t\tmode: import")
    lines.append(f"\t\tsource =")
    lines.append(f"\t\t\t\tlet")
    lines.append(f'\t\t\t\t    Source = Csv.Document(File.Contents("{csv_file}"),[Delimiter="{delimiter}", Columns={len(cols_spec)}, Encoding=65001, QuoteStyle=QuoteStyle.None]),')
    lines.append(f'\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),')
    lines.append(f'\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{{transforms_str}}})')
    lines.append(f'\t\t\t\tin')
    lines.append(f'\t\t\t\t    #"Changed Type"\n')
    lines.append(f"\tannotation PBI_ResultType = Table\n")
    return fill_guids("\n".join(lines))

def update_semantic_model():
    tables_dir = os.path.join(SEMANTIC_DIR, "tables")
    os.makedirs(tables_dir, exist_ok=True)

    # 1. Write the 9 new TMDL tables
    for tname, spec in NEW_TABLES_SPEC.items():
        tmdl_path = os.path.join(tables_dir, f"{tname}.tmdl")
        content = make_tmdl(tname, spec['columns'], spec['csv'])
        with open(tmdl_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Wrote table {tname}.tmdl")

    # 2. Update model.tmdl to reference all 25 tables
    all_tables = [
        "DimAccountHierarchy", "DimDate", "DimDate_2027", "DimForecastVersion", "DimOrganization",
        "FactAction", "FactAction_2027", "FactBudget", "FactBudget_2027", "FactEVM",
        "FactFTE", "FactFTE_2027", "FactGL", "FactStudents", "FactStudents_2027",
        "FactVarianceDriver", "FactMonthHotspot", "FactActionPlan", "FactDecisionGate",
        "FactDriverAnalysis", "FactClosurePlan", "FactForecastMethod", "FactRoutineStep",
        "FactPlan2027Unit", "_Measures"
    ]
    query_order_str = json.dumps(all_tables)
    ref_tables_str = "\n".join([f"ref table {t}" for t in all_tables])
    
    model_content = f"""model Model
\tculture: en-US
\tdefaultPowerBIDataSourceVersion: powerBI_V3
\tsourceQueryCulture: en-US
\tvalueFilterBehavior: independent
\tdataAccessOptions
\t\tlegacyRedirects
\t\treturnErrorValuesAsNull

annotation __PBI_TimeIntelligenceEnabled = 1

annotation PBI_ProTooling = ["DevMode","TMDL-Extension"]

annotation PBI_QueryOrder = {query_order_str}

{ref_tables_str}

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
    print("Updated model.tmdl with 25 tables.")

    # 3. Update relationships.tmdl to include new relationships
    rel_path = os.path.join(SEMANTIC_DIR, "relationships.tmdl")
    with open(rel_path, "r", encoding="utf-8") as f:
        rel_text = f.read()

    new_rels = ""
    if "rel_factvariancedriver_dimorg" not in rel_text:
        new_rels += """
relationship rel_factvariancedriver_dimorg
\tfromColumn: FactVarianceDriver.OrgKode
\ttoColumn: DimOrganization.OrgKode
"""
    if "rel_factplan2027unit_dimorg" not in rel_text:
        new_rels += """
relationship rel_factplan2027unit_dimorg
\tfromColumn: FactPlan2027Unit.OrgKode
\ttoColumn: DimOrganization.OrgKode
"""
    if new_rels:
        with open(rel_path, "a", encoding="utf-8") as f:
            f.write(new_rels)
        print("Appended new relationships to relationships.tmdl.")

    # 4. Add new measures to _Measures.tmdl
    from build_hhu_rapport_pbip import parse_dax_measures, build_measures_tmdl
    measures = parse_dax_measures()

    extra_new_measures = [
        {
            'name': 'Samlet Tiltakseffekt Handlingsplan',
            'desc': 'Summert forventet effekt av prioriterte tiltak i handlingsplan',
            'folder': '_07 Omstilling & Tiltak',
            'expr': "SUM('FactActionPlan'[ForventetEffektNOK])",
            'formatString': '#,##0 kr'
        },
        {
            'name': 'Samlet Brutto Gap Handlingsplan',
            'desc': 'Summert brutto gap som krever tiltak',
            'folder': '_07 Omstilling & Tiltak',
            'expr': "SUM('FactActionPlan'[BruttoGapNOK])",
            'formatString': '#,##0 kr'
        },
        {
            'name': 'Netto Restrisiko Handlingsplan',
            'desc': 'Netto gjenværende gap etter planlagt tiltakseffekt',
            'folder': '_07 Omstilling & Tiltak',
            'expr': "[Samlet Brutto Gap Handlingsplan] - [Samlet Tiltakseffekt Handlingsplan]",
            'formatString': '#,##0 kr'
        },
        {
            'name': 'Antall Tiltak i Handlingsplan',
            'desc': 'Antall prioriterte tiltak i handlingsplanen',
            'folder': '_07 Omstilling & Tiltak',
            'expr': "COUNTROWS('FactActionPlan')",
            'formatString': '0'
        },
        {
            'name': 'Antall Avviksdrivere',
            'desc': 'Antall identifiserte rotårsaksdrivere for avvik',
            'folder': '_03 Avvik & Varians',
            'expr': "COUNTROWS('FactVarianceDriver')",
            'formatString': '0'
        },
        {
            'name': 'Største Enkeltavvik MNOK',
            'desc': 'Største negative enkeltavvik blant driverne i MNOK',
            'folder': '_03 Avvik & Varians',
            'expr': "DIVIDE(MIN('FactVarianceDriver'[AvvikBelop]), 1000000, 0)",
            'formatString': '#,##0.0 MNOK'
        },
        {
            'name': 'Budsjett 2027 Inntektsgap MNOK',
            'desc': 'Identifisert rammegap mellom kildemodell og vedtatt ramme',
            'folder': '_08 RAG & Design',
            'expr': "2.0",
            'formatString': '0.0 MNOK'
        },
        {
            'name': '2027 Ramme Plan Inntekt MNOK',
            'desc': 'Summert planlagt inntektsramme for 2027 per enhet',
            'folder': '_01 Accounting',
            'expr': "DIVIDE(SUM('FactPlan2027Unit'[InntekterNOK]), 1000000, 0)",
            'formatString': '#,##0.0 MNOK'
        },
        {
            'name': '2027 Ramme Plan Kostnad MNOK',
            'desc': 'Summert planlagte kostnader for 2027 per enhet',
            'folder': '_01 Accounting',
            'expr': "DIVIDE(SUM('FactPlan2027Unit'[KostnaderNOK]), 1000000, 0)",
            'formatString': '#,##0.0 MNOK'
        },
        {
            'name': '2027 Ramme Plan Netto MNOK',
            'desc': 'Summert planlagt nettoresultat for 2027 per enhet',
            'folder': '_01 Accounting',
            'expr': "DIVIDE(SUM('FactPlan2027Unit'[NettoResultatNOK]), 1000000, 0)",
            'formatString': '+#,##0.0 MNOK'
        },
        {
            'name': '2027 Plan Årsverk',
            'desc': 'Summert planlagte årsverk for 2027',
            'folder': '_05 Staffing & FTE',
            'expr': "SUM('FactPlan2027Unit'[AarsverkTotalt])",
            'formatString': '#,##0.0 ÅV'
        },
        {
            'name': '2027 Plan UF Årsverk',
            'desc': 'Summert planlagte faglige årsverk (UF) for 2027',
            'folder': '_05 Staffing & FTE',
            'expr': "SUM('FactPlan2027Unit'[UFAarsverk])",
            'formatString': '#,##0 ÅV'
        },
        {
            'name': '2027 Plan Studenter',
            'desc': 'Planlagt studentantall for 2027',
            'folder': '_06 Utdanning & SPE60',
            'expr': "SUM('FactPlan2027Unit'[Studenter])",
            'formatString': '#,##0'
        },
        {
            'name': '2027 Plan SPE60',
            'desc': 'Planlagte studiepoengekvivalenter for 2027',
            'folder': '_06 Utdanning & SPE60',
            'expr': "SUM('FactPlan2027Unit'[SPE60])",
            'formatString': '#,##0'
        },
        {
            'name': 'Port 5 Flaskehals Status',
            'desc': 'Status for beslutningsport 5 styringsavstemming',
            'folder': '_08 RAG & Design',
            'expr': '"🔴 Ikke klar (Lønnsandel 66,8% & 2,0M gap)"',
            'formatString': None
        }
    ]

    existing_names = {m['name'] for m in measures}
    for em in extra_new_measures:
        if em['name'] not in existing_names:
            measures.append(em)

    measures_tmdl = build_measures_tmdl(measures)
    with open(os.path.join(tables_dir, "_Measures.tmdl"), "w", encoding="utf-8") as f:
        f.write(measures_tmdl)
    print(f"Updated _Measures.tmdl with {len(measures)} measures.")

if __name__ == '__main__':
    export_all_csvs()
    update_semantic_model()

