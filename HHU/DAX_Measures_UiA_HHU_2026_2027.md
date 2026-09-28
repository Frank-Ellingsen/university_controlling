# DAX Measure Library: UiA & Handelshøyskolen (HHU) — 2026 & 2027

> **Formål:** Komplett, produksjonsklar samling av alle DAX-målekoder for Universitetet i Agder (UiA) og Handelshøyskolen ved UiA (HHU) for regnskaps- og budsjettårene **2026** og **2027**.
> **Arkitektur:** Strukturert for Power BI Desktop i 10 dedikerte display folders under tabellen `_Measures`.

---

## Folder Overview & Display Folders

| Folder Navn | Beskrivelse & Innhold |
| :--- | :--- |
| **`_01 Accounting`** | Bokført regnskap YTD, periodisert budsjett og månedlig regnskaps/prognose-bro. |
| **`_02 Forecast & LE`** | Rullende prognoser, Latest Estimate (EAC), Budget at Completion (BAC) og Sluttavvik (VAC). |
| **`_03 Temporal YoY & MoM`** | Historisk sammenligning: Year-over-Year (YoY) og Month-over-Month (MoM) vekst og deltar. |
| **`_04 EVM`** | Earned Value Management: Planned Value (PV), Earned Value (EV), Actual Cost (AC), CPI og SPI. |
| **`_05 Staffing & FTE`** | Bemanningsanalyser: UF/TA-årsverk, lønnsandel %, vakansgrad % og rekrutteringstid. |
| **`_06 Utdanning & SPE60`** | Studenttall, studiepoengekvivalenter (SPE60), lærertetthet og KDs 2025/2027-modell. |
| **`_07 Action Tracker`** | Omstillingstiltak (T001–T004), forventet vs. realisert innsparing og restavvik. |
| **`_08 RAG & Design`** | Dynamic RAG status, trafikklys-symboler, fargekoder (Hex) og Tufte-kompatibel bakgrunn. |
| **`_09 HHU 2026 Ansvarsområder`** | HHU 2026 sporing for rammen på **130 153 825 kr** fordelt på K10000, K11000, K12000 og K13000. |
| **`_10 HHU 2027 Budsjett`** | HHU 2027 fremtidsprognose, 2-års etterslep (lag), Kategori 1 og TDI-overhead. |

---

## 1. Core Accounting & YTD Measures (`_01 Accounting`)

```dax
// 1. Actual YTD (Bokført regnskap M01 - M09 / Sept 30 Cutoff)
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
```

---

## 2. Rolling Forecasts & Year-End Estimates (`_02 Forecast & LE`)

```dax
// 6. Forecast Q4 / Estimate to Complete (ETC M10 - M12)
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
```

---

## 3. Temporal Baseline Comparisons (`_03 Temporal YoY & MoM`)

```dax
// 11. Prior Year Actuals (PY YTD)
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
```

---

## 4. Earned Value Management (`_04 EVM`)

```dax
// 18. Planned Value (PV)
Planned Value (PV) = SUM('FactEVM'[Planned_Value_PV_MNOK])

// 19. Earned Value (EV)
Earned Value (EV) = SUM('FactEVM'[Earned_Value_EV_MNOK])

// 20. Actual Cost (AC)
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
```

---

## 5. Staffing & Capacity KPIs (`_05 Staffing & FTE`)

```dax
// 24. Totale Årsverk (FTE Snapshot)
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

// 29. Vakansgrad % (Planlagt vs Faktisk Årsverk)
Vakansgrad % = 
VAR BudsjettÅV = CALCULATE(SUM('FactFTE'[Budsjettert_Aarsverk]), 'DimDate'[DatoNokkel] = MAX('FactFTE'[DatoNokkel]))
VAR FaktiskÅV = [Totale Årsverk]
RETURN DIVIDE(BudsjettÅV - FaktiskÅV, BudsjettÅV, 0)
```

---

## 6. Student Production & KD 2025/2027 Model (`_06 Utdanning & SPE60`)

