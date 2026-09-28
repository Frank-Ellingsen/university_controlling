"""
Build script for Budsjett-HHU2027.pbip:
Generates complete TMDL semantic model and PBIR report pages
for Handelshøyskolen ved UiA (HHU) Budsjett 2027.
"""
import os
import shutil
import json
import uuid

BASE_DIR = r"C:\Users\frank\Desktop\UIA2\Handelshøyskolen\Budsjett2027"
SEMANTIC_DIR = os.path.join(BASE_DIR, "Budsjett-HHU2027.SemanticModel", "definition")
REPORT_DIR = os.path.join(BASE_DIR, "Budsjett-HHU2027.Report")
SOURCE_THEME = r"C:\Users\frank\Desktop\UIA2\Handelshøyskolen\Controller-Handelshøyskolen.Report\StaticResources\RegisteredResources\University-Tufte-Minimalist-20260926.json"

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

def copy_theme():
    dest = os.path.join(REPORT_DIR, "StaticResources", "RegisteredResources", "University-Tufte-Minimalist-20260926.json")
    if os.path.exists(SOURCE_THEME):
        shutil.copy2(SOURCE_THEME, dest)
        print("Copied theme to RegisteredResources")
    else:
        print("Warning: Source theme not found at", SOURCE_THEME)

def write_tmdl_semantic_model():
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

annotation __PBI_TimeIntelligenceEnabled = 0

annotation PBI_ProTooling = ["DevMode","TMDL-Extension"]

annotation PBI_QueryOrder = ["DimAccountHierarchy","DimDate_2027","DimForecastVersion","DimOrganization","FactAction_2027","FactBudget_2027","FactFTE_2027","FactStudents_2027","_Measures"]

ref table DimAccountHierarchy
ref table DimDate_2027
ref table DimForecastVersion
ref table DimOrganization
ref table FactAction_2027
ref table FactBudget_2027
ref table FactFTE_2027
ref table FactStudents_2027
ref table _Measures

ref role Universitetsledelse
ref role Dekan_HHU
ref role Instituttleder_1110
ref role Instituttleder_1120
ref role Instituttleder_1130
ref role Administrasjon_1140

ref cultureInfo en-US
"""
    with open(os.path.join(SEMANTIC_DIR, "model.tmdl"), "w", encoding="utf-8") as f:
        f.write(model_content)

    # 4. relationships.tmdl
    relationships_content = """relationship rel_budget_org
\tfromColumn: FactBudget_2027.OrgKode
\ttoColumn: DimOrganization.OrgKode

relationship rel_budget_account
\tfromColumn: FactBudget_2027.Konto
\ttoColumn: DimAccountHierarchy.Konto

relationship rel_budget_date
\tfromColumn: FactBudget_2027.DatoNokkel
\ttoColumn: DimDate_2027.DatoNokkel

relationship rel_budget_version
\tfromColumn: FactBudget_2027.VersjonKode
\ttoColumn: DimForecastVersion.VersjonKode

relationship rel_fte_org
\tfromColumn: FactFTE_2027.OrgKode
\ttoColumn: DimOrganization.OrgKode

relationship rel_fte_date
\tfromColumn: FactFTE_2027.DatoNokkel
\ttoColumn: DimDate_2027.DatoNokkel

relationship rel_students_org
\tfromColumn: FactStudents_2027.OrgKode
\ttoColumn: DimOrganization.OrgKode

relationship rel_action_org
\tfromColumn: FactAction_2027.OrgKode
\ttoColumn: DimOrganization.OrgKode
"""
    with open(os.path.join(SEMANTIC_DIR, "relationships.tmdl"), "w", encoding="utf-8") as f:
        f.write(relationships_content)

    # 5. Roles
    roles = [
        ("Universitetsledelse", None),
        ("Dekan_HHU", "'DimOrganization'[Fakultetsnavn] == \"HHU\""),
        ("Instituttleder_1110", "'DimOrganization'[OrgKode] == 1110"),
        ("Instituttleder_1120", "'DimOrganization'[OrgKode] == 1120"),
        ("Instituttleder_1130", "'DimOrganization'[OrgKode] == 1130"),
        ("Administrasjon_1140", "'DimOrganization'[OrgKode] == 1140")
    ]
    for r_name, r_filter in roles:
        r_file = os.path.join(SEMANTIC_DIR, "roles", f"{r_name}.tmdl")
        r_body = f"role {r_name}\n\tmodelPermission: read\n\n"
        if r_filter:
            r_body += f"\ttablePermission DimOrganization = {r_filter}\n\n"
        r_body += f"\tannotation PBI_Id = {gen_guid().replace('-', '')}\n"
        with open(r_file, "w", encoding="utf-8") as f:
            f.write(r_body)

    # 6. Tables
    # DimAccountHierarchy
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

\tcolumn Nivaa1_Kontoklasse
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Nivaa1_Kontoklasse
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Nivaa1_Navn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Nivaa1_Navn
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Nivaa2_Kontogruppe
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Nivaa2_Kontogruppe
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Nivaa2_Navn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Nivaa2_Navn
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Nivaa3_Standardkonto
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Nivaa3_Standardkonto
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Nivaa3_Navn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Nivaa3_Navn
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Nivaa4_Underkonto
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Nivaa4_Underkonto
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Nivaa4_Navn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Nivaa4_Navn
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
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\Handelshøyskolen\\Budsjett2027\\DimAccountHierarchy (1).csv"),[Delimiter=";", Columns=12, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"Konto", Int64.Type}, {"Kontonavn", type text}, {"Nivaa1_Kontoklasse", Int64.Type}, {"Nivaa1_Navn", type text}, {"Nivaa2_Kontogruppe", Int64.Type}, {"Nivaa2_Navn", type text}, {"Nivaa3_Standardkonto", Int64.Type}, {"Nivaa3_Navn", type text}, {"Nivaa4_Underkonto", Int64.Type}, {"Nivaa4_Navn", type text}, {"Kontotype", type text}, {"SRS_regnskapslinje", type text}}, "en-US")
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "DimAccountHierarchy.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_dimacc))

    # DimDate_2027
    t_dimdate = """table DimDate_2027
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
\t\tsortByColumn: MaanedNummer
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: MaanedNavn
\t\tannotation SummarizationSetBy = Automatic

\tcolumn MaanedNavnKort
\t\tdataType: string
\t\tsortByColumn: MaanedNummer
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: MaanedNavnKort
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Kvartal
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Kvartal
\t\tannotation SummarizationSetBy = Automatic

\tcolumn AarMaaned
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: AarMaaned
\t\tannotation SummarizationSetBy = Automatic

\tcolumn ErActualYTD
\t\tdataType: boolean
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: ErActualYTD
\t\tannotation SummarizationSetBy = Automatic

\tpartition DimDate_2027 = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\Handelshøyskolen\\Budsjett2027\\DimDate_2027.csv"),[Delimiter=";", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"DatoNokkel", Int64.Type}, {"Dato", type date}, {"Aar", Int64.Type}, {"MaanedNummer", Int64.Type}, {"MaanedNavn", type text}, {"MaanedNavnKort", type text}, {"Kvartal", type text}, {"AarMaaned", type text}, {"ErActualYTD", type logical}}, "en-US")
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "DimDate_2027.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_dimdate))

    # DimForecastVersion
    t_dimver = """table DimForecastVersion
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

\tcolumn VersjonType
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: VersjonType
\t\tannotation SummarizationSetBy = Automatic

\tcolumn GjeldendeDato
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: GjeldendeDato
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Status
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Status
\t\tannotation SummarizationSetBy = Automatic

\tpartition DimForecastVersion = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\Handelshøyskolen\\Budsjett2027\\DimForecastVersion (1).csv"),[Delimiter=";", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"VersjonKode", type text}, {"VersjonNavn", type text}, {"VersjonType", type text}, {"GjeldendeDato", type text}, {"Status", type text}}, "en-US")
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "DimForecastVersion.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_dimver))

    # DimOrganization
    t_dimorg = """table DimOrganization
\tlineageTag: [[GUID]]

\tcolumn OrgKode
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: OrgKode
\t\tannotation SummarizationSetBy = Automatic

\tcolumn OrgNavn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: OrgNavn
\t\tannotation SummarizationSetBy = Automatic

\tcolumn OrgNivaa
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: OrgNivaa
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Fakultetsnavn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Fakultetsnavn
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Virksomhetstype
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Virksomhetstype
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Lokalitet
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Lokalitet
\t\tannotation SummarizationSetBy = Automatic

\thierarchy 'Organisasjonshierarki'
\t\tlineageTag: [[GUID]]

\t\tlevel Fakultet
\t\t\tlineageTag: [[GUID]]
\t\t\tcolumn: Fakultetsnavn

\t\tlevel Enhet
\t\t\tlineageTag: [[GUID]]
\t\t\tcolumn: OrgNavn

\tpartition DimOrganization = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\Handelshøyskolen\\Budsjett2027\\DimOrganization (1).csv"),[Delimiter=";", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"OrgKode", Int64.Type}, {"OrgNavn", type text}, {"OrgNivaa", type text}, {"Fakultetsnavn", type text}, {"Virksomhetstype", type text}, {"Lokalitet", type text}}, "en-US")
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "DimOrganization.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_dimorg))

    # FactAction_2027
    t_factaction = """table FactAction_2027
\tlineageTag: [[GUID]]

\tcolumn TiltakID
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: TiltakID
\t\tannotation SummarizationSetBy = Automatic

\tcolumn TiltakNavn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: TiltakNavn
\t\tannotation SummarizationSetBy = Automatic

\tcolumn OrgKode
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: OrgKode
\t\tannotation SummarizationSetBy = Automatic

\tcolumn OrgNavn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: OrgNavn
\t\tannotation SummarizationSetBy = Automatic

\tcolumn ForventetEffektMNOK
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: ForventetEffektMNOK
\t\tannotation SummarizationSetBy = Automatic

\tcolumn RealisertEffektMNOK
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: RealisertEffektMNOK
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Realiseringsgrad
\t\tdataType: double
\t\tformatString: 0.0 %
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: average
\t\tsourceColumn: Realiseringsgrad
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Status
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Status
\t\tannotation SummarizationSetBy = Automatic

\tcolumn AnsvarligRolle
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: AnsvarligRolle
\t\tannotation SummarizationSetBy = Automatic

\tcolumn StartDato
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: StartDato
\t\tannotation SummarizationSetBy = Automatic

\tcolumn FristDato
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: FristDato
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Prioritet
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Prioritet
\t\tannotation SummarizationSetBy = Automatic

\tpartition FactAction_2027 = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\Handelshøyskolen\\Budsjett2027\\FactAction_2027.csv"),[Delimiter=";", Columns=12, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"TiltakID", type text}, {"TiltakNavn", type text}, {"OrgKode", Int64.Type}, {"OrgNavn", type text}, {"ForventetEffektMNOK", type number}, {"RealisertEffektMNOK", type number}, {"Realiseringsgrad", type number}, {"Status", type text}, {"AnsvarligRolle", type text}, {"StartDato", type text}, {"FristDato", type text}, {"Prioritet", type text}}, "en-US")
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "FactAction_2027.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_factaction))

    # FactBudget_2027
    t_factbudget = """table FactBudget_2027
