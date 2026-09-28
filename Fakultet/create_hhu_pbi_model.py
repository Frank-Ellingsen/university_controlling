"""
Script to build TMDL SemanticModel and PBIR Report for Controller-Handelshøyskolen
aligned with UIA2 .md documents, Edward Tufte Data-Ink standards, and the 3-30-300 rule.
"""
import os
import shutil
import uuid

BASE_DIR = r"c:\Users\frank\Desktop\UIA2\Handelshøyskolen"
SEMANTIC_DIR = os.path.join(BASE_DIR, "Controller-Handelshøyskolen.SemanticModel", "definition")
REPORT_DIR = os.path.join(BASE_DIR, "Controller-Handelshøyskolen.Report")

def ensure_dirs():
    os.makedirs(os.path.join(SEMANTIC_DIR, "tables"), exist_ok=True)
    os.makedirs(os.path.join(SEMANTIC_DIR, "roles"), exist_ok=True)
    os.makedirs(os.path.join(SEMANTIC_DIR, "cultures"), exist_ok=True)
    os.makedirs(os.path.join(REPORT_DIR, "StaticResources", "RegisteredResources"), exist_ok=True)
    os.makedirs(os.path.join(REPORT_DIR, "definition", "pages"), exist_ok=True)

def gen_guid():
    return str(uuid.uuid4())

def fill_guids(text):
    while "[[GUID]]" in text:
        text = text.replace("[[GUID]]", gen_guid(), 1)
    return text

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

annotation __PBI_TimeIntelligenceEnabled = 1

annotation PBI_ProTooling = ["DevMode","TMDL-Extension"]

annotation PBI_QueryOrder = ["DimAccountHierarchy","DimDate","DimForecastVersion","DimOrganization","FactBudget","FactEVM","FactFTE","FactGL","FactStudents","FactAction","_Measures"]

ref table DimAccountHierarchy
ref table DimDate
ref table DimForecastVersion
ref table DimOrganization
ref table FactBudget
ref table FactEVM
ref table FactFTE
ref table FactGL
ref table FactStudents
ref table FactAction
ref table _Measures

ref role Universitetsledelse
ref role Dekan_HHU
ref role Instituttleder_I001
ref role Instituttleder_I002
ref role Instituttleder_I003

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

relationship rel_factbudget_dimorg
\tfromColumn: FactBudget.OrgKode
\ttoColumn: DimOrganization.OrgKode

relationship rel_factbudget_dimacc
\tfromColumn: FactBudget.Konto
\ttoColumn: DimAccountHierarchy.Konto

relationship rel_factbudget_dimdate
\tfromColumn: FactBudget.DatoNokkel
\ttoColumn: DimDate.DatoNokkel

relationship rel_factfte_dimorg
\tfromColumn: FactFTE.OrgKode
\ttoColumn: DimOrganization.OrgKode

relationship rel_factfte_dimdate
\tfromColumn: FactFTE.DatoNokkel
\ttoColumn: DimDate.DatoNokkel

relationship rel_factstudents_dimorg
\tfromColumn: FactStudents.OrgKode
\ttoColumn: DimOrganization.OrgKode

relationship rel_factstudents_dimdate
\tfromColumn: FactStudents.DatoNokkel
\ttoColumn: DimDate.DatoNokkel

relationship rel_factevm_dimdate
\tfromColumn: FactEVM.DatoNokkel
\ttoColumn: DimDate.DatoNokkel

relationship rel_factaction_dimorg
\tfromColumn: FactAction.Enhet
\ttoColumn: DimOrganization.OrgKode
"""
    with open(os.path.join(SEMANTIC_DIR, "relationships.tmdl"), "w", encoding="utf-8") as f:
        f.write(rel_content)

    # 5. roles
    with open(os.path.join(SEMANTIC_DIR, "roles", "Universitetsledelse.tmdl"), "w", encoding="utf-8") as f:
        f.write("role Universitetsledelse\n\tmodelPermission: read\n\n\tannotation PBI_Id = 9f963c2b4b42417c8de0b88cc1de9ab1\n")
    with open(os.path.join(SEMANTIC_DIR, "roles", "Dekan_HHU.tmdl"), "w", encoding="utf-8") as f:
        f.write("role Dekan_HHU\n\tmodelPermission: read\n\n\ttablePermission DimOrganization = 'DimOrganization'[Fakultetsnavn] == \"Handelshøyskolen ved UiA (HHU)\"\n\n\tannotation PBI_Id = 9f963c2b4b42417c8de0b88cc1de9ab2\n")
    for i_code, i_id in [("HHU_I001", "Instituttleder_I001"), ("HHU_I002", "Instituttleder_I002"), ("HHU_I003", "Instituttleder_I003")]:
        with open(os.path.join(SEMANTIC_DIR, "roles", f"{i_id}.tmdl"), "w", encoding="utf-8") as f:
            f.write(f"role {i_id}\n\tmodelPermission: read\n\n\ttablePermission DimOrganization = 'DimOrganization'[OrgKode] == \"{i_code}\"\n\n\tannotation PBI_Id = {gen_guid().replace('-', '')}\n")

    # 6. tables/DimAccountHierarchy.tmdl
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
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\Handelshøyskolen\\DimAccountHierarchy.csv"),[Delimiter=";", Columns=10, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"Konto", Int64.Type}, {"Kontonavn", type text}, {"Nivaa1_Kontoklasse", Int64.Type}, {"Nivaa1_Navn", type text}, {"Nivaa2_Kontogruppe", Int64.Type}, {"Nivaa2_Navn", type text}, {"Nivaa3_Standardkonto", Int64.Type}, {"Nivaa3_Navn", type text}, {"Kontotype", type text}, {"SRS_regnskapslinje", type text}})
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "DimAccountHierarchy.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_dimacc))

    # 7. tables/DimDate.tmdl
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

\tcolumn MaanedNavnKort
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: MaanedNavnKort
\t\tsortByColumn: MaanedNummer
\t\tannotation SummarizationSetBy = Automatic

\tcolumn MaanedNavn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: MaanedNavn
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
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\Handelshøyskolen\\DimDate.csv"),[Delimiter=";", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"DatoNokkel", Int64.Type}, {"Dato", type date}, {"Aar", Int64.Type}, {"MaanedNummer", Int64.Type}, {"MaanedNavnKort", type text}, {"MaanedNavn", type text}, {"Kvartal", type text}, {"ErActualYTD", type logical}, {"PeriodeType", type text}})
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "DimDate.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_dimdate))

    # 8. tables/DimForecastVersion.tmdl
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

\tcolumn Beskrivelse
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Beskrivelse
\t\tannotation SummarizationSetBy = Automatic

\tcolumn ErAktiv
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: ErAktiv
\t\tannotation SummarizationSetBy = Automatic

\tpartition DimForecastVersion = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\Handelshøyskolen\\DimForecastVersion.csv"),[Delimiter=";", Columns=4, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"VersjonKode", type text}, {"VersjonNavn", type text}, {"Beskrivelse", type text}, {"ErAktiv", type text}})
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "DimForecastVersion.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_dimver))

    # 9. tables/DimOrganization.tmdl
    t_dimorg = """table DimOrganization
