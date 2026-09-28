 complete, production-grade DAX Measure Library for the UiA Controller Project and Financial Management Framework12.This library covers the entire semantic datamodel (FactGL, FactBudget, FactFTE, FactStudents, FactEVM, FactAction, DimOrganization, DimAccountHierarchy, DimDate)3more_horiz. It is organized into 8 display folders for Power BI Desktop and incorporates the "So What?" decision-support framework67, Edward Tufte's data-ink principles89, temporal context (YoY and MoM)1011, and strict Red-Amber-Green (RAG) conditional formatting1213.Folder 1: Core Accounting & YTD Measures (_01 Accounting)// 1. Actual YTD (Bokført regnskap M01 - M09 / Sept 30 Cutoff)
Actual YTD = 
CALCULATE(
    SUM('FactGL'[Belop_signert]),
    'FactGL'[Bokforingstype] = "Actual"
)

// 2. Budsjett YTD (Akkumulert periodisert budsjett M01 - M09)
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

// 5. Monthly Actuals and Forecast Bridge (M01-M09 Actuals + M10-M12 Q4 Forecast)
Monthly Actuals and Forecast = 
VAR CutoffMonth = 9
VAR CurrentMonth = MAX('DimDate'[MaanedNummer])
VAR ActualAmount = CALCULATE(SUM('FactGL'[Belop_signert]), 'FactGL'[Bokforingstype] = "Actual")
VAR ForecastAmount = CALCULATE(SUM('FactGL'[Belop_signert]), 'FactGL'[Bokforingstype] = "Forecast")
RETURN
IF(CurrentMonth <= CutoffMonth, ActualAmount, ForecastAmount)
Note: Actual YTD sums historical general ledger transactions up to the September 30 cutoff date (1 072,1 MNOK revenue / 1 092,0 MNOK expenses for UiA)1415.Folder 2: Rolling Forecasts & Year-End Estimates (_02 Forecast & LE)// 6. Forecast Q4 / Estimate to Complete (ETC M10 - M12)
Forecast Q4 (ETC) = 
CALCULATE(
    SUM('FactGL'[Belop_signert]),
    'FactGL'[Bokforingstype] = "Forecast"
)

// 7. Forecast LE / Estimate at Completion (EAC = Actual YTD + Q4 Forecast)
Forecast LE (EAC) = [Actual YTD] + [Forecast Q4 (ETC)]

// 8. Vedtatt Årsbudsjett / Budget at Completion (BAC)
Årsbudsjett (BAC) = SUM('FactBudget'[BudsjettBelop])

// 9. Sluttavvik / Variance at Completion (VAC MNOK = BAC - EAC)
Sluttavvik (VAC) = [Årsbudsjett (BAC)] - [Forecast LE (EAC)]

// 10. VAC % (Relativ overskridelse eller innsparing)
VAC % = 
DIVIDE([Sluttavvik (VAC)], [Årsbudsjett (BAC)], 0)
Note: The total full-year forecast (Forecast LE / EAC) equals 1 433,0 MNOK in revenue against 1 444,0 MNOK in expenses, yielding a net full-year deficit (VAC) of -11,0 MNOK that is covered by accumulated reserves pursuant to Note 15 and Circular F-05-201617.Folder 3: Temporal Baseline Comparisons (_03 Temporal YoY & MoM)// 11. Prior Year Actuals (PY YTD)
Actual PY = 
CALCULATE(
    [Actual YTD],
    SAMEPERIODLASTYEAR('DimDate'[Dato])
)

// 12. Absolute Year-over-Year Difference (YoY MNOK)
Actual YoY = [Actual YTD] - [Actual PY]

// 13. Percentage Year-over-Year Growth (YoY %)
Actual YoY % = 
DIVIDE([Actual YoY], [Actual PY], 0)

// 14. Prior Month Actuals (PM)
Actual PM = 
CALCULATE(
    SUM('FactGL'[Belop_signert]),
    PREVIOUSMONTH('DimDate'[Dato]),
    'FactGL'[Bokforingstype] = "Actual"
)

// 15. Current Month Actuals (CM)
Actual CM = 
CALCULATE(
    SUM('FactGL'[Belop_signert]),
    'DimDate'[DatoNokkel] = MAX('FactGL'[DatoNokkel]),
    'FactGL'[Bokforingstype] = "Actual"
)

// 16. Month-over-Month Difference (MoM MNOK)
Actual MoM = [Actual CM] - [Actual PM]