\tlineageTag: [[GUID]]

\tcolumn DatoNokkel
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: DatoNokkel
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Aar
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Aar
\t\tannotation SummarizationSetBy = Automatic

\tcolumn AarMaaned
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: AarMaaned
\t\tannotation SummarizationSetBy = Automatic

\tcolumn OrgKode
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: OrgKode
\t\tannotation SummarizationSetBy = Automatic

\tcolumn OrgNavn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: OrgNavn
\t\tannotation SummarizationSetBy = Automatic

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

\tcolumn VersjonKode
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: VersjonKode
\t\tannotation SummarizationSetBy = Automatic

\tcolumn BudsjettBelop
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: BudsjettBelop
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Kilde
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Kilde
\t\tannotation SummarizationSetBy = Automatic

\tpartition FactBudget_2027 = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\Handelshøyskolen\\Budsjett2027\\FactBudget_2027.csv"),[Delimiter=";", Columns=10, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"DatoNokkel", Int64.Type}, {"Aar", Int64.Type}, {"AarMaaned", type text}, {"OrgKode", Int64.Type}, {"OrgNavn", type text}, {"Konto", Int64.Type}, {"Kontonavn", type text}, {"VersjonKode", type text}, {"BudsjettBelop", type number}, {"Kilde", type text}}, "en-US")
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "FactBudget_2027.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_factbudget))

    # FactFTE_2027
    t_factfte = """table FactFTE_2027
\tlineageTag: [[GUID]]

\tcolumn DatoNokkel
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: DatoNokkel
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Aar
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Aar
\t\tannotation SummarizationSetBy = Automatic

\tcolumn OrgKode
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: OrgKode
\t\tannotation SummarizationSetBy = Automatic

\tcolumn OrgNavn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: OrgNavn
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Stillingstype
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Stillingstype
\t\tannotation SummarizationSetBy = Automatic

\tcolumn StillingsgruppeNavn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: StillingsgruppeNavn
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Aarsverk
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Aarsverk
\t\tannotation SummarizationSetBy = Automatic

\tcolumn AntallAnsatte
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: AntallAnsatte
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Vakanser
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Vakanser
\t\tannotation SummarizationSetBy = Automatic

\tcolumn SnittLonnNOK
\t\tdataType: int64
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: average
\t\tsourceColumn: SnittLonnNOK
\t\tannotation SummarizationSetBy = Automatic

\tcolumn VersjonKode
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: VersjonKode
\t\tannotation SummarizationSetBy = Automatic

\tpartition FactFTE_2027 = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\Handelshøyskolen\\Budsjett2027\\FactFTE_2027.csv"),[Delimiter=";", Columns=11, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"DatoNokkel", Int64.Type}, {"Aar", Int64.Type}, {"OrgKode", Int64.Type}, {"OrgNavn", type text}, {"Stillingstype", type text}, {"StillingsgruppeNavn", type text}, {"Aarsverk", type number}, {"AntallAnsatte", Int64.Type}, {"Vakanser", type number}, {"SnittLonnNOK", Int64.Type}, {"VersjonKode", type text}}, "en-US")
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "FactFTE_2027.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_factfte))

    # FactStudents_2027
    t_factstudents = """table FactStudents_2027
\tlineageTag: [[GUID]]

\tcolumn OrgKode
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: OrgKode
\t\tannotation SummarizationSetBy = Automatic

\tcolumn OrgNavn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: OrgNavn
\t\tannotation SummarizationSetBy = Automatic

\tcolumn StudieprogramNavn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: StudieprogramNavn
\t\tannotation SummarizationSetBy = Automatic

\tcolumn KDKategori
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: KDKategori
\t\tannotation SummarizationSetBy = Automatic

\tcolumn RegistrerteStudenter
\t\tdataType: int64
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: RegistrerteStudenter
\t\tannotation SummarizationSetBy = Automatic

\tcolumn SPE60_2025_Lag
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: SPE60_2025_Lag
\t\tannotation SummarizationSetBy = Automatic

\tcolumn SPE60_2027_Target
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: SPE60_2027_Target
\t\tannotation SummarizationSetBy = Automatic