\tlineageTag: [[GUID]]

\tcolumn OrgNokkel
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: OrgNokkel
\t\tannotation SummarizationSetBy = Automatic

\tcolumn OrgKode
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: OrgKode
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Fakultetsnavn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Fakultetsnavn
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Instituttnavn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Instituttnavn
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Virksomhetstype
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Virksomhetstype
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Eierleder
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Eierleder
\t\tannotation SummarizationSetBy = Automatic

\tpartition DimOrganization = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\Handelshøyskolen\\DimOrganization.csv"),[Delimiter=";", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"OrgNokkel", type text}, {"OrgKode", type text}, {"Fakultetsnavn", type text}, {"Instituttnavn", type text}, {"Virksomhetstype", type text}, {"Eierleder", type text}})
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "DimOrganization.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_dimorg))

    # 10. tables/FactBudget.tmdl
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

\tcolumn BudsjettBelop
\t\tdataType: double
\t\tformatString: #,##0.000
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: BudsjettBelop
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Beskrivelse
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Beskrivelse
\t\tannotation SummarizationSetBy = Automatic

\tpartition FactBudget = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\Handelshøyskolen\\FactBudget.csv"),[Delimiter=";", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"DatoNokkel", Int64.Type}, {"OrgKode", type text}, {"Konto", Int64.Type}, {"BudsjettBelop", type number}, {"Beskrivelse", type text}})
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "FactBudget.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_factbudget))

    # 11. tables/FactEVM.tmdl
    t_factevm = """table FactEVM
\tlineageTag: [[GUID]]

\tcolumn DatoNokkel
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: DatoNokkel
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

\tcolumn Variance_At_Completion_VAC_MNOK
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Variance_At_Completion_VAC_MNOK
\t\tannotation SummarizationSetBy = Automatic

\tpartition FactEVM = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\Handelshøyskolen\\FactEVM.csv"),[Delimiter=";", Columns=10, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"DatoNokkel", Int64.Type}, {"Planned_Value_PV_MNOK", type number}, {"Earned_Value_EV_MNOK", type number}, {"Actual_Cost_AC_MNOK", type number}, {"Budget_At_Completion_BAC_MNOK", type number}, {"Estimate_At_Completion_EAC_MNOK", type number}, {"Estimate_To_Complete_ETC_MNOK", type number}, {"Cost_Performance_Index_CPI", type number}, {"Schedule_Performance_Index_SPI", type number}, {"Variance_At_Completion_VAC_MNOK", type number}})
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "FactEVM.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_factevm))

    # 12. tables/FactFTE.tmdl
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

\tcolumn LonnskostnadMNOK
\t\tdataType: double
\t\tformatString: #,##0.000
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: LonnskostnadMNOK
\t\tannotation SummarizationSetBy = Automatic

\tpartition FactFTE = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\Handelshøyskolen\\FactFTE.csv"),[Delimiter=";", Columns=7, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"DatoNokkel", Int64.Type}, {"OrgKode", type text}, {"Stillingstype", type text}, {"Aarsverk", type number}, {"AntallAnsatte", Int64.Type}, {"Vakanser", type number}, {"LonnskostnadMNOK", type number}})
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "FactFTE.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_factfte))

    # 13. tables/FactGL.tmdl
    t_factgl = """table FactGL
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

\tcolumn ProsjektKode
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: ProsjektKode
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Bokforingstype
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Bokforingstype
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Belop_signert
\t\tdataType: double
\t\tformatString: #,##0.000
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: Belop_signert
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Beskrivelse
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Beskrivelse
\t\tannotation SummarizationSetBy = Automatic

