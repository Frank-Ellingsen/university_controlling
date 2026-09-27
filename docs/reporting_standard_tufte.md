# Edward Tufte Data-Ink Standard for University Rapportering

Dette dokumentet definerer de visuelle standardene for rapportering ved University, basert på prinsippene til **Edward Tufte** (The Visual Display of Quantitative Information).

Målet er å maksimere **Data-Ink Ratio**:
$$\text{Data-Ink Ratio} = \frac{\text{Data-Ink (blekk brukt til faktisk datainformasjon)}}{\text{Total Ink (samlet grafisk blekk i rapporten)}}$$

---

## 1. De 5 Grunnreglene

### 1.1 Fjern Visuell Støy (Chartjunk)
* **Ingen bakgrunnsskygger (drop shadows)** eller 3D-effekter på kort (KPI cards) eller tabeller.
* **Fjern vertikale rutenettlinjer** i tabeller og matriser. Kun lette, diskrete horisontale linjer tillates (`#E2E8F0`).
* **Ingen dekorative ikoner** som stjeler oppmerksomhet fra tallene.

### 1.2 Muted Fargepalett med Selektiv Fremheving
* Bruk en nøytral grunnfarge: skifergrå (`#334155`), koksgrå (`#0F172A`) og dempet grå (`#64748B`).
* Kraftige signalfarger (rød `#EF4444`, gul `#F59E0B`) skal **kun** brukes for å markere aktive avvik, overskridelser eller risiko (RAG-unntaksrapportering).
* Hvis alt er markert med farger, er ingenting fremhevet.

### 1.3 Direkte Merking (Direct Labeling)
* På S-Kurver (EVM kumulativ PV, EV, AC):
  * **Ikke** tving leseren til å flakke blikket mellom en fargeforklaring (legend) og kurvene.
  * Plasser etiketten direkte ved enden av kurven (f.eks. `AC: 1444 MNOK`, `EV: 1344 MNOK`, `PV: 1508 MNOK`).

### 1.4 Typografi og Talljustering
* **Tekstkolonner**: Alltid venstrejustert.
* **Tallkolonner**: Alltid høyrejustert.
* **Desimaljustering**: Sørg for at desimaler flukter vertikalt for umiddelbar sammenligning.
* Bruk rene skrifttyper: `Segoe UI`, `Aptos` eller `Inter`.

### 1.5 Sparklines og Mikro-visualiseringer
* Bruk kompakte sparklines i tabeller for å vise 12-måneders trend for kostnader eller timeforbruk uten å kreve store, plasskrevende stolpediagrammer.

---

## 2. Bruk av Temafilen i Power BI

1. I **Power BI Desktop**, naviger til fanen **View**.
2. Klikk på **Themes**-nedtrekksmenyen og velg **Browse for themes**.
3. Velg filen [`powerbi/themes/tufte_minimalist_theme.json`](../powerbi/themes/tufte_minimalist_theme.json).
4. Temaet slår automatisk av skygger, rammer, vertikale tabellinjer og overflødige diagramforklaringer.