// 17. Percentage Month-over-Month Growth (MoM %)
Actual MoM % = 
DIVIDE([Actual MoM], [Actual PM], 0)
Note: Adding temporal baselines (YoY and MoM) ensures that executives evaluate performance momentum alongside annual budget targets1011.Folder 4: Earned Value Management (_04 EVM)// 18. Planned Value (PV) - Akkumulert planlagt verdi
Planned Value (PV) = SUM('FactEVM'[Planned_Value_PV_MNOK])

// 19. Earned Value (EV) - Akkumulert opptjent verdi
Earned Value (EV) = SUM('FactEVM'[Earned_Value_EV_MNOK])

// 20. Actual Cost (AC) - Akkumulert faktisk kostnad
Actual Cost (AC) = SUM('FactEVM'[Actual_Cost_AC_MNOK])

// 21. Cost Performance Index (CPI = EV / AC)
CPI = DIVIDE([Earned Value (EV)], [Actual Cost (AC)], 1)

// 22. Schedule Performance Index (SPI = EV / PV)
SPI = DIVIDE([Earned Value (EV)], [Planned Value (PV)], 1)

// 23. EVM Status Subtitle Callout
EVM Status Subtitle = 
VAR CPIVal = [CPI]
VAR SPIVal = [SPI]
RETURN
"CPI: " & FORMAT(CPIVal, "0.00") & " (Kost) | SPI: " & FORMAT(SPIVal, "0.00") & " (Fremdrift)"
Note: At the late-year control cutoff, UiA's CPI is 0.95 (5% cost overrun) and SPI is 0.92 (8% schedule lag)1718.Folder 5: Staffing & Capacity KPIs (_05 Staffing & FTE)// 24. Totale Årsverk (FTE Snapshot)
Totale Årsverk = 
CALCULATE(
    SUM('FactFTE'[Aarsverk]),
    'DimDate'[DatoNokkel] = MAX('FactFTE'[DatoNokkel])
)

// 25. Faglige Årsverk (UF - Undervisning og Forskning)
Faglige Årsverk (UF) = 
CALCULATE(
    [Totale Årsverk],
    'FactFTE'[Stillingstype] = "UF"
)

// 26. Teknisk-Administrative Årsverk (TA)
Teknisk-Admin Årsverk (TA) = 
CALCULATE(
    [Totale Årsverk],
    'FactFTE'[Stillingstype] = "TA"
)

// 27. Faglig Andel % (Sektormål: > 50-55%)
Faglig Andel % = DIVIDE([Faglige Årsverk (UF)], [Totale Årsverk], 0)

// 28. Lønnsandel % av Totale Driftskostnader (Sektornorm: 62-65%)
Lønnsandel % = 
VAR Lonn = CALCULATE(SUM('FactGL'[Belop_signert]), 'DimAccountHierarchy'[Nivaa1_Navn] = "Lønnskostnad")
VAR TotalKost = CALCULATE(SUM('FactGL'[Belop_signert]), 'DimAccountHierarchy'[Kontotype] = "Kostnad")
RETURN DIVIDE(Lonn, TotalKost, 0)

// 29. Staffing Card Subtitle Callout
Staffing Card Subtitle = 
VAR UF = [Faglige Årsverk (UF)]
VAR TA = [Teknisk-Admin Årsverk (TA)]
VAR LonnPct = [Lønnsandel %]
RETURN
FORMAT(UF, "#0") & " UF / " & FORMAT(TA, "#0") & " TA | Lønnsandel: " & FORMAT(LonnPct, "0.0%")
Note: Personnel expenses represent 65.4% of total operating expenses across UiA (944.0 MNOK), slightly exceeding the sector benchmark upper threshold of 65.0%19more_horiz.Folder 6: Student Production & KD 2025 Model (_06 Utdanning & SPE60)// 30. Registrerte Studenter
Registrerte Studenter = SUM('FactStudents'[RegistrerteStudenter])

// 31. Avlagte Studiepoengekvivalenter (SPE60 = Total SP / 60)
Avlagte SPE60 = SUM('FactStudents'[SPE60])

// 32. Studenter pr Faglig Årsverk (Lærertetthet & Kapasitet)
Studenter pr UF-Årsverk = 
DIVIDE([Registrerte Studenter], [Faglige Årsverk (UF)], 0)

// 33. Enhetskostnad pr SPE60 (NOK pr produserte helårsstudent)
Enhetskostnad pr SPE60 = 
DIVIDE([Forecast LE (EAC)] * 1000000, [Avlagte SPE60], 0)