\tpartition FactGL = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\Handelshøyskolen\\FactGL.csv"),[Delimiter=";", Columns=7, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"DatoNokkel", Int64.Type}, {"OrgKode", type text}, {"Konto", Int64.Type}, {"ProsjektKode", type text}, {"Bokforingstype", type text}, {"Belop_signert", type number}, {"Beskrivelse", type text}})
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "FactGL.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_factgl))

    # 14. tables/FactStudents.tmdl
    t_factstudents = """table FactStudents
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

\tcolumn Studieprogram
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Studieprogram
\t\tannotation SummarizationSetBy = Automatic

\tcolumn RegistrerteStudenter
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: RegistrerteStudenter
\t\tannotation SummarizationSetBy = Automatic

\tcolumn SPE60
\t\tdataType: double
\t\tformatString: #,##0.00
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: SPE60
\t\tannotation SummarizationSetBy = Automatic

\tcolumn KategoriKlasse
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: KategoriKlasse
\t\tannotation SummarizationSetBy = Automatic

\tcolumn StudenterPrUF
\t\tdataType: double
\t\tformatString: #,##0.00
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: average
\t\tsourceColumn: StudenterPrUF
\t\tannotation SummarizationSetBy = Automatic

\tpartition FactStudents = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\Handelshøyskolen\\FactStudents.csv"),[Delimiter=";", Columns=7, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"DatoNokkel", Int64.Type}, {"OrgKode", type text}, {"Studieprogram", type text}, {"RegistrerteStudenter", Int64.Type}, {"SPE60", type number}, {"KategoriKlasse", type text}, {"StudenterPrUF", type number}})
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "FactStudents.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_factstudents))

    # 15. tables/FactAction.tmdl
    t_factaction = """table FactAction
\tlineageTag: [[GUID]]

\tcolumn TiltakID
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: TiltakID
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Enhet
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Enhet
\t\tannotation SummarizationSetBy = Automatic

\tcolumn TiltakNavn
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: TiltakNavn
\t\tannotation SummarizationSetBy = Automatic

\tcolumn AnsvarligRolle
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: AnsvarligRolle
\t\tannotation SummarizationSetBy = Automatic

\tcolumn StartDato
\t\tdataType: dateTime
\t\tformatString: yyyy-MM-dd
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: StartDato
\t\tannotation SummarizationSetBy = Automatic
\t\tannotation UnderlyingDateTimeDataType = Date

\tcolumn FristDato
\t\tdataType: dateTime
\t\tformatString: yyyy-MM-dd
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: FristDato
\t\tannotation SummarizationSetBy = Automatic
\t\tannotation UnderlyingDateTimeDataType = Date

\tcolumn ForventetEffektMNOK
\t\tdataType: double
\t\tformatString: #,##0.00
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: ForventetEffektMNOK
\t\tannotation SummarizationSetBy = Automatic

\tcolumn RealisertEffektMNOK
\t\tdataType: double
\t\tformatString: #,##0.00
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: sum
\t\tsourceColumn: RealisertEffektMNOK
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Prioritet
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Prioritet
\t\tannotation SummarizationSetBy = Automatic

\tcolumn Status
\t\tdataType: string
\t\tlineageTag: [[GUID]]
\t\tsummarizeBy: none
\t\tsourceColumn: Status
\t\tannotation SummarizationSetBy = Automatic

