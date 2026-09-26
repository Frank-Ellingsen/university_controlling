// ==============================================================================
// Universitetet i Agder (UiA) - Power Query M: DuckDB Python Bridge
// Kobler Power BI Desktop direkte til den lokale DuckDB-analysedatabasen
// (uia_analytics.duckdb) via Python-motoren.
//
// Forfatter: Frank Ellingsen (Project Controller)
// ==============================================================================

// ------------------------------------------------------------------------------
// Parameter: DuckDBDatabasePath
// ------------------------------------------------------------------------------
let
    DuckDBDatabasePath = "C:\Users\frank\Desktop\UIA2\uia_analytics.duckdb" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
in
    DuckDBDatabasePath


// ------------------------------------------------------------------------------
// Fellesfunksjon: fnDuckDBQuery
// Tar inn en SQL-streng og returnerer en ferdig typet Power Query-tabell fra DuckDB
// ------------------------------------------------------------------------------
let
    fnDuckDBQuery = (sqlQuery as text) as table =>
    let
        PythonCode = 
            "import duckdb#(lf)" & 
            "con = duckdb.connect(r'" & DuckDBDatabasePath & "', read_only=True)#(lf)" & 
            "df = con.execute('''" & sqlQuery & "''').df()#(lf)" & 
            "con.close()",
        Source = Python.Execute(PythonCode),
        ResultTable = Source{[Name="df"]}[Value]
    in
        ResultTable
in
    fnDuckDBQuery


// ==============================================================================
// 1. ANALYTISKE VISNINGER (PRE-AGREGATED / JOINED VIEWS)
// ==============================================================================

// ------------------------------------------------------------------------------
// Spørring 1: DuckDB_v_avvik_budsjett_actual
// Henter ferdig avstemt budsjettavvik per fakultet og regnskapslinje
// ------------------------------------------------------------------------------
let
    Source = Python.Execute(
        "import duckdb#(lf)" & 
        "con = duckdb.connect(r'" & DuckDBDatabasePath & "', read_only=True)#(lf)" & 
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


// ------------------------------------------------------------------------------
// Spørring 2: DuckDB_v_evm_sammendrag
// Henter Earned Value Management-nøkkeltall (PV, EV, AC, CPI, SPI, EAC, VAC)
// ------------------------------------------------------------------------------
let
    Source = Python.Execute(
        "import duckdb#(lf)" & 
        "con = duckdb.connect(r'" & DuckDBDatabasePath & "', read_only=True)#(lf)" & 
        "df = con.execute('SELECT * FROM v_evm_sammendrag').df()#(lf)" & 
        "con.close()"
    ),
    df_Table = Source{[Name="df"]}[Value],
    #"Changed Type" = Table.TransformColumnTypes(df_Table,{
        {"DatoNokkel", Int64.Type}, 
        {"MaanedNavn", type text}, 
        {"Kvartal", type text}, 
        {"OrgKode", Int64.Type}, 
        {"Enhet", type text}, 
        {"PV", type number}, 
        {"EV", type number}, 
        {"AC", type number}, 
        {"BAC", type number}, 
        {"EAC", type number}, 
        {"ETC", type number}, 
        {"CPI", type number}, 
        {"SPI", type number}, 
        {"VAC", type number}, 
        {"Cost_Variance_CV", type number}, 
        {"Schedule_Variance_SV", type number}
    })
in
    #"Changed Type"


// ------------------------------------------------------------------------------
// Spørring 3: DuckDB_v_ytd_regnskap
// Henter komplett beriket hovedbokstransaksjoner med SRS-linjer og organisasjon
// ------------------------------------------------------------------------------
let
    Source = Python.Execute(
        "import duckdb#(lf)" & 
        "con = duckdb.connect(r'" & DuckDBDatabasePath & "', read_only=True)#(lf)" & 
        "df = con.execute('SELECT * FROM v_ytd_regnskap').df()#(lf)" & 
        "con.close()"
    ),
    df_Table = Source{[Name="df"]}[Value],
    #"Changed Type" = Table.TransformColumnTypes(df_Table,{
        {"DatoNokkel", Int64.Type}, 
        {"Dato", type date}, 
        {"MaanedNavn", type text}, 
        {"Kvartal", type text}, 
        {"OrgKode", Int64.Type}, 
        {"Enhet", type text}, 
        {"FakultetKort", type text}, 
        {"Konto", Int64.Type}, 
        {"Kontonavn", type text}, 
        {"Kontoklasse", type text}, 
        {"Kontogruppe", type text}, 
        {"SRS_regnskapslinje", type text}, 
        {"Artstype", type text}, 
        {"Kategori", type text}, 
        {"Belop_MNOK", type number}, 
        {"Belop_signert_MNOK", type number}, 
        {"VersjonKode", type text}
    })
in
    #"Changed Type"


// ==============================================================================
// 2. BASISTABELLER DIREKTE FRA DUCKDB (ALTERNATIVER TIL CSV-IMPORT)
// ==============================================================================

// FactGL via DuckDB
let
    Source = Python.Execute(
        "import duckdb#(lf)" & 
        "con = duckdb.connect(r'" & DuckDBDatabasePath & "', read_only=True)#(lf)" & 
        "df = con.execute('SELECT * FROM FactGL').df()#(lf)" & 
        "con.close()"
    ),
    df = Source{[Name="df"]}[Value],
    #"Changed Type" = Table.TransformColumnTypes(df,{
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

// FactBudget via DuckDB
let
    Source = Python.Execute(
        "import duckdb#(lf)" & 
        "con = duckdb.connect(r'" & DuckDBDatabasePath & "', read_only=True)#(lf)" & 
        "df = con.execute('SELECT * FROM FactBudget').df()#(lf)" & 
        "con.close()"
    ),
    df = Source{[Name="df"]}[Value],
    #"Changed Type" = Table.TransformColumnTypes(df,{
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
