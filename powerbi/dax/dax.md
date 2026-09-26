Folder 1: Base Accounting & YTD Measures (\_01 Accounting)
// 1. Actual YTD (Jan - Sep 2026)
Actual YTD =
CALCULATE(
SUM('FactGL'[Belop_signert]),
'FactGL'[Bokforingstype] = "Actual"
)

// 2. Budsjett YTD (Jan - Sep 2026)
Budsjett YTD =
CALCULATE(
SUM('FactBudget'[BudsjettBelop]),
'DimDate'[ErActualYTD] = TRUE()
)

// 3. Avvik YTD (MNOK) [Positivt = Merforbruk / Negativt = Mindreforbruk]
Avvik YTD = [Actual YTD] - [Budsjett YTD]

// 4. Avvik YTD %
Avvik YTD % =
DIVIDE([Avvik YTD], [Budsjett YTD], 0)
Folder 2: Rolling Forecast & Year-End Estimates (\_02 Forecast & LE)
// 5. Forecast Q4 (Oct - Dec 2026 / ETC)
Forecast Q4 =
CALCULATE(
SUM('FactGL'[Belop_signert]),
'FactGL'[Bokforingstype] = "Forecast"
)

// 6. Forecast LE / EAC (Latest Estimate / Estimate at Completion)
Forecast LE (EAC) = [Actual YTD] + [Forecast Q4]

// 7. Vedtatt Årsbudsjett (BAC - Budget at Completion)
Årsbudsjett (BAC) = SUM('FactBudget'[BudsjettBelop])

// 8. Sluttavvik / VAC (Variance at Completion MNOK)
Sluttavvik (VAC) = [Årsbudsjett (BAC)] - [Forecast LE (EAC)]

// 9. VAC % (Relativ overskridelse eller innsparing)
VAC % =
DIVIDE([Sluttavvik (VAC)], [Årsbudsjett (BAC)], 0)
Folder 3: Earned Value Management (\_03 EVM)
// 10. Planned Value (PV)
Planned Value (PV) = SUM('FactEVM'[Planned_Value_PV_MNOK])

// 11. Earned Value (EV)
Earned Value (EV) = SUM('FactEVM'[Earned_Value_EV_MNOK])

// 12. Actual Cost (AC)
Actual Cost (AC) = SUM('FactEVM'[Actual_Cost_AC_MNOK])

// 13. Cost Performance Index (CPI)
CPI = DIVIDE([Earned Value (EV)], [Actual Cost (AC)], 1)

// 14. Schedule Performance Index (SPI)
SPI = DIVIDE([Earned Value (EV)], [Planned Value (PV)], 1)
Folder 4: Staffing & Capacity KPIs (\_04 FTE & Bemanning)
// 15. Totale Årsverk (FTE) - Månedlig Snapshot
Totale Årsverk =
CALCULATE(
SUM('FactFTE'[Aarsverk]),
'DimDate'[DatoNokkel] = MAX('FactFTE'[DatoNokkel])
)

// 16. Faglige Årsverk (UF - Undervisning og Forskning)
Faglige Årsverk (UF) =
CALCULATE(
[Totale Årsverk],
'FactFTE'[Stillingstype] = "UF"
)

// 17. Teknisk-Administrative Årsverk (TA)
Teknisk-Admin Årsverk (TA) =
CALCULATE(
[Totale Årsverk],
'FactFTE'[Stillingstype] = "TA"
)

// 18. Faglig Andel % (Sektormål: > 50%)
Faglig Andel % = DIVIDE([Faglige Årsverk (UF)], [Totale Årsverk], 0)

// 19. Lønnsandel % av Totale Driftskostnader
Lønnsandel % =
VAR Lonn = CALCULATE(SUM('FactGL'[Belop_signert]), 'DimAccountHierarchy'[Nivaa1_Navn] = "Lønnskostnad")
VAR TotalKost = SUM('FactGL'[Belop_signert])
RETURN DIVIDE(Lonn, TotalKost, 0)
Folder 5: Student & Production KPIs (\_05 Utdanning)
// 20. Registrerte Studenter
Registrerte Studenter = SUM('FactStudents'[RegistrerteStudenter])

// 21. Avlagte Studiepoengekvivalenter (SPE60)
Avlagte SPE60 = SUM('FactStudents'[SPE60])

// 22. Studenter per Faglig Årsverk (Lærertetthet)
Studenter pr UF-Årsverk =
DIVIDE([Registrerte Studenter], [Faglige Årsverk (UF)], 0)

// 23. Enhetskostnad per SPE60 (NOK pr produserte helårsstudent)
Enhetskostnad pr SPE60 =
DIVIDE([Forecast LE (EAC)] \* 1000000, [Avlagte SPE60], 0)
Folder 6: RAG Status & Formatting (\_06 RAG & Design)
// 24. Forecast RAG Status
Forecast RAG Status =
IF([Sluttavvik (VAC)] >= 0, "🟢 Under/I budsjett",
IF([VAC %] >= -0.05, "🟡 Moderat overskridelse (2-5%)",
"🔴 Kritisk overskridelse (>5%)"
)
)

// 25. RAG Hex Color Code (Power BI Conditional Formatting)
RAG Hex Color =
IF([Sluttavvik (VAC)] >= 0, "#10b981", // Emerald Green
IF([VAC %] >= -0.05, "#f59e0b", // Amber
"#ef4444" // Red
)
)
Implementation Instructions in Power BI
Create a blank table named \_Measures in Power BI Desktop (Home > Enter Data).
Create new measures and paste the DAX snippets above.
Assign each measure to its respective Display Folder under the Model View.
Apply RAG Hex Color directly in visual Conditional Formatting > Field Value.