// 34. KD Kategori 1 Inntekt (Humaniora, Samfunnsfag, Økonomi @ 54 550 kr/SPE60)
KD Kat 1 Inntekt = 
CALCULATE(
    SUM('FactStudents'[SPE60]) * 54550,
    'FactStudents'[KDKategori] = "Kategori 1"
)

// 35. Student KPI Card Subtitle Callout
Student KPI Subtitle = 
VAR SPE = [Avlagte SPE60]
VAR Ratio = [Studenter pr UF-Årsverk]
RETURN
FORMAT(SPE, "#,##0") & " SPE60 | " & FORMAT(Ratio, "0.0") & " Studenter/UF-ÅV"
Note: Under KD's 2025 funding model, Category 1 produces 54 550 NOK per 60 SPE. Category 1 rates apply strictly to marginal volume changes rather than baseline historical positions22more_horiz.Folder 7: Restructuring & Action Tracker (_07 Action Tracker)// 36. Forventet Tiltakseffekt (Planlagt innsparing i MNOK)
Forventet Tiltakseffekt = SUM('FactAction'[ForventetEffekt])

// 37. Realisert Tiltakseffekt (Bokført innsparing hittil)
Realisert Tiltakseffekt = SUM('FactAction'[RealisertEffekt])

// 38. Tiltak Realiseringsgrad %
Tiltak Realiseringsgrad % = 
DIVIDE([Realisert Tiltakseffekt], [Forventet Tiltakseffekt], 0)

// 39. Forecast etter Tiltak (Netto Sluttresultat inkl. omstilling)
Forecast etter Tiltak = [Forecast LE (EAC)] + [Forventet Tiltakseffekt]

// 40. Restavvik etter Tiltak (Gjenværende risikogap)
Restavvik etter Tiltak = [Forecast etter Tiltak] - [Årsbudsjett (BAC)]
Note: FactAction connects restructuring initiatives (e.g., administrative vacancy freezes T001/T002) directly to ledger accounts and forecast drift5more_horiz.Folder 8: RAG Formatting & Dynamic Design (_08 RAG & Design)// 41. Budget Variance RAG Status Text Badge
Budget Variance RAG Status = 
VAR Budget = [Årsbudsjett (BAC)]
VAR Forecast = [Forecast LE (EAC)]
VAR Vac = Forecast - Budget
VAR VacPct = DIVIDE(Vac, Budget, 0)
RETURN
SWITCH(
    TRUE(),
    Vac >= 0, "🟢 Under/I budsjett",
    VacPct >= -0.05, "🟡 Moderat overskridelse (2-5%)",
    "🔴 Kritisk overskridelse (>5%)"
)

// 42. Primary RAG Hex Color (For Bars, Card Accents & Text)
RAG Hex Color = 
VAR Vac = [Sluttavvik (VAC)]
VAR VacPct = [VAC %]
RETURN
IF(
    Vac >= 0, 
    "#10b981", // Emerald Green
    IF(
        VacPct >= -0.05, 
        "#f59e0b", // Amber Yellow
        "#ef4444"  // Crimson Red
    )
)

// 43. Soft RAG Background Fill Hex (Tufte 85% Opacity Tint for Matrix Cells)
RAG Soft Background Hex = 
VAR Vac = [Sluttavvik (VAC)]
VAR VacPct = [VAC %]
RETURN
IF(
    Vac >= 0, 
    "#ecfdf5", // Soft Mint Green
    IF(
        VacPct >= -0.05, 
        "#fffbeb", // Soft Warm Amber
        "#fef2f2"  // Soft Crimson Red
    )
)

// 44. Multi-Context Card Subtitle with RAG Icons (New Card Visual)
Multi-Context Revenue Subtitle = 
VAR Budget = [Årsbudsjett (BAC)]
VAR Forecast = [Forecast LE (EAC)]
VAR PlanDiffPct = DIVIDE(Forecast - Budget, Budget, 0)
VAR YoYPct = [Actual YoY %]
VAR MoMPct = [Actual MoM %]

VAR PlanIcon = IF(PlanDiffPct >= 0, "🟢", IF(PlanDiffPct >= -0.05, "🟡", "🔴"))
VAR YoYIcon = IF(YoYPct >= 0, "🟢", "🔴")

