# Veileder for DAX-måltall (UiA Prosjekt- og Virksomhetsrapportering)

Denne veilederen beskriver implementering og forretningslogikk for de 25 sentrale DAX-måltallene i Power BI-prosjektet `UIA-project-2026YTD.pbip`.

---

## 1. Måltallshierarki og Visningsmapper (Display Folders)

For å sikre ryddig modellering i Power BI Desktop (Model View), er måltallene strukturert i en egen dedikert måltallstabell `_Measures`:

| Visningsmappe | Formål | Nøkkelmåltall |
| :--- | :--- | :--- |
| `_01 Regnskap & YTD` | Månedlige faktiske regnskapstall mot periodisert budsjett | `Actual YTD`, `Budsjett YTD`, `Avvik YTD`, `Avvik YTD %` |
| `_02 Prognose & EAC` | Rullende prognoser og årsavslutningsestimater | `Forecast Q4`, `Forecast LE (EAC)`, `Årsbudsjett (BAC)`, `Sluttavvik (VAC)` |
| `_03 EVM` | Earned Value Management for portefølje- og prosjektstyring | `Planned Value (PV)`, `Earned Value (EV)`, `Actual Cost (AC)`, `CPI`, `SPI` |
| `_04 Bemanning & FTE` | Stillingsgrupper, kapasitet og faglig andel | `Totale Årsverk`, `Faglige Årsverk (UF)`, `Teknisk-Admin Årsverk (TA)`, `Faglig Andel %` |
| `_05 Utdanning` | Studenttall, studiepoeng og KD-uttelling | `Registrerte Studenter`, `Avlagte SPE60`, `Enhetskostnad pr SPE60`, `KD Resultatbevilgning` |
| `_06 RAG & Design` | Fargekoder og statusflagg for betinget formatering | `Forecast RAG Status`, `RAG Hex Color`, `CPI Hex Color` |

---

## 2. Implementering i Power BI Desktop

1. Åpne **Power BI Desktop** via `UIA-project-2026YTD.pbip`.
2. Gå til **Home > Enter Data** og opprett en tom tabell med navn `_Measures`.
3. Opprett nye mål (New Measure) ved å kopiere kodene fra [`powerbi/dax/measures.dax`](./measures.dax).
4. I **Model View**: Marker hvert mål og angi verdien under **Properties > Display folder** (f.eks. `_01 Regnskap & YTD`).
5. Slett `Column1` i `_Measures`-tabellen slik at den automatisk konverteres til et kalkulator-ikon øverst i feltlisten.

---

## 3. Betinget Formatering (Edward Tufte Standard)

Bruk måltallet `[RAG Hex Color]` direkte i Power BI:
* Marker tabell eller matrisevisual.
* Gå til **Visual > Cell elements > Background color** (eller Font color).
* Velg **Format style: Field value** og velg målet `_Measures[RAG Hex Color]`.

> [!TIP]
> Tufte-prinsipp: Unngå heldekkende bakgrunnsfarge i hele tabellen. Påfør farge kun på **Avvik**- eller **Status**-kolonnen for å minimere visuell støy og maksimere informasjonsverdien.