```dax
// 30. Registrerte Studenter
Registrerte Studenter = SUM('FactStudents'[RegistrerteStudenter])

// 31. Avlagte Studiepoengekvivalenter (SPE60 = Total SP / 60)
Avlagte SPE60 = SUM('FactStudents'[SPE60])

// 32. Studenter pr Faglig Årsverk (Lærertetthet)
Studenter pr UF-Årsverk = 
DIVIDE([Registrerte Studenter], [Faglige Årsverk (UF)], 0)

// 33. KD Kategori 1 Inntekt (Humaniora, Samfunnsfag, Økonomi @ 54 550 kr/SPE60)
KD Kat 1 Inntekt = 
CALCULATE(
    SUM('FactStudents'[SPE60]) * 54550,
    'FactStudents'[KDKategori] = "Kategori 1"
)
```

---

## 7. Restructuring & Action Tracker (`_07 Action Tracker`)

```dax
// 34. Forventet Tiltakseffekt (Planlagt innsparing i MNOK)
Forventet Tiltakseffekt = SUM('FactAction'[ForventetEffekt])

// 35. Realisert Tiltakseffekt (Bokført innsparing hittil)
Realisert Tiltakseffekt = SUM('FactAction'[RealisertEffekt])

// 36. Tiltak Realiseringsgrad %
Tiltak Realiseringsgrad % = 
DIVIDE([Realisert Tiltakseffekt], [Forventet Tiltakseffekt], 0)

// 37. Forecast etter Tiltak
Forecast etter Tiltak = [Forecast LE (EAC)] + [Forventet Tiltakseffekt]
```

---

## 8. RAG Formatting & Dynamic Design (`_08 RAG & Design`)

```dax
// 38. Budget Variance RAG Status Text Badge
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

// 39. Primary RAG Hex Color (For Bars, Card Accents & Text)
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

// 40. Soft RAG Background Fill Hex (Tufte 85% Opacity Tint for Matrix Cells)
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

// 41. Multi-Context Card Subtitle with RAG Icons (New Card Visual)
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
```

---

## 9. HHU Specific Measures 2026 (`_09 HHU 2026 Ansvarsområder`)
*Spesifikt utarbeidet for å styre HHUs vedtatte 2026-ramme på **130 153 825 kr** fordelt på fire budsjettansvarsområder.*

```dax
// 42. Vedtatt Årsbudsjett Baseline 2026 (Nøyaktig 130 153 825 kr)
HHU 2026 Vedtatt Årsbudsjett = 
CALCULATE(
    SUM('FactBudget'[BudsjettBelop]),
    'DimForecastVersion'[VersjonKode] = "BUD2026"
)

// 43. Ansvarsområde: K10000 Admin & Felles (14 000 000 kr)
HHU K10000 Admin Budsjett = 
CALCULATE([HHU 2026 Vedtatt Årsbudsjett], 'DimOrganization'[OrgKode] = "K10000")

// 44. Ansvarsområde: K11000 Inst. for ledelse og innovasjon (38 500 000 kr)
HHU K11000 Ledelse Budsjett = 
CALCULATE([HHU 2026 Vedtatt Årsbudsjett], 'DimOrganization'[OrgKode] = "K11000")

// 45. Ansvarsområde: K12000 Inst. for rettsvitenskap (29 250 000 kr)
HHU K12000 Rettsvitenskap Budsjett = 
CALCULATE([HHU 2026 Vedtatt Årsbudsjett], 'DimOrganization'[OrgKode] = "K12000")

// 46. Ansvarsområde: K13000 Inst. for økonomi (48 403 825 kr)
HHU K13000 Økonomi Budsjett = 
CALCULATE([HHU 2026 Vedtatt Årsbudsjett], 'DimOrganization'[OrgKode] = "K13000")

// 47. Ansvarsområde Regnskap YTD M01-M09
Ansvarsområde Actual YTD 2026 = 
CALCULATE(
    SUM('FactGL'[Belop_signert]),
    'FactGL'[Bokforingstype] = "Actual",
    'DimOrganization'[Fakultetsnavn] = "Handelshøyskolen ved UiA (HHU)"
)

// 48. Ansvarsområde Avvik YTD M01-M09 (MNOK / NOK)
Ansvarsområde Avvik YTD 2026 = 
VAR BudgetYTD = CALCULATE(SUM('FactBudget'[BudsjettBelop]), 'DimDate'[ErActualYTD] = TRUE(), 'DimOrganization'[Fakultetsnavn] = "Handelshøyskolen ved UiA (HHU)")
RETURN [Ansvarsområde Actual YTD 2026] - BudgetYTD

// 49. Ansvarsområde Helårs Sluttavvik (VAC 2026)
Ansvarsområde Sluttavvik VAC 2026 = 
VAR ActualYTD = [Ansvarsområde Actual YTD 2026]
VAR ForecastQ4 = CALCULATE(SUM('FactGL'[Belop_signert]), 'FactGL'[Bokforingstype] = "Forecast", 'DimOrganization'[Fakultetsnavn] = "Handelshøyskolen ved UiA (HHU)")
VAR TotalEAC = ActualYTD + ForecastQ4
RETURN [HHU 2026 Vedtatt Årsbudsjett] - TotalEAC

// 50. HHU 2026 Lønnsandel % (Mål: < 65,0%)
HHU 2026 Lønnsandel % = 
VAR Lonn = CALCULATE(SUM('FactGL'[Belop_signert]), 'DimOrganization'[Fakultetsnavn] = "Handelshøyskolen ved UiA (HHU)", 'DimAccountHierarchy'[Nivaa1_Navn] = "Lønnskostnad")
VAR TotalKost = CALCULATE(SUM('FactGL'[Belop_signert]), 'DimOrganization'[Fakultetsnavn] = "Handelshøyskolen ved UiA (HHU)", 'DimAccountHierarchy'[Kontotype] = "Kostnad")
RETURN DIVIDE(Lonn, TotalKost, 0)
```

