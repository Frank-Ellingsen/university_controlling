"""
Generator for TMDL (Tabular Model Definition Language) for UiA Power BI Semantisk Modell.
Genererer komplette TMDL-tabellfiler, relasjoner og måltall direkte inn i:
UIA-project-2026YTD.SemanticModel/definition/

Forfatter: Frank Ellingsen (Project Controller)
"""

import uuid
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SEMANTIC_DIR = BASE_DIR / "UIA-project-2026YTD.SemanticModel" / "definition"
TABLES_DIR = SEMANTIC_DIR / "tables"

def uid():
    return str(uuid.uuid4())

def fill_uids(template: str) -> str:
    while "__UID__" in template:
        template = template.replace("__UID__", uid(), 1)
    return template

def generate():
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    print("=" * 80)
    print("GENERERER POWER BI TMDL DATAMODELL")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # 1. DimOrganization
    # -------------------------------------------------------------------------
    dim_org = fill_uids("""table DimOrganization
\tlineageTag: __UID__

\tcolumn OrgKode
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: OrgKode

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Enhet
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Enhet

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Kortnavn
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Kortnavn

\t\tannotation SummarizationSetBy = Automatic

\tcolumn OverordnetEnhet
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: OverordnetEnhet

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Nivaa
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Nivaa

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Type
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Type

\t\tannotation SummarizationSetBy = Automatic

\tpartition DimOrganization = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\data\\DimOrganization.csv"),[Delimiter=";", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"OrgKode", Int64.Type}, {"Enhet", type text}, {"Kortnavn", type text}, {"OverordnetEnhet", Int64.Type}, {"Nivaa", Int64.Type}, {"Type", type text}})
\t\t\tin
\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
""")
    (TABLES_DIR / "DimOrganization.tmdl").write_text(dim_org, encoding="utf-8")
    print("  - DimOrganization.tmdl generert")

    # -------------------------------------------------------------------------
    # 2. DimDate
    # -------------------------------------------------------------------------
    dim_date = fill_uids("""table DimDate
\tlineageTag: __UID__
\tdataCategory: Time

\tcolumn DatoNokkel
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: DatoNokkel

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Dato
\t\tdataType: dateTime
\t\tformatString: yyyy-MM-dd
\t\tisKey
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Dato

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Aar
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Aar

\t\tannotation SummarizationSetBy = Automatic

\tcolumn MaanedNummer
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: MaanedNummer

\t\tannotation SummarizationSetBy = Automatic

\tcolumn MaanedNavn
\t\tdataType: string
\t\tsortByColumn: MaanedNummer
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: MaanedNavn

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Kvartal
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Kvartal

\t\tannotation SummarizationSetBy = Automatic

\tcolumn StatusPr30Sep
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: StatusPr30Sep

\t\tannotation SummarizationSetBy = Automatic

\tpartition DimDate = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\data\\DimDate.csv"),[Delimiter=";", Columns=7, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"DatoNokkel", Int64.Type}, {"Dato", type date}, {"Aar", Int64.Type}, {"MaanedNummer", Int64.Type}, {"MaanedNavn", type text}, {"Kvartal", type text}, {"StatusPr30Sep", type text}})
\t\t\tin
\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
""")
    (TABLES_DIR / "DimDate.tmdl").write_text(dim_date, encoding="utf-8")
    print("  - DimDate.tmdl generert")

    # -------------------------------------------------------------------------
    # 3. DimForecastVersion
    # -------------------------------------------------------------------------
    dim_ver = fill_uids("""table DimForecastVersion
\tlineageTag: __UID__

\tcolumn VersjonKode
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: VersjonKode

\t\tannotation SummarizationSetBy = Automatic

\tcolumn VersjonNavn
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: VersjonNavn

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Beskrivelse
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Beskrivelse

\t\tannotation SummarizationSetBy = Automatic

\tpartition DimForecastVersion = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\data\\DimForecastVersion.csv"),[Delimiter=";", Columns=3, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"VersjonKode", type text}, {"VersjonNavn", type text}, {"Beskrivelse", type text}})
\t\t\tin
\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
""")
    (TABLES_DIR / "DimForecastVersion.tmdl").write_text(dim_ver, encoding="utf-8")
    print("  - DimForecastVersion.tmdl generert")

    # -------------------------------------------------------------------------
    # 4. DimAccountHierarchy
    # -------------------------------------------------------------------------
    dim_acc = fill_uids("""table DimAccountHierarchy
\tlineageTag: __UID__

\tcolumn Konto
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Konto

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Kontonavn
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Kontonavn

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Nivaa1_Kontoklasse
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Nivaa1_Kontoklasse

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Nivaa1_Navn
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Nivaa1_Navn

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Nivaa2_Kontogruppe
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Nivaa2_Kontogruppe

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Nivaa2_Navn
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Nivaa2_Navn

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Nivaa3_Standardkonto
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Nivaa3_Standardkonto

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Nivaa3_Navn
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Nivaa3_Navn

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Nivaa4_Underkonto
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Nivaa4_Underkonto

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Nivaa4_Navn
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Nivaa4_Navn

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Kontotype
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Kontotype

\t\tannotation SummarizationSetBy = Automatic

\tcolumn SRS_regnskapslinje
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: SRS_regnskapslinje

\t\tannotation SummarizationSetBy = Automatic

\tpartition DimAccountHierarchy = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\data\\DimAccountHierarchy.csv"),[Delimiter=";", Columns=12, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"Konto", Int64.Type}, {"Kontonavn", type text}, {"Nivaa1_Kontoklasse", Int64.Type}, {"Nivaa1_Navn", type text}, {"Nivaa2_Kontogruppe", Int64.Type}, {"Nivaa2_Navn", type text}, {"Nivaa3_Standardkonto", Int64.Type}, {"Nivaa3_Navn", type text}, {"Nivaa4_Underkonto", Int64.Type}, {"Nivaa4_Navn", type text}, {"Kontotype", type text}, {"SRS_regnskapslinje", type text}})
\t\t\tin
\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
""")
    (TABLES_DIR / "DimAccountHierarchy.tmdl").write_text(dim_acc, encoding="utf-8")
    print("  - DimAccountHierarchy.tmdl generert")

    # -------------------------------------------------------------------------
    # 5. FactGL
    # -------------------------------------------------------------------------
    fact_gl = fill_uids("""table FactGL
\tlineageTag: __UID__

\tcolumn DatoNokkel
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: DatoNokkel

\t\tannotation SummarizationSetBy = Automatic

\tcolumn OrgKode
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: OrgKode

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Konto
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Konto

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Kontonavn
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Kontonavn

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Artstype
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Artstype

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Kategori
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Kategori

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Belop_MNOK
\t\tdataType: double
\t\tformatString: #,##0.000
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Belop_MNOK

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Belop_signert_MNOK
\t\tdataType: double
\t\tformatString: #,##0.000
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Belop_signert_MNOK

\t\tannotation SummarizationSetBy = Automatic

\tcolumn VersjonKode
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: VersjonKode

\t\tannotation SummarizationSetBy = Automatic

\tpartition FactGL = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\data\\FactGL.csv"),[Delimiter=";", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"DatoNokkel", Int64.Type}, {"OrgKode", Int64.Type}, {"Konto", Int64.Type}, {"Kontonavn", type text}, {"Artstype", type text}, {"Kategori", type text}, {"Belop_MNOK", type number}, {"Belop_signert_MNOK", type number}, {"VersjonKode", type text}})
\t\t\tin
\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
""")
    (TABLES_DIR / "FactGL.tmdl").write_text(fact_gl, encoding="utf-8")
    print("  - FactGL.tmdl generert")

    # -------------------------------------------------------------------------
    # 6. FactBudget
    # -------------------------------------------------------------------------
    fact_budget = fill_uids("""table FactBudget
\tlineageTag: __UID__

\tcolumn DatoNokkel
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: DatoNokkel

\t\tannotation SummarizationSetBy = Automatic

\tcolumn OrgKode
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: OrgKode

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Konto
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Konto

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Kontonavn
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Kontonavn

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Artstype
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Artstype

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Kategori
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Kategori

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Budsjett_MNOK
\t\tdataType: double
\t\tformatString: #,##0.000
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Budsjett_MNOK

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Budsjett_signert_MNOK
\t\tdataType: double
\t\tformatString: #,##0.000
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Budsjett_signert_MNOK

\t\tannotation SummarizationSetBy = Automatic

\tcolumn VersjonKode
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: VersjonKode

\t\tannotation SummarizationSetBy = Automatic

\tpartition FactBudget = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\data\\FactBudget.csv"),[Delimiter=";", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"DatoNokkel", Int64.Type}, {"OrgKode", Int64.Type}, {"Konto", Int64.Type}, {"Kontonavn", type text}, {"Artstype", type text}, {"Kategori", type text}, {"Budsjett_MNOK", type number}, {"Budsjett_signert_MNOK", type number}, {"VersjonKode", type text}})
\t\t\tin
\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
""")
    (TABLES_DIR / "FactBudget.tmdl").write_text(fact_budget, encoding="utf-8")
    print("  - FactBudget.tmdl generert")

    # -------------------------------------------------------------------------
    # 7. FactEVM
    # -------------------------------------------------------------------------
    fact_evm = fill_uids("""table FactEVM
\tlineageTag: __UID__

\tcolumn DatoNokkel
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: DatoNokkel

\t\tannotation SummarizationSetBy = Automatic

\tcolumn OrgKode
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: OrgKode

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Planned_Value_PV_MNOK
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Planned_Value_PV_MNOK

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Earned_Value_EV_MNOK
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Earned_Value_EV_MNOK

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Actual_Cost_AC_MNOK
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Actual_Cost_AC_MNOK

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Budget_At_Completion_BAC_MNOK
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Budget_At_Completion_BAC_MNOK

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Estimate_At_Completion_EAC_MNOK
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Estimate_At_Completion_EAC_MNOK

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Estimate_To_Complete_ETC_MNOK
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Estimate_To_Complete_ETC_MNOK

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Cost_Performance_Index_CPI
\t\tdataType: double
\t\tformatString: 0.00
\t\tlineageTag: __UID__
\t\tsummarizeBy: average
\t\tsourceColumn: Cost_Performance_Index_CPI

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Schedule_Performance_Index_SPI
\t\tdataType: double
\t\tformatString: 0.00
\t\tlineageTag: __UID__
\t\tsummarizeBy: average
\t\tsourceColumn: Schedule_Performance_Index_SPI

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Variance_At_Completion_VAC_MNOK
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Variance_At_Completion_VAC_MNOK

\t\tannotation SummarizationSetBy = Automatic

\tpartition FactEVM = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\data\\FactEVM.csv"),[Delimiter=";", Columns=11, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"DatoNokkel", Int64.Type}, {"OrgKode", Int64.Type}, {"Planned_Value_PV_MNOK", type number}, {"Earned_Value_EV_MNOK", type number}, {"Actual_Cost_AC_MNOK", type number}, {"Budget_At_Completion_BAC_MNOK", type number}, {"Estimate_At_Completion_EAC_MNOK", type number}, {"Estimate_To_Complete_ETC_MNOK", type number}, {"Cost_Performance_Index_CPI", type number}, {"Schedule_Performance_Index_SPI", type number}, {"Variance_At_Completion_VAC_MNOK", type number}})
\t\t\tin
\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
""")
    (TABLES_DIR / "FactEVM.tmdl").write_text(fact_evm, encoding="utf-8")
    print("  - FactEVM.tmdl generert")

    # -------------------------------------------------------------------------
    # 8. FactFTE
    # -------------------------------------------------------------------------
    fact_fte = fill_uids("""table FactFTE
\tlineageTag: __UID__

\tcolumn DatoNokkel
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: DatoNokkel

\t\tannotation SummarizationSetBy = Automatic

\tcolumn OrgKode
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: OrgKode

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Aarsverk_UF
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Aarsverk_UF

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Aarsverk_TA
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Aarsverk_TA

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Aarsverk_Faktisk
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Aarsverk_Faktisk

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Aarsverk_Budsjett
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Aarsverk_Budsjett

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Antall_Ansatte
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Antall_Ansatte

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Ubesatte_Vakanser
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Ubesatte_Vakanser

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Faglig_Andel_Pct
\t\tdataType: double
\t\tformatString: 0.0%
\t\tlineageTag: __UID__
\t\tsummarizeBy: average
\t\tsourceColumn: Faglig_Andel_Pct

\t\tannotation SummarizationSetBy = Automatic

\tcolumn VersjonKode
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: VersjonKode

\t\tannotation SummarizationSetBy = Automatic

\tpartition FactFTE = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\data\\FactFTE.csv"),[Delimiter=";", Columns=10, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"DatoNokkel", Int64.Type}, {"OrgKode", Int64.Type}, {"Aarsverk_UF", type number}, {"Aarsverk_TA", type number}, {"Aarsverk_Faktisk", type number}, {"Aarsverk_Budsjett", type number}, {"Antall_Ansatte", Int64.Type}, {"Ubesatte_Vakanser", type number}, {"Faglig_Andel_Pct", type number}, {"VersjonKode", type text}})
\t\t\tin
\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
""")
    (TABLES_DIR / "FactFTE.tmdl").write_text(fact_fte, encoding="utf-8")
    print("  - FactFTE.tmdl generert")

    # -------------------------------------------------------------------------
    # 9. FactFacultyKPI
    # -------------------------------------------------------------------------
    fact_kpi = fill_uids("""table FactFacultyKPI
\tlineageTag: __UID__

\tcolumn OrgKode
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: OrgKode

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Fakultet
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Fakultet

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Statlig_Bevilgning_MNOK
\t\tdataType: double
\t\tformatString: #,##0.00
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Statlig_Bevilgning_MNOK

\t\tannotation SummarizationSetBy = Automatic

\tcolumn BOA_Andre_Inntekt_MNOK
\t\tdataType: double
\t\tformatString: #,##0.00
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: BOA_Andre_Inntekt_MNOK

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Total_Inntekt_MNOK
\t\tdataType: double
\t\tformatString: #,##0.00
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Total_Inntekt_MNOK

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Lonnskostnader_MNOK
\t\tdataType: double
\t\tformatString: #,##0.00
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Lonnskostnader_MNOK

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Driftskostnader_MNOK
\t\tdataType: double
\t\tformatString: #,##0.00
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Driftskostnader_MNOK

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Investeringer_Capex_MNOK
\t\tdataType: double
\t\tformatString: #,##0.00
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Investeringer_Capex_MNOK

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Total_Kostnad_MNOK
\t\tdataType: double
\t\tformatString: #,##0.00
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Total_Kostnad_MNOK

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Netto_Resultat_MNOK
\t\tdataType: double
\t\tformatString: #,##0.00
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Netto_Resultat_MNOK

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Lonnsandel_Pct
\t\tdataType: double
\t\tformatString: 0.0%
\t\tlineageTag: __UID__
\t\tsummarizeBy: average
\t\tsourceColumn: Lonnsandel_Pct

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Aarsverk_UF
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Aarsverk_UF

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Aarsverk_TA
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Aarsverk_TA

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Total_Aarsverk
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Total_Aarsverk

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Antall_Ansatte
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Antall_Ansatte

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Antall_Studenter
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Antall_Studenter

\t\tannotation SummarizationSetBy = Automatic

\tcolumn SPE60_Helarsstudenter
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: SPE60_Helarsstudenter

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Studenter_Pr_Faglig_AV
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: __UID__
\t\tsummarizeBy: average
\t\tsourceColumn: Studenter_Pr_Faglig_ÅV

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Kostnad_Pr_SPE60_NOK
\t\tdataType: int64
\t\tformatString: #,##0
\t\tlineageTag: __UID__
\t\tsummarizeBy: average
\t\tsourceColumn: Kostnad_Pr_SPE60_NOK

\t\tannotation SummarizationSetBy = Automatic

\tcolumn RAG_Status
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: RAG_Status

\t\tannotation SummarizationSetBy = Automatic

\tpartition FactFacultyKPI = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\data\\FactFacultyKPI.csv"),[Delimiter=";", Columns=20, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"OrgKode", Int64.Type}, {"Fakultet", type text}, {"Statlig_Bevilgning_MNOK", type number}, {"BOA_Andre_Inntekt_MNOK", type number}, {"Total_Inntekt_MNOK", type number}, {"Lonnskostnader_MNOK", type number}, {"Driftskostnader_MNOK", type number}, {"Investeringer_Capex_MNOK", type number}, {"Total_Kostnad_MNOK", type number}, {"Netto_Resultat_MNOK", type number}, {"Lonnsandel_Pct", type number}, {"Aarsverk_UF", type number}, {"Aarsverk_TA", type number}, {"Total_Aarsverk", type number}, {"Antall_Ansatte", Int64.Type}, {"Antall_Studenter", Int64.Type}, {"SPE60_Helarsstudenter", type number}, {"Studenter_Pr_Faglig_ÅV", type number}, {"Kostnad_Pr_SPE60_NOK", Int64.Type}, {"RAG_Status", type text}})
\t\t\tin
\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
""")
    (TABLES_DIR / "FactFacultyKPI.tmdl").write_text(fact_kpi, encoding="utf-8")
    print("  - FactFacultyKPI.tmdl generert")

    # -------------------------------------------------------------------------
    # 10. FactStudents
    # -------------------------------------------------------------------------
    fact_stud = fill_uids("""table FactStudents
\tlineageTag: __UID__

\tcolumn Aar
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Aar

\t\tannotation SummarizationSetBy = Automatic

\tcolumn OrgKode
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: OrgKode

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Registrerte_Studenter
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Registrerte_Studenter

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Avlagte_Studiepoeng_Totalt
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: Avlagte_Studiepoeng_Totalt

\t\tannotation SummarizationSetBy = Automatic

\tcolumn SPE60_Helarsstudenter
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: SPE60_Helarsstudenter

\t\tannotation SummarizationSetBy = Automatic

\tcolumn KD_Kategori1_SPE60
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: KD_Kategori1_SPE60

\t\tannotation SummarizationSetBy = Automatic

\tcolumn KD_Kategori2_SPE60
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: KD_Kategori2_SPE60

\t\tannotation SummarizationSetBy = Automatic

\tcolumn KD_Kategori3_SPE60
\t\tdataType: double
\t\tformatString: #,##0.0
\t\tlineageTag: __UID__
\t\tsummarizeBy: sum
\t\tsourceColumn: KD_Kategori3_SPE60

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Bestattandel_Pct
\t\tdataType: double
\t\tformatString: 0.0%
\t\tlineageTag: __UID__
\t\tsummarizeBy: average
\t\tsourceColumn: Bestattandel_Pct

\t\tannotation SummarizationSetBy = Automatic

\tcolumn Gjennomforing_Normert_Pct
\t\tdataType: double
\t\tformatString: 0.0%
\t\tlineageTag: __UID__
\t\tsummarizeBy: average
\t\tsourceColumn: Gjennomforing_Normert_Pct

\t\tannotation SummarizationSetBy = Automatic

\tpartition FactStudents = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t    Source = Csv.Document(File.Contents("C:\\Users\\frank\\Desktop\\UIA2\\data\\FactStudents.csv"),[Delimiter=";", Columns=10, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"Aar", Int64.Type}, {"OrgKode", Int64.Type}, {"Registrerte_Studenter", Int64.Type}, {"Avlagte_Studiepoeng_Totalt", Int64.Type}, {"SPE60_Helarsstudenter", type number}, {"KD_Kategori1_SPE60", type number}, {"KD_Kategori2_SPE60", type number}, {"KD_Kategori3_SPE60", type number}, {"Bestattandel_Pct", type number}, {"Gjennomforing_Normert_Pct", type number}})
\t\t\tin
\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
""")
    (TABLES_DIR / "FactStudents.tmdl").write_text(fact_stud, encoding="utf-8")
    print("  - FactStudents.tmdl generert")

    # -------------------------------------------------------------------------
    # 11. _Measures
    # -------------------------------------------------------------------------
    measures_tmdl = fill_uids("""table _Measures
\tlineageTag: __UID__

\tcolumn Column1
\t\tdataType: string
\t\tlineageTag: __UID__
\t\tsummarizeBy: none
\t\tsourceColumn: Column1
\t\tisHidden

\t\tannotation SummarizationSetBy = Automatic

\tmeasure 'Actual YTD' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactGL'[Belop_signert_MNOK]),
\t\t\t    'FactGL'[VersjonKode] = "ACTUAL_YTD_SEP2026"
\t\t\t)
\t\tformatString: #,##0.00
\t\tdisplayFolder: _01 Regnskap & YTD
\t\tlineageTag: __UID__

\tmeasure 'Budsjett YTD' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactBudget'[Budsjett_signert_MNOK]),
\t\t\t    'DimDate'[StatusPr30Sep] = "Actual"
\t\t\t)
\t\tformatString: #,##0.00
\t\tdisplayFolder: _01 Regnskap & YTD
\t\tlineageTag: __UID__

\tmeasure 'Avvik YTD' = [Actual YTD] - [Budsjett YTD]
\t\tformatString: #,##0.00
\t\tdisplayFolder: _01 Regnskap & YTD
\t\tlineageTag: __UID__

\tmeasure 'Avvik YTD %' = DIVIDE([Avvik YTD], ABS([Budsjett YTD]), 0)
\t\tformatString: 0.0%
\t\tdisplayFolder: _01 Regnskap & YTD
\t\tlineageTag: __UID__

\tmeasure 'Forecast Q4' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactGL'[Belop_signert_MNOK]),
\t\t\t    'FactGL'[VersjonKode] = "FC_Q4_2026"
\t\t\t)
\t\tformatString: #,##0.00
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: __UID__

\tmeasure 'Forecast LE (EAC)' = [Actual YTD] + [Forecast Q4]
\t\tformatString: #,##0.00
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: __UID__

\tmeasure 'Årsbudsjett (BAC)' = SUM('FactBudget'[Budsjett_signert_MNOK])
\t\tformatString: #,##0.00
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: __UID__

\tmeasure 'Sluttavvik (VAC)' = [Årsbudsjett (BAC)] - [Forecast LE (EAC)]
\t\tformatString: #,##0.00
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: __UID__

\tmeasure 'VAC %' = DIVIDE([Sluttavvik (VAC)], ABS([Årsbudsjett (BAC)]), 0)
\t\tformatString: 0.0%
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: __UID__

\tmeasure 'Planned Value (PV)' = SUM('FactEVM'[Planned_Value_PV_MNOK])
\t\tformatString: #,##0.0
\t\tdisplayFolder: _03 EVM
\t\tlineageTag: __UID__

\tmeasure 'Earned Value (EV)' = SUM('FactEVM'[Earned_Value_EV_MNOK])
\t\tformatString: #,##0.0
\t\tdisplayFolder: _03 EVM
\t\tlineageTag: __UID__

\tmeasure 'Actual Cost (AC)' = SUM('FactEVM'[Actual_Cost_AC_MNOK])
\t\tformatString: #,##0.0
\t\tdisplayFolder: _03 EVM
\t\tlineageTag: __UID__

\tmeasure 'CPI' = DIVIDE([Earned Value (EV)], [Actual Cost (AC)], 1)
\t\tformatString: 0.00
\t\tdisplayFolder: _03 EVM
\t\tlineageTag: __UID__

\tmeasure 'SPI' = DIVIDE([Earned Value (EV)], [Planned Value (PV)], 1)
\t\tformatString: 0.00
\t\tdisplayFolder: _03 EVM
\t\tlineageTag: __UID__

\tmeasure 'Totale Årsverk' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactFTE'[Aarsverk_Faktisk]),
\t\t\t    'DimDate'[DatoNokkel] = MAX('FactFTE'[DatoNokkel])
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _04 Bemanning & FTE
\t\tlineageTag: __UID__

\tmeasure 'Faglige Årsverk (UF)' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactFTE'[Aarsverk_UF]),
\t\t\t    'DimDate'[DatoNokkel] = MAX('FactFTE'[DatoNokkel])
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _04 Bemanning & FTE
\t\tlineageTag: __UID__

\tmeasure 'Teknisk-Admin Årsverk (TA)' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactFTE'[Aarsverk_TA]),
\t\t\t    'DimDate'[DatoNokkel] = MAX('FactFTE'[DatoNokkel])
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _04 Bemanning & FTE
\t\tlineageTag: __UID__

\tmeasure 'Faglig Andel %' = DIVIDE([Faglige Årsverk (UF)], [Totale Årsverk], 0)
\t\tformatString: 0.0%
\t\tdisplayFolder: _04 Bemanning & FTE
\t\tlineageTag: __UID__

\tmeasure 'Registrerte Studenter' = SUM('FactStudents'[Registrerte_Studenter])
\t\tformatString: #,##0
\t\tdisplayFolder: _05 Utdanning
\t\tlineageTag: __UID__

\tmeasure 'Avlagte SPE60' = SUM('FactStudents'[SPE60_Helarsstudenter])
\t\tformatString: #,##0.0
\t\tdisplayFolder: _05 Utdanning
\t\tlineageTag: __UID__

\tmeasure 'Studenter pr UF-Årsverk' = DIVIDE([Registrerte Studenter], [Faglige Årsverk (UF)], 0)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _05 Utdanning
\t\tlineageTag: __UID__

\tmeasure 'Enhetskostnad pr SPE60' = DIVIDE([Forecast LE (EAC)] * 1000000, [Avlagte SPE60], 0)
\t\tformatString: #,##0
\t\tdisplayFolder: _05 Utdanning
\t\tlineageTag: __UID__

\tmeasure 'KD Resultatbevilgning MNOK' =
\t\t\tVAR Kat1 = SUM('FactStudents'[KD_Kategori1_SPE60]) * 54550
\t\t\tVAR Kat2 = SUM('FactStudents'[KD_Kategori2_SPE60]) * 81800
\t\t\tVAR Kat3 = SUM('FactStudents'[KD_Kategori3_SPE60]) * 190900
\t\t\tRETURN DIVIDE(Kat1 + Kat2 + Kat3, 1000000, 0)
\t\tformatString: #,##0.00
\t\tdisplayFolder: _05 Utdanning
\t\tlineageTag: __UID__

\tmeasure 'Forecast RAG Status' =
\t\t\tIF([Sluttavvik (VAC)] >= 0, "🟢 Under/I budsjett",
\t\t\t    IF([VAC %] >= -0.05, "🟡 Moderat overskridelse (< 5%)",
\t\t\t        "🔴 Kritisk overskridelse (> 5%)"
\t\t\t    )
\t\t\t)
\t\tdisplayFolder: _06 RAG & Design
\t\tlineageTag: __UID__

\tmeasure 'RAG Hex Color' =
\t\t\tIF([Sluttavvik (VAC)] >= 0, "#10b981",
\t\t\t    IF([VAC %] >= -0.05, "#f59e0b",
\t\t\t        "#ef4444"
\t\t\t    )
\t\t\t)
\t\tdisplayFolder: _06 RAG & Design
\t\tlineageTag: __UID__

\tpartition _Measures = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("i44FAA==", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type nullable text) meta [Serialized.Text = true]) in type table [Column1 = _t])
\t\t\tin
\t\t\t    Source

\tannotation PBI_ResultType = Table
""")
    (TABLES_DIR / "_Measures.tmdl").write_text(measures_tmdl, encoding="utf-8")
    print("  - _Measures.tmdl generert")

    # -------------------------------------------------------------------------
    # 12. relationships.tmdl
    # -------------------------------------------------------------------------
    rel_content = fill_uids("""relationship __UID__
\tfromColumn: FactGL.OrgKode
\ttoColumn: DimOrganization.OrgKode

relationship __UID__
\tfromColumn: FactBudget.OrgKode
\ttoColumn: DimOrganization.OrgKode

relationship __UID__
\tfromColumn: FactFTE.OrgKode
\ttoColumn: DimOrganization.OrgKode

relationship __UID__
\tfromColumn: FactStudents.OrgKode
\ttoColumn: DimOrganization.OrgKode

relationship __UID__
\tfromColumn: FactFacultyKPI.OrgKode
\ttoColumn: DimOrganization.OrgKode

relationship __UID__
\tfromColumn: FactGL.DatoNokkel
\ttoColumn: DimDate.DatoNokkel

relationship __UID__
\tfromColumn: FactBudget.DatoNokkel
\ttoColumn: DimDate.DatoNokkel

relationship __UID__
\tfromColumn: FactFTE.DatoNokkel
\ttoColumn: DimDate.DatoNokkel

relationship __UID__
\tfromColumn: FactEVM.DatoNokkel
\ttoColumn: DimDate.DatoNokkel

relationship __UID__
\tfromColumn: FactGL.VersjonKode
\ttoColumn: DimForecastVersion.VersjonKode

relationship __UID__
\tfromColumn: FactBudget.VersjonKode
\ttoColumn: DimForecastVersion.VersjonKode

relationship __UID__
\tfromColumn: FactGL.Konto
\ttoColumn: DimAccountHierarchy.Konto
""")
    (SEMANTIC_DIR / "relationships.tmdl").write_text(rel_content, encoding="utf-8")
    print("  - relationships.tmdl generert (12 stjernemodell-relasjoner)")

    # -------------------------------------------------------------------------
    # 13. model.tmdl oppdatering
    # -------------------------------------------------------------------------
    model_content = """model Model
\tculture: en-US
\tdefaultPowerBIDataSourceVersion: powerBI_V3
\tsourceQueryCulture: en-US
\tvalueFilterBehavior: independent
\tdataAccessOptions
\t\tlegacyRedirects
\t\treturnErrorValuesAsNull

annotation __PBI_TimeIntelligenceEnabled = 1

annotation PBI_ProTooling = ["DevMode"]

ref table DimAccountHierarchy
ref table DimDate
ref table DimForecastVersion
ref table DimOrganization
ref table FactBudget
ref table FactEVM
ref table FactFTE
ref table FactFacultyKPI
ref table FactGL
ref table FactStudents
ref table _Measures

ref cultureInfo en-US
"""
    (SEMANTIC_DIR / "model.tmdl").write_text(model_content, encoding="utf-8")
    print("  - model.tmdl oppdatert med referanser til alle 11 tabeller")
    print("\n" + "=" * 80)
    print("TMDL DATAMODELL FULLFØRT.")
    print("=" * 80)

if __name__ == "__main__":
    generate()