VAR PlanText = PlanIcon & " Budsj: " & IF(PlanDiffPct >= 0, "▲ +", "▼ ") & FORMAT(PlanDiffPct, "0.0%")
VAR YoYText = YoYIcon & " YoY: " & IF(YoYPct >= 0, "▲ +", "▼ ") & FORMAT(YoYPct, "0.0%")
VAR MoMText = "MoM: " & IF(MoMPct >= 0, "▲ +", "▼ ") & FORMAT(MoMPct, "0.0%")

RETURN
PlanText & " | " & YoYText & " | " & MoMText
Note: Applying soft background fills (#ECFDF5, #FFFBEB, #FEF2F2) prevents saturated neon glare, adhering strictly to Tufte's data-ink standard8more_horiz.Special Sub-Folder: Handelshøyskolen ved UiA (_09 HHU Measures)// 45. HHU Total Revenue (276.6 MNOK)
HHU Total Revenue = 
CALCULATE(
    [Forecast LE (EAC)],
    'DimOrganization'[Fakultetsnavn] = "Handelshøyskolen ved UiA (HHU)",
    'DimAccountHierarchy'[Nivaa1_Navn] = "Salgs- og driftsinntekt"
)

// 46. HHU Net Result (+2.2 MNOK Surplus)
HHU Net Result = 
CALCULATE(
    [Sluttavvik (VAC)],
    'DimOrganization'[Fakultetsnavn] = "Handelshøyskolen ved UiA (HHU)"
)

// 47. HHU Lønnsandel % (65.4%)
HHU Lønnsandel % = 
CALCULATE(
    [Lønnsandel %],
    'DimOrganization'[Fakultetsnavn] = "Handelshøyskolen ved UiA (HHU)"
)

// 48. HHU Studenter pr UF-Årsverk (22.3 Ratio)
HHU Studenter pr UF-Årsverk = 
VAR Studenter = CALCULATE(SUM('FactStudents'[RegistrerteStudenter]), 'DimOrganization'[Fakultetsnavn] = "Handelshøyskolen ved UiA (HHU)")
VAR UF = CALCULATE(SUM('FactFTE'[Aarsverk]), 'DimOrganization'[Fakultetsnavn] = "Handelshøyskolen ved UiA (HHU)", 'FactFTE'[Stillingstype] = "UF")
RETURN DIVIDE(Studenter, UF, 0)

// 49. HHU BOA Frikjøpsgrad (Buy-Out Share)
HHU BOA Frikjøpsgrad = 
VAR BOALonn = CALCULATE(SUM('FactGL'[Belop_signert]), 'DimOrganization'[Fakultetsnavn] = "Handelshøyskolen ved UiA (HHU)", 'DimAccountHierarchy'[Nivaa1_Navn] = "Lønnskostnad", 'DimOrganization'[Virksomhetstype] = "BOA")
VAR TotalLonn = CALCULATE(SUM('FactGL'[Belop_signert]), 'DimOrganization'[Fakultetsnavn] = "Handelshøyskolen ved UiA (HHU)", 'DimAccountHierarchy'[Nivaa1_Navn] = "Lønnskostnad")
RETURN DIVIDE(BOALonn, TotalLonn, 0)

// 50. HHU RAG Status
HHU RAG Status = 
VAR Resultat = [HHU Net Result]
RETURN
IF(Resultat >= 0, "🟢 Overskudd (+2.2 MNOK / Ramme overholdt)",
    IF(Resultat >= -2.0, "🟡 Moderat merforbruk (< 2 MNOK)", "🔴 Kritisk merforbruk (> 2 MNOK)")
)
Note: HHU delivers a positive net operating result of +2.2 MNOK2930. However, its high student-to-faculty ratio (22.3) combined with KD Category 1 funding constraints requires active controller monitoring22.Implementation Instructions in Power BI DesktopCreate Measures Table: Go to Home > Enter Data, create a table named _Measures, and load it.Add Measures: Click New Measure and paste each DAX block.Set Display Folders: In Model View, select each measure and enter the folder path (e.g., _01 Accounting, _08 RAG & Design).Conditional Formatting:For Card Accent Bars: Enable Accent Bar on New Card Visual $\rightarrow$ fx (Conditional Formatting) $\rightarrow$ Format Style: Field Value $\rightarrow$ Select [RAG Hex Color]3132.For Matrix Fills: Go to Cell Elements $\rightarrow$ Enable Background Color $\rightarrow$ Format Style: Field Value $\rightarrow$ Select [RAG Soft Background Hex]