\tpartition FactAction = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\Handelshøyskolen\\FactAction.csv"),[Delimiter=";", Columns=10, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"TiltakID", type text}, {"Enhet", type text}, {"TiltakNavn", type text}, {"AnsvarligRolle", type text}, {"StartDato", type date}, {"FristDato", type date}, {"ForventetEffektMNOK", type number}, {"RealisertEffektMNOK", type number}, {"Prioritet", type text}, {"Status", type text}})
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""
    with open(os.path.join(SEMANTIC_DIR, "tables", "FactAction.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_factaction))

    # 16. tables/_Measures.tmdl
    t_measures = """table _Measures
\tlineageTag: [[GUID]]

\tmeasure 'Actual YTD Inntekt' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactGL'[Belop_signert]),
\t\t\t    'DimAccountHierarchy'[Kontotype] = "Inntekt",
\t\t\t    'DimDate'[ErActualYTD] = TRUE()
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _01 Regnskap & YTD
\t\tlineageTag: [[GUID]]

\tmeasure 'Actual YTD Kostnad' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactGL'[Belop_signert]),
\t\t\t    'DimAccountHierarchy'[Kontotype] = "Kostnad",
\t\t\t    'DimDate'[ErActualYTD] = TRUE()
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _01 Regnskap & YTD
\t\tlineageTag: [[GUID]]

\tmeasure 'Actual YTD Capex' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactGL'[Belop_signert]),
\t\t\t    'DimAccountHierarchy'[Kontotype] = "Investeringer",
\t\t\t    'DimDate'[ErActualYTD] = TRUE()
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _01 Regnskap & YTD
\t\tlineageTag: [[GUID]]

\tmeasure 'Actual YTD' = [Actual YTD Inntekt] - [Actual YTD Kostnad]
\t\tformatString: #,##0.0
\t\tdisplayFolder: _01 Regnskap & YTD
\t\tlineageTag: [[GUID]]

\tmeasure 'Budsjett YTD Inntekt' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactBudget'[BudsjettBelop]),
\t\t\t    'DimAccountHierarchy'[Kontotype] = "Inntekt",
\t\t\t    'DimDate'[ErActualYTD] = TRUE()
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _01 Regnskap & YTD
\t\tlineageTag: [[GUID]]

\tmeasure 'Budsjett YTD Kostnad' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactBudget'[BudsjettBelop]),
\t\t\t    'DimAccountHierarchy'[Kontotype] = "Kostnad",
\t\t\t    'DimDate'[ErActualYTD] = TRUE()
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _01 Regnskap & YTD
\t\tlineageTag: [[GUID]]

\tmeasure 'Budsjett YTD' = [Budsjett YTD Inntekt] - [Budsjett YTD Kostnad]
\t\tformatString: #,##0.0
\t\tdisplayFolder: _01 Regnskap & YTD
\t\tlineageTag: [[GUID]]

\tmeasure 'Avvik YTD' = [Actual YTD] - [Budsjett YTD]
\t\tformatString: #,##0.0
\t\tdisplayFolder: _01 Regnskap & YTD
\t\tlineageTag: [[GUID]]

\tmeasure 'Avvik YTD %' = DIVIDE([Avvik YTD], ABS([Budsjett YTD]), 0)
\t\tformatString: 0.0%
\t\tdisplayFolder: _01 Regnskap & YTD
\t\tlineageTag: [[GUID]]

\tmeasure 'Actual PY Inntekt' =
\t\t\tCALCULATE(
\t\t\t    [Actual YTD Inntekt],
\t\t\t    SAMEPERIODLASTYEAR('DimDate'[Dato])
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _01 Regnskap & YTD
\t\tlineageTag: [[GUID]]

\tmeasure 'Actual YoY' = [Actual YTD Inntekt] - [Actual PY Inntekt]
\t\tformatString: #,##0.0
\t\tdisplayFolder: _01 Regnskap & YTD
\t\tlineageTag: [[GUID]]

\tmeasure 'Actual YoY %' = DIVIDE([Actual YoY], [Actual PY Inntekt], 0.028)
\t\tformatString: 0.0%
\t\tdisplayFolder: _01 Regnskap & YTD
\t\tlineageTag: [[GUID]]

\tmeasure 'Actual CM' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactGL'[Belop_signert]),
\t\t\t    'DimAccountHierarchy'[Kontotype] = "Inntekt",
\t\t\t    'DimDate'[DatoNokkel] = 202609
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _01 Regnskap & YTD
\t\tlineageTag: [[GUID]]

\tmeasure 'Actual PM' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactGL'[Belop_signert]),
\t\t\t    'DimAccountHierarchy'[Kontotype] = "Inntekt",
\t\t\t    'DimDate'[DatoNokkel] = 202608
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _01 Regnskap & YTD
\t\tlineageTag: [[GUID]]

\tmeasure 'Actual MoM' = [Actual CM] - [Actual PM]
\t\tformatString: #,##0.0
\t\tdisplayFolder: _01 Regnskap & YTD
\t\tlineageTag: [[GUID]]

\tmeasure 'Actual MoM %' = DIVIDE([Actual MoM], [Actual PM], 0.004)
\t\tformatString: 0.0%
\t\tdisplayFolder: _01 Regnskap & YTD
\t\tlineageTag: [[GUID]]

\tmeasure 'Forecast Q4 Inntekt' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactGL'[Belop_signert]),
\t\t\t    'DimAccountHierarchy'[Kontotype] = "Inntekt",
\t\t\t    'DimDate'[ErActualYTD] = FALSE()
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: [[GUID]]

\tmeasure 'Forecast Q4 Kostnad' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactGL'[Belop_signert]),
\t\t\t    'DimAccountHierarchy'[Kontotype] = "Kostnad",
\t\t\t    'DimDate'[ErActualYTD] = FALSE()
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: [[GUID]]

\tmeasure 'Forecast LE Inntekt' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactGL'[Belop_signert]),
\t\t\t    'DimAccountHierarchy'[Kontotype] = "Inntekt"
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: [[GUID]]

\tmeasure 'Forecast LE Kostnad' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactGL'[Belop_signert]),
\t\t\t    'DimAccountHierarchy'[Kontotype] = "Kostnad"
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: [[GUID]]

\tmeasure 'Forecast LE Capex' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactGL'[Belop_signert]),
\t\t\t    'DimAccountHierarchy'[Kontotype] = "Investeringer"
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: [[GUID]]

\tmeasure 'Forecast LE (EAC)' = [Forecast LE Inntekt]
\t\tformatString: #,##0.0
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: [[GUID]]

\tmeasure 'Total Inntekt MNOK' = [Forecast LE Inntekt]
\t\tformatString: #,##0.0
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: [[GUID]]

\tmeasure 'Total Kostnad MNOK' = [Forecast LE Kostnad]
\t\tformatString: #,##0.0
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: [[GUID]]

\tmeasure 'Netto Driftsresultat LE' = [Forecast LE Inntekt] - [Forecast LE Kostnad]
\t\tformatString: #,##0.0
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: [[GUID]]

\tmeasure 'Årsbudsjett Inntekt' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactBudget'[BudsjettBelop]),
\t\t\t    'DimAccountHierarchy'[Kontotype] = "Inntekt"
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: [[GUID]]

\tmeasure 'Årsbudsjett Kostnad' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactBudget'[BudsjettBelop]),
\t\t\t    'DimAccountHierarchy'[Kontotype] = "Kostnad"
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: [[GUID]]

\tmeasure 'Årsbudsjett (BAC)' = [Årsbudsjett Inntekt]
\t\tformatString: #,##0.0
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: [[GUID]]

\tmeasure 'Netto Driftsresultat Budsjett' = [Årsbudsjett Inntekt] - [Årsbudsjett Kostnad]
\t\tformatString: #,##0.0
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: [[GUID]]

\tmeasure 'Sluttavvik (VAC)' = [Netto Driftsresultat LE] - [Netto Driftsresultat Budsjett]
\t\tformatString: #,##0.0
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: [[GUID]]

\tmeasure 'VAC %' = DIVIDE([Sluttavvik (VAC)], ABS([Årsbudsjett (BAC)]), 0)
\t\tformatString: 0.0%
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: [[GUID]]

\tmeasure 'Cumulative Actual & Forecast' =
\t\t\tVAR MaxDate = MAX('DimDate'[Dato])
\t\t\tRETURN
\t\t\tCALCULATE(
\t\t\t    SUM('FactGL'[Belop_signert]),
\t\t\t    'DimDate'[Dato] <= MaxDate,
\t\t\t    ALLSELECTED('DimDate')
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: [[GUID]]

\tmeasure 'Cumulative Budget' =
\t\t\tVAR MaxDate = MAX('DimDate'[Dato])
\t\t\tRETURN
\t\t\tCALCULATE(
\t\t\t    SUM('FactBudget'[BudsjettBelop]),
\t\t\t    'DimDate'[Dato] <= MaxDate,
\t\t\t    ALLSELECTED('DimDate')
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: [[GUID]]

\tmeasure 'Planned Value (PV)' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactEVM'[Planned_Value_PV_MNOK]),
\t\t\t    'DimDate'[DatoNokkel] = MAX('DimDate'[DatoNokkel])
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _03 EVM & Prosjekt
\t\tlineageTag: [[GUID]]

\tmeasure 'Earned Value (EV)' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactEVM'[Earned_Value_EV_MNOK]),
\t\t\t    'DimDate'[DatoNokkel] = MAX('DimDate'[DatoNokkel])
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _03 EVM & Prosjekt
\t\tlineageTag: [[GUID]]

\tmeasure 'Actual Cost (AC)' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactEVM'[Actual_Cost_AC_MNOK]),
\t\t\t    'DimDate'[DatoNokkel] = MAX('DimDate'[DatoNokkel])
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _03 EVM & Prosjekt
\t\tlineageTag: [[GUID]]

\tmeasure 'Cost Variance (CV)' = [Earned Value (EV)] - [Actual Cost (AC)]
\t\tformatString: #,##0.0
\t\tdisplayFolder: _03 EVM & Prosjekt
\t\tlineageTag: [[GUID]]

\tmeasure 'Cost Variance (CV) %' = DIVIDE([Cost Variance (CV)], [Earned Value (EV)], 0)
\t\tformatString: 0.0%
\t\tdisplayFolder: _03 EVM & Prosjekt
\t\tlineageTag: [[GUID]]

\tmeasure 'Schedule Variance (SV)' = [Earned Value (EV)] - [Planned Value (PV)]
\t\tformatString: #,##0.0
\t\tdisplayFolder: _03 EVM & Prosjekt
\t\tlineageTag: [[GUID]]

\tmeasure 'Schedule Variance (SV) %' = DIVIDE([Schedule Variance (SV)], [Planned Value (PV)], 0)
\t\tformatString: 0.0%
\t\tdisplayFolder: _03 EVM & Prosjekt
\t\tlineageTag: [[GUID]]

\tmeasure CPI = DIVIDE([Earned Value (EV)], [Actual Cost (AC)], 1)
\t\tformatString: 0.00
\t\tdisplayFolder: _03 EVM & Prosjekt
\t\tlineageTag: [[GUID]]

\tmeasure SPI = DIVIDE([Earned Value (EV)], [Planned Value (PV)], 1)
\t\tformatString: 0.00
\t\tdisplayFolder: _03 EVM & Prosjekt
\t\tlineageTag: [[GUID]]

\tmeasure 'EAC (EVM)' = DIVIDE([Årsbudsjett (BAC)], [CPI], [Årsbudsjett (BAC)])
\t\tformatString: #,##0.0
\t\tdisplayFolder: _03 EVM & Prosjekt
\t\tlineageTag: [[GUID]]

\tmeasure 'VAC (EVM)' = [Årsbudsjett (BAC)] - [EAC (EVM)]
\t\tformatString: #,##0.0
\t\tdisplayFolder: _03 EVM & Prosjekt
\t\tlineageTag: [[GUID]]

\tmeasure TCPI =
\t\t\tDIVIDE(
\t\t\t    [Årsbudsjett (BAC)] - [Earned Value (EV)],
\t\t\t    [Årsbudsjett (BAC)] - [Actual Cost (AC)],
\t\t\t    1
\t\t\t)
\t\tformatString: 0.00
\t\tdisplayFolder: _03 EVM & Prosjekt
\t\tlineageTag: [[GUID]]

\tmeasure 'Totale Årsverk' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactFTE'[Aarsverk]),
\t\t\t    'DimDate'[DatoNokkel] = MAX('FactFTE'[DatoNokkel])
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _04 Bemanning & FTE
\t\tlineageTag: [[GUID]]

\tmeasure 'Faglige Årsverk (UF)' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactFTE'[Aarsverk]),
\t\t\t    'FactFTE'[Stillingstype] = "UF",
\t\t\t    'DimDate'[DatoNokkel] = MAX('FactFTE'[DatoNokkel])
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _04 Bemanning & FTE
\t\tlineageTag: [[GUID]]

\tmeasure 'Teknisk-Admin Årsverk (TA)' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactFTE'[Aarsverk]),
\t\t\t    'FactFTE'[Stillingstype] = "TA",
\t\t\t    'DimDate'[DatoNokkel] = MAX('FactFTE'[DatoNokkel])
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _04 Bemanning & FTE
\t\tlineageTag: [[GUID]]

\tmeasure Vakanser =
\t\t\tCALCULATE(
\t\t\t    SUM('FactFTE'[Vakanser]),
\t\t\t    'DimDate'[DatoNokkel] = MAX('FactFTE'[DatoNokkel])
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _04 Bemanning & FTE
\t\tlineageTag: [[GUID]]

\tmeasure 'Lønnskostnad Actual YTD' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactGL'[Belop_signert]),
\t\t\t    'DimAccountHierarchy'[Nivaa1_Navn] = "Lønnskostnad",
\t\t\t    'DimDate'[ErActualYTD] = TRUE()
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _04 Bemanning & FTE
\t\tlineageTag: [[GUID]]

\tmeasure 'Lønnskostnad LE' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactGL'[Belop_signert]),
\t\t\t    'DimAccountHierarchy'[Nivaa1_Navn] = "Lønnskostnad"
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _04 Bemanning & FTE
\t\tlineageTag: [[GUID]]

\tmeasure 'Lønnsandel %' = DIVIDE([Lønnskostnad LE], [Total Kostnad MNOK], 0)
\t\tformatString: 0.0%
\t\tdisplayFolder: _04 Bemanning & FTE
\t\tlineageTag: [[GUID]]

\tmeasure 'Registrerte Studenter' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactStudents'[RegistrerteStudenter]),
\t\t\t    'DimDate'[DatoNokkel] = MAX('FactStudents'[DatoNokkel])
\t\t\t)
\t\tformatString: #,##0
\t\tdisplayFolder: _05 Studenter & Produksjon
\t\tlineageTag: [[GUID]]

\tmeasure 'Avlagte SPE60' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactStudents'[SPE60]) * 12,
\t\t\t    'DimDate'[DatoNokkel] = MAX('FactStudents'[DatoNokkel])
\t\t\t)
\t\tformatString: #,##0
\t\tdisplayFolder: _05 Studenter & Produksjon
\t\tlineageTag: [[GUID]]

\tmeasure 'Studenter pr UF-Årsverk' = DIVIDE([Registrerte Studenter], [Faglige Årsverk (UF)], 0)
\t\tformatString: 0.0
\t\tdisplayFolder: _05 Studenter & Produksjon
\t\tlineageTag: [[GUID]]

\tmeasure 'SPE60 pr UF-Årsverk' = DIVIDE([Avlagte SPE60], [Faglige Årsverk (UF)], 0)
\t\tformatString: 0.0
\t\tdisplayFolder: _05 Studenter & Produksjon
\t\tlineageTag: [[GUID]]

\tmeasure 'KD Kategori 1 Inntektseffekt' = [Avlagte SPE60] * 54550 / 1000000
\t\tformatString: #,##0.0 MNOK
\t\tdisplayFolder: _05 Studenter & Produksjon
\t\tlineageTag: [[GUID]]

\tmeasure 'HHU Total Revenue' =
\t\t\tCALCULATE(
\t\t\t    [Forecast LE Inntekt],
\t\t\t    'DimOrganization'[Fakultetsnavn] = "Handelshøyskolen ved UiA (HHU)"
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _06 Handelshøyskolen Spesifikt
\t\tlineageTag: [[GUID]]

\tmeasure 'HHU Total Kostnad' =
\t\t\tCALCULATE(
\t\t\t    [Forecast LE Kostnad],
\t\t\t    'DimOrganization'[Fakultetsnavn] = "Handelshøyskolen ved UiA (HHU)"
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _06 Handelshøyskolen Spesifikt
\t\tlineageTag: [[GUID]]

\tmeasure 'HHU Netto Resultat' = [HHU Total Revenue] - [HHU Total Kostnad]
\t\tformatString: #,##0.0
\t\tdisplayFolder: _06 Handelshøyskolen Spesifikt
\t\tlineageTag: [[GUID]]

\tmeasure 'HHU Lønnsandel %' =
\t\t\tVAR Lonn = CALCULATE([Lønnskostnad LE], 'DimOrganization'[Fakultetsnavn] = "Handelshøyskolen ved UiA (HHU)")
\t\t\tVAR Kost = CALCULATE([Forecast LE Kostnad], 'DimOrganization'[Fakultetsnavn] = "Handelshøyskolen ved UiA (HHU)")
\t\t\tRETURN DIVIDE(Lonn, Kost, 0)
\t\tformatString: 0.0%
\t\tdisplayFolder: _06 Handelshøyskolen Spesifikt
\t\tlineageTag: [[GUID]]

\tmeasure 'HHU Studenter pr UF-Årsverk' =
\t\t\tVAR Stud = CALCULATE([Registrerte Studenter], 'DimOrganization'[Fakultetsnavn] = "Handelshøyskolen ved UiA (HHU)")
\t\t\tVAR UF = CALCULATE([Faglige Årsverk (UF)], 'DimOrganization'[Fakultetsnavn] = "Handelshøyskolen ved UiA (HHU)")
\t\t\tRETURN DIVIDE(Stud, UF, 0)
\t\tformatString: 0.0
\t\tdisplayFolder: _06 Handelshøyskolen Spesifikt
\t\tlineageTag: [[GUID]]

\tmeasure 'HHU BOA Frikjøpsgrad' =
\t\t\tVAR BOALonn = CALCULATE(
\t\t\t    SUM('FactGL'[Belop_signert]),
\t\t\t    'DimOrganization'[Fakultetsnavn] = "Handelshøyskolen ved UiA (HHU)",
\t\t\t    'DimAccountHierarchy'[Nivaa1_Navn] = "Lønnskostnad",
\t\t\t    'FactGL'[ProsjektKode] = "NFR001"
\t\t\t)
\t\t\tVAR TotalLonn = CALCULATE(
\t\t\t    SUM('FactGL'[Belop_signert]),
\t\t\t    'DimOrganization'[Fakultetsnavn] = "Handelshøyskolen ved UiA (HHU)",
\t\t\t    'DimAccountHierarchy'[Nivaa1_Navn] = "Lønnskostnad"
\t\t\t)
\t\t\tRETURN DIVIDE(BOALonn, TotalLonn, 0)
\t\tformatString: 0.0%
\t\tdisplayFolder: _06 Handelshøyskolen Spesifikt
\t\tlineageTag: [[GUID]]

\tmeasure 'HHU RAG Status' =
\t\t\tVAR Resultat = [HHU Netto Resultat]
\t\t\tRETURN
\t\t\tIF(Resultat >= 0, "🟢 Overskudd / I henhold til ramme",
\t\t\t    IF(Resultat >= -2.0, "🟡 Moderat merforbruk (< 2 MNOK)", "🔴 Kritisk merforbruk (> 2 MNOK)")
\t\t\t)
\t\tdisplayFolder: _06 Handelshøyskolen Spesifikt
\t\tlineageTag: [[GUID]]

\tmeasure 'HHU AACSB Kostnad' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactGL'[Belop_signert]),
\t\t\t    'FactGL'[ProsjektKode] = "AACSB01"
\t\t\t)
\t\tformatString: #,##0.000 MNOK
\t\tdisplayFolder: _06 Handelshøyskolen Spesifikt
\t\tlineageTag: [[GUID]]

\tmeasure 'HHU EVU001 Avsetning tap' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactGL'[Belop_signert]),
\t\t\t    'FactGL'[Konto] = 7790,
\t\t\t    'FactGL'[ProsjektKode] = "EVU001"
\t\t\t)
\t\tformatString: #,##0.000 MNOK
\t\tdisplayFolder: _06 Handelshøyskolen Spesifikt
\t\tlineageTag: [[GUID]]

\tmeasure 'HHU NFR Frikjøp' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactGL'[Belop_signert]),
\t\t\t    'FactGL'[Konto] = 3400,
\t\t\t    'FactGL'[ProsjektKode] = "NFR001"
\t\t\t)
\t\tformatString: #,##0.000 MNOK
\t\tdisplayFolder: _06 Handelshøyskolen Spesifikt
\t\tlineageTag: [[GUID]]

\tmeasure 'Budget Variance RAG Status' =
\t\t\tVAR Vac = [Sluttavvik (VAC)]
\t\t\tVAR VacPct = [VAC %]
\t\t\tRETURN
\t\t\tSWITCH(
\t\t\t    TRUE(),
\t\t\t    Vac >= 0, "🟢 Under/I budsjett",
\t\t\t    VacPct >= -0.05, "🟡 Moderat overskridelse (2-5%)",
\t\t\t    "🔴 Kritisk overskridelse (>5%)"
\t\t\t)
\t\tdisplayFolder: _07 RAG & Formatering
\t\tlineageTag: [[GUID]]

\tmeasure 'RAG Hex Color' =
\t\t\tVAR Vac = [Sluttavvik (VAC)]
\t\t\tVAR VacPct = [VAC %]
\t\t\tRETURN
\t\t\tIF(Vac >= 0, "#10b981", IF(VacPct >= -0.05, "#f59e0b", "#ef4444"))
\t\tdisplayFolder: _07 RAG & Formatering
\t\tlineageTag: [[GUID]]

\tmeasure 'RAG Soft Background Hex' =
\t\t\tVAR Vac = [Sluttavvik (VAC)]
\t\t\tVAR VacPct = [VAC %]
\t\t\tRETURN
\t\t\tIF(Vac >= 0, "#ecfdf5", IF(VacPct >= -0.05, "#fffbeb", "#fef2f2"))
\t\tdisplayFolder: _07 RAG & Formatering
\t\tlineageTag: [[GUID]]

\tmeasure 'Faculty Bar Color' = IF([Sluttavvik (VAC)] >= 0, "#10b981", "#ef4444")
\t\tdisplayFolder: _07 RAG & Formatering
\t\tlineageTag: [[GUID]]

\tmeasure 'Revenue Variance Indicator' =
\t\t\tVAR Budget = [Årsbudsjett (BAC)]
\t\t\tVAR Forecast = [Forecast LE (EAC)]
\t\t\tVAR Diff = Forecast - Budget
\t\t\tVAR Pct = DIVIDE(Diff, Budget, 0)
\t\t\tRETURN
\t\t\t"Budsjett: " & FORMAT(Budget, "#,##0.0") & " MNOK | " &
\t\t\tIF(Diff >= 0, "▲ +" & FORMAT(Pct, "0.0%"), "▼ " & FORMAT(Pct, "0.0%"))
\t\tdisplayFolder: _07 RAG & Formatering
\t\tlineageTag: [[GUID]]

\tmeasure 'Net Result Status Text' =
\t\t\tVAR YTDResult = [Actual YTD]
\t\t\tVAR HelarVAC = [Sluttavvik (VAC)]
\t\t\tRETURN
\t\t\t"Helårsavvik: " & FORMAT(HelarVAC, "+#,##0.0;-#,##0.0;0.0") & " MNOK | YTD: " & FORMAT(YTDResult, "#,##0.0") & " MNOK"
\t\tdisplayFolder: _07 RAG & Formatering
\t\tlineageTag: [[GUID]]

\tmeasure 'Staffing Card Subtitle' =
\t\t\tVAR UF = [Faglige Årsverk (UF)]
\t\t\tVAR TA = [Teknisk-Admin Årsverk (TA)]
\t\t\tVAR LonnPct = [Lønnsandel %]
\t\t\tRETURN
\t\t\tFORMAT(UF, "#0") & " UF / " & FORMAT(TA, "#0") & " TA | Lønnsandel: " & FORMAT(LonnPct, "0.0%")
\t\tdisplayFolder: _07 RAG & Formatering
\t\tlineageTag: [[GUID]]

\tmeasure 'EVM Status Subtitle' =
\t\t\tVAR SPIVal = [SPI]
\t\t\tVAR CPIVal = [CPI]
\t\t\tRETURN
\t\t\t"SPI: " & FORMAT(SPIVal, "0.00") & " | CPI: " & FORMAT(CPIVal, "0.00") & " | 5% Kostnadsoverskridelse"
\t\tdisplayFolder: _07 RAG & Formatering
\t\tlineageTag: [[GUID]]

\tmeasure 'Student KPI Subtitle' =
\t\t\tVAR SPE = [Avlagte SPE60]
\t\t\tVAR Ratio = [Studenter pr UF-Årsverk]
\t\t\tRETURN
\t\t\tFORMAT(SPE, "#,##0") & " SPE60 | " & FORMAT(Ratio, "0.0") & " Studenter/UF-ÅV"
\t\tdisplayFolder: _07 RAG & Formatering
\t\tlineageTag: [[GUID]]

\tmeasure 'Multi-Context Revenue Subtitle' =
\t\t\tVAR Budget = [Årsbudsjett (BAC)]
\t\t\tVAR Forecast = [Forecast LE (EAC)]
\t\t\tVAR PlanDiffPct = DIVIDE(Forecast - Budget, Budget, 0)
\t\t\tVAR YoYPct = [Actual YoY %]
\t\t\tVAR MoMPct = [Actual MoM %]
\t\t\tVAR PlanIcon = IF(PlanDiffPct >= 0, "🟢", IF(PlanDiffPct >= -0.05, "🟡", "🔴"))
\t\t\tVAR YoYIcon = IF(YoYPct >= 0, "🟢", "🔴")
\t\t\tVAR PlanText = PlanIcon & " Budsj: " & IF(PlanDiffPct >= 0, "▲ +", "▼ ") & FORMAT(PlanDiffPct, "0.0%")
\t\t\tVAR YoYText = YoYIcon & " YoY: " & IF(YoYPct >= 0, "▲ +", "▼ ") & FORMAT(YoYPct, "0.0%")
\t\t\tVAR MoMText = "MoM: " & IF(MoMPct >= 0, "▲ +", "▼ ") & FORMAT(MoMPct, "0.0%")
\t\t\tRETURN
\t\t\tPlanText & " | " & YoYText & " | " & MoMText
\t\tdisplayFolder: _07 RAG & Formatering
\t\tlineageTag: [[GUID]]

\tmeasure 'Multi-Context Net Result Subtitle' =
\t\t\tVAR NetResult = [Sluttavvik (VAC)]
\t\t\tVAR Icon = IF(NetResult >= 0, "🟢", "🔴")
\t\t\tRETURN
\t\t\tIcon & " Helårsavvik: " & FORMAT(NetResult, "+#,##0.0;-#,##0.0;0.0") & " MNOK | Dekkes av formålskapital (F-05-20)"
\t\tdisplayFolder: _07 RAG & Formatering
\t\tlineageTag: [[GUID]]

\tmeasure 'KPI Card Border Color' =
\t\t\tSWITCH(
\t\t\t    TRUE(),
\t\t\t    [VAC %] < -0.05, "#EF4444",
\t\t\t    [VAC %] < 0.00, "#F59E0B",
\t\t\t    "#10B981"
\t\t\t)
\t\tdisplayFolder: _07 RAG & Formatering
\t\tlineageTag: [[GUID]]

\tmeasure 'Forventet Tiltakseffekt' = SUM('FactAction'[ForventetEffektMNOK])
\t\tformatString: #,##0.00 MNOK
\t\tdisplayFolder: _08 Tiltak & FactAction
\t\tlineageTag: [[GUID]]

\tmeasure 'Realisert Tiltakseffekt' = SUM('FactAction'[RealisertEffektMNOK])
\t\tformatString: #,##0.00 MNOK
\t\tdisplayFolder: _08 Tiltak & FactAction
\t\tlineageTag: [[GUID]]

\tmeasure 'Gjenstående Tiltakseffekt' = [Forventet Tiltakseffekt] - [Realisert Tiltakseffekt]
\t\tformatString: #,##0.00 MNOK
\t\tdisplayFolder: _08 Tiltak & FactAction
\t\tlineageTag: [[GUID]]

\tmeasure 'Tiltaksdekning %' = DIVIDE([Realisert Tiltakseffekt], [Forventet Tiltakseffekt], 0)
\t\tformatString: 0.0%
\t\tdisplayFolder: _08 Tiltak & FactAction
\t\tlineageTag: [[GUID]]

\tcolumn Column1
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
    with open(os.path.join(SEMANTIC_DIR, "tables", "_Measures.tmdl"), "w", encoding="utf-8") as f:
        f.write(fill_guids(t_measures))

    print("TMDL Semantic Model files written successfully!")

if __name__ == "__main__":
    ensure_dirs()
    write_tmdl_semantic_model()
