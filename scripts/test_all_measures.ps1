Add-Type -Path "$env:TEMP\Microsoft.PowerBI.AdomdClient.dll"

$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:58843;Initial Catalog=76913953-bf01-4c8f-bf51-21fa84edc128")
$conn.Open()
Write-Output "Successfully connected to Power BI SSAS on port 58843!"

# Read measures from _Measures.tmdl
$tmdlPath = "University-project-2026YTD.SemanticModel\definition\tables\_Measures.tmdl"
$lines = Get-Content $tmdlPath -Encoding UTF8

$measures = @()
foreach ($line in $lines) {
    if ($line -match "^\s*measure\s+['""]?([^='""\r\n]+)['""]?\s*=") {
        $measures += $matches[1].Trim()
    }
}

Write-Output "Testing $($measures.Count) measures against the live tabular engine..."

$failed = @()
$passed = 0

foreach ($m in $measures) {
    $cmd = $conn.CreateCommand()
    $cmd.CommandText = "EVALUATE ROW(""val"", [$m])"
    try {
        $reader = $cmd.ExecuteReader()
        $reader.Close()
        $passed++
    } catch {
        $errMsg = $_.Exception.Message
        Write-Output "[FAIL] Measure: '$m' -> $errMsg"
        $failed += [PSCustomObject]@{
            Measure = $m
            Error = $errMsg
        }
    }
}

Write-Output "`n=== SUMMARY ==="
Write-Output "Passed: $passed / $($measures.Count)"
Write-Output "Failed: $($failed.Count) / $($measures.Count)"

$conn.Close()
