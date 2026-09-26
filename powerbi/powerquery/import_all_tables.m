// ==============================================================================
// Universitetet i Agder (UiA) - Power Query M Importskript
// Inneholder spørringer for alle dimensjons- og faktatabeller
// Forfatter: Frank Ellingsen (Project Controller)
// ==============================================================================

// Parameter: DataFolder
// Angir stien til data-katalogen (kan endres ved distribusjon eller CI/CD)
let
    DataFolder = "C:\Users\frank\Desktop\UIA2\data\" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
in
    DataFolder

// ------------------------------------------------------------------------------
// DimOrganization
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolder & "DimOrganization.csv"), [Delimiter=";", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"OrgKode", Int64.Type}, 
        {"Enhet", type text}, 
        {"Kortnavn", type text}, 
        {"OverordnetEnhet", Int64.Type}, 
        {"Nivaa", Int64.Type}, 
        {"Type", type text}
    })
in
    #"Changed Type"

// ------------------------------------------------------------------------------
// DimDate
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolder & "DimDate.csv"), [Delimiter=";", Columns=7, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"DatoNokkel", Int64.Type}, 
        {"Dato", type date}, 
        {"Aar", Int64.Type}, 
        {"MaanedNummer", Int64.Type}, 
        {"MaanedNavn", type text}, 
        {"Kvartal", type text}, 
        {"StatusPr30Sep", type text}
    })
in
    #"Changed Type"

// ------------------------------------------------------------------------------
// DimForecastVersion
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolder & "DimForecastVersion.csv"), [Delimiter=";", Columns=3, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"VersjonKode", type text}, 
        {"VersjonNavn", type text}, 
        {"Beskrivelse", type text}
    })
in
    #"Changed Type"

// ------------------------------------------------------------------------------
// DimAccountHierarchy
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolder & "DimAccountHierarchy.csv"), [Delimiter=";", Columns=12, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"Konto", Int64.Type}, 
        {"Kontonavn", type text}, 
        {"Nivaa1_Kontoklasse", Int64.Type}, 
        {"Nivaa1_Navn", type text}, 
        {"Nivaa2_Kontogruppe", Int64.Type}, 
        {"Nivaa2_Navn", type text}, 
        {"Nivaa3_Standardkonto", Int64.Type}, 
        {"Nivaa3_Navn", type text}, 
        {"Nivaa4_Underkonto", Int64.Type}, 
        {"Nivaa4_Navn", type text}, 
        {"Kontotype", type text}, 
        {"SRS_regnskapslinje", type text}
    })
in
    #"Changed Type"

// ------------------------------------------------------------------------------
// FactGL
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolder & "FactGL.csv"), [Delimiter=";", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"DatoNokkel", Int64.Type}, 
        {"OrgKode", Int64.Type}, 
        {"Konto", Int64.Type}, 
        {"Kontonavn", type text}, 
        {"Artstype", type text}, 
        {"Kategori", type text}, 
        {"Belop_MNOK", type number}, 
        {"Belop_signert_MNOK", type number}, 
        {"VersjonKode", type text}
    })
in
    #"Changed Type"

// ------------------------------------------------------------------------------
// FactBudget
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolder & "FactBudget.csv"), [Delimiter=";", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"DatoNokkel", Int64.Type}, 
        {"OrgKode", Int64.Type}, 
        {"Konto", Int64.Type}, 
        {"Kontonavn", type text}, 
        {"Artstype", type text}, 
        {"Kategori", type text}, 
        {"Budsjett_MNOK", type number}, 
        {"Budsjett_signert_MNOK", type number}, 
        {"VersjonKode", type text}
    })
in
    #"Changed Type"

// ------------------------------------------------------------------------------
// FactEVM
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolder & "FactEVM.csv"), [Delimiter=";", Columns=11, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"DatoNokkel", Int64.Type}, 
        {"OrgKode", Int64.Type}, 
        {"Planned_Value_PV_MNOK", type number}, 
        {"Earned_Value_EV_MNOK", type number}, 
        {"Actual_Cost_AC_MNOK", type number}, 
        {"Budget_At_Completion_BAC_MNOK", type number}, 
        {"Estimate_At_Completion_EAC_MNOK", type number}, 
        {"Estimate_To_Complete_ETC_MNOK", type number}, 
        {"Cost_Performance_Index_CPI", type number}, 
        {"Schedule_Performance_Index_SPI", type number}, 
        {"Variance_At_Completion_VAC_MNOK", type number}
    })
in
    #"Changed Type"

// ------------------------------------------------------------------------------
// FactFTE
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolder & "FactFTE.csv"), [Delimiter=";", Columns=10, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"DatoNokkel", Int64.Type}, 
        {"OrgKode", Int64.Type}, 
        {"Aarsverk_UF", type number}, 
        {"Aarsverk_TA", type number}, 
        {"Aarsverk_Faktisk", type number}, 
        {"Aarsverk_Budsjett", type number}, 
        {"Antall_Ansatte", Int64.Type}, 
        {"Ubesatte_Vakanser", type number}, 
        {"Faglig_Andel_Pct", type number}, 
        {"VersjonKode", type text}
    })
in
    #"Changed Type"

// ------------------------------------------------------------------------------
// FactStudents
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolder & "FactStudents.csv"), [Delimiter=";", Columns=10, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"Aar", Int64.Type}, 
        {"OrgKode", Int64.Type}, 
        {"Registrerte_Studenter", Int64.Type}, 
        {"Avlagte_Studiepoeng_Totalt", Int64.Type}, 
        {"SPE60_Helarsstudenter", type number}, 
        {"KD_Kategori1_SPE60", type number}, 
        {"KD_Kategori2_SPE60", type number}, 
        {"KD_Kategori3_SPE60", type number}, 
        {"Bestattandel_Pct", type number}, 
        {"Gjennomforing_Normert_Pct", type number}
    })
in
    #"Changed Type"