---

## 10. HHU Specific Measures 2027 (`_10 HHU 2027 Budsjett`)
*Bygger på BUD2027-rammen (**288,07 MNOK Inntekt / 282,00 MNOK Kostnad**), 2-års etterslep på Kategori 1 (54 550 kr/SPE60) og TDI-overhead.*

```dax
// 51. Vedtatt Inntekt BUD2027 HHU (288,07 MNOK)
BUD2027 Inntekter HHU = 
CALCULATE(
    SUM('FactBudget_2027'[BudsjettBelop]),
    'DimOrganization'[Fakultetsnavn] = "Handelshøyskolen ved UiA (HHU)",
    'DimAccountHierarchy'[Kontotype] = "Inntekt",
    'DimForecastVersion'[VersjonKode] = "BUD2027"
)

// 52. Vedtatt Kostnad BUD2027 HHU (282,00 MNOK)
BUD2027 Kostnader HHU = 
CALCULATE(
    SUM('FactBudget_2027'[BudsjettBelop]),
    'DimOrganization'[Fakultetsnavn] = "Handelshøyskolen ved UiA (HHU)",
    'DimAccountHierarchy'[Kontotype] = "Kostnad",
    'DimForecastVersion'[VersjonKode] = "BUD2027"
)

// 53. Planlagt Netto Driftsresultat BUD2027 (+6,07 MNOK til Note 15)
BUD2027 Netto Resultat HHU = [BUD2027 Inntekter HHU] - [BUD2027 Kostnader HHU]

// 54. 2-Års Lag Resultatutbetaling 2027 (Kategori 1 for 2025-produksjon)
KD Kat 1 Resultatutbetaling 2027 = 
CALCULATE(
    SUM('FactStudents_2027'[KD_Marginal_Inntekt_2027]),
    'DimOrganization'[Fakultetsnavn] = "Handelshøyskolen ved UiA (HHU)",
    'FactStudents_2027'[KDKategori] = "Kategori 1"
)

// 55. HHU Lønnsandel 2027 % (Mål: < 64,5%)
HHU Lønnsandel 2027 % = 
VAR Lonn2027 = CALCULATE(SUM('FactBudget_2027'[BudsjettBelop]), 'DimOrganization'[Fakultetsnavn] = "Handelshøyskolen ved UiA (HHU)", 'DimAccountHierarchy'[Nivaa1_Navn] = "Lønnskostnad")
RETURN DIVIDE(Lonn2027, [BUD2027 Inntekter HHU], 0)

// 56. HHU 2027 RAG Status Text Badge
HHU 2027 RAG Status Badge = 
VAR Resultat = [BUD2027 Netto Resultat HHU]
VAR LonnPct = [HHU Lønnsandel 2027 %]
RETURN
SWITCH(
    TRUE(),
    Resultat >= 4.0 && LonnPct <= 0.645, "🟢 Sterk margin (Overskudd > 4 MNOK & Lønn < 64,5%)",
    Resultat >= 0.0, "🟡 Moderat overskudd (< 4 MNOK)",
    "🔴 Underskudd / Høy lønnsandel"
)
```