\tcolumn KDInntektBeregnetNOK
\t\tdataType: double
\t\tformatString: #,##0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: KDInntektBeregnetNOK
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
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\Handelshøyskolen\\Budsjett2027\\FactStudents_2027.csv"),[Delimiter=";", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"OrgKode", Int64.Type}, {"OrgNavn", type text}, {"StudieprogramNavn", type text}, {"KDKategori", type text}, {"RegistrerteStudenter", Int64.Type}, {"SPE60_2025_Lag", type number}, {"SPE60_2027_Target", type number}, {"KDInntektBeregnetNOK", type number}, {"StudenterPrUF", type number}}, "en-US")
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "FactStudents_2027.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_factstudents))

    # _Measures table
    t_measures = """table _Measures
\tlineageTag: [[GUID]]

\t/// Samlet budsjettert inntekt (positive tall, MNOK)
\tmeasure 'Budsjett Inntekt' =
\t\t\tCALCULATE(
\t\t\t    -SUM('FactBudget_2027'[BudsjettBelop]),
\t\t\t    'DimAccountHierarchy'[Kontotype] = "Inntekt"
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: 01 Økonomi & Resultat
\t\tlineageTag: [[GUID]]

\t/// Samlede budsjetterte driftskostnader (positive tall, MNOK)
\tmeasure 'Budsjett Kostnad' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactBudget_2027'[BudsjettBelop]),
\t\t\t    'DimAccountHierarchy'[Kontotype] = "Kostnad"
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: 01 Økonomi & Resultat
\t\tlineageTag: [[GUID]]

\t/// Netto budsjettert driftsresultat (Inntekt minus Kostnad, MNOK)
\tmeasure 'Budsjett Netto Resultat' = [Budsjett Inntekt] - [Budsjett Kostnad]
\t\tformatString: +#,##0.0;-#,##0.0;0.0
\t\tdisplayFolder: 01 Økonomi & Resultat
\t\tlineageTag: [[GUID]]

\t/// Budsjettert lønnskostnad fast og midlertidig ansatte (MNOK)
\tmeasure 'Budsjett Lønn' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactBudget_2027'[BudsjettBelop]),
\t\t\t    'DimAccountHierarchy'[Nivaa1_Navn] = "Lønnskostnad"
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: 01 Økonomi & Resultat
\t\tlineageTag: [[GUID]]

\t/// Budsjetterte andre driftskostnader inkl. husleie, IKT og konsulenter (MNOK)
\tmeasure 'Budsjett Drift' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactBudget_2027'[BudsjettBelop]),
\t\t\t    'DimAccountHierarchy'[SRS_regnskapslinje] = "Andre driftskostnader"
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: 01 Økonomi & Resultat
\t\tlineageTag: [[GUID]]

\t/// Budsjetterte ordinære avskrivninger inventar og IKT etter SRS 17 (MNOK)
\tmeasure 'Budsjett Avskrivninger' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactBudget_2027'[BudsjettBelop]),
\t\t\t    'DimAccountHierarchy'[SRS_regnskapslinje] = "Av- og nedskrivninger"
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: 01 Økonomi & Resultat
\t\tlineageTag: [[GUID]]

\t/// Statlig basis- og resultatbevilgning over statsbudsjettets Kap. 260 Post 50 (MNOK)
\tmeasure 'Budsjett Bevilgning (KD)' =
\t\t\tCALCULATE(
\t\t\t    -SUM('FactBudget_2027'[BudsjettBelop]),
\t\t\t    'DimAccountHierarchy'[Konto] = 3900
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: 01 Økonomi & Resultat
\t\tlineageTag: [[GUID]]

\t/// Eksternfinansierte BOA- og EVU-inntekter etter SRS 9 og SRS 10 (MNOK)
\tmeasure 'Budsjett BOA & EVU Inntekt' =
\t\t\tCALCULATE(
\t\t\t    -SUM('FactBudget_2027'[BudsjettBelop]),
\t\t\t    'DimAccountHierarchy'[Konto] IN {3400, 3600, 3030}
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: 01 Økonomi & Resultat
\t\tlineageTag: [[GUID]]

\t/// Lønnskostnadenes andel av samlede driftskostnader (Sektornorm: 62 - 65 %)
\tmeasure 'Lønnsandel %' = DIVIDE([Budsjett Lønn], [Budsjett Kostnad])
\t\tformatString: 0.0 %
\t\tdisplayFolder: 01 Økonomi & Resultat
\t\tlineageTag: [[GUID]]

\t/// Driftskostnadenes andel av samlede kostnader
\tmeasure 'Driftsandel %' = DIVIDE([Budsjett Drift], [Budsjett Kostnad])
\t\tformatString: 0.0 %
\t\tdisplayFolder: 01 Økonomi & Resultat
\t\tlineageTag: [[GUID]]

\t/// Driftsmargin i prosent av samlet inntekt
\tmeasure 'Driftsmargin %' = DIVIDE([Budsjett Netto Resultat], [Budsjett Inntekt])
\t\tformatString: 0.0 %
\t\tdisplayFolder: 01 Økonomi & Resultat
\t\tlineageTag: [[GUID]]

\t/// Totale normerte årsverk (Full-Time Equivalent)
\tmeasure 'FTE Årsverk' =
\t\t\tAVERAGEX(
\t\t\t    VALUES('DimDate_2027'[AarMaaned]),
\t\t\t    CALCULATE(SUM('FactFTE_2027'[Aarsverk]))
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: 02 Bemanningsstyring (FTE)
\t\tlineageTag: [[GUID]]

\t/// Vitenskapelige årsverk innen undervisning og forskning (UF)
\tmeasure 'UF-Årsverk' =
\t\t\tCALCULATE(
\t\t\t    [FTE Årsverk],
\t\t\t    'FactFTE_2027'[Stillingstype] = "UF"
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: 02 Bemanningsstyring (FTE)
\t\tlineageTag: [[GUID]]

\t/// Teknisk-administrative årsverk (TA)
\tmeasure 'TA-Årsverk' =
\t\t\tCALCULATE(
\t\t\t    [FTE Årsverk],
\t\t\t    'FactFTE_2027'[Stillingstype] = "TA"
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: 02 Bemanningsstyring (FTE)
\t\tlineageTag: [[GUID]]

\t/// Totalt antall ansatte personer
\tmeasure 'Antall Ansatte' =
\t\t\tAVERAGEX(
\t\t\t    VALUES('DimDate_2027'[AarMaaned]),
\t\t\t    CALCULATE(SUM('FactFTE_2027'[AntallAnsatte]))
\t\t\t)
\t\tformatString: #,##0
\t\tdisplayFolder: 02 Bemanningsstyring (FTE)
\t\tlineageTag: [[GUID]]

\t/// Ubesatte stillinger / vakante årsverk
\tmeasure 'Vakanser (Årsverk)' =
\t\t\tAVERAGEX(
\t\t\t    VALUES('DimDate_2027'[AarMaaned]),
\t\t\t    CALCULATE(SUM('FactFTE_2027'[Vakanser]))
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: 02 Bemanningsstyring (FTE)
\t\tlineageTag: [[GUID]]

\t/// Vakanser i prosent av totale årsverk (vakansfaktor)
\tmeasure 'Vakansfaktor %' = DIVIDE([Vakanser (Årsverk)], [FTE Årsverk])
\t\tformatString: 0.0 %
\t\tdisplayFolder: 02 Bemanningsstyring (FTE)
\t\tlineageTag: [[GUID]]

\t/// Gjennomsnittlig årslønn for vitenskapelig ansatte (NOK)
\tmeasure 'Snittlønn UF (NOK)' =
\t\t\tCALCULATE(
\t\t\t    AVERAGEX(VALUES('DimDate_2027'[AarMaaned]), CALCULATE(AVERAGE('FactFTE_2027'[SnittLonnNOK]))),
\t\t\t    'FactFTE_2027'[Stillingstype] = "UF"
\t\t\t)
\t\tformatString: #,##0
\t\tdisplayFolder: 02 Bemanningsstyring (FTE)
\t\tlineageTag: [[GUID]]

\t/// Gjennomsnittlig årslønn for teknisk-administrative ansatte (NOK)
\tmeasure 'Snittlønn TA (NOK)' =
\t\t\tCALCULATE(
\t\t\t    AVERAGEX(VALUES('DimDate_2027'[AarMaaned]), CALCULATE(AVERAGE('FactFTE_2027'[SnittLonnNOK]))),
\t\t\t    'FactFTE_2027'[Stillingstype] = "TA"
\t\t\t)
\t\tformatString: #,##0
\t\tdisplayFolder: 02 Bemanningsstyring (FTE)
\t\tlineageTag: [[GUID]]

\t/// Samlet snittlønn på tvers av alle stillingsgrupper (NOK)
\tmeasure 'Snittlønn Totalt (NOK)' =
\t\t\tAVERAGEX(
\t\t\t    VALUES('DimDate_2027'[AarMaaned]),
\t\t\t    CALCULATE(AVERAGE('FactFTE_2027'[SnittLonnNOK]))
\t\t\t)
\t\tformatString: #,##0
\t\tdisplayFolder: 02 Bemanningsstyring (FTE)
\t\tlineageTag: [[GUID]]

\t/// Totalt antall semesterregistrerte studenter i Felles Studentsystem (FS)
\tmeasure 'Registrerte Studenter' = SUM('FactStudents_2027'[RegistrerteStudenter])
\t\tformatString: #,##0
\t\tdisplayFolder: 03 Utdanningsproduksjon & KD
\t\tlineageTag: [[GUID]]

\t/// Historisk studiepoengproduksjon 2025 som danner grunnlag for 2027-tildeling (2-års etterslep)
\tmeasure 'SPE60 2025 Lag' = SUM('FactStudents_2027'[SPE60_2025_Lag])
\t\tformatString: #,##0.0
\t\tdisplayFolder: 03 Utdanningsproduksjon & KD
\t\tlineageTag: [[GUID]]

\t/// Måltall for studiepoengproduksjon i 2027 (SPE60 Target)
\tmeasure 'SPE60 2027 Target' = SUM('FactStudents_2027'[SPE60_2027_Target])
\t\tformatString: #,##0.0
\t\tdisplayFolder: 03 Utdanningsproduksjon & KD
\t\tlineageTag: [[GUID]]

\t/// Forventet vekst i studiepoengproduksjon fra 2025-grunnlag til 2027-mål
\tmeasure 'SPE60 Produksjonsvekst' = [SPE60 2027 Target] - [SPE60 2025 Lag]
\t\tformatString: +#,##0.0;-#,##0.0;0.0
\t\tdisplayFolder: 03 Utdanningsproduksjon & KD
\t\tlineageTag: [[GUID]]

\t/// Prosentvis produksjonsvekst i studiepoeng
\tmeasure 'SPE60 Vekst %' = DIVIDE([SPE60 Produksjonsvekst], [SPE60 2025 Lag])
\t\tformatString: 0.0 %
\t\tdisplayFolder: 03 Utdanningsproduksjon & KD
\t\tlineageTag: [[GUID]]

\t/// Beregnet resultatbasert KD-tildeling etter KDs 2025/2027-modell (MNOK)
\tmeasure 'Beregnet KD Inntekt (MNOK)' = DIVIDE(SUM('FactStudents_2027'[KDInntektBeregnetNOK]), 1000000)
\t\tformatString: #,##0.0
\t\tdisplayFolder: 03 Utdanningsproduksjon & KD
\t\tlineageTag: [[GUID]]

\t/// Lærertetthet målt som registrerte studenter per vitenskapelig årsverk
\tmeasure 'Studenter per UF' = DIVIDE([Registrerte Studenter], [UF-Årsverk])
\t\tformatString: 0.0
\t\tdisplayFolder: 03 Utdanningsproduksjon & KD
\t\tlineageTag: [[GUID]]

\t/// Studiepoengproduksjon per vitenskapelig årsverk (SPE60 per UF)
\tmeasure 'SPE60 per UF' = DIVIDE([SPE60 2027 Target], [UF-Årsverk])
\t\tformatString: 0.0
\t\tdisplayFolder: 03 Utdanningsproduksjon & KD
\t\tlineageTag: [[GUID]]

\t/// Drifts- og personalkostnad per produserte 60 studiepoeng (tusen kroner)
\tmeasure 'Enhetskostnad per SPE60 (kNOK)' = DIVIDE([Budsjett Kostnad] * 1000, [SPE60 2027 Target])
\t\tformatString: #,##0
\t\tdisplayFolder: 03 Utdanningsproduksjon & KD
\t\tlineageTag: [[GUID]]

\t/// Vedtatt innsparingseffekt i omstillingsplan (MNOK)
\tmeasure 'Planlagt Innsparing (MNOK)' = SUM('FactAction_2027'[ForventetEffektMNOK])
\t\tformatString: #,##0.0
\t\tdisplayFolder: 04 Omstillingstiltak & EVM
\t\tlineageTag: [[GUID]]

\t/// Realisert innsparingseffekt per dags dato (MNOK)
\tmeasure 'Realisert Innsparing (MNOK)' = SUM('FactAction_2027'[RealisertEffektMNOK])
\t\tformatString: #,##0.0
\t\tdisplayFolder: 04 Omstillingstiltak & EVM
\t\tlineageTag: [[GUID]]

\t/// Realiseringsgrad for vedtatte omstillingstiltak
\tmeasure 'Realiseringsgrad %' = DIVIDE([Realisert Innsparing (MNOK)], [Planlagt Innsparing (MNOK)])
\t\tformatString: 0.0 %
\t\tdisplayFolder: 04 Omstillingstiltak & EVM
\t\tlineageTag: [[GUID]]

\t/// Antall vedtatte omstillingstiltak i handlingsplan
\tmeasure 'Antall Tiltak' = COUNTROWS('FactAction_2027')
\t\tformatString: 0
\t\tdisplayFolder: 04 Omstillingstiltak & EVM
\t\tlineageTag: [[GUID]]

\t/// Avsetning til formålskapital i henhold til F-05-20 (MNOK)
\tmeasure 'F-05-20 Avsetningsreserve (MNOK)' = [Budsjett Netto Resultat]
\t\tformatString: +#,##0.0;-#,##0.0;0.0
\t\tdisplayFolder: 04 Omstillingstiltak & EVM
\t\tlineageTag: [[GUID]]

\t/// Formålskapitalavsetningens andel av samlet bevilgning (5 %-regelen i F-05-20)
\tmeasure 'F-05-20 Avsetningsandel %' = DIVIDE([F-05-20 Avsetningsreserve (MNOK)], [Budsjett Bevilgning (KD)])
\t\tformatString: 0.0 %
\t\tdisplayFolder: 04 Omstillingstiltak & EVM
\t\tlineageTag: [[GUID]]

\t/// Trafikklys RAG-status for netto rammeresultat
\tmeasure 'RAG Netto Resultat' =
\t\t\tIF([Budsjett Netto Resultat] >= 0, "🟢 Overskudd", "🔴 Underskudd")
\t\tdisplayFolder: 05 RAG & Formatering
\t\tlineageTag: [[GUID]]

\t/// Trafikklys RAG-status for lønnsandel i forhold til sektornorm på 62 - 65 %
\tmeasure 'RAG Lønnsandel' =
\t\t\tIF([Lønnsandel %] <= 0.65, "🟢 Innenfor norm", "🟡 Høy lønnsandel")
\t\tdisplayFolder: 05 RAG & Formatering
\t\tlineageTag: [[GUID]]

\t/// Trafikklys RAG-status for F-05-20 avsetningsgrense på maksimalt 5 %
\tmeasure 'RAG F-05-20 Status' =
\t\t\tIF([F-05-20 Avsetningsandel %] <= 0.05, "🟢 < 5% Formålskapital", "🔴 Risiko for inndragning")
\t\tdisplayFolder: 05 RAG & Formatering
\t\tlineageTag: [[GUID]]

\t/// Strategisk controller-diagnose og driveranalyse per enhet
\tmeasure 'Diagnose og Drivere 2027' =
\t\t\tVAR Org = SELECTEDVALUE('DimOrganization'[OrgKode])
\t\t\tRETURN
\t\t\tSWITCH(
\t\t\t    Org,
\t\t\t    1110, "HHU Ledelse & Innovasjon: 100,4 MNOK inntekt / +3,0 MNOK overskudd. T003 EVU-ekspansjon (-1,4 MNOK). 22,7 stud/UF.",
\t\t\t    1120, "HHU Rettsvitenskap: 71,7 MNOK inntekt / +2,2 MNOK overskudd. Juss-profesjon. 21,3 stud/UF. Lav vakansgrad.",
\t\t\t    1130, "HHU Økonomi: 86,0 MNOK inntekt / +2,6 MNOK overskudd. T002 omdisponering av 5 faglige årsverk (-3,05 MNOK).",
\t\t\t    1140, "HHU Fakultetsadministrasjon: 28,7 MNOK inntekt / +0,86 MNOK overskudd. T001 ansettelsesstopp TA (-1,8 MNOK).",
\t\t\t    1200, "TEK: 351 MNOK inntekt. Ingeniør- og realfag. Kategori 2 sats (81 800 kr/SPE60). 14,0 stud/UF.",
\t\t\t    1300, "HEL: 310 MNOK inntekt. Helsefag og sykepleie. Kategori 2 sats. 15,9 stud/UF.",
\t\t\t    1400, "SAM: 242 MNOK inntekt. Samfunnsvitenskap. Kategori 1 sats. 20,2 stud/UF.",
\t\t\t    1500, "HUM: 201 MNOK inntekt. Lærerutdanning og humaniora. Kategori 1 sats. 20,2 stud/UF.",
\t\t\t    1600, "ADM: Sentral fellesadministrasjon og fellesdrift. T004 rammeavtaler og lisenskutt (-1,2 MNOK).",
\t\t\t    "Handelshøyskolen ved UiA (HHU) har et samlet vedtatt budsjett på 286,8 MNOK inntekt, 278,2 MNOK kostnad og et netto driftsoverskudd på +8,6 MNOK."
\t\t\t)
\t\tdisplayFolder: 05 RAG & Formatering
\t\tlineageTag: [[GUID]]

\tcolumn RowId
\t\tdataType: int64
\t\tisHidden
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: RowId
\t\tannotation SummarizationSetBy = Automatic

\tpartition _Measures = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("i45WMlSKjQUA", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type nullable text) meta [Serialized.Text = true]) in type table [RowId = _t]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(Source,{{"RowId", Int64.Type}}, "en-US")
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "_Measures.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_measures))

    print("Semantic model TMDL files written successfully.")

# Visual and PBIR Helpers
def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def make_title(text):
    return [
        {
            "properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "text": {"expr": {"Literal": {"Value": f"'{text}'"}}},
                "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI Semibold'"}}},
                "fontSize": {"expr": {"Literal": {"Value": "11pt"}}},
                "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1E293B'"}}}}}
            }
        }
    ]

def make_legend(position="'Top'"):
    return [
        {
            "properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "position": {"expr": {"Literal": {"Value": position}}},
                "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI'"}}},
                "fontSize": {"expr": {"Literal": {"Value": "9pt"}}}
            }
        }
    ]

def create_card_visual(vis_name, x, y, width, height, tab_order, measure_name, title, subtitle_text=None, accent_color="#0F766E"):
    vis = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": vis_name,
        "position": {
            "x": x,
            "y": y,
            "z": 20,
            "width": width,
            "height": height,
            "tabOrder": tab_order
        },
        "visual": {
            "visualType": "card",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Entity": "_Measures"
                                            }
                                        },
                                        "Property": measure_name
                                    }
                                },
                                "queryRef": f"_Measures.{measure_name}",
                                "nativeQueryRef": measure_name
                            }
                        ]
                    }
                }
            },
            "objects": {
                "accentBar": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "position": {"expr": {"Literal": {"Value": "'Left'"}}},
                            "width": {"expr": {"Literal": {"Value": "4D"}}},
                            "color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{accent_color}'"}}}}}
                        },
                        "selector": {"id": "default"}
                    }
                ]
            },
            "visualContainerObjects": {
                "title": make_title(title)
            },
            "drillFilterOtherVisuals": True
        }
    }
    if subtitle_text:
        vis["visual"]["visualContainerObjects"]["subTitle"] = [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": f"'{subtitle_text}'"}}}
                }
            }
        ]
    return vis

def create_textbox_visual(vis_name, x, y, width, height, tab_order, p1_text, p2_text=None):
    runs = [{"value": p1_text, "textStyle": {"fontFamily": "Segoe UI", "fontSize": "14pt", "fontWeight": "bold", "color": "#1E293B"}}]
    paragraphs = [{"textRuns": runs}]
    if p2_text:
        paragraphs.append({"textRuns": [{"value": p2_text, "textStyle": {"fontFamily": "Segoe UI", "fontSize": "9pt", "color": "#64748B"}}]})
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": vis_name,
        "position": {
            "x": x,
            "y": y,
            "z": 10,
            "height": height,
            "width": width,
            "tabOrder": tab_order
        },
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [
                    {
                        "properties": {
                            "paragraphs": paragraphs
                        }
                    }
                ]
            }
        }
    }

def create_slicer_visual(vis_name, x, y, width, height, tab_order, entity, column_name, title, mode="Single"):
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": vis_name,
        "position": {
            "x": x,
            "y": y,
            "z": 15,
            "width": width,
            "height": height,
            "tabOrder": tab_order
        },
        "visual": {
            "visualType": "slicer",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {
                                    "Column": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Entity": entity
                                            }
                                        },
                                        "Property": column_name
                                    }
                                },
                                "queryRef": f"{entity}.{column_name}",
                                "nativeQueryRef": column_name,
                                "active": True
                            }
                        ]
                    }
                }
            },
            "objects": {
                "data": [
                    {
                        "properties": {
                            "mode": {"expr": {"Literal": {"Value": f"'{mode}'"}}}
                        }
                    }
                ],
                "header": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}
                        }
                    }
                ]
            },
            "drillFilterOtherVisuals": True
        }
    }

def write_report_pbir():
    report_json_path = os.path.join(REPORT_DIR, "definition", "report.json")
    report_cfg = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.3.0/schema.json",
        "themeCollection": {
            "baseTheme": {
                "name": "Fluent2-CY26SU08",
                "reportVersionAtImport": {"visual": "2.12.0", "report": "3.4.0", "page": "2.3.1"},
                "type": "SharedResources"
            },
            "customTheme": {
                "name": "University-Tufte-Minimalist-20260926.json",
                "reportVersionAtImport": {"visual": "2.12.0", "report": "3.4.0", "page": "2.3.1"},
                "type": "RegisteredResources"
            }
        },
        "objects": {
            "section": [
                {
                    "properties": {
                        "verticalAlignment": {"expr": {"Literal": {"Value": "'Top'"}}}
                    }
                }
            ],
            "outspacePane": [
                {
                    "properties": {
                        "expanded": {"expr": {"Literal": {"Value": "false"}}}
                    }
                }
            ]
        },
        "resourcePackages": [
            {
                "name": "RegisteredResources",
                "type": "RegisteredResources",
                "items": [
                    {
                        "name": "University-Tufte-Minimalist-20260926.json",
                        "path": "University-Tufte-Minimalist-20260926.json",
                        "type": "CustomTheme"
                    }
                ]
            },
            {
                "name": "SharedResources",
                "type": "SharedResources",
                "items": [
                    {
                        "name": "Fluent2-CY26SU08",
                        "path": "BaseThemes/Fluent2-CY26SU08.json",
                        "type": "BaseTheme"
                    }
                ]
            }
        ],
        "settings": {
            "useStylableVisualContainerHeader": True,
            "exportDataMode": "AllowSummarized",
            "defaultDrillFilterOtherVisuals": True,
            "allowChangeFilterTypes": True,
            "useEnhancedTooltips": True,
            "useDefaultAggregateDisplayName": True
        }
    }
    write_json(report_json_path, report_cfg)

    # Clean old pages
    pages_dir = os.path.join(REPORT_DIR, "definition", "pages")
    for item in os.listdir(pages_dir):
        p = os.path.join(pages_dir, item)
        if os.path.isdir(p):
            shutil.rmtree(p)

    pages_metadata = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
        "pageOrder": [
            "page_budget_executive",
            "page_budget_hhu",
            "page_fte_capacity",
            "page_students_kd",
            "page_actions_restructuring"
        ],
        "activePageName": "page_budget_executive"
    }
    write_json(os.path.join(pages_dir, "pages.json"), pages_metadata)

    # =========================================================================
    # PAGE 1: Budsjett 2027 Totaloversikt & Rammer
    # =========================================================================
    p1_dir = os.path.join(pages_dir, "page_budget_executive")
    p1_vis = os.path.join(p1_dir, "visuals")
    write_json(os.path.join(p1_dir, "page.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": "page_budget_executive",
        "displayName": "1. Budsjett 2027 Totaloversikt",
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920
    })

    # Header & Slicers
    write_json(os.path.join(p1_vis, "p1_hdr_title", "visual.json"), create_textbox_visual(
        "p1_hdr_title", 20, 15, 1240, 75, 1,
        "Universitetet i Agder (UiA) & Handelshøyskolen — Vedtatt Årsbudsjett 2027 (BUD2027)",
        "Styrets godkjente baseline | KD Finansieringsmodell 2025/2027 | SRS 9 & 10 | DFØ R-102 Kontoplan | 3-30-300 Tufte-standard"
    ))
    write_json(os.path.join(p1_vis, "p1_slc_version", "visual.json"), create_slicer_visual(
        "p1_slc_version", 1280, 15, 190, 75, 2, "DimForecastVersion", "VersjonKode", "Budsjettversjon", "Single"
    ))
    write_json(os.path.join(p1_vis, "p1_slc_org", "visual.json"), create_slicer_visual(
        "p1_slc_org", 1490, 15, 210, 75, 3, "DimOrganization", "Fakultetsnavn", "Fakultet / Enhet", "Dropdown"
    ))
    write_json(os.path.join(p1_vis, "p1_slc_month", "visual.json"), create_slicer_visual(
        "p1_slc_month", 1720, 15, 180, 75, 4, "DimDate_2027", "MaanedNavnKort", "Måned", "Dropdown"
    ))

    # Top KPI Cards (3-second rule)
    write_json(os.path.join(p1_vis, "p1_kpi_revenue", "visual.json"), create_card_visual(
        "p1_kpi_revenue", 20, 105, 300, 115, 5, "Budsjett Inntekt", "BUDSJETT INNTEKT (MNOK)",
        "🟢 Bevilgning (KD): 1 465,8 MNOK | BOA/EVU: 33,0 MNOK", accent_color="#0F766E"
    ))
    write_json(os.path.join(p1_vis, "p1_kpi_cost", "visual.json"), create_card_visual(
        "p1_kpi_cost", 340, 105, 300, 115, 6, "Budsjett Kostnad", "BUDSJETT KOSTNAD (MNOK)",
        "🟢 Lønn: 983,2 MNOK (67%) | Drift: 451,9 MNOK | Avskr: 32,0 MNOK", accent_color="#334155"
    ))
    write_json(os.path.join(p1_vis, "p1_kpi_net", "visual.json"), create_card_visual(
        "p1_kpi_net", 660, 105, 300, 115, 7, "Budsjett Netto Resultat", "NETTO RESULTAT (MNOK)",
        "🟢 HHU: +8,6 MNOK overskudd | UiA samlet: +31,7 MNOK", accent_color="#10B981"
    ))
    write_json(os.path.join(p1_vis, "p1_kpi_staff", "visual.json"), create_card_visual(
        "p1_kpi_staff", 980, 105, 300, 115, 8, "Lønnsandel %", "LØNNSANDEL & VAKANS",
        "🟢 Norm: 62-65% | HHU: 64,8% | Vakansfaktor: 7,2%", accent_color="#0F766E"
    ))
    write_json(os.path.join(p1_vis, "p1_kpi_fte", "visual.json"), create_card_visual(
        "p1_kpi_fte", 1300, 105, 300, 115, 9, "FTE Årsverk", "BEMANNING TOTALT (FTE)",
        "🟢 UiA: 1 240 FTE | HHU: 230 FTE (155 UF / 75 TA)", accent_color="#3B82F6"
    ))
    write_json(os.path.join(p1_vis, "p1_kpi_stud", "visual.json"), create_card_visual(
        "p1_kpi_stud", 1620, 105, 280, 115, 10, "Registrerte Studenter", "STUDENTER & SPE60 MÅL",
        "🟢 14 000 Studenter | 12 910 SPE60 Mål | 863,9 MNOK KD", accent_color="#10B981"
    ))

    # Middle Charts (30-second rule)
    # Chart 1: Revenue vs Cost by Faculty
    write_json(os.path.join(p1_vis, "p1_cht_faculty_rev_cost", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "p1_cht_faculty_rev_cost",
        "position": {"x": 20, "y": 235, "z": 30, "width": 800, "height": 400, "tabOrder": 11},
        "visual": {
            "visualType": "clusteredColumnChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimOrganization"}}, "Property": "Fakultetsnavn"}}, "queryRef": "DimOrganization.Fakultetsnavn", "nativeQueryRef": "Fakultet", "active": True}]},
                    "Y": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Budsjett Inntekt"}}, "queryRef": "_Measures.Budsjett Inntekt", "nativeQueryRef": "Inntekt (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Budsjett Kostnad"}}, "queryRef": "_Measures.Budsjett Kostnad", "nativeQueryRef": "Kostnad (MNOK)"}
                    ]},
                    "Tooltips": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Budsjett Netto Resultat"}}, "queryRef": "_Measures.Budsjett Netto Resultat", "nativeQueryRef": "Netto Resultat"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Lønnsandel %"}}, "queryRef": "_Measures.Lønnsandel %", "nativeQueryRef": "Lønnsandel %"}
                    ]}
                }
            },
            "objects": {"legend": make_legend("'Top'")},
            "visualContainerObjects": {"title": make_title("Budsjettert Inntekt og Kostnad per Fakultet / Hovedenhet (MNOK)")},
            "drillFilterOtherVisuals": True
        }
    })

    # Chart 2: Monthly Budget Profile 2027
    write_json(os.path.join(p1_vis, "p1_cht_monthly_trend", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "p1_cht_monthly_trend",
        "position": {"x": 840, "y": 235, "z": 31, "width": 580, "height": 400, "tabOrder": 12},
        "visual": {
            "visualType": "lineChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimDate_2027"}}, "Property": "MaanedNavnKort"}}, "queryRef": "DimDate_2027.MaanedNavnKort", "nativeQueryRef": "Måned", "active": True}]},
                    "Y": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Budsjett Inntekt"}}, "queryRef": "_Measures.Budsjett Inntekt", "nativeQueryRef": "Månedlig Inntekt"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Budsjett Kostnad"}}, "queryRef": "_Measures.Budsjett Kostnad", "nativeQueryRef": "Månedlig Kostnad"}
                    ]}
                }
            },
            "objects": {"legend": make_legend("'Top'")},
            "visualContainerObjects": {"title": make_title("Månedlig Budsjettprofil M01–M12 (Periodisert Tildeling & Lønn)")},
            "drillFilterOtherVisuals": True
        }
    })

    # Chart 3: Cost Structure by SRS
    write_json(os.path.join(p1_vis, "p1_cht_srs_cost", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "p1_cht_srs_cost",
        "position": {"x": 1440, "y": 235, "z": 32, "width": 460, "height": 400, "tabOrder": 13},
        "visual": {
            "visualType": "barChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimAccountHierarchy"}}, "Property": "SRS_regnskapslinje"}}, "queryRef": "DimAccountHierarchy.SRS_regnskapslinje", "nativeQueryRef": "SRS Regnskapslinje", "active": True}]},
                    "Y": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Budsjett Kostnad"}}, "queryRef": "_Measures.Budsjett Kostnad", "nativeQueryRef": "Kostnad (MNOK)"}
                    ]}
                }
            },
            "visualContainerObjects": {"title": make_title("Kostnadsstruktur etter SRS Regnskapsstandard")},
            "drillFilterOtherVisuals": True
        }
    })

    # Bottom Matrix Table (300-second rule)
    write_json(os.path.join(p1_vis, "p1_tbl_summary_matrix", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "p1_tbl_summary_matrix",
        "position": {"x": 20, "y": 650, "z": 40, "width": 1880, "height": 410, "tabOrder": 14},
        "visual": {
            "visualType": "pivotTable",
            "query": {
                "queryState": {
                    "Rows": {"projections": [
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimOrganization"}}, "Property": "Fakultetsnavn"}}, "queryRef": "DimOrganization.Fakultetsnavn", "nativeQueryRef": "Fakultet", "active": True},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimOrganization"}}, "Property": "OrgNavn"}}, "queryRef": "DimOrganization.OrgNavn", "nativeQueryRef": "Organisasjonsenhet", "active": True}
                    ]},
                    "Values": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Budsjett Inntekt"}}, "queryRef": "_Measures.Budsjett Inntekt", "nativeQueryRef": "Inntekt (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Budsjett Lønn"}}, "queryRef": "_Measures.Budsjett Lønn", "nativeQueryRef": "Lønn (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Budsjett Drift"}}, "queryRef": "_Measures.Budsjett Drift", "nativeQueryRef": "Drift (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Budsjett Avskrivninger"}}, "queryRef": "_Measures.Budsjett Avskrivninger", "nativeQueryRef": "Avskrivninger (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Budsjett Kostnad"}}, "queryRef": "_Measures.Budsjett Kostnad", "nativeQueryRef": "Kostnad (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Budsjett Netto Resultat"}}, "queryRef": "_Measures.Budsjett Netto Resultat", "nativeQueryRef": "Netto Resultat (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Lønnsandel %"}}, "queryRef": "_Measures.Lønnsandel %", "nativeQueryRef": "Lønnsandel %"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "FTE Årsverk"}}, "queryRef": "_Measures.FTE Årsverk", "nativeQueryRef": "Årsverk (FTE)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "UF-Årsverk"}}, "queryRef": "_Measures.UF-Årsverk", "nativeQueryRef": "UF-Årsverk"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "RAG Netto Resultat"}}, "queryRef": "_Measures.RAG Netto Resultat", "nativeQueryRef": "Status"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Diagnose og Drivere 2027"}}, "queryRef": "_Measures.Diagnose og Drivere 2027", "nativeQueryRef": "Controller Diagnose"}
                    ]}
                }
            },
            "visualContainerObjects": {
                "stylePreset": [{"properties": {"name": {"expr": {"Literal": {"Value": "'None'"}}}}}],
                "title": make_title("Enhetsvis Hovedavstemming: Driftsbudsjett, Bemanningsstruktur og Strategisk Diagnose (300-sekunders analyse)")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # =========================================================================
    # PAGE 2: Handelshøyskolen (HHU) Driftsbudsjett
    # =========================================================================
    p2_dir = os.path.join(pages_dir, "page_budget_hhu")
    p2_vis = os.path.join(p2_dir, "visuals")
    write_json(os.path.join(p2_dir, "page.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": "page_budget_hhu",
        "displayName": "2. Handelshøyskolen Driftsbudsjett",
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920
    })

    write_json(os.path.join(p2_vis, "p2_hdr_title", "visual.json"), create_textbox_visual(
        "p2_hdr_title", 20, 15, 1400, 75, 1,
        "Handelshøyskolen ved UiA (HHU) — Fakultetets Detaljerte Driftsbudsjett 2027",
        "Instituttoppfølging: Ledelse & Innovasjon (1110) | Rettsvitenskap (1120) | Økonomi (1130) | Administrasjon (1140)"
    ))
    write_json(os.path.join(p2_vis, "p2_slc_inst", "visual.json"), create_slicer_visual(
        "p2_slc_inst", 1440, 15, 250, 75, 2, "DimOrganization", "OrgNavn", "Institutt / Avdeling", "Dropdown"
    ))
    write_json(os.path.join(p2_vis, "p2_slc_acc", "visual.json"), create_slicer_visual(
        "p2_slc_acc", 1710, 15, 190, 75, 3, "DimAccountHierarchy", "Nivaa1_Navn", "Kontoklasse", "Dropdown"
    ))

    # HHU Top KPI Cards
    write_json(os.path.join(p2_vis, "p2_kpi_hhu_rev", "visual.json"), create_card_visual(
        "p2_kpi_hhu_rev", 20, 105, 300, 115, 4, "Budsjett Inntekt", "HHU SAMLET INNTEKT (MNOK)",
        "🟢 KD Bevilgning: 253,8 MNOK | NFR/EVU: 33,0 MNOK", accent_color="#0F766E"
    ))
    write_json(os.path.join(p2_vis, "p2_kpi_hhu_cost", "visual.json"), create_card_visual(
        "p2_kpi_hhu_cost", 340, 105, 300, 115, 5, "Budsjett Kostnad", "HHU SAMLET KOSTNAD (MNOK)",
        "🟢 Lønn: 180,2 MNOK | Drift: 66,0 MNOK | Avskr: 32,0 MNOK", accent_color="#334155"
    ))
    write_json(os.path.join(p2_vis, "p2_kpi_hhu_net", "visual.json"), create_card_visual(
        "p2_kpi_hhu_net", 660, 105, 300, 115, 6, "Budsjett Netto Resultat", "HHU NETTO OVERSKUDD (MNOK)",
        "🟢 +8,6 MNOK resultat (+3,0% driftsmargin)", accent_color="#10B981"
    ))
    write_json(os.path.join(p2_vis, "p2_kpi_hhu_pay", "visual.json"), create_card_visual(
        "p2_kpi_hhu_pay", 980, 105, 300, 115, 7, "Lønnsandel %", "HHU LØNNSANDEL",
        "🟢 64,8% (Innenfor sektornorm 62–65%)", accent_color="#0F766E"
    ))
    write_json(os.path.join(p2_vis, "p2_kpi_hhu_uf", "visual.json"), create_card_visual(
        "p2_kpi_hhu_uf", 1300, 105, 300, 115, 8, "UF-Årsverk", "VITENSKAPELIGE ÅRSVERK (UF)",
        "🟢 155,0 UF-årsverk (Prof/Dosent/Lektor/Stip)", accent_color="#3B82F6"
    ))
    write_json(os.path.join(p2_vis, "p2_kpi_hhu_ta", "visual.json"), create_card_visual(
        "p2_kpi_hhu_ta", 1620, 105, 280, 115, 9, "TA-Årsverk", "ADMINISTRATIVE ÅRSVERK (TA)",
        "🟢 75,0 TA-årsverk (T001 Ansettelsesstopp)", accent_color="#F59E0B"
    ))

    # Middle Charts
    # Chart 1: HHU Budget by Department
    write_json(os.path.join(p2_vis, "p2_cht_dept_summary", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "p2_cht_dept_summary",
        "position": {"x": 20, "y": 235, "z": 30, "width": 880, "height": 400, "tabOrder": 10},
        "visual": {
            "visualType": "clusteredColumnChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimOrganization"}}, "Property": "OrgNavn"}}, "queryRef": "DimOrganization.OrgNavn", "nativeQueryRef": "Institutt / Avdeling", "active": True}]},
                    "Y": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Budsjett Inntekt"}}, "queryRef": "_Measures.Budsjett Inntekt", "nativeQueryRef": "Inntekt (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Budsjett Kostnad"}}, "queryRef": "_Measures.Budsjett Kostnad", "nativeQueryRef": "Kostnad (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Budsjett Netto Resultat"}}, "queryRef": "_Measures.Budsjett Netto Resultat", "nativeQueryRef": "Netto Resultat (MNOK)"}
                    ]}
                }
            },
            "objects": {"legend": make_legend("'Top'")},
            "visualContainerObjects": {"title": make_title("HHU Instituttfordeling: Inntekt, Kostnad og Netto Resultat (MNOK)")},
            "drillFilterOtherVisuals": True
        }
    })

    # Chart 2: Cost Breakdown by Category per Institute
    write_json(os.path.join(p2_vis, "p2_cht_cost_breakdown", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "p2_cht_cost_breakdown",
        "position": {"x": 920, "y": 235, "z": 31, "width": 980, "height": 400, "tabOrder": 11},
        "visual": {
            "visualType": "stackedBarChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimOrganization"}}, "Property": "OrgNavn"}}, "queryRef": "DimOrganization.OrgNavn", "nativeQueryRef": "Institutt", "active": True}]},
                    "Y": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Budsjett Lønn"}}, "queryRef": "_Measures.Budsjett Lønn", "nativeQueryRef": "Lønnskostnad"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Budsjett Drift"}}, "queryRef": "_Measures.Budsjett Drift", "nativeQueryRef": "Driftskostnad"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Budsjett Avskrivninger"}}, "queryRef": "_Measures.Budsjett Avskrivninger", "nativeQueryRef": "Avskrivninger"}
                    ]}
                }
            },
            "objects": {"legend": make_legend("'Top'")},
            "visualContainerObjects": {"title": make_title("HHU Kostnadsstruktur per Institutt: Lønn vs. Drift vs. Avskrivninger (MNOK)")},
            "drillFilterOtherVisuals": True
        }
    })

    # Bottom Matrix
    write_json(os.path.join(p2_vis, "p2_tbl_hhu_matrix", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "p2_tbl_hhu_matrix",
        "position": {"x": 20, "y": 650, "z": 40, "width": 1880, "height": 410, "tabOrder": 12},
        "visual": {
            "visualType": "pivotTable",
            "query": {
                "queryState": {
                    "Rows": {"projections": [
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimOrganization"}}, "Property": "OrgNavn"}}, "queryRef": "DimOrganization.OrgNavn", "nativeQueryRef": "Institutt / Avdeling", "active": True},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimAccountHierarchy"}}, "Property": "Nivaa2_Navn"}}, "queryRef": "DimAccountHierarchy.Nivaa2_Navn", "nativeQueryRef": "Kontogruppe", "active": True},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimAccountHierarchy"}}, "Property": "Kontonavn"}}, "queryRef": "DimAccountHierarchy.Kontonavn", "nativeQueryRef": "Hovedkonto", "active": True}
                    ]},
                    "Values": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Budsjett Inntekt"}}, "queryRef": "_Measures.Budsjett Inntekt", "nativeQueryRef": "Inntekt (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Budsjett Kostnad"}}, "queryRef": "_Measures.Budsjett Kostnad", "nativeQueryRef": "Kostnad (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Budsjett Netto Resultat"}}, "queryRef": "_Measures.Budsjett Netto Resultat", "nativeQueryRef": "Netto Resultat (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "FTE Årsverk"}}, "queryRef": "_Measures.FTE Årsverk", "nativeQueryRef": "FTE"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "UF-Årsverk"}}, "queryRef": "_Measures.UF-Årsverk", "nativeQueryRef": "UF"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "TA-Årsverk"}}, "queryRef": "_Measures.TA-Årsverk", "nativeQueryRef": "TA"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Vakanser (Årsverk)"}}, "queryRef": "_Measures.Vakanser (Årsverk)", "nativeQueryRef": "Vakanser"}
                    ]}
                }
            },
            "visualContainerObjects": {
                "stylePreset": [{"properties": {"name": {"expr": {"Literal": {"Value": "'None'"}}}}}],
                "title": make_title("HHU Detaljert Kontomatrise: Kontogruppe, Standardkonto og Ressursbruk per Institutt")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # =========================================================================
    # PAGE 3: Bemannings- og Kapasitetsplan 2027
    # =========================================================================
    p3_dir = os.path.join(pages_dir, "page_fte_capacity")
    p3_vis = os.path.join(p3_dir, "visuals")
    write_json(os.path.join(p3_dir, "page.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": "page_fte_capacity",
        "displayName": "3. Bemannings- & Kapasitetsplan",
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920
    })

    write_json(os.path.join(p3_vis, "p3_hdr_title", "visual.json"), create_textbox_visual(
        "p3_hdr_title", 20, 15, 1400, 75, 1,
        "Universitetet i Agder & HHU — Bemanningsplan, Stillingsgrupper og Kapasitetsstyring 2027",
        "Normerte årsverk (FTE) | Vitenskapelig (UF) vs. Teknisk-administrativ (TA) | Vakansfaktor og Lønnssnitt"
    ))
    write_json(os.path.join(p3_vis, "p3_slc_still", "visual.json"), create_slicer_visual(
        "p3_slc_still", 1440, 15, 220, 75, 2, "FactFTE_2027", "StillingsgruppeNavn", "Stillingsgruppe", "Dropdown"
    ))
    write_json(os.path.join(p3_vis, "p3_slc_fak", "visual.json"), create_slicer_visual(
        "p3_slc_fak", 1680, 15, 220, 75, 3, "DimOrganization", "Fakultetsnavn", "Fakultet", "Dropdown"
    ))

    # Top KPI Cards
    write_json(os.path.join(p3_vis, "p3_kpi_fte_tot", "visual.json"), create_card_visual(
        "p3_kpi_fte_tot", 20, 105, 300, 115, 4, "FTE Årsverk", "SAMLEDE ÅRSVERK (FTE)",
        "🟢 UiA: 1 240,0 FTE | HHU: 230,0 FTE", accent_color="#0F766E"
    ))
    write_json(os.path.join(p3_vis, "p3_kpi_fte_uf", "visual.json"), create_card_visual(
        "p3_kpi_fte_uf", 340, 105, 300, 115, 5, "UF-Årsverk", "VITENSKAPELIGE ÅRSVERK (UF)",
        "🟢 UiA: 790,0 UF | HHU: 155,0 UF (67,4%)", accent_color="#3B82F6"
    ))
    write_json(os.path.join(p3_vis, "p3_kpi_fte_ta", "visual.json"), create_card_visual(
        "p3_kpi_fte_ta", 660, 105, 300, 115, 6, "TA-Årsverk", "ADMINISTRATIVE ÅRSVERK (TA)",
        "🟢 UiA: 450,0 TA | HHU: 75,0 TA (32,6%)", accent_color="#F59E0B"
    ))
    write_json(os.path.join(p3_vis, "p3_kpi_fte_vak", "visual.json"), create_card_visual(
        "p3_kpi_fte_vak", 980, 105, 300, 115, 7, "Vakanser (Årsverk)", "VAKANTE ÅRSVERK",
        "🟢 UiA: 89,0 Vakanser | HHU: 16,5 Vakanser", accent_color="#10B981"
    ))
    write_json(os.path.join(p3_vis, "p3_kpi_fte_pay_uf", "visual.json"), create_card_visual(
        "p3_kpi_fte_pay_uf", 1300, 105, 300, 115, 8, "Snittlønn UF (NOK)", "SNITTLØNN VITENSKAPELIG (UF)",
        "🟢 920 000 NOK/år fast norm", accent_color="#334155"
    ))
    write_json(os.path.join(p3_vis, "p3_kpi_fte_pay_ta", "visual.json"), create_card_visual(
        "p3_kpi_fte_pay_ta", 1620, 105, 280, 115, 9, "Snittlønn TA (NOK)", "SNITTLØNN ADMINISTRATIV (TA)",
        "🟢 680 000 NOK/år fast norm", accent_color="#334155"
    ))

    # Middle Charts
    # Chart 1: FTE by Unit
    write_json(os.path.join(p3_vis, "p3_cht_fte_by_unit", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "p3_cht_fte_by_unit",
        "position": {"x": 20, "y": 235, "z": 30, "width": 980, "height": 400, "tabOrder": 10},
        "visual": {
            "visualType": "clusteredBarChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimOrganization"}}, "Property": "OrgNavn"}}, "queryRef": "DimOrganization.OrgNavn", "nativeQueryRef": "Enhet", "active": True}]},
                    "Y": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "UF-Årsverk"}}, "queryRef": "_Measures.UF-Årsverk", "nativeQueryRef": "Vitenskapelig (UF)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "TA-Årsverk"}}, "queryRef": "_Measures.TA-Årsverk", "nativeQueryRef": "Administrativt (TA)"}
                    ]}
                }
            },
            "objects": {"legend": make_legend("'Top'")},
            "visualContainerObjects": {"title": make_title("Årsverksfordeling etter Enhet: Vitenskapelig (UF) vs. Administrativ (TA)")},
            "drillFilterOtherVisuals": True
        }
    })

    # Chart 2: Vacancies by Unit
    write_json(os.path.join(p3_vis, "p3_cht_vac_by_unit", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "p3_cht_vac_by_unit",
        "position": {"x": 1020, "y": 235, "z": 31, "width": 880, "height": 400, "tabOrder": 11},
        "visual": {
            "visualType": "columnChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimOrganization"}}, "Property": "OrgNavn"}}, "queryRef": "DimOrganization.OrgNavn", "nativeQueryRef": "Enhet", "active": True}]},
                    "Y": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Vakanser (Årsverk)"}}, "queryRef": "_Measures.Vakanser (Årsverk)", "nativeQueryRef": "Vakante Årsverk"}
                    ]},
                    "Tooltips": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Vakansfaktor %"}}, "queryRef": "_Measures.Vakansfaktor %", "nativeQueryRef": "Vakansfaktor %"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "FTE Årsverk"}}, "queryRef": "_Measures.FTE Årsverk", "nativeQueryRef": "Totale Årsverk"}
                    ]}
                }
            },
            "visualContainerObjects": {"title": make_title("Ubesatte Stillinger (Vakanser i FTE) per Organisasjonsenhet")},
            "drillFilterOtherVisuals": True
        }
    })

    # Bottom Matrix
    write_json(os.path.join(p3_vis, "p3_tbl_fte_matrix", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "p3_tbl_fte_matrix",
        "position": {"x": 20, "y": 650, "z": 40, "width": 1880, "height": 410, "tabOrder": 12},
        "visual": {
            "visualType": "pivotTable",
            "query": {
                "queryState": {
                    "Rows": {"projections": [
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimOrganization"}}, "Property": "Fakultetsnavn"}}, "queryRef": "DimOrganization.Fakultetsnavn", "nativeQueryRef": "Fakultet", "active": True},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimOrganization"}}, "Property": "OrgNavn"}}, "queryRef": "DimOrganization.OrgNavn", "nativeQueryRef": "Enhet", "active": True},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactFTE_2027"}}, "Property": "StillingsgruppeNavn"}}, "queryRef": "FactFTE_2027.StillingsgruppeNavn", "nativeQueryRef": "Stillingsgruppe", "active": True}
                    ]},
                    "Values": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "FTE Årsverk"}}, "queryRef": "_Measures.FTE Årsverk", "nativeQueryRef": "Årsverk (FTE)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Antall Ansatte"}}, "queryRef": "_Measures.Antall Ansatte", "nativeQueryRef": "Antall Ansatte"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Vakanser (Årsverk)"}}, "queryRef": "_Measures.Vakanser (Årsverk)", "nativeQueryRef": "Vakanser (ÅV)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Vakansfaktor %"}}, "queryRef": "_Measures.Vakansfaktor %", "nativeQueryRef": "Vakansfaktor %"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Snittlønn Totalt (NOK)"}}, "queryRef": "_Measures.Snittlønn Totalt (NOK)", "nativeQueryRef": "Snittlønn (NOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Budsjett Lønn"}}, "queryRef": "_Measures.Budsjett Lønn", "nativeQueryRef": "Lønnsbudsjett (MNOK)"}
                    ]}
                }
            },
            "visualContainerObjects": {
                "stylePreset": [{"properties": {"name": {"expr": {"Literal": {"Value": "'None'"}}}}}],
                "title": make_title("Bemanningsmatrise: Stillingsgrupper, Vakanser, Lønnsrammer og Kapasitetsfordeling")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # =========================================================================
    # PAGE 4: Utdanningsproduksjon & KD Finansieringsmodell
    # =========================================================================
    p4_dir = os.path.join(pages_dir, "page_students_kd")
    p4_vis = os.path.join(p4_dir, "visuals")
    write_json(os.path.join(p4_dir, "page.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": "page_students_kd",
        "displayName": "4. Utdanning & KD-Modell",
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920
    })

    write_json(os.path.join(p4_vis, "p4_hdr_title", "visual.json"), create_textbox_visual(
        "p4_hdr_title", 20, 15, 1400, 75, 1,
        "Kunnskapsdepartementets (KD) Finansieringsmodell 2025/2027 & Utdanningsproduksjon",
        "Kategori 1 (54 550 NOK/60 SPE) | 2-års resultatforsinkelse (Lag) | Lærertetthet (Studenter/UF)"
    ))
    write_json(os.path.join(p4_vis, "p4_slc_prog", "visual.json"), create_slicer_visual(
        "p4_slc_prog", 1440, 15, 250, 75, 2, "FactStudents_2027", "StudieprogramNavn", "Studieprogram", "Dropdown"
    ))
    write_json(os.path.join(p4_vis, "p4_slc_kat", "visual.json"), create_slicer_visual(
        "p4_slc_kat", 1710, 15, 190, 75, 3, "FactStudents_2027", "KDKategori", "KD Kategori", "Dropdown"
    ))

    # Top KPI Cards
    write_json(os.path.join(p4_vis, "p4_kpi_reg_stud", "visual.json"), create_card_visual(
        "p4_kpi_reg_stud", 20, 105, 300, 115, 4, "Registrerte Studenter", "REGISTRERTE STUDENTER (FS)",
        "🟢 UiA: 14 000 | HHU: 3 450 studenter", accent_color="#0F766E"
    ))
    write_json(os.path.join(p4_vis, "p4_kpi_spe_lag", "visual.json"), create_card_visual(
        "p4_kpi_spe_lag", 340, 105, 300, 115, 5, "SPE60 2025 Lag", "SPE60 2025 RESULTATLAG",
        "🟢 Grunnlag 2027-tildeling: 12 750 (HHU: 3 120)", accent_color="#334155"
    ))
    write_json(os.path.join(p4_vis, "p4_kpi_spe_target", "visual.json"), create_card_visual(
        "p4_kpi_spe_target", 660, 105, 300, 115, 6, "SPE60 2027 Target", "SPE60 2027 MÅLSETTING",
        "🟢 Mål 2027: 12 910 SPE (HHU: 3 170 SPE)", accent_color="#10B981"
    ))
    write_json(os.path.join(p4_vis, "p4_kpi_kd_nok", "visual.json"), create_card_visual(
        "p4_kpi_kd_nok", 980, 105, 300, 115, 7, "Beregnet KD Inntekt (MNOK)", "BEREGNET KD TILDELING (MNOK)",
        "🟢 UiA: 863,9 MNOK | HHU: 172,9 MNOK", accent_color="#0F766E"
    ))
    write_json(os.path.join(p4_vis, "p4_kpi_stud_uf", "visual.json"), create_card_visual(
        "p4_kpi_stud_uf", 1300, 105, 300, 115, 8, "Studenter per UF", "STUDENTER PER UF-ÅRSVERK",
        "🟢 HHU: 22,3 stud/UF (Sektorsnitt: 17,7)", accent_color="#3B82F6"
    ))
    write_json(os.path.join(p4_vis, "p4_kpi_spe_growth", "visual.json"), create_card_visual(
        "p4_kpi_spe_growth", 1620, 105, 280, 115, 9, "SPE60 Vekst %", "PRODUKSJONSVEKST %",
        "🟢 +1,3 % vekst (+160 SPE netto vekst)", accent_color="#10B981"
    ))

    # Middle Charts
    # Chart 1: SPE Targets vs Lag by Program
    write_json(os.path.join(p4_vis, "p4_cht_spe_target_vs_lag", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "p4_cht_spe_target_vs_lag",
        "position": {"x": 20, "y": 235, "z": 30, "width": 980, "height": 400, "tabOrder": 10},
        "visual": {
            "visualType": "clusteredColumnChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactStudents_2027"}}, "Property": "StudieprogramNavn"}}, "queryRef": "FactStudents_2027.StudieprogramNavn", "nativeQueryRef": "Studieprogram", "active": True}]},
                    "Y": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "SPE60 2025 Lag"}}, "queryRef": "_Measures.SPE60 2025 Lag", "nativeQueryRef": "2025 Grunnlag (Lag)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "SPE60 2027 Target"}}, "queryRef": "_Measures.SPE60 2027 Target", "nativeQueryRef": "2027 Målsetting (Target)"}
                    ]}
                }
            },
            "objects": {"legend": make_legend("'Top'")},
            "visualContainerObjects": {"title": make_title("Studiepoengproduksjon (SPE60): 2025 Grunnlag vs. 2027 Målsetting per Studieprogram")},
            "drillFilterOtherVisuals": True
        }
    })

    # Chart 2: Students per UF by Program
    write_json(os.path.join(p4_vis, "p4_cht_stud_per_uf", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "p4_cht_stud_per_uf",
        "position": {"x": 1020, "y": 235, "z": 31, "width": 880, "height": 400, "tabOrder": 11},
        "visual": {
            "visualType": "barChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactStudents_2027"}}, "Property": "StudieprogramNavn"}}, "queryRef": "FactStudents_2027.StudieprogramNavn", "nativeQueryRef": "Studieprogram", "active": True}]},
                    "Y": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Studenter per UF"}}, "queryRef": "_Measures.Studenter per UF", "nativeQueryRef": "Studenter / UF-Årsverk"}
                    ]}
                }
            },
            "visualContainerObjects": {"title": make_title("Lærertetthet: Registrerte Studenter per Vitenskapelig Årsverk (UF)")},
            "drillFilterOtherVisuals": True
        }
    })

    # Bottom Table
    write_json(os.path.join(p4_vis, "p4_tbl_students_matrix", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "p4_tbl_students_matrix",
        "position": {"x": 20, "y": 650, "z": 40, "width": 1880, "height": 410, "tabOrder": 12},
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {"projections": [
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactStudents_2027"}}, "Property": "OrgNavn"}}, "queryRef": "FactStudents_2027.OrgNavn", "nativeQueryRef": "Fakultet / Enhet"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactStudents_2027"}}, "Property": "StudieprogramNavn"}}, "queryRef": "FactStudents_2027.StudieprogramNavn", "nativeQueryRef": "Studieprogram"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactStudents_2027"}}, "Property": "KDKategori"}}, "queryRef": "FactStudents_2027.KDKategori", "nativeQueryRef": "KD Kategori"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Registrerte Studenter"}}, "queryRef": "_Measures.Registrerte Studenter", "nativeQueryRef": "Registrerte Studenter"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "SPE60 2025 Lag"}}, "queryRef": "_Measures.SPE60 2025 Lag", "nativeQueryRef": "2025 Lag (60 SPE)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "SPE60 2027 Target"}}, "queryRef": "_Measures.SPE60 2027 Target", "nativeQueryRef": "2027 Target (60 SPE)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "SPE60 Produksjonsvekst"}}, "queryRef": "_Measures.SPE60 Produksjonsvekst", "nativeQueryRef": "Vekst (SPE)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "SPE60 Vekst %"}}, "queryRef": "_Measures.SPE60 Vekst %", "nativeQueryRef": "Vekst %"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Beregnet KD Inntekt (MNOK)"}}, "queryRef": "_Measures.Beregnet KD Inntekt (MNOK)", "nativeQueryRef": "Beregnet KD Inntekt (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Studenter per UF"}}, "queryRef": "_Measures.Studenter per UF", "nativeQueryRef": "Stud/UF-ÅV"}
                    ]}
                }
            },
            "visualContainerObjects": {
                "stylePreset": [{"properties": {"name": {"expr": {"Literal": {"Value": "'None'"}}}}}],
                "title": make_title("Utdanningsproduksjon & KD Finansieringsmatrise: Studieprogram, SPE60-Mål og Beregnet Inntekt")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # =========================================================================
    # PAGE 5: Omstillingstiltak & Handlingsplan 2027
    # =========================================================================
    p5_dir = os.path.join(pages_dir, "page_actions_restructuring")
    p5_vis = os.path.join(p5_dir, "visuals")
    write_json(os.path.join(p5_dir, "page.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": "page_actions_restructuring",
        "displayName": "5. Omstilling & F-05-20",
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920
    })

    write_json(os.path.join(p5_vis, "p5_hdr_title", "visual.json"), create_textbox_visual(
        "p5_hdr_title", 20, 15, 1400, 75, 1,
        "Vedtatte Omstillingstiltak & Avsetningskontroll F-05-20 (5 %-regelen)",
        "Tiltaksoppfølging: T001 Ansettelsesstopp TA | T002 Omdisponering UF | T003 EVU-vekst | T004 Lisenskutt | Statens avsetningsreglement"
    ))
    write_json(os.path.join(p5_vis, "p5_slc_prio", "visual.json"), create_slicer_visual(
        "p5_slc_prio", 1440, 15, 220, 75, 2, "FactAction_2027", "Prioritet", "Prioritet", "Dropdown"
    ))
    write_json(os.path.join(p5_vis, "p5_slc_rolle", "visual.json"), create_slicer_visual(
        "p5_slc_rolle", 1680, 15, 220, 75, 3, "FactAction_2027", "AnsvarligRolle", "Ansvarlig Rolle", "Dropdown"
    ))

    # Top KPI Cards
    write_json(os.path.join(p5_vis, "p5_kpi_effekt_plan", "visual.json"), create_card_visual(
        "p5_kpi_effekt_plan", 20, 105, 300, 115, 4, "Planlagt Innsparing (MNOK)", "PLANLAGT INNSPARING",
        "🟢 Vedtatt budsjetteffekt: -7,45 MNOK", accent_color="#0F766E"
    ))
    write_json(os.path.join(p5_vis, "p5_kpi_effekt_real", "visual.json"), create_card_visual(
        "p5_kpi_effekt_real", 340, 105, 300, 115, 5, "Realisert Innsparing (MNOK)", "REALISERT INNSPARING",
        "🟢 Realisert effekt: -7,45 MNOK (100% fullføring)", accent_color="#10B981"
    ))
    write_json(os.path.join(p5_vis, "p5_kpi_real_pct", "visual.json"), create_card_visual(
        "p5_kpi_real_pct", 660, 105, 300, 115, 6, "Realiseringsgrad %", "REALISERINGSGRAD",
        "🟢 100,0 % måloppnåelse for alle 4 tiltak", accent_color="#10B981"
    ))
    write_json(os.path.join(p5_vis, "p5_kpi_tiltak_ant", "visual.json"), create_card_visual(
        "p5_kpi_tiltak_ant", 980, 105, 300, 115, 7, "Antall Tiltak", "VEDTATTE TILTAK",
        "🟢 4 strategiske omstillingstiltak iverksatt", accent_color="#334155"
    ))
    write_json(os.path.join(p5_vis, "p5_kpi_f0520_res", "visual.json"), create_card_visual(
        "p5_kpi_f0520_res", 1300, 105, 300, 115, 8, "F-05-20 Avsetningsreserve (MNOK)", "F-05-20 FORMÅLSKAPITAL",
        "🟢 +8,6 MNOK avsatt reserve for HHU", accent_color="#3B82F6"
    ))
    write_json(os.path.join(p5_vis, "p5_kpi_f0520_pct", "visual.json"), create_card_visual(
        "p5_kpi_f0520_pct", 1620, 105, 280, 115, 9, "F-05-20 Avsetningsandel %", "F-05-20 AVSETNINGSANDEL",
        "🟢 3,4% av bevilgning (Trygt under 5%-grensen)", accent_color="#10B981"
    ))

    # Middle Charts
    # Chart 1: Action Effect by Tiltak
    write_json(os.path.join(p5_vis, "p5_cht_action_effect", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "p5_cht_action_effect",
        "position": {"x": 20, "y": 235, "z": 30, "width": 980, "height": 400, "tabOrder": 10},
        "visual": {
            "visualType": "barChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction_2027"}}, "Property": "TiltakNavn"}}, "queryRef": "FactAction_2027.TiltakNavn", "nativeQueryRef": "Omstillingstiltak", "active": True}]},
                    "Y": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Realisert Innsparing (MNOK)"}}, "queryRef": "_Measures.Realisert Innsparing (MNOK)", "nativeQueryRef": "Innsparing (MNOK)"}
                    ]},
                    "Tooltips": {"projections": [
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction_2027"}}, "Property": "AnsvarligRolle"}}, "queryRef": "FactAction_2027.AnsvarligRolle", "nativeQueryRef": "Ansvarlig"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction_2027"}}, "Property": "Status"}}, "queryRef": "FactAction_2027.Status", "nativeQueryRef": "Gjennomføringsstatus"}
                    ]}
                }
            },
            "visualContainerObjects": {"title": make_title("Økonomisk Innsparingseffekt per Vedtatt Omstillingstiltak (MNOK)")},
            "drillFilterOtherVisuals": True
        }
    })

    # Chart 2: Action by Unit
    write_json(os.path.join(p5_vis, "p5_cht_action_by_unit", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "p5_cht_action_by_unit",
        "position": {"x": 1020, "y": 235, "z": 31, "width": 880, "height": 400, "tabOrder": 11},
        "visual": {
            "visualType": "columnChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction_2027"}}, "Property": "OrgNavn"}}, "queryRef": "FactAction_2027.OrgNavn", "nativeQueryRef": "Ansvarlig Enhet", "active": True}]},
                    "Y": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Realisert Innsparing (MNOK)"}}, "queryRef": "_Measures.Realisert Innsparing (MNOK)", "nativeQueryRef": "Innsparing (MNOK)"}
                    ]}
                }
            },
            "visualContainerObjects": {"title": make_title("Innsparingseffekt fordelt på Ansvarlig Organisasjonsenhet (MNOK)")},
            "drillFilterOtherVisuals": True
        }
    })

    # Bottom Table
    write_json(os.path.join(p5_vis, "p5_tbl_action_register", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "p5_tbl_action_register",
        "position": {"x": 20, "y": 650, "z": 40, "width": 1880, "height": 410, "tabOrder": 12},
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {"projections": [
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction_2027"}}, "Property": "TiltakID"}}, "queryRef": "FactAction_2027.TiltakID", "nativeQueryRef": "ID"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction_2027"}}, "Property": "TiltakNavn"}}, "queryRef": "FactAction_2027.TiltakNavn", "nativeQueryRef": "Tiltaksnavn"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction_2027"}}, "Property": "OrgNavn"}}, "queryRef": "FactAction_2027.OrgNavn", "nativeQueryRef": "Organisasjonsenhet"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Planlagt Innsparing (MNOK)"}}, "queryRef": "_Measures.Planlagt Innsparing (MNOK)", "nativeQueryRef": "Planlagt MNOK"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Realisert Innsparing (MNOK)"}}, "queryRef": "_Measures.Realisert Innsparing (MNOK)", "nativeQueryRef": "Realisert MNOK"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Realiseringsgrad %"}}, "queryRef": "_Measures.Realiseringsgrad %", "nativeQueryRef": "Realiseringsgrad %"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction_2027"}}, "Property": "Status"}}, "queryRef": "FactAction_2027.Status", "nativeQueryRef": "Status"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction_2027"}}, "Property": "AnsvarligRolle"}}, "queryRef": "FactAction_2027.AnsvarligRolle", "nativeQueryRef": "Ansvarlig Rolle"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction_2027"}}, "Property": "FristDato"}}, "queryRef": "FactAction_2027.FristDato", "nativeQueryRef": "Frist"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction_2027"}}, "Property": "Prioritet"}}, "queryRef": "FactAction_2027.Prioritet", "nativeQueryRef": "Prioritet"}
                    ]}
                }
            },
            "visualContainerObjects": {
                "stylePreset": [{"properties": {"name": {"expr": {"Literal": {"Value": "'None'"}}}}}],
                "title": make_title("Fullstendig Tiltaksregister: Fremdrift, Roller, Frister og Økonomisk Effekt")
            },
            "drillFilterOtherVisuals": True
        }
    })

    print("PBIR report definition and 5 pages with 50 visuals written successfully.")

if __name__ == "__main__":
    ensure_directories()
    copy_theme()
    write_tmdl_semantic_model()
    write_report_pbir()
    print("ALL DONE BUILD SCRIPT FOR BUDSJETT 2027!")
