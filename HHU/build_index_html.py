"""
Comprehensive Builder for C:\\Users\\frank\\Desktop\\UIA2\\HHU\\index.html
Incorporates the complete reporting from:
1. build_hhu_rapport_pbip.py & build_hhu_rapport_pages.py (PBIR 7 pages & TMDL Semantic Model)
2. UIA-Handelshøyskolen USE-CASE.xlsx:
   - Executive Report (3-30-300 visning, ledelseskonklusjon)
   - Unit Analysis (Enhetsanalyse, tiltak og analytisk konklusjon)
   - Variance Actions (Rotårsaker, avviksdrivere, månedshotspots, prioritert handlingsplan, ledelsesvurdering)
   - 2027 Plan Report (Økonomi og kapasitet, 2027-tiltak, beslutningsstøtte, 2,0 MNOK inntektsgap)
   - Budget Process 2027 (6 Beslutningsporter, driveranalyse, styringsmodell, prioritert lukkeplan før frys)
   - Forecast Methods 2027 (Metodebibliotek for 11 poster, standard prognoseformel, månedlig årshjul dag 1-10)
   - Model Guide (Importkontroll, datakvalitetsfunn, tabeller og relasjoner)
Following Edward Tufte Data-Ink Ratio standards and Frank Ellingsen's Project Controlling guidelines.
"""
import os
import json
import openpyxl
import pandas as pd

HHU_DIR = r"c:\Users\frank\Desktop\UIA2\HHU"
OUTPUT_HTML = os.path.join(HHU_DIR, "index.html")
EXCEL_PATH = os.path.join(HHU_DIR, "UIA-Handelshøyskolen USE-CASE.xlsx")

def load_csv(name):
    path = os.path.join(HHU_DIR, name)
    try:
        return pd.read_csv(path, sep=';', encoding='utf-8-sig')
    except Exception:
        return pd.read_csv(path, sep=';', encoding='latin1')

def extract_all_data():
    orgs = load_csv('DimOrganization.csv')
    accs = load_csv('DimAccountHierarchy.csv')
    dates = load_csv('DimDate.csv')
    dates27 = load_csv('DimDate_2027.csv')
    evm = load_csv('FactEVM.csv')
    fte = load_csv('FactFTE.csv')
    fte27 = load_csv('FactFTE_2027.csv')
    students = load_csv('FactStudents.csv')
    students27 = load_csv('FactStudents_2027.csv')
    actions = load_csv('FactAction.csv')
    actions27 = load_csv('FactAction_2027.csv')
    b26 = load_csv('FactBudget.csv')
    b27 = load_csv('FactBudget_2027.csv')
    gl26 = load_csv('FactGL.csv')

    for col in actions.columns:
        if 'ansvars' in col.lower(): actions.rename(columns={col: 'Budsjettansvarsomraade'}, inplace=True)
        if 'leder' in col.lower(): actions.rename(columns={col: 'AnsvarligLeder'}, inplace=True)
    for col in fte.columns:
        if 'ansvars' in col.lower(): fte.rename(columns={col: 'Budsjettansvarsomraade'}, inplace=True)
        if 'leder' in col.lower(): fte.rename(columns={col: 'BudsjettansvarligLeder'}, inplace=True)

    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)

    # Variance Actions
    va_sheet = wb['Variance Actions']
    variance_drivers = []
    for r in list(va_sheet.iter_rows(values_only=True))[10:21]:
        if r[0]:
            variance_drivers.append({
                'org': str(r[0]), 'konto': int(r[1]) if r[1] else '', 'driver': str(r[2]),
                'budget': float(r[3]) if r[3] else 0, 'le': float(r[4]) if r[4] else 0,
                'avvik': float(r[5]) if r[5] else 0, 'avvik_pct': float(r[6]) if r[6] else 0,
                'rag': str(r[7])
            })

    month_hotspots = []
    for r in list(va_sheet.iter_rows(values_only=True))[10:14]:
        if r[9]:
            month_hotspots.append({
                'month': str(r[9]), 'avvik': float(r[10]) if r[10] else 0, 'forklaring': str(r[11])
            })

    action_plan = []
    for r in list(va_sheet.iter_rows(values_only=True))[25:30]:
        if r[0]:
            action_plan.append({
                'prio': int(r[0]), 'omraade': str(r[1]), 'rotaarsak': str(r[2]), 'handling': str(r[3]),
                'eier': str(r[4]), 'frist': str(r[5])[:10] if r[5] else '', 'brutto_gap': float(r[6]) if r[6] else 0,
                'effekt': float(r[7]) if r[7] else 0, 'kpi': str(r[8]), 'rag': str(r[9]),
                'beslutning': str(r[10]), 'oppfoelging': str(r[11])
            })

    # Budget Process 2027
    bp_sheet = wb['Budget Process 2027']
    gates = []
    for r in list(bp_sheet.iter_rows(values_only=True))[11:17]:
        if r[0]:
            gates.append({
                'port': int(r[0]), 'periode': str(r[1]), 'sporsmaal': str(r[2]), 'aktivitet': str(r[3]),
                'input': str(r[4]), 'ansvarlig': str(r[5]), 'leveranse': str(r[6]), 'arena': str(r[7]),
                'status': str(r[8]), 'rag_icon': str(r[9]), 'kriterier': str(r[10]), 'forutsetninger': str(r[11]),
                'tiltak': str(r[12]), 'frist': str(r[13])[:10] if r[13] else ''
            })

    driver_analysis = []
    for r in list(bp_sheet.iter_rows(values_only=True))[21:27]:
        if r[0]:
            driver_analysis.append({
                'driver': str(r[0]), 'mekanisme': str(r[1]), 'kvantifisering': str(r[2]), 'effekt': str(r[3]),
                'risiko': str(r[4]), 'kontroll': str(r[5]), 'eier': str(r[6]), 'rag': str(r[7]),
                'avstemming': str(r[9]) if len(r)>9 and r[9] else '',
                'modellverdi': float(r[10]) if len(r)>10 and r[10] else 0,
                'referanse': float(r[11]) if len(r)>11 and r[11] else 0,
                'differanse': float(r[12]) if len(r)>12 and r[12] else 0,
                'konklusjon': str(r[13]) if len(r)>13 and r[13] else ''
            })

    closure_plan = []
    for r in list(bp_sheet.iter_rows(values_only=True))[40:46]:
        if r[0]:
            closure_plan.append({
                'prio': int(r[0]), 'avvik_risiko': str(r[1]), 'handling': str(r[2]), 'eier': str(r[3]),
                'frist': str(r[4])[:10] if r[4] else '', 'bevis': str(r[5]), 'konsekvens': str(r[6]), 'rag': str(r[7])
            })

    # Forecast Methods 2027
    fm_sheet = wb['Forecast Methods 2027']
    forecast_posts = []
    for r in list(fm_sheet.iter_rows(values_only=True))[11:22]:
        if r[0]:
            forecast_posts.append({
                'prio': str(r[0]), 'post': str(r[1]), 'konto': str(r[2]), 'baseline': float(r[3]) if r[3] else 0,
                'metode': str(r[4]), 'driver': str(r[5]), 'beregning': str(r[6]), 'oppdatering': str(r[7])
            })

    routine_steps = []
    for r in list(fm_sheet.iter_rows(values_only=True))[26:32]:
        if r[0]:
            routine_steps.append({
                'trinn': int(r[0]), 'formel': str(r[1]), 'forklaring': str(r[2]), 'kontroll': str(r[3]),
                'aktivitet': str(r[5]) if len(r)>5 and r[5] else '',
                'd1_3': str(r[6]) if len(r)>6 and r[6] else '',
                'd4_5': str(r[7]) if len(r)>7 and r[7] else '',
                'd6_7': str(r[8]) if len(r)>8 and r[8] else ''
            })

    # 2027 Plan Report
    p27_sheet = wb['2027 Plan Report']
    p27_units = []
    for r in list(p27_sheet.iter_rows(values_only=True))[11:15]:
        if r[0]:
            p27_units.append({
                'org': str(r[0]), 'enhet': str(r[1]), 'inntekter': float(r[2]), 'kostnader': float(r[3]),
                'netto': float(r[4]), 'aarsverk': float(r[5]), 'uf': float(r[6]), 'studenter': int(r[7]), 'spe60': int(r[8])
            })

    p27_actions = []
    for r in list(p27_sheet.iter_rows(values_only=True))[11:15]:
        if len(r) > 10 and r[10]:
            p27_actions.append({
                'tiltak': str(r[10]), 'enhet': str(r[11]), 'effekt': float(r[12]), 'status': str(r[13]), 'driver': str(r[14])
            })

    return {
        'orgs': orgs.to_dict(orient='records'),
        'accounts': accs.to_dict(orient='records'),
        'dates': dates.to_dict(orient='records'),
        'dates27': dates27.to_dict(orient='records'),
        'evm': evm.to_dict(orient='records'),
        'fte': fte.to_dict(orient='records'),
        'fte27': fte27.to_dict(orient='records'),
        'students': students.to_dict(orient='records'),
        'students27': students27.to_dict(orient='records'),
        'actions': actions.to_dict(orient='records'),
        'actions27': actions27.to_dict(orient='records'),
        'budget26': b26.to_dict(orient='records'),
        'budget27': b27.to_dict(orient='records'),
        'gl26': gl26.to_dict(orient='records'),
        'variance_drivers': variance_drivers,
        'month_hotspots': month_hotspots,
        'action_plan': action_plan,
        'gates': gates,
        'driver_analysis': driver_analysis,
        'closure_plan': closure_plan,
        'forecast_posts': forecast_posts,
        'routine_steps': routine_steps,
        'p27_units': p27_units,
        'p27_actions': p27_actions
    }

def generate_html():
    data = extract_all_data()
    json_data = json.dumps(data, ensure_ascii=False)

    html = """<!DOCTYPE html>
<html lang="no">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Handelshøyskolen ved UiA (HHU) — Virksomhetsstyring & Ledelsesrapportering</title>
  <meta name="description" content="Integrert virksomhetsstyring, avviksanalyse og driverbasert budsjettprosess for HHU UiA iht. Edward Tufte Data-Ink standarder.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-canvas: #f8fafc;
      --bg-card: #ffffff;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --text-light: #94a3b8;
      --border-color: #e2e8f0;
      --border-subtle: #f1f5f9;
      --brand-navy: #1e293b;
      --brand-blue: #0284c7;
      --rag-green: #10b981;
      --rag-green-bg: #ecfdf5;
      --rag-green-text: #065f46;
      --rag-amber: #f59e0b;
      --rag-amber-bg: #fffbeb;
      --rag-amber-text: #92400e;
      --rag-red: #ef4444;
      --rag-red-bg: #fef2f2;
      --rag-red-text: #991b1b;
      --font-stack: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: var(--font-stack);
      background-color: var(--bg-canvas);
      color: var(--text-main);
      font-size: 13px;
      line-height: 1.45;
      -webkit-font-smoothing: antialiased;
    }

    .num, td.num, th.num, .kpi-val {
      font-variant-numeric: tabular-nums;
      text-align: right;
    }

    /* Layout Containers */
    .app-header {
      background-color: #ffffff;
      border-bottom: 1px solid var(--border-color);
      padding: 14px 24px;
      position: sticky;
      top: 0;
      z-index: 100;
    }

    .header-top {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;
      gap: 16px;
      flex-wrap: wrap;
    }

    .header-brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .brand-badge {
      background-color: var(--brand-navy);
      color: #ffffff;
      font-weight: 700;
      font-size: 11px;
      letter-spacing: 0.5px;
      padding: 4px 8px;
      border-radius: 4px;
      text-transform: uppercase;
    }

    .header-titles h1 {
      font-size: 18px;
      font-weight: 700;
      color: var(--text-main);
      letter-spacing: -0.3px;
      margin-bottom: 2px;
    }

    .header-titles p {
      font-size: 12px;
      color: var(--text-muted);
    }

    .slicer-toolbar {
      display: flex;
      gap: 10px;
      align-items: center;
      flex-wrap: wrap;
    }

    .slicer-group {
      display: flex;
      flex-direction: column;
      gap: 3px;
    }

    .slicer-group label {
      font-size: 10px;
      font-weight: 600;
      text-transform: uppercase;
      color: var(--text-muted);
    }

    .slicer-select {
      font-family: inherit;
      font-size: 12px;
      background-color: #ffffff;
      border: 1px solid var(--border-color);
      border-radius: 4px;
      padding: 5px 10px;
      color: var(--text-main);
      min-width: 140px;
      cursor: pointer;
      outline: none;
    }

    .btn-action {
      background-color: #ffffff;
      border: 1px solid var(--border-color);
      padding: 6px 12px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 500;
      color: var(--text-main);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      align-self: flex-end;
    }

    .btn-action:hover {
      background-color: var(--border-subtle);
      border-color: #cbd5e1;
    }

    /* Tabbed Navigation Bar */
    .tab-nav-wrapper {
      background-color: #ffffff;
      border-bottom: 1px solid var(--border-color);
      padding: 0 24px;
      overflow-x: auto;
    }

    .tab-nav {
      display: flex;
      gap: 2px;
      min-width: max-content;
    }

    .tab-btn {
      background: none;
      border: none;
      padding: 10px 14px;
      font-size: 12px;
      font-weight: 500;
      color: var(--text-muted);
      cursor: pointer;
      border-bottom: 2px solid transparent;
      white-space: nowrap;
      transition: all 0.15s;
    }

    .tab-btn:hover { color: var(--text-main); }
    .tab-btn.active {
      color: var(--brand-blue);
      font-weight: 600;
      border-bottom-color: var(--brand-blue);
    }

    .tab-group-tag {
      font-size: 9px;
      font-weight: 700;
      text-transform: uppercase;
      padding: 1px 4px;
      border-radius: 3px;
      background: #f1f5f9;
      color: #475569;
      margin-right: 4px;
    }

    /* Canvas */
    .canvas-container {
      max-width: 1920px;
      margin: 0 auto;
      padding: 20px 24px 60px 24px;
    }

    .page-section { display: none; }
    .page-section.active {
      display: block;
      animation: fadeIn 0.2s ease-in-out;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(3px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* KPI Cards */
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 14px;
      margin-bottom: 20px;
    }

    .kpi-card {
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 6px;
      padding: 14px 16px;
      position: relative;
      overflow: hidden;
    }

    .kpi-card::before {
      content: '';
      position: absolute;
      left: 0; top: 0; bottom: 0;
      width: 4px;
      background-color: var(--card-accent, var(--brand-navy));
    }

    .kpi-card-header {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 6px;
    }

    .kpi-title {
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      color: var(--text-muted);
      letter-spacing: 0.3px;
    }

    .kpi-badge {
      font-size: 10px;
      font-weight: 600;
      padding: 2px 6px;
      border-radius: 3px;
    }

    .kpi-val {
      font-size: 24px;
      font-weight: 700;
      color: var(--text-main);
      line-height: 1.1;
      margin-bottom: 4px;
      text-align: left;
    }

    .kpi-sub {
      font-size: 11px;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 4px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    /* Panels & Tables */
    .panel-card {
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 6px;
      padding: 16px 20px;
      margin-bottom: 20px;
    }

    .panel-header {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 12px;
      border-bottom: 1px solid var(--border-subtle);
      padding-bottom: 8px;
    }

    .panel-title {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-main);
    }

    .panel-meta {
      font-size: 11px;
      color: var(--text-muted);
    }

    /* Executive Callout Note */
    .callout-box {
      background-color: #f8fafc;
      border: 1px solid var(--border-color);
      border-left: 4px solid var(--brand-blue);
      padding: 12px 16px;
      border-radius: 4px;
      margin-bottom: 20px;
    }

    .callout-box.alert-red {
      border-left-color: var(--rag-red);
      background-color: #fef2f2;
    }

    .callout-box.alert-amber {
      border-left-color: var(--rag-amber);
      background-color: #fffbeb;
    }

    .callout-box.alert-green {
      border-left-color: var(--rag-green);
      background-color: #ecfdf5;
    }

    .callout-title {
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-main);
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .callout-text {
      font-size: 12px;
      color: #334155;
      line-height: 1.5;
    }

    .table-container {
      overflow-x: auto;
      margin-top: 6px;
    }

    table.tufte-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
      border: none;
    }

    table.tufte-table th {
      background-color: #f8fafc;
      color: var(--text-main);
      font-weight: 600;
      text-align: left;
      padding: 8px 12px;
      border-bottom: 1px solid var(--border-color);
      white-space: nowrap;
      cursor: pointer;
      user-select: none;
    }

    table.tufte-table th:hover { background-color: #f1f5f9; }
    table.tufte-table th.num { text-align: right; }

    table.tufte-table td {
      padding: 8px 12px;
      border-bottom: 1px solid #f1f5f9;
      color: #1e293b;
      white-space: nowrap;
    }

    table.tufte-table tr:hover td { background-color: #f8fafc; }
    table.tufte-table tr.total-row td {
      font-weight: 700;
      border-top: 1px solid var(--border-color);
      border-bottom: 2px solid var(--border-color);
      background-color: #f8fafc;
    }

    .badge-rag {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 11px;
      font-weight: 500;
      padding: 2px 6px;
      border-radius: 4px;
    }

    .badge-green { background-color: var(--rag-green-bg); color: var(--rag-green-text); }
    .badge-amber { background-color: var(--rag-amber-bg); color: var(--rag-amber-text); }
    .badge-red { background-color: var(--rag-red-bg); color: var(--rag-red-text); }
    .badge-neutral { background-color: #f1f5f9; color: #334155; }

    .text-green { color: var(--rag-green); }
    .text-amber { color: var(--rag-amber); }
    .text-red { color: var(--rag-red); }

    .charts-grid-60-40 {
      display: grid;
      grid-template-columns: 1.5fr 1fr;
      gap: 16px;
      margin-bottom: 20px;
    }

    .charts-grid-half {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-bottom: 20px;
    }

    .chart-box {
      width: 100%;
      position: relative;
    }

    svg.tufte-chart {
      width: 100%;
      height: auto;
      display: block;
      overflow: visible;
    }

    .chart-tooltip {
      position: absolute;
      background: #0f172a;
      color: #ffffff;
      padding: 6px 10px;
      border-radius: 4px;
      font-size: 11px;
      pointer-events: none;
      opacity: 0;
      transition: opacity 0.15s;
      z-index: 1000;
      white-space: nowrap;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* Decision Gates Roadmap */
    .gate-pipeline {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 10px;
      margin-bottom: 20px;
    }

    .gate-node {
      background: #ffffff;
      border: 1px solid var(--border-color);
      border-radius: 6px;
      padding: 10px 12px;
      position: relative;
    }

    .gate-node.passed { border-top: 4px solid var(--rag-green); }
    .gate-node.in-progress { border-top: 4px solid var(--rag-amber); }
    .gate-node.blocked { border-top: 4px solid var(--rag-red); }
    .gate-node.future { border-top: 4px solid var(--text-light); }

    .gate-num { font-size: 10px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; }
    .gate-title { font-size: 12px; font-weight: 600; color: var(--text-main); margin: 3px 0; }
    .gate-status { font-size: 11px; font-weight: 500; }

    @media print {
      .app-header { position: static; border-bottom: none; }
      .tab-nav-wrapper, .btn-action, .slicer-toolbar { display: none !important; }
      .page-section { display: block !important; page-break-after: always; }
      body { background-color: #ffffff; font-size: 10pt; }
      .canvas-container { padding: 0; }
      .panel-card { border: none; padding: 10px 0; }
    }

    @media (max-width: 1024px) {
      .charts-grid-60-40, .charts-grid-half { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>

  <!-- Header -->
  <header class="app-header">
    <div class="header-top">
      <div class="header-brand">
        <span class="brand-badge">HHU CONTROLLING</span>
        <div class="header-titles">
          <h1>Handelshøyskolen ved UiA (HHU) — Virksomhetsstyring & Ledelsesrapportering</h1>
          <p>Integrert lederrapport, avviks- og handlingsplan, samt driverbasert budsjettprosess 2026/2027 | Edward Tufte Data-Ink Standard</p>
        </div>
      </div>

      <!-- Slicer Bar Toolbar -->
      <div class="slicer-toolbar">
        <div class="slicer-group">
          <label for="slicer-year">Regnskapsår</label>
          <select id="slicer-year" class="slicer-select" onchange="applyGlobalFilters()">
            <option value="2026" selected>2026 (Inneværende)</option>
            <option value="2027">2027 (Budsjettramme)</option>
          </select>
        </div>

        <div class="slicer-group">
          <label for="slicer-month">Rapporteringsmåned</label>
          <select id="slicer-month" class="slicer-select" onchange="applyGlobalFilters()">
            <option value="ALL" selected>Hele Året (M01-M12)</option>
            <option value="9">M09 Sept (T3 Cutoff YTD)</option>
            <option value="1">M01 Januar</option>
            <option value="2">M02 Februar</option>
            <option value="3">M03 Mars</option>
            <option value="4">M04 April</option>
            <option value="5">M05 Mai</option>
            <option value="6">M06 Juni</option>
            <option value="7">M07 Juli</option>
            <option value="8">M08 August</option>
            <option value="10">M10 Oktober</option>
            <option value="11">M11 November</option>
            <option value="12">M12 Desember</option>
          </select>
        </div>

        <div class="slicer-group">
          <label for="slicer-org">Enhet / Institutt</label>
          <select id="slicer-org" class="slicer-select" onchange="applyGlobalFilters()">
            <option value="ALL" selected>Alle Enheter (HHU Total)</option>
            <option value="K10000">K10000 Admin & Felles</option>
            <option value="K11000">K11000 Ledelse & Innovasjon</option>
            <option value="K12000">K12000 Rettsvitenskap</option>
            <option value="K13000">K13000 Økonomi</option>
          </select>
        </div>

        <div class="slicer-group">
          <label for="slicer-account">Kontotype</label>
          <select id="slicer-account" class="slicer-select" onchange="applyGlobalFilters()">
            <option value="ALL" selected>Alle Kontotyper</option>
            <option value="Inntekt">Inntekt</option>
            <option value="Lønnskostnad">Kostnad: Lønn</option>
            <option value="Annen driftskostnad">Kostnad: Drift</option>
          </select>
        </div>

        <button class="btn-action" onclick="resetFilters()">🔄 Nullstill</button>
        <button class="btn-action" onclick="exportActiveTableToCSV()">📥 Eksporter CSV</button>
        <button class="btn-action" onclick="window.print()">🖨️ Skriv ut / PDF</button>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="tab-nav-wrapper">
      <nav class="tab-nav">
        <button class="tab-btn active" onclick="switchTab('p1_summary')"><span class="tab-group-tag">2026</span>1. Ledelsessammendrag</button>
        <button class="tab-btn" onclick="switchTab('p2_institutter')"><span class="tab-group-tag">2026</span>2. Enhets- & Kontooppfølging</button>
        <button class="tab-btn" onclick="switchTab('p3_variance')"><span class="tab-group-tag">Avvik</span>3. Avviks- & Rotårsaksanalyse</button>
        <button class="tab-btn" onclick="switchTab('p4_actionplan')"><span class="tab-group-tag">Tiltak</span>4. Prioritert Handlingsplan</button>
        <button class="tab-btn" onclick="switchTab('p5_staffing')"><span class="tab-group-tag">HR</span>5. Bemanningsanalyse & Årsverk</button>
        <button class="tab-btn" onclick="switchTab('p6_evm')"><span class="tab-group-tag">EVM</span>6. EVM Fremdrift & S-Kurve</button>
        <button class="tab-btn" onclick="switchTab('p7_students')"><span class="tab-group-tag">Utd</span>7. Studieproduksjon & KD</button>
        <button class="tab-btn" onclick="switchTab('p8_budget2027')"><span class="tab-group-tag">2027</span>8. Budsjett 2027 Planrapport</button>
        <button class="tab-btn" onclick="switchTab('p9_process')"><span class="tab-group-tag">Prosess</span>9. Budsjettprosess & Lukkeplan</button>
        <button class="tab-btn" onclick="switchTab('p10_methods')"><span class="tab-group-tag">Metode</span>10. Prognosemetodikk 2027</button>
        <button class="tab-btn" onclick="switchTab('p11_modelguide')"><span class="tab-group-tag">Modell</span>11. Datamodell & Kvalitetskontroll</button>
      </nav>
    </div>
  </header>

  <main class="canvas-container">
    <div id="chart-tooltip" class="chart-tooltip"></div>

    <!-- ========================================================================= -->
    <!-- TAB 1: LEDELSESSAMMENDRAG 2026                                            -->
    <!-- ========================================================================= -->
    <section id="p1_summary" class="page-section active">
      <div class="kpi-grid">
        <div class="kpi-card" style="--card-accent: #10b981;">
          <div class="kpi-card-header"><span class="kpi-title">HELÅRSPROGNOSE (LE)</span><span class="kpi-badge badge-green">Cutoff 30.09</span></div>
          <div class="kpi-val" id="p1-kpi-rev">129,6 MNOK</div>
          <div class="kpi-sub">Vedtatt budsjett (BAC): 130,2 MNOK</div>
        </div>
        <div class="kpi-card" style="--card-accent: #10b981;">
          <div class="kpi-card-header"><span class="kpi-title">SLUTTAVVIK (VAC)</span><span class="kpi-badge badge-green" id="p1-vac-badge">🟢 Mindreforbruk</span></div>
          <div class="kpi-val text-green" id="p1-kpi-vac">+0,5 MNOK</div>
          <div class="kpi-sub" id="p1-kpi-vac-sub">522 258 kr under budsjett (+0,4%)</div>
        </div>
        <div class="kpi-card" style="--card-accent: #f59e0b;">
          <div class="kpi-card-header"><span class="kpi-title">ÅRSVERK TOTALT</span><span class="kpi-badge badge-amber">Aktiv</span></div>
          <div class="kpi-val" id="p1-kpi-fte">229 ÅV</div>
          <div class="kpi-sub">154 UF / 75 TA | Lønnsandel: 62,1%</div>
        </div>
        <div class="kpi-card" style="--card-accent: #10b981;">
          <div class="kpi-card-header"><span class="kpi-title">EVM EFFEKTIVITET (CPI/SPI)</span><span class="kpi-badge badge-green">Stabil</span></div>
          <div class="kpi-val" id="p1-kpi-cpi">0,97 / 0,98</div>
          <div class="kpi-sub">CPI 0,97 (Kostnad) | SPI 0,98 (Fremdrift)</div>
        </div>
        <div class="kpi-card" style="--card-accent: #0284c7;">
          <div class="kpi-card-header"><span class="kpi-title">STUDIEPRODUKSJON</span><span class="kpi-badge badge-neutral">Mål</span></div>
          <div class="kpi-val" id="p1-kpi-stud">3 450 Stud.</div>
          <div class="kpi-sub">3 153 SPE60 | 22,3 Studenter/UF-ÅV</div>
        </div>
      </div>

      <!-- Ledelseskonklusjon Callout from Executive Report -->
      <div class="callout-box alert-green">
        <div class="callout-title">📌 LEDELSESKONKLUSJON (September YTD + Q4-prognose | 3–30–300 beslutningsvisning)</div>
        <div class="callout-text">
          2026 ventes <strong>0,52 MNOK innenfor budsjett</strong>, drevet av <strong>1,15 MNOK mindreforbruk i Rettsvitenskap</strong>. Økonomi ligger 0,71 MNOK over plan, og EVM-indeksene CPI 0,97 / SPI 0,98 viser fortsatt moderat gjennomføringsrisiko. Prioriter BOA-frikjøp, EVU-kontroll og bemanningsstyring før årsavslutningen.
        </div>
      </div>

      <div class="charts-grid-60-40">
        <div class="panel-card">
          <div class="panel-header">
            <h3 class="panel-title">Månedlig Kostnadsutvikling vs. Budsjett M01–M12 (T3 Cutoff pr 30.09)</h3>
            <span class="panel-meta">Stolper: Faktisk/Prognose | Stiplet: Periodisert Budsjett</span>
          </div>
          <div class="chart-box" id="chart-p1-monthly"></div>
        </div>

        <div class="panel-card">
          <div class="panel-header">
            <h3 class="panel-title">Enhetsvis Netto Sluttavvik (VAC MNOK) — Merforbruk vs. Mindreforbruk</h3>
            <span class="panel-meta">Grønn: Mindreforbruk | Rød: Merforbruk</span>
          </div>
          <div class="chart-box" id="chart-p1-variance"></div>
        </div>
      </div>

      <div class="panel-card">
        <div class="panel-header">
          <h3 class="panel-title">Fakultets- og Instituttoversikt: Totalregnskap, Stillingsstruktur og Styringsdiagnose (DFØ / SRS)</h3>
          <span class="panel-meta">Tall i MNOK | Sorterbar tabell</span>
        </div>
        <div class="table-container">
          <table class="tufte-table" id="table-p1-matrix">
            <thead>
              <tr>
                <th onclick="sortTable('table-p1-matrix', 0)">OrgKode</th>
                <th onclick="sortTable('table-p1-matrix', 1)">Enhetsnavn</th>
                <th class="num" onclick="sortTable('table-p1-matrix', 2, true)">Total Ramme</th>
                <th class="num" onclick="sortTable('table-p1-matrix', 3, true)">Lønn (EAC)</th>
                <th class="num" onclick="sortTable('table-p1-matrix', 4, true)">Drift (EAC)</th>
                <th class="num" onclick="sortTable('table-p1-matrix', 5, true)">Sluttavvik (VAC)</th>
                <th class="num" onclick="sortTable('table-p1-matrix', 6, true)">UF-Årsverk</th>
                <th class="num" onclick="sortTable('table-p1-matrix', 7, true)">Stud/UF-ÅV</th>
                <th>RAG Status</th>
                <th>Strategisk Styringsdiagnose & Økonomiske Drivere</th>
              </tr>
            </thead>
            <tbody id="tbody-p1-matrix"></tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ========================================================================= -->
    <!-- TAB 2: ENHETS- & KONTOOPPFØLGING (Unit Analysis & DFØ R-102)               -->
    <!-- ========================================================================= -->
    <section id="p2_institutter" class="page-section">
      <div class="kpi-grid">
        <div class="kpi-card" style="--card-accent: #334155;">
          <div class="kpi-card-header"><span class="kpi-title">K10000 FAKULTETSADMIN & FELLES</span><span class="kpi-badge badge-green">🟢 Innenfor</span></div>
          <div class="kpi-val">14,00 MNOK</div>
          <div class="kpi-sub">Budsjett: 14,00 M | LE: 13,91 M | VAC: +0,09 MNOK</div>
        </div>
        <div class="kpi-card" style="--card-accent: #0284c7;">
          <div class="kpi-card-header"><span class="kpi-title">K11000 LEDELSE & INNOVASJON</span><span class="kpi-badge badge-amber">🟡 Følg opp</span></div>
          <div class="kpi-val">38,50 MNOK</div>
          <div class="kpi-sub">Budsjett: 38,50 M | LE: 38,50 M | VAC: -0,00 MNOK</div>
        </div>
        <div class="kpi-card" style="--card-accent: #475569;">
          <div class="kpi-card-header"><span class="kpi-title">K12000 RETTSVITENSKAP</span><span class="kpi-badge badge-green">🟢 Innenfor</span></div>
          <div class="kpi-val">29,25 MNOK</div>
          <div class="kpi-sub">Budsjett: 29,25 M | LE: 28,10 M | VAC: +1,15 MNOK</div>
        </div>
        <div class="kpi-card" style="--card-accent: #10b981;">
          <div class="kpi-card-header"><span class="kpi-title">K13000 ØKONOMI</span><span class="kpi-badge badge-amber">🟡 Følg opp</span></div>
          <div class="kpi-val">48,40 MNOK</div>
          <div class="kpi-sub">Budsjett: 48,40 M | LE: 49,11 M | VAC: -0,71 MNOK</div>
        </div>
      </div>

      <div class="callout-box alert-amber">
        <div class="callout-title">📋 ANALYTISK KONKLUSJON (Fra Unit Analysis)</div>
        <div class="callout-text">
          Rettsvitenskap er hoveddriveren bak positivt sluttavvik (+1,15 MNOK), mens Økonomi har størst oppfølgingsbehov (–0,71 MNOK). Tiltakene har realisert 3,60 av 4,60 MNOK (78,3 %). De største gjenstående gapene ligger i BOA-frikjøp (0,40 MNOK) og EVU-kontroll (0,35 MNOK).
        </div>
      </div>

      <div class="panel-card">
        <div class="panel-header">
          <h3 class="panel-title">Detaljert Kontooppfølging iht. DFØ R-102 Kontoplan & SRS Regnskapslinjer</h3>
          <span class="panel-meta">Beløp i hele NOK</span>
        </div>
        <div class="table-container">
          <table class="tufte-table" id="table-p2-accounts">
            <thead>
              <tr>
                <th onclick="sortTable('table-p2-accounts', 0, true)">Konto</th>
                <th onclick="sortTable('table-p2-accounts', 1)">Kontonavn</th>
                <th onclick="sortTable('table-p2-accounts', 2)">Kontogruppe</th>
                <th onclick="sortTable('table-p2-accounts', 3)">SRS Regnskapslinje</th>
                <th class="num" onclick="sortTable('table-p2-accounts', 4, true)">Vedtatt Budsjett (BAC)</th>
                <th class="num" onclick="sortTable('table-p2-accounts', 5, true)">Bokført YTD</th>
                <th class="num" onclick="sortTable('table-p2-accounts', 6, true)">Prognose Q4 (ETC)</th>
                <th class="num" onclick="sortTable('table-p2-accounts', 7, true)">Sluttprognose (EAC)</th>
                <th class="num" onclick="sortTable('table-p2-accounts', 8, true)">Sluttavvik (VAC)</th>
                <th class="num" onclick="sortTable('table-p2-accounts', 9, true)">VAC %</th>
              </tr>
            </thead>
            <tbody id="tbody-p2-accounts"></tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ========================================================================= -->
    <!-- TAB 3: AVVIKS- & ROTÅRSAKSANALYSE (Variance Actions Sheet)                -->
    <!-- ========================================================================= -->
    <section id="p3_variance" class="page-section">
      <div class="kpi-grid">
        <div class="kpi-card" style="--card-accent: #10b981;">
          <div class="kpi-card-header"><span class="kpi-title">NETTO SLUTTAVVIK (VAC)</span></div>
          <div class="kpi-val text-green">+522 258 kr</div>
          <div class="kpi-sub">Foretrukket positivt helårsavvik</div>
        </div>
        <div class="kpi-card" style="--card-accent: #10b981;">
          <div class="kpi-card-header"><span class="kpi-title">POSITIVE DRIVERE</span></div>
          <div class="kpi-val text-green">+2 107 632 kr</div>
          <div class="kpi-sub">Feriepenger & vakanser</div>
        </div>
        <div class="kpi-card" style="--card-accent: #ef4444;">
          <div class="kpi-card-header"><span class="kpi-title">NEGATIVE DRIVERE</span></div>
          <div class="kpi-val text-red">-1 585 374 kr</div>
          <div class="kpi-sub">Lønnsmerforbruk K13 + EVU tapsavsetning</div>
        </div>
        <div class="kpi-card" style="--card-accent: #f59e0b;">
          <div class="kpi-card-header"><span class="kpi-title">TILTAKSGAP (UREALISERT)</span></div>
          <div class="kpi-val text-amber">1 000 000 kr</div>
          <div class="kpi-sub">Gjenstår for T001–T003</div>
        </div>
        <div class="kpi-card" style="--card-accent: #ef4444;">
          <div class="kpi-card-header"><span class="kpi-title">STØRSTE RISIKO</span></div>
          <div class="kpi-val text-red">K13000 Lønn</div>
          <div class="kpi-sub">-983k avvik på fast lønn (5000)</div>
        </div>
      </div>

      <div class="callout-box alert-amber">
        <div class="callout-title">⚠️ LEDELSESVURDERING OG ROBUSTHETSANALYSE</div>
        <div class="callout-text">
          Nettoresultatet er positivt, men robustheten er svak: <strong>1,15 MNOK i vakansbesparelse ved Rettsvitenskap</strong> dekker i stor grad lønnsmerforbruket i Økonomi og avvik knyttet til EVU/AACSB. Ledelsen bør derfor ikke tolke +0,52 MNOK som strukturelt handlingsrom. Første prioritet er å lukke lønns- og BOA-gapet i K13000; andre prioritet er å stoppe videre marginerosjon i EVU001. Besparelsen i K12000 bør beholdes som buffer inntil disse risikoene er lukket.
        </div>
      </div>

      <div class="charts-grid-60-40">
        <!-- 1. Avviksdrivere -->
        <div class="panel-card">
          <div class="panel-header">
            <h3 class="panel-title">1. Avviksdrivere — Budsjett minus Latest Estimate (De 11 største postene)</h3>
            <span class="panel-meta">Sortert etter vesentlighet</span>
          </div>
          <div class="table-container">
            <table class="tufte-table" id="table-variance-drivers">
              <thead>
                <tr>
                  <th>Enhet</th>
                  <th>Konto</th>
                  <th>Driver</th>
                  <th class="num">Budsjett</th>
                  <th class="num">Latest Est.</th>
                  <th class="num">Avvik (kr)</th>
                  <th class="num">Avvik %</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody id="tbody-variance-drivers"></tbody>
            </table>
          </div>
        </div>

        <!-- 2. Månedshotspots -->
        <div class="panel-card">
          <div class="panel-header">
            <h3 class="panel-title">2. Månedshotspots (Største månedlige avvik)</h3>
            <span class="panel-meta">Identifiserte periodiske avvik</span>
          </div>
          <div class="table-container">
            <table class="tufte-table" id="table-month-hotspots">
              <thead>
                <tr>
                  <th>Måned</th>
                  <th class="num">Netto Avvik</th>
                  <th>Forklaring & Rotårsak</th>
                </tr>
              </thead>
              <tbody id="tbody-month-hotspots"></tbody>
            </table>
          </div>
        </div>
      </div>
    </section>

    <!-- ========================================================================= -->
    <!-- TAB 4: PRIORITERT HANDLINGSPLAN (Variance Actions Sheet Del 3)             -->
    <!-- ========================================================================= -->
    <section id="p4_actionplan" class="page-section">
      <div class="panel-card">
        <div class="panel-header">
          <h3 class="panel-title">Prioritert Handlingsplan og Tiltaksoppfølging (Rotårsak & Beslutning)</h3>
          <span class="panel-meta">Eierskap, tidsfrister og eskalering</span>
        </div>
        <div class="table-container">
          <table class="tufte-table" id="table-action-plan">
            <thead>
              <tr>
                <th>Prio</th>
                <th>Område</th>
                <th>Rotårsak / Observasjon</th>
                <th>Anbefalt Handling</th>
                <th>Eier</th>
                <th>Frist</th>
                <th class="num">Brutto Gap</th>
                <th class="num">Effekt</th>
                <th>KPI / Kontrollpunkt</th>
                <th>RAG</th>
                <th>Beslutning nå</th>
                <th>Oppfølging</th>
              </tr>
            </thead>
            <tbody id="tbody-action-plan"></tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ========================================================================= -->
    <!-- TAB 5: BEMANNINGSANALYSE & ÅRSVERK                                         -->
    <!-- ========================================================================= -->
    <section id="p5_staffing" class="page-section">
      <div class="kpi-grid">
        <div class="kpi-card" style="--card-accent: #334155;">
          <div class="kpi-card-header"><span class="kpi-title">TOTALE ÅRSVERK (SNAPSHOT)</span></div>
          <div class="kpi-val" id="p3-kpi-totale">229,0 ÅV</div>
          <div class="kpi-sub">Siste registrerte måned (M12)</div>
        </div>
        <div class="kpi-card" style="--card-accent: #0284c7;">
          <div class="kpi-card-header"><span class="kpi-title">FAGLIGE ÅRSVERK (UF)</span></div>
          <div class="kpi-val" id="p3-kpi-uf">154,0 ÅV</div>
          <div class="kpi-sub">Undervisning og forskning</div>
        </div>
        <div class="kpi-card" style="--card-accent: #475569;">
          <div class="kpi-card-header"><span class="kpi-title">ADMIN. ÅRSVERK (TA)</span></div>
          <div class="kpi-val" id="p3-kpi-ta">75,0 ÅV</div>
          <div class="kpi-sub">Teknisk-administrativ støtte</div>
        </div>
        <div class="kpi-card" style="--card-accent: #10b981;">
          <div class="kpi-card-header"><span class="kpi-title">FAGLIG ANDEL %</span></div>
          <div class="kpi-val" id="p3-kpi-andel">67,2%</div>
          <div class="kpi-sub">Sektormål: &gt; 50–55% | <span class="text-green">Over målkrav</span></div>
        </div>
        <div class="kpi-card" style="--card-accent: #f59e0b;">
          <div class="kpi-card-header"><span class="kpi-title">VAKANSGRAD %</span></div>
          <div class="kpi-val" id="p3-kpi-vakans">-0,8%</div>
          <div class="kpi-sub">Planlagte vs. faktiske årsverk</div>
        </div>
        <div class="kpi-card" style="--card-accent: #10b981;">
          <div class="kpi-card-header"><span class="kpi-title">LØNNSANDEL %</span></div>
          <div class="kpi-val" id="p3-kpi-lonn">62,1%</div>
          <div class="kpi-sub">Mål: &lt; 65,0% | <span class="text-green">I balanse</span></div>
        </div>
      </div>

      <div class="charts-grid-half">
        <div class="panel-card">
          <div class="panel-header">
            <h3 class="panel-title">Månedlig Årsverksutvikling fordelt på UF og TA (M01–M12)</h3>
            <span class="panel-meta">Stablet søylediagram: Blå = UF, Grå = TA</span>
          </div>
          <div class="chart-box" id="chart-p3-monthly-fte"></div>
        </div>

        <div class="panel-card">
          <div class="panel-header">
            <h3 class="panel-title">Bemanningsstørrelse (Totale Årsverk) per Enhet</h3>
            <span class="panel-meta">Status pr M12</span>
          </div>
          <div class="chart-box" id="chart-p3-unit-fte"></div>
        </div>
      </div>

      <div class="panel-card">
        <div class="panel-header">
          <h3 class="panel-title">Detaljert Månedlig Bemannings- og Vakanslogg per Avdeling</h3>
          <span class="panel-meta">Stillingsstruktur og rekrutteringsstatus</span>
        </div>
        <div class="table-container">
          <table class="tufte-table" id="table-p3-fte">
            <thead>
              <tr>
                <th onclick="sortTable('table-p3-fte', 0)">Måned</th>
                <th onclick="sortTable('table-p3-fte', 1)">Enhet</th>
                <th class="num" onclick="sortTable('table-p3-fte', 2, true)">UF-Årsverk</th>
                <th class="num" onclick="sortTable('table-p3-fte', 3, true)">TA-Årsverk</th>
                <th class="num" onclick="sortTable('table-p3-fte', 4, true)">Totalt Årsverk</th>
                <th class="num" onclick="sortTable('table-p3-fte', 5, true)">Budsjett ÅV</th>
                <th class="num" onclick="sortTable('table-p3-fte', 6, true)">Vakans ÅV</th>
                <th class="num" onclick="sortTable('table-p3-fte', 7, true)">Vakansgrad %</th>
                <th class="num" onclick="sortTable('table-p3-fte', 8, true)">Ansatte</th>
              </tr>
            </thead>
            <tbody id="tbody-p3-fte"></tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ========================================================================= -->
    <!-- TAB 6: EVM FREMDRIFT & S-KURVE                                             -->
    <!-- ========================================================================= -->
    <section id="p6_evm" class="page-section">
      <div class="kpi-grid">
        <div class="kpi-card" style="--card-accent: #334155;">
          <div class="kpi-card-header"><span class="kpi-title">PLANLAGT VERDI (PV)</span></div>
          <div class="kpi-val">130,2 MNOK</div>
          <div class="kpi-sub">Budsjettert fremdrift M12</div>
        </div>
        <div class="kpi-card" style="--card-accent: #0284c7;">
          <div class="kpi-card-header"><span class="kpi-title">OPPTJENT VERDI (EV)</span></div>
          <div class="kpi-val">127,6 MNOK</div>
          <div class="kpi-sub">Realisert produksjon M12</div>
        </div>
        <div class="kpi-card" style="--card-accent: #475569;">
          <div class="kpi-card-header"><span class="kpi-title">FAKTISK KOSTNAD (AC)</span></div>
          <div class="kpi-val">131,5 MNOK</div>
          <div class="kpi-sub">Påløpte kostnader M12</div>
        </div>
        <div class="kpi-card" style="--card-accent: #f59e0b;">
          <div class="kpi-card-header"><span class="kpi-title">KOSTNADSINDEKS (CPI)</span></div>
          <div class="kpi-val">0,97</div>
          <div class="kpi-sub">Mål &ge; 1,00 | Moderat avvik</div>
        </div>
        <div class="kpi-card" style="--card-accent: #10b981;">
          <div class="kpi-card-header"><span class="kpi-title">FREMDRIFTSINDEKS (SPI)</span></div>
          <div class="kpi-val">0,98</div>
          <div class="kpi-sub">Mål &ge; 1,00 | Planmessig tidsplan</div>
        </div>
        <div class="kpi-card" style="--card-accent: #10b981;">
          <div class="kpi-card-header"><span class="kpi-title">EVM STATUSINDEKS</span></div>
          <div class="kpi-val">🟢 Stabil</div>
          <div class="kpi-sub">CPI 0,97 | SPI 0,98</div>
        </div>
      </div>

      <div class="charts-grid-half">
        <div class="panel-card">
          <div class="panel-header">
            <h3 class="panel-title">EVM S-Kurve: PV, EV og AC per Måned (MNOK)</h3>
            <span class="panel-meta">Edward Tufte Direct Labeling (Direkte kurvemerking)</span>
          </div>
          <div class="chart-box" id="chart-p4-scurve"></div>
        </div>

        <div class="panel-card">
          <div class="panel-header">
            <h3 class="panel-title">Månedlig Effektivitetsutvikling (CPI & SPI)</h3>
            <span class="panel-meta">Referanselinje ved indeks 1,00</span>
          </div>
          <div class="chart-box" id="chart-p4-indices"></div>
        </div>
      </div>

      <div class="panel-card">
        <div class="panel-header">
          <h3 class="panel-title">Månedlig Earned Value Prosjektlogg (NOK og Nøkkeltall)</h3>
          <span class="panel-meta">EVM beregninger iht. PMI-standard</span>
        </div>
        <div class="table-container">
          <table class="tufte-table" id="table-p4-evm">
            <thead>
              <tr>
                <th onclick="sortTable('table-p4-evm', 0)">Måned</th>
                <th class="num" onclick="sortTable('table-p4-evm', 1, true)">BAC (Budsjett)</th>
                <th class="num" onclick="sortTable('table-p4-evm', 2, true)">Planned Value (PV)</th>
                <th class="num" onclick="sortTable('table-p4-evm', 3, true)">Earned Value (EV)</th>
                <th class="num" onclick="sortTable('table-p4-evm', 4, true)">Actual Cost (AC)</th>
                <th class="num" onclick="sortTable('table-p4-evm', 5, true)">Prognose (EAC)</th>
                <th class="num" onclick="sortTable('table-p4-evm', 6, true)">Sluttavvik (VAC)</th>
                <th class="num" onclick="sortTable('table-p4-evm', 7, true)">CPI</th>
                <th class="num" onclick="sortTable('table-p4-evm', 8, true)">SPI</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody id="tbody-p4-evm"></tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ========================================================================= -->
    <!-- TAB 7: STUDIEPRODUKSJON & KD                                               -->
    <!-- ========================================================================= -->
    <section id="p7_students" class="page-section">
      <div class="kpi-grid">
        <div class="kpi-card" style="--card-accent: #334155;">
          <div class="kpi-card-header"><span class="kpi-title">REGISTRERTE STUDENTER</span></div>
          <div class="kpi-val">3 450</div>
          <div class="kpi-sub">Totalt HHU studieopptak</div>
        </div>
        <div class="kpi-card" style="--card-accent: #0284c7;">
          <div class="kpi-card-header"><span class="kpi-title">AVLAGTE STUDIEPOENGEKVIVALENTER</span></div>
          <div class="kpi-val">3 153 SPE60</div>
          <div class="kpi-sub">Total studiepoengproduksjon</div>
        </div>
        <div class="kpi-card" style="--card-accent: #f59e0b;">
          <div class="kpi-card-header"><span class="kpi-title">LÆRERTETTHET (STUD / UF-ÅV)</span></div>
          <div class="kpi-val">22,3</div>
          <div class="kpi-sub">Gjennomsnittlig studenttetthet</div>
        </div>
        <div class="kpi-card" style="--card-accent: #10b981;">
          <div class="kpi-card-header"><span class="kpi-title">BEREGNET KD KATEGORI 1 INNTEKT</span></div>
          <div class="kpi-val">171,99 MNOK</div>
          <div class="kpi-sub">Sats: 54 550 kr per SPE60</div>
        </div>
      </div>

      <div class="charts-grid-half">
        <div class="panel-card">
          <div class="panel-header">
            <h3 class="panel-title">Studiepoengproduksjon (SPE60) per Studieprogram: 2025 Grunnlag vs Mål</h3>
            <span class="panel-meta">Kategori 1 finansieringsgrunnlag</span>
          </div>
          <div class="chart-box" id="chart-p5-spe"></div>
        </div>

        <div class="panel-card">
          <div class="panel-header">
            <h3 class="panel-title">Lærertetthet (Studenter per UF-årsverk)</h3>
            <span class="panel-meta">Kapasitetsbelastning per studieprogram</span>
          </div>
          <div class="chart-box" id="chart-p5-ratio"></div>
        </div>
      </div>

      <div class="panel-card">
        <div class="panel-header">
          <h3 class="panel-title">Utdannings- og Studiepoengmodell: Kategori 1 Satser, 2-års Etterslep og Lærertetthet</h3>
          <span class="panel-meta">Kunnskapsdepartementets finansieringsmodell</span>
        </div>
        <div class="table-container">
          <table class="tufte-table" id="table-p5-students">
            <thead>
              <tr>
                <th onclick="sortTable('table-p5-students', 0)">Studieprogram</th>
                <th onclick="sortTable('table-p5-students', 1)">Tilhørende Institutt</th>
                <th>KD Kategori</th>
                <th class="num" onclick="sortTable('table-p5-students', 3, true)">Registrerte Studenter</th>
                <th class="num" onclick="sortTable('table-p5-students', 4, true)">2025 Grunnlag (SPE60)</th>
                <th class="num" onclick="sortTable('table-p5-students', 5, true)">Mål 2026 (SPE60)</th>
                <th class="num" onclick="sortTable('table-p5-students', 6, true)">KD Sats (kr)</th>
                <th class="num" onclick="sortTable('table-p5-students', 7, true)">Beregnet KD Inntekt (kr)</th>
                <th class="num" onclick="sortTable('table-p5-students', 8, true)">Stud/UF-ÅV</th>
              </tr>
            </thead>
            <tbody id="tbody-p5-students"></tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ========================================================================= -->
    <!-- TAB 8: BUDSJETT 2027 PLANRAPPORT (2027 Plan Report Sheet)                 -->
    <!-- ========================================================================= -->
    <section id="p8_budget2027" class="page-section">
      <div class="kpi-grid">
        <div class="kpi-card" style="--card-accent: #ef4444;">
          <div class="kpi-card-header"><span class="kpi-title">BUD2027 INNTEKTER</span><span class="kpi-badge badge-red">🔴 -2,0M Gap</span></div>
          <div class="kpi-val text-red">286,07 MNOK</div>
          <div class="kpi-sub">Dokumentert ramme: 288,07 MNOK</div>
        </div>
        <div class="kpi-card" style="--card-accent: #334155;">
          <div class="kpi-card-header"><span class="kpi-title">BUD2027 KOSTNADER</span><span class="kpi-badge badge-neutral">Plan</span></div>
          <div class="kpi-val">282,00 MNOK</div>
          <div class="kpi-sub">Planlagte driftskostnader 2027</div>
        </div>
        <div class="kpi-card" style="--card-accent: #f59e0b;">
          <div class="kpi-card-header"><span class="kpi-title">NETTO DRIFTSRESULTAT</span><span class="kpi-badge badge-amber">🟡 Under mål</span></div>
          <div class="kpi-val text-amber">+4,07 MNOK</div>
          <div class="kpi-sub">Mål Note 15: +6,07 MNOK (Differanse: -2,0 MNOK)</div>
        </div>
        <div class="kpi-card" style="--card-accent: #ef4444;">
          <div class="kpi-card-header"><span class="kpi-title">LØNNSANDEL 2027 %</span><span class="kpi-badge badge-red">🔴 66,8%</span></div>
          <div class="kpi-val text-red">66,8%</div>
          <div class="kpi-sub">Mål: &lt; 64,5% (+2,27 pp over mål)</div>
        </div>
        <div class="kpi-card" style="--card-accent: #0284c7;">
          <div class="kpi-card-header"><span class="kpi-title">STUDENTER 2027</span></div>
          <div class="kpi-val">3 450 Stud.</div>
          <div class="kpi-sub">3 153 SPE60 | 22,3 stud./UF</div>
        </div>
      </div>

      <!-- Beslutningsstøtte 2027 Card -->
      <div class="callout-box alert-red">
        <div class="callout-title">⚠️ STRATEGISK BESLUTNINGSSTØTTE 2027</div>
        <div class="callout-text">
          <strong>1.</strong> Avklar manglende 2,0 MNOK inntekt før budsjettet publiseres.<br>
          <strong>2.</strong> Konto-basert lønnsandel er 66,8 %, over mål 64,5 %; avstem mot FTE-filens 63,9 %.<br>
          <strong>3.</strong> Beskytt tiltak T003/T004: 3,2 MNOK inntektsvekst fra EVU og BOA er nødvendig for handlingsrommet.<br>
          <strong>4.</strong> K13000 bærer 45 % av inntektene og krever tett prosjekt- og kapasitetsstyring.
        </div>
      </div>

      <div class="charts-grid-half">
        <div class="panel-card">
          <div class="panel-header">
            <h3 class="panel-title">Økonomi og Kapasitet per Enhet 2027 (MNOK og Årsverk)</h3>
            <span class="panel-meta">Enhetsfordeling</span>
          </div>
          <div class="table-container">
            <table class="tufte-table" id="table-p27-units">
              <thead>
                <tr>
                  <th>Enhet</th>
                  <th class="num">Inntekter</th>
                  <th class="num">Kostnader</th>
                  <th class="num">Netto</th>
                  <th class="num">Totalt ÅV</th>
                  <th class="num">UF-ÅV</th>
                  <th class="num">Stud.</th>
                  <th class="num">SPE60</th>
                </tr>
              </thead>
              <tbody id="tbody-p27-units"></tbody>
            </table>
          </div>
        </div>

        <div class="panel-card">
          <div class="panel-header">
            <h3 class="panel-title">Omstillingstiltak 2027 (Planlagt Inntekt & Kostnadskutt)</h3>
            <span class="panel-meta">T001–T004</span>
          </div>
          <div class="table-container">
            <table class="tufte-table" id="table-p27-actions">
              <thead>
                <tr>
                  <th>Tiltak</th>
                  <th>Enhet</th>
                  <th class="num">Effekt (NOK)</th>
                  <th>Status</th>
                  <th>Beslutningsdriver</th>
                </tr>
              </thead>
              <tbody id="tbody-p27-actions"></tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="panel-card">
        <div class="panel-header">
          <h3 class="panel-title">Periodisert Budsjett 2027 per Måned, Konto og Enhet (M01–M12)</h3>
          <span class="panel-meta">Detaljert budsjetttransaksjonslogg</span>
        </div>
        <div class="table-container">
          <table class="tufte-table" id="table-p7-budget">
            <thead>
              <tr>
                <th onclick="sortTable('table-p7-budget', 0)">Måned</th>
                <th onclick="sortTable('table-p7-budget', 1)">Enhet</th>
                <th onclick="sortTable('table-p7-budget', 2, true)">Konto</th>
                <th onclick="sortTable('table-p7-budget', 3)">Kontonavn</th>
                <th onclick="sortTable('table-p7-budget', 4)">SRS Regnskapslinje</th>
                <th class="num" onclick="sortTable('table-p7-budget', 5, true)">Budsjettbeløp (NOK)</th>
                <th>Kommentar</th>
              </tr>
            </thead>
            <tbody id="tbody-p7-budget"></tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ========================================================================= -->
    <!-- TAB 9: BUDSJETTPROSESS 2027 & LUKKEPLAN (Budget Process 2027 Sheet)         -->
    <!-- ========================================================================= -->
    <section id="p9_process" class="page-section">
      <!-- 6 Decision Gates Roadmap -->
      <div class="panel-card">
        <div class="panel-header">
          <h3 class="panel-title">De 6 Beslutningsportene i Budsjettprosessen (Driverbasert Styringsmodell)</h3>
          <span class="panel-meta">Port 5 Status: 🔴 Ikke klar (Utsett frys til avstemming er signert)</span>
        </div>
        <div class="gate-pipeline" id="gate-pipeline-container"></div>
      </div>

      <div class="callout-box alert-amber">
        <div class="callout-title">📋 SAMLET PROSESSANALYSE OG ANBEFALING</div>
        <div class="callout-text">
          Budsjettprosessen er riktig bygget som en driverbasert styringsprosess: ekstern ramme og SPE60-etterslep oversettes til inntekter, bemanning og aktivitet; instituttplanene konsolideres; risiko og langtidsvirkning testes; deretter godkjennes og låses baseline før månedlig oppfølging. Dagens modell er likevel <strong>ikke klar for endelig systemfrys</strong>. Inntektsrammen er 2,0 MNOK lavere enn dokumentert mål, og konto-basert lønnsandel på 66,8 % avviker fra både målet på 64,5 % og FTE-filens 63,9 %. <strong>Anbefalingen er å stoppe ved beslutningsport 5 til disse forholdene er signert avklart.</strong> Deretter bør BUD2027 låses sammen med investeringsplan, tiltakseiere og månedlig RAG-rapportering.
        </div>
      </div>

      <!-- Seksjon 1: Beslutningsportene Tabell -->
      <div class="panel-card">
        <div class="panel-header">
          <h3 class="panel-title">1. Beslutningsporter — Milepæler, Ansvar og Kriterier</h3>
          <span class="panel-meta">Gjennomgang av fase 1 til 6</span>
        </div>
        <div class="table-container">
          <table class="tufte-table" id="table-gates">
            <thead>
              <tr>
                <th>Port</th>
                <th>Periode</th>
                <th>Kjernespørsmål</th>
                <th>Hovedaktivitet</th>
                <th>Ansvarlig</th>
                <th>Leveranse</th>
                <th>Beslutningsarena</th>
                <th>Status</th>
                <th>Frist</th>
              </tr>
            </thead>
            <tbody id="tbody-gates"></tbody>
          </table>
        </div>
      </div>

      <!-- Seksjon 2: Driveranalyse og Avstemming -->
      <div class="panel-card">
        <div class="panel-header">
          <h3 class="panel-title">2. Driveranalyse og Modellavstemming</h3>
          <span class="panel-meta">Finansieringsmekanismer og risikokontroll</span>
        </div>
        <div class="table-container">
          <table class="tufte-table" id="table-driver-analysis">
            <thead>
              <tr>
                <th>Driver</th>
                <th>Mekanisme</th>
                <th>Kvantifisering</th>
                <th>Budsjetteffekt</th>
                <th>Risiko</th>
                <th>Kontroll</th>
                <th>Eier</th>
                <th>Avstemming</th>
                <th class="num">Modellverdi</th>
                <th class="num">Referanse</th>
                <th class="num">Differanse</th>
                <th>Konklusjon</th>
              </tr>
            </thead>
            <tbody id="tbody-driver-analysis"></tbody>
          </table>
        </div>
      </div>

      <!-- Seksjon 4: Prioritert Lukkeplan -->
      <div class="panel-card">
        <div class="panel-header">
          <h3 class="panel-title">3. Prioritert Lukkeplan før Systemfrys (UBW-låsing)</h3>
          <span class="panel-meta">Handlinger for å oppnå godkjenning ved Beslutningsport 5</span>
        </div>
        <div class="table-container">
          <table class="tufte-table" id="table-closure-plan">
            <thead>
              <tr>
                <th>Prio</th>
                <th>Avvik / Risiko</th>
                <th>Påkrevd Handling</th>
                <th>Eier</th>
                <th>Frist</th>
                <th>Bevis / Ferdigkriterium</th>
                <th>Konsekvens hvis ikke lukket</th>
                <th>RAG</th>
              </tr>
            </thead>
            <tbody id="tbody-closure-plan"></tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ========================================================================= -->
    <!-- TAB 10: PROGNOSEMETODIKK 2027 (Forecast Methods 2027 Sheet)                -->
    <!-- ========================================================================= -->
    <section id="p10_methods" class="page-section">
      <!-- Method Architecture Banner -->
      <div class="callout-box alert-green">
        <div class="callout-title">📐 STANDARD PROGNOSEFORMEL & PRINSIPP</div>
        <div class="callout-text">
          <strong>Actual YTD</strong> (Låst regnskap hittil i året) + <strong>ETC</strong> (Prognose for resterende måneder basert på drivere) = <strong>EAC / Latest Estimate</strong> (Ny forventet helårsverdi).<br>
          <em>Sluttavvik (VAC) = BUD2027 − EAC.</em> Positivt tall er gunstig for kostnader (mindreforbruk). RAG: Grønn &ge; 0 %; Gul 0 til -5 %; Rød &lt; -5 %.
        </div>
      </div>

      <div class="panel-card">
        <div class="panel-header">
          <h3 class="panel-title">1. Prognosemetodikk for hver Budsjettpost (11 Poster)</h3>
          <span class="panel-meta">Metode, inputdrivere, operativ beregning og oppdateringsfrekvens</span>
        </div>
        <div class="table-container">
          <table class="tufte-table" id="table-forecast-posts">
            <thead>
              <tr>
                <th>Prio</th>
                <th>Budsjettpost</th>
                <th>Konto / Tabell</th>
                <th class="num">2027 Baseline</th>
                <th>Prognosemetode</th>
                <th>Driver / Input</th>
                <th>Operativ Beregning</th>
                <th>Oppdatering</th>
              </tr>
            </thead>
            <tbody id="tbody-forecast-posts"></tbody>
          </table>
        </div>
      </div>

      <div class="panel-card">
        <div class="panel-header">
          <h3 class="panel-title">2. Månedlig Rapporteringsrutine og Årshjul (Dag 1–10)</h3>
          <span class="panel-meta">Arbeidsprosess fra periodelukking til publisering</span>
        </div>
        <div class="table-container">
          <table class="tufte-table" id="table-routine-steps">
            <thead>
              <tr>
                <th>Trinn</th>
                <th>Formel / Metode</th>
                <th>Forklaring</th>
                <th>Kontrollaktivitet</th>
                <th>Månedlig Tidslinje</th>
              </tr>
            </thead>
            <tbody id="tbody-routine-steps"></tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ========================================================================= -->
    <!-- TAB 11: DATAMODELL & KVALITETSKONTROLL (Model Guide Sheet)                 -->
    <!-- ========================================================================= -->
    <section id="p11_modelguide" class="page-section">
      <div class="kpi-grid">
        <div class="kpi-card" style="--card-accent: #10b981;">
          <div class="kpi-card-header"><span class="kpi-title">KILDETABELLER</span></div>
          <div class="kpi-val">16 Tabeller</div>
          <div class="kpi-sub">1 448 datarader importert</div>
        </div>
        <div class="kpi-card" style="--card-accent: #0284c7;">
          <div class="kpi-card-header"><span class="kpi-title">RELASJONER</span></div>
          <div class="kpi-val">22 Relasjoner</div>
          <div class="kpi-sub">11 kilde + 11 modellkompletteringer</div>
        </div>
        <div class="kpi-card" style="--card-accent: #10b981;">
          <div class="kpi-card-header"><span class="kpi-title">DAX-MÅL</span></div>
          <div class="kpi-val">36 Mål</div>
          <div class="kpi-sub">100% validert mot kildekolonner</div>
        </div>
        <div class="kpi-card" style="--card-accent: #ef4444;">
          <div class="kpi-card-header"><span class="kpi-title">INNTEKTSGAP 2027</span><span class="kpi-badge badge-red">Obs</span></div>
          <div class="kpi-val text-red">-2,0 MNOK</div>
          <div class="kpi-sub">286,07 MNOK vs. 288,07 MNOK ramme</div>
        </div>
      </div>

      <div class="callout-box alert-red">
        <div class="callout-title">⚠️ VIKTIG DATAKVALITETSFUNN (2027 Inntektsgap)</div>
        <div class="callout-text">
          <strong>Funn:</strong> FactBudget_2027 summerer til <strong>286 069 999,8 kr</strong>, mens dokumentert ramme i budsjettnotatet er <strong>288 070 000,0 kr</strong> (differanse: <strong>-2 000 000,2 kr</strong>).<br>
          <strong>Konsekvens:</strong> Netto driftsresultat blir <strong>4,07 MNOK</strong>, ikke 6,07 MNOK som forutsatt.<br>
          <strong>Anbefaling:</strong> Avklar manglende 2,0 MNOK inntektslinje med sentral økonomi før formell systemfrys ved Port 5.
        </div>
      </div>

      <div class="panel-card">
        <div class="panel-header">
          <h3 class="panel-title">Oversikt over Semantisk Modell: Tabeller, Rader og Status</h3>
          <span class="panel-meta">Power BI TMDL / Fabric definisjon</span>
        </div>
        <div class="table-container">
          <table class="tufte-table">
            <thead>
              <tr>
                <th>Tabellnavn</th>
                <th class="num">Datarader</th>
                <th>Type</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr><td><strong>DimAccountHierarchy</strong></td><td class="num">16</td><td>Dimensjon</td><td><span class="badge-rag badge-green">Importert</span></td></tr>
              <tr><td><strong>DimDate</strong></td><td class="num">12</td><td>Tidsdimensjon (2026)</td><td><span class="badge-rag badge-green">Importert</span></td></tr>
              <tr><td><strong>DimDate_2027</strong></td><td class="num">12</td><td>Tidsdimensjon (2027)</td><td><span class="badge-rag badge-green">Importert</span></td></tr>
              <tr><td><strong>DimForecastVersion</strong></td><td class="num">4</td><td>Versjonsdimensjon</td><td><span class="badge-rag badge-green">Importert</span></td></tr>
              <tr><td><strong>DimOrganization</strong></td><td class="num">4</td><td>Organisasjon / Enhet</td><td><span class="badge-rag badge-green">Importert</span></td></tr>
              <tr><td><strong>FactAction</strong></td><td class="num">4</td><td>Tiltakssporing 2026</td><td><span class="badge-rag badge-green">Importert</span></td></tr>
              <tr><td><strong>FactAction_2027</strong></td><td class="num">4</td><td>Tiltaksplan 2027</td><td><span class="badge-rag badge-green">Importert</span></td></tr>
              <tr><td><strong>FactBudget</strong></td><td class="num">432</td><td>Årsbudsjett 2026 (BAC)</td><td><span class="badge-rag badge-green">Importert</span></td></tr>
              <tr><td><strong>FactBudget_2027</strong></td><td class="num">384</td><td>Periodisert Budsjett 2027</td><td><span class="badge-rag badge-green">Importert</span></td></tr>
              <tr><td><strong>FactEVM</strong></td><td class="num">12</td><td>EVM Månedslogg 2026</td><td><span class="badge-rag badge-green">Importert</span></td></tr>
              <tr><td><strong>FactFTE</strong></td><td class="num">48</td><td>Årsverk & Vakanser 2026</td><td><span class="badge-rag badge-green">Importert</span></td></tr>
              <tr><td><strong>FactFTE_2027</strong></td><td class="num">48</td><td>Bemanningsplan 2027</td><td><span class="badge-rag badge-green">Importert</span></td></tr>
              <tr><td><strong>FactGL</strong></td><td class="num">433</td><td>Hovedbok (Actual YTD + FC)</td><td><span class="badge-rag badge-green">Importert</span></td></tr>
              <tr><td><strong>FactStudents</strong></td><td class="num">12</td><td>Studieproduksjon & SPE60</td><td><span class="badge-rag badge-green">Importert</span></td></tr>
              <tr><td><strong>FactStudents_2027</strong></td><td class="num">12</td><td>Studieproduksjon 2027</td><td><span class="badge-rag badge-green">Importert</span></td></tr>
              <tr><td><strong>_Measures</strong></td><td class="num">36</td><td>DAX Beregninger</td><td><span class="badge-rag badge-green">Validert</span></td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

  </main>

  <script>
    const DATA = """ + json_data + """;

    const state = {
      activeTab: 'p1_summary',
      year: '2026',
      month: 'ALL',
      org: 'ALL',
      accountType: 'ALL'
    };

    function fmtNum(val, decimals = 0) {
      if (val === null || val === undefined || isNaN(val)) return '—';
      return Number(val).toLocaleString('no-NO', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
      });
    }

    function fmtMNOK(val, decimals = 1) {
      if (val === null || val === undefined || isNaN(val)) return '—';
      return fmtNum(val / 1000000, decimals) + ' MNOK';
    }

    function fmtPct(val, decimals = 1) {
      if (val === null || val === undefined || isNaN(val)) return '—';
      return fmtNum(val * 100, decimals) + '%';
    }

    function switchTab(tabId) {
      state.activeTab = tabId;
      document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
      document.querySelectorAll('.page-section').forEach(sec => sec.classList.remove('active'));

      const activeBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(tabId));
      if (activeBtn) activeBtn.classList.add('active');

      const sec = document.getElementById(tabId);
      if (sec) sec.classList.add('active');

      renderActiveTab();
    }

    function applyGlobalFilters() {
      state.year = document.getElementById('slicer-year').value;
      state.month = document.getElementById('slicer-month').value;
      state.org = document.getElementById('slicer-org').value;
      state.accountType = document.getElementById('slicer-account').value;

      renderActiveTab();
    }

    function resetFilters() {
      document.getElementById('slicer-year').value = '2026';
      document.getElementById('slicer-month').value = 'ALL';
      document.getElementById('slicer-org').value = 'ALL';
      document.getElementById('slicer-account').value = 'ALL';
      applyGlobalFilters();
    }

    const tooltip = document.getElementById('chart-tooltip');
    function showTooltip(evt, text) {
      tooltip.innerHTML = text;
      tooltip.style.opacity = 1;
      const rect = evt.target.getBoundingClientRect();
      tooltip.style.left = (window.scrollX + rect.left + rect.width / 2) + 'px';
      tooltip.style.top = (window.scrollY + rect.top - 32) + 'px';
    }
    function hideTooltip() { tooltip.style.opacity = 0; }

    window.addEventListener('DOMContentLoaded', () => {
      renderAllTabs();
    });

    function renderAllTabs() {
      renderPage1();
      renderPage2();
      renderPage3();
      renderPage4();
      renderPage5();
      renderPage6();
      renderPage7();
      renderPage8();
      renderPage9();
      renderPage10();
    }

    function renderActiveTab() {
      if (state.activeTab === 'p1_summary') renderPage1();
      else if (state.activeTab === 'p2_institutter') renderPage2();
      else if (state.activeTab === 'p3_variance') renderPage3();
      else if (state.activeTab === 'p4_actionplan') renderPage4();
      else if (state.activeTab === 'p5_staffing') renderPage5();
      else if (state.activeTab === 'p6_evm') renderPage6();
      else if (state.activeTab === 'p7_students') renderPage7();
      else if (state.activeTab === 'p8_budget2027') renderPage8();
      else if (state.activeTab === 'p9_process') renderPage9();
      else if (state.activeTab === 'p10_methods') renderPage10();
    }

    // =========================================================================
    // PAGE 1: LEDELSESSAMMENDRAG 2026
    // =========================================================================
    function renderPage1() {
      let filteredGL = DATA.gl26;
      let filteredBudget = DATA.budget26;

      if (state.org !== 'ALL') {
        filteredGL = filteredGL.filter(r => r.OrgKode === state.org);
        filteredBudget = filteredBudget.filter(r => r.OrgKode === state.org);
      }
      if (state.accountType !== 'ALL') {
        const accMap = new Map(DATA.accounts.map(a => [a.Konto, a.Nivaa1_Navn]));
        filteredGL = filteredGL.filter(r => accMap.get(r.Konto) === state.accountType);
        filteredBudget = filteredBudget.filter(r => accMap.get(r.Konto) === state.accountType);
      }

      const totalBudget = filteredBudget.reduce((sum, r) => sum + (r.BudsjettBelop || 0), 0);
      const actualYTD = filteredGL.filter(r => r.Bokforingstype === 'Actual').reduce((sum, r) => sum + (r.Belop_signert || 0), 0);
      const forecastQ4 = filteredGL.filter(r => r.Bokforingstype === 'Forecast').reduce((sum, r) => sum + (r.Belop_signert || 0), 0);
      const totalEAC = actualYTD + forecastQ4;
      const sluttavvikVAC = totalBudget - totalEAC;
      const vacPct = totalBudget > 0 ? (sluttavvikVAC / totalBudget) : 0;

      document.getElementById('p1-kpi-rev').innerText = fmtMNOK(totalEAC, 1);
      const vacSign = sluttavvikVAC >= 0 ? '+' : '';
      document.getElementById('p1-kpi-vac').innerText = vacSign + fmtNum(sluttavvikVAC / 1000000, 1) + ' MNOK';
      document.getElementById('p1-kpi-vac').style.color = sluttavvikVAC >= 0 ? 'var(--rag-green)' : 'var(--rag-red)';
      document.getElementById('p1-kpi-vac-sub').innerText = fmtNum(sluttavvikVAC) + ' kr under budsjett (' + fmtPct(vacPct) + ')';

      const vacBadge = document.getElementById('p1-vac-badge');
      if (sluttavvikVAC >= 0) {
        vacBadge.className = 'kpi-badge badge-green';
        vacBadge.innerText = '🟢 Mindreforbruk';
      } else if (vacPct >= -0.05) {
        vacBadge.className = 'kpi-badge badge-amber';
        vacBadge.innerText = '🟡 Moderat avvik';
      } else {
        vacBadge.className = 'kpi-badge badge-red';
        vacBadge.innerText = '🔴 Merforbruk';
      }

      renderP1MonthlyChart(filteredGL, filteredBudget);
      renderP1VarianceChart();
      renderP1MatrixTable();
    }

    function renderP1MonthlyChart(glRows, budgetRows) {
      const container = document.getElementById('chart-p1-monthly');
      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Des'];

      const monthlyActual = new Array(12).fill(0);
      const monthlyForecast = new Array(12).fill(0);
      const monthlyBudget = new Array(12).fill(0);

      glRows.forEach(r => {
        const m = (r.DatoNokkel % 100) - 1;
        if (m >= 0 && m < 12) {
          if (r.Bokforingstype === 'Actual') monthlyActual[m] += r.Belop_signert;
          else monthlyForecast[m] += r.Belop_signert;
        }
      });

      budgetRows.forEach(r => {
        const m = (r.DatoNokkel % 100) - 1;
        if (m >= 0 && m < 12) {
          monthlyBudget[m] += r.BudsjettBelop;
        }
      });

      const width = 640;
      const height = 240;
      const padL = 45;
      const padR = 25;
      const padT = 20;
      const padB = 35;

      const maxVal = Math.max(
        ...monthlyActual.map((a, i) => a + monthlyForecast[i]),
        ...monthlyBudget,
        12000000
      ) * 1.15;

      const innerW = width - padL - padR;
      const innerH = height - padT - padB;
      const colW = innerW / 12;
      const barW = colW * 0.65;

      let svg = `<svg class="tufte-chart" viewBox="0 0 ${width} ${height}">`;
      for (let i = 0; i <= 4; i++) {
        const yVal = (maxVal / 4) * i;
        const yPos = padT + innerH - (yVal / maxVal) * innerH;
        svg += `<line x1="${padL}" y1="${yPos}" x2="${width - padR}" y2="${yPos}" stroke="#f1f5f9" stroke-width="1" />`;
        svg += `<text x="${padL - 6}" y="${yPos + 3}" text-anchor="end" font-size="9" fill="#94a3b8">${(yVal / 1000000).toFixed(1)}M</text>`;
      }

      const cutoffX = padL + colW * 9;
      svg += `<line x1="${cutoffX}" y1="${padT}" x2="${cutoffX}" y2="${padT + innerH}" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="3,3" />`;
      svg += `<text x="${cutoffX - 4}" y="${padT + 12}" text-anchor="end" font-size="9" fill="#b45309" font-weight="600">T3 Cutoff</text>`;

      for (let m = 0; m < 12; m++) {
        const x = padL + m * colW + (colW - barW) / 2;
        const actH = (monthlyActual[m] / maxVal) * innerH;
        const fcH = (monthlyForecast[m] / maxVal) * innerH;
        const budVal = monthlyBudget[m];

        if (monthlyActual[m] > 0) {
          const y = padT + innerH - actH;
          svg += `<rect x="${x}" y="${y}" width="${barW}" height="${actH}" fill="#1e293b" rx="2" 
                    onmouseover="showTooltip(event, '${months[m]}: Faktisk ' + fmtNum(${monthlyActual[m]}) + ' kr (Budsjett: ' + fmtNum(${budVal}) + ' kr)')" 
                    onmouseout="hideTooltip()" />`;
        }
        if (monthlyForecast[m] > 0) {
          const y = padT + innerH - actH - fcH;
          svg += `<rect x="${x}" y="${y}" width="${barW}" height="${fcH}" fill="#94a3b8" rx="2"
                    onmouseover="showTooltip(event, '${months[m]}: Q4 Prognose ' + fmtNum(${monthlyForecast[m]}) + ' kr (Budsjett: ' + fmtNum(${budVal}) + ' kr)')" 
                    onmouseout="hideTooltip()" />`;
        }
        svg += `<text x="${x + barW / 2}" y="${padT + innerH + 16}" text-anchor="middle" font-size="10" fill="#64748b">${months[m]}</text>`;
      }

      let linePts = [];
      for (let m = 0; m < 12; m++) {
        const x = padL + m * colW + colW / 2;
        const y = padT + innerH - (monthlyBudget[m] / maxVal) * innerH;
        linePts.push(`${x},${y}`);
      }
      svg += `<polyline points="${linePts.join(' ')}" fill="none" stroke="#ef4444" stroke-width="1.8" stroke-dasharray="4,3" />`;

      svg += `
        <g transform="translate(${padL + 10}, ${padT + 4})">
          <rect x="0" y="0" width="10" height="10" fill="#1e293b" rx="2" />
          <text x="14" y="9" font-size="10" fill="#1e293b">M01–M09 Faktisk</text>
          <rect x="110" y="0" width="10" height="10" fill="#94a3b8" rx="2" />
          <text x="124" y="9" font-size="10" fill="#64748b">M10–M12 Prognose</text>
          <line x1="230" y1="5" x2="245" y2="5" stroke="#ef4444" stroke-width="2" stroke-dasharray="3,2" />
          <text x="250" y="9" font-size="10" fill="#ef4444">Periodisert Budsjett</text>
        </g>
      `;
      svg += `</svg>`;
      container.innerHTML = svg;
    }

    function renderP1VarianceChart() {
      const container = document.getElementById('chart-p1-variance');
      const width = 420;
      const height = 240;
      const padL = 120;
      const padR = 60;
      const padT = 30;
      const padB = 25;

      const orgData = [
        { code: 'K10000', name: 'Admin & Felles', vac: 87499, budget: 14000000 },
        { code: 'K11000', name: 'Ledelse & Innovasjon', vac: -3496, budget: 38500000 },
        { code: 'K12000', name: 'Rettsvitenskap', vac: 1148940, budget: 29250000 },
        { code: 'K13000', name: 'Økonomi', vac: -710685, budget: 48403825 }
      ];

      const maxAbs = 1400000;
      const innerW = width - padL - padR;
      const innerH = height - padT - padB;
      const rowH = innerH / orgData.length;
      const zeroX = padL + innerW / 2;

      let svg = `<svg class="tufte-chart" viewBox="0 0 ${width} ${height}">`;
      svg += `<line x1="${zeroX}" y1="${padT}" x2="${zeroX}" y2="${padT + innerH}" stroke="#cbd5e1" stroke-width="1.5" />`;
      svg += `<text x="${zeroX}" y="${padT - 8}" text-anchor="middle" font-size="9" fill="#94a3b8">Nullpunkt (Budsjett)</text>`;

      orgData.forEach((d, idx) => {
        const y = padT + idx * rowH + (rowH - 20) / 2;
        const barLen = Math.abs(d.vac) / maxAbs * (innerW / 2);
        const isPos = d.vac >= 0;
        const color = isPos ? '#10b981' : '#ef4444';
        const barX = isPos ? zeroX : (zeroX - barLen);

        svg += `<text x="${padL - 8}" y="${y + 14}" text-anchor="end" font-size="11" fill="#1e293b" font-weight="500">${d.name}</text>`;
        svg += `<rect x="${barX}" y="${y}" width="${barLen}" height="20" fill="${color}" rx="3" 
                  onmouseover="showTooltip(event, '${d.name} (${d.code})<br>Sluttavvik: ' + fmtNum(${d.vac}) + ' kr<br>Budsjett: ' + fmtNum(${d.budget}) + ' kr')"
                  onmouseout="hideTooltip()" />`;

        const labelX = isPos ? (zeroX + barLen + 6) : (zeroX - barLen - 6);
        const anchor = isPos ? 'start' : 'end';
        const sign = isPos ? '+' : '';
        svg += `<text x="${labelX}" y="${y + 14}" text-anchor="${anchor}" font-size="10" font-weight="600" fill="${color}">${sign}${(d.vac / 1000).toFixed(0)}k</text>`;
      });

      svg += `</svg>`;
      container.innerHTML = svg;
    }

    function renderP1MatrixTable() {
      const tbody = document.getElementById('tbody-p1-matrix');
      const rows = [
        {
          code: 'K10000', name: 'HHU Fakultetsadministrasjon & Felles', budget: 14000000,
          lonn: 8645000, drift: 5267501, vac: 87499, uf: 0, ratio: 0.0,
          rag: '🟢 Planmessig', ragClass: 'badge-green',
          diagnose: 'T001 administrativ ansettelsesstopp gjennomført. AACSB akkrediteringskostnad dekkes. Ramme 14,0 MNOK.'
        },
        {
          code: 'K11000', name: 'Institutt for ledelse og innovasjon', budget: 38500000,
          lonn: 31200000, drift: 7303496, vac: -3496, uf: 41, ratio: 25.6,
          rag: '🟢 Planmessig', ragClass: 'badge-green',
          diagnose: 'Høy SPE-produksjon. KD Kat 1 sats opprettholdes. T003 EVU-ekspansjon og prosjektkontroll pågår. Ramme 38,5 MNOK.'
        },
        {
          code: 'K12000', name: 'Institutt for rettsvitenskap', budget: 29250000,
          lonn: 23450000, drift: 4651060, vac: 1148940, uf: 35, ratio: 22.4,
          rag: '🟢 Planmessig', ragClass: 'badge-green',
          diagnose: 'Stabil drift. T004 midlertidig vakanshold gir 1,15 MNOK mindreforbruk. Ramme 29,25 MNOK.'
        },
        {
          code: 'K13000', name: 'Institutt for økonomi', budget: 48403825,
          lonn: 43800917, drift: 5313593, vac: -710685, uf: 61, ratio: 21.6,
          rag: '🟡 Moderat avvik', ragClass: 'badge-amber',
          diagnose: 'Høy studenttetthet (21,6 stud/UF). T002 overføring av vitenskapelig tid til BOA frikjøp (NFR/EU) pågår for å hente inn avvik.'
        }
      ];

      let filteredRows = rows;
      if (state.org !== 'ALL') {
        filteredRows = rows.filter(r => r.code === state.org);
      }

      let html = '';
      let totBudget = 0, totLonn = 0, totDrift = 0, totVac = 0, totUf = 0;

      filteredRows.forEach(r => {
        totBudget += r.budget;
        totLonn += r.lonn;
        totDrift += r.drift;
        totVac += r.vac;
        totUf += r.uf;

        const vacColor = r.vac >= 0 ? 'text-green' : 'text-red';
        const vacSign = r.vac >= 0 ? '+' : '';

        html += `
          <tr>
            <td><strong>${r.code}</strong></td>
            <td>${r.name}</td>
            <td class="num">${fmtNum(r.budget / 1000000, 2)}</td>
            <td class="num">${fmtNum(r.lonn / 1000000, 2)}</td>
            <td class="num">${fmtNum(r.drift / 1000000, 2)}</td>
            <td class="num ${vacColor}"><strong>${vacSign}${fmtNum(r.vac / 1000000, 2)}</strong></td>
            <td class="num">${r.uf}</td>
            <td class="num">${r.ratio > 0 ? r.ratio.toFixed(1) : '—'}</td>
            <td><span class="badge-rag ${r.ragClass}">${r.rag}</span></td>
            <td style="white-space: normal; max-width: 380px;">${r.diagnose}</td>
          </tr>
        `;
      });

      if (filteredRows.length > 1) {
        const avgRatio = (3450 / totUf).toFixed(1);
        html += `
          <tr class="total-row">
            <td>TOTAL</td>
            <td>Handelshøyskolen ved UiA (HHU) Samlet</td>
            <td class="num">${fmtNum(totBudget / 1000000, 2)}</td>
            <td class="num">${fmtNum(totLonn / 1000000, 2)}</td>
            <td class="num">${fmtNum(totDrift / 1000000, 2)}</td>
            <td class="num text-green">+${fmtNum(totVac / 1000000, 2)}</td>
            <td class="num">${totUf}</td>
            <td class="num">${avgRatio}</td>
            <td><span class="badge-rag badge-green">🟢 Balansert</span></td>
            <td style="white-space: normal;">Samlet vedtatt ramme 130,15 MNOK med kontrollert lønnsandel og solid måloppnåelse.</td>
          </tr>
        `;
      }
      tbody.innerHTML = html;
    }

    // =========================================================================
    // PAGE 2: ENHETS- & KONTOOPPFØLGING
    // =========================================================================
    function renderPage2() {
      const tbody = document.getElementById('tbody-p2-accounts');
      const accMap = new Map();

      DATA.accounts.forEach(a => {
        accMap.set(a.Konto, {
          konto: a.Konto, navn: a.Kontonavn, gruppe: a.Nivaa1_Navn, srs: a.SRS_regnskapslinje,
          bac: 0, ytd: 0, q4: 0
        });
      });

      let bRows = DATA.budget26;
      let glRows = DATA.gl26;
      if (state.org !== 'ALL') {
        bRows = bRows.filter(r => r.OrgKode === state.org);
        glRows = glRows.filter(r => r.OrgKode === state.org);
      }
      if (state.accountType !== 'ALL') {
        const typeMap = new Map(DATA.accounts.map(a => [a.Konto, a.Nivaa1_Navn]));
        bRows = bRows.filter(r => typeMap.get(r.Konto) === state.accountType);
        glRows = glRows.filter(r => typeMap.get(r.Konto) === state.accountType);
      }

      bRows.forEach(r => {
        if (accMap.has(r.Konto)) accMap.get(r.Konto).bac += r.BudsjettBelop;
      });

      glRows.forEach(r => {
        if (accMap.has(r.Konto)) {
          if (r.Bokforingstype === 'Actual') accMap.get(r.Konto).ytd += r.Belop_signert;
          else accMap.get(r.Konto).q4 += r.Belop_signert;
        }
      });

      let html = '';
      let totBAC = 0, totYTD = 0, totQ4 = 0, totEAC = 0, totVAC = 0;

      Array.from(accMap.values())
        .filter(a => state.accountType === 'ALL' || a.gruppe === state.accountType)
        .sort((a, b) => a.konto - b.konto)
        .forEach(a => {
          const eac = a.ytd + a.q4;
          const vac = a.bac - eac;
          const vacPct = a.bac > 0 ? (vac / a.bac) : 0;

          totBAC += a.bac;
          totYTD += a.ytd;
          totQ4 += a.q4;
          totEAC += eac;
          totVAC += vac;

          const vacColor = vac >= 0 ? 'text-green' : 'text-red';
          const vacSign = vac >= 0 ? '+' : '';

          html += `
            <tr>
              <td><strong>${a.konto}</strong></td>
              <td>${a.navn}</td>
              <td>${a.gruppe}</td>
              <td>${a.srs}</td>
              <td class="num">${fmtNum(a.bac)}</td>
              <td class="num">${fmtNum(a.ytd)}</td>
              <td class="num">${fmtNum(a.q4)}</td>
              <td class="num">${fmtNum(eac)}</td>
              <td class="num ${vacColor}"><strong>${vacSign}${fmtNum(vac)}</strong></td>
              <td class="num ${vacColor}">${(vacPct * 100).toFixed(1)}%</td>
            </tr>
          `;
        });

      const totVacSign = totVAC >= 0 ? '+' : '';
      const totVacColor = totVAC >= 0 ? 'text-green' : 'text-red';
      html += `
        <tr class="total-row">
          <td colspan="4">SUM TOTALT</td>
          <td class="num">${fmtNum(totBAC)}</td>
          <td class="num">${fmtNum(totYTD)}</td>
          <td class="num">${fmtNum(totQ4)}</td>
          <td class="num">${fmtNum(totEAC)}</td>
          <td class="num ${totVacColor}"><strong>${totVacSign}${fmtNum(totVAC)}</strong></td>
          <td class="num ${totVacColor}">${totBAC > 0 ? ((totVAC / totBAC) * 100).toFixed(1) : '0.0'}%</td>
        </tr>
      `;
      tbody.innerHTML = html;
    }

    // =========================================================================
    // PAGE 3: AVVIKS- & ROTÅRSAKSANALYSE (Variance Actions Sheet)
    // =========================================================================
    function renderPage3() {
      // 1. Variance Drivers Table
      const tbodyDrivers = document.getElementById('tbody-variance-drivers');
      let htmlDrivers = '';
      DATA.variance_drivers.forEach(d => {
        const isFavorable = d.avvik >= 0;
        const color = isFavorable ? 'text-green' : (d.rag.includes('Moderat') ? 'text-amber' : 'text-red');
        const badgeClass = isFavorable ? 'badge-green' : (d.rag.includes('Moderat') ? 'badge-amber' : 'badge-red');
        const sign = isFavorable ? '+' : '';

        htmlDrivers += `
          <tr>
            <td><strong>${d.org}</strong></td>
            <td>${d.konto}</td>
            <td>${d.driver}</td>
            <td class="num">${fmtNum(d.budget)}</td>
            <td class="num">${fmtNum(d.le)}</td>
            <td class="num ${color}"><strong>${sign}${fmtNum(d.avvik)}</strong></td>
            <td class="num ${color}">${(d.avvik_pct * 100).toFixed(1)}%</td>
            <td><span class="badge-rag ${badgeClass}">${d.rag}</span></td>
          </tr>
        `;
      });
      tbodyDrivers.innerHTML = htmlDrivers;

      // 2. Month Hotspots Table
      const tbodyHotspots = document.getElementById('tbody-month-hotspots');
      let htmlHotspots = '';
      DATA.month_hotspots.forEach(h => {
        const isFav = h.avvik >= 0;
        const color = isFav ? 'text-green' : 'text-red';
        const sign = isFav ? '+' : '';

        htmlHotspots += `
          <tr>
            <td><strong>${h.month}</strong></td>
            <td class="num ${color}"><strong>${sign}${fmtNum(h.avvik)} kr</strong></td>
            <td style="white-space: normal;">${h.forklaring}</td>
          </tr>
        `;
      });
      tbodyHotspots.innerHTML = htmlHotspots;
    }

    // =========================================================================
    // PAGE 4: PRIORITERT HANDLINGSPLAN
    // =========================================================================
    function renderPage4() {
      const tbody = document.getElementById('tbody-action-plan');
      let html = '';
      DATA.action_plan.forEach(a => {
        const ragClass = a.rag.includes('Høy') ? 'badge-red' : (a.rag.includes('Moderat') ? 'badge-amber' : 'badge-green');
        html += `
          <tr>
            <td><strong>#${a.prio}</strong></td>
            <td><strong>${a.omraade}</strong></td>
            <td style="white-space: normal; max-width: 200px;">${a.rotaarsak}</td>
            <td style="white-space: normal; max-width: 240px;">${a.handling}</td>
            <td>${a.eier}</td>
            <td>${a.frist}</td>
            <td class="num">${fmtNum(a.brutto_gap)} kr</td>
            <td class="num text-green"><strong>${fmtNum(a.effekt)} kr</strong></td>
            <td style="white-space: normal;">${a.kpi}</td>
            <td><span class="badge-rag ${ragClass}">${a.rag}</span></td>
            <td style="white-space: normal; font-weight: 500;">${a.beslutning}</td>
            <td>${a.oppfoelging}</td>
          </tr>
        `;
      });
      tbody.innerHTML = html;
    }

    // =========================================================================
    // PAGE 5: BEMANNINGSANALYSE & ÅRSVERK
    // =========================================================================
    function renderPage5() {
      const container = document.getElementById('chart-p3-monthly-fte');
      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Des'];

      const monthlyUF = new Array(12).fill(0);
      const monthlyTA = new Array(12).fill(0);

      DATA.fte.forEach(r => {
        const m = (r.DatoNokkel % 100) - 1;
        if (m >= 0 && m < 12) {
          monthlyUF[m] += (r.Aarsverk_UF || 0);
          monthlyTA[m] += (r.Aarsverk_TA || 0);
        }
      });

      const width = 500;
      const height = 220;
      const padL = 40;
      const padR = 20;
      const padT = 20;
      const padB = 30;

      const maxFTE = 260;
      const innerW = width - padL - padR;
      const innerH = height - padT - padB;
      const colW = innerW / 12;
      const barW = colW * 0.65;

      let svg = `<svg class="tufte-chart" viewBox="0 0 ${width} ${height}">`;
      for (let i = 0; i <= 4; i++) {
        const val = (maxFTE / 4) * i;
        const yPos = padT + innerH - (val / maxFTE) * innerH;
        svg += `<line x1="${padL}" y1="${yPos}" x2="${width - padR}" y2="${yPos}" stroke="#f1f5f9" />`;
        svg += `<text x="${padL - 6}" y="${yPos + 3}" text-anchor="end" font-size="9" fill="#94a3b8">${val.toFixed(0)}</text>`;
      }

      for (let m = 0; m < 12; m++) {
        const x = padL + m * colW + (colW - barW) / 2;
        const ufH = (monthlyUF[m] / maxFTE) * innerH;
        const taH = (monthlyTA[m] / maxFTE) * innerH;
        const yUF = padT + innerH - ufH;
        const yTA = yUF - taH;

        svg += `<rect x="${x}" y="${yUF}" width="${barW}" height="${ufH}" fill="#0284c7" rx="1"
                  onmouseover="showTooltip(event, '${months[m]}: UF ' + ${monthlyUF[m].toFixed(1)} + ' ÅV')" onmouseout="hideTooltip()" />`;
        svg += `<rect x="${x}" y="${yTA}" width="${barW}" height="${taH}" fill="#64748b" rx="1"
                  onmouseover="showTooltip(event, '${months[m]}: TA ' + ${monthlyTA[m].toFixed(1)} + ' ÅV')" onmouseout="hideTooltip()" />`;
        svg += `<text x="${x + barW / 2}" y="${padT + innerH + 14}" text-anchor="middle" font-size="9" fill="#64748b">${months[m]}</text>`;
      }

      svg += `
        <g transform="translate(${padL + 10}, ${padT + 4})">
          <rect x="0" y="0" width="10" height="10" fill="#0284c7" rx="2" />
          <text x="14" y="9" font-size="10" fill="#0284c7">Vitenskapelig UF</text>
          <rect x="130" y="0" width="10" height="10" fill="#64748b" rx="2" />
          <text x="144" y="9" font-size="10" fill="#64748b">Administrativ TA</text>
        </g>
      `;
      svg += `</svg>`;
      container.innerHTML = svg;

      renderP3UnitFTE();
      renderP3Table();
    }

    function renderP3UnitFTE() {
      const container = document.getElementById('chart-p3-unit-fte');
      const width = 450;
      const height = 220;
      const padL = 120;
      const padR = 40;
      const padT = 20;
      const padB = 20;

      const units = [
        { name: 'Admin & Felles', fte: 22.0, uf: 0, ta: 22 },
        { name: 'Ledelse & Innovasjon', fte: 63.0, uf: 45, ta: 18 },
        { name: 'Rettsvitenskap', fte: 46.0, uf: 35, ta: 11 },
        { name: 'Økonomi', fte: 98.0, uf: 74, ta: 24 }
      ];

      const maxFTE = 110;
      const innerW = width - padL - padR;
      const innerH = height - padT - padB;
      const rowH = innerH / units.length;

      let svg = `<svg class="tufte-chart" viewBox="0 0 ${width} ${height}">`;
      units.forEach((u, i) => {
        const y = padT + i * rowH + (rowH - 22) / 2;
        const bLen = (u.fte / maxFTE) * innerW;

        svg += `<text x="${padL - 8}" y="${y + 15}" text-anchor="end" font-size="11" fill="#1e293b" font-weight="500">${u.name}</text>`;
        svg += `<rect x="${padL}" y="${y}" width="${bLen}" height="22" fill="#334155" rx="3"
                  onmouseover="showTooltip(event, '${u.name}: Totalt ${u.fte} ÅV (${u.uf} UF / ${u.ta} TA)')" onmouseout="hideTooltip()" />`;
        svg += `<text x="${padL + bLen + 6}" y="${y + 15}" font-size="10" font-weight="600" fill="#334155">${u.fte.toFixed(1)} ÅV</text>`;
      });
      svg += `</svg>`;
      container.innerHTML = svg;
    }

    function renderP3Table() {
      const tbody = document.getElementById('tbody-p3-fte');
      const months = ['Januar', 'Februar', 'Mars', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Desember'];
      const orgNames = {
        'K10000': 'Admin & Felles', 'K11000': 'Ledelse & Innovasjon',
        'K12000': 'Rettsvitenskap', 'K13000': 'Økonomi'
      };

      let html = '';
      DATA.fte.slice(0, 24).forEach(r => {
        const mIdx = (r.DatoNokkel % 100) - 1;
        const mNavn = months[mIdx] || 'Måned';
        const oNavn = orgNames[r.OrgKode] || r.OrgKode;

        html += `
          <tr>
            <td>${mNavn} 2026</td>
            <td>${oNavn} (${r.OrgKode})</td>
            <td class="num">${r.Aarsverk_UF.toFixed(1)}</td>
            <td class="num">${r.Aarsverk_TA.toFixed(1)}</td>
            <td class="num"><strong>${r.Aarsverk_Totalt.toFixed(1)}</strong></td>
            <td class="num">${r.Budsjettert_Aarsverk.toFixed(1)}</td>
            <td class="num ${r.Vakans_Aarsverk > 0 ? 'text-amber' : ''}">${r.Vakans_Aarsverk.toFixed(1)}</td>
            <td class="num">${(r.Vakansgrad_Pct * 100).toFixed(1)}%</td>
            <td class="num">${r.Antall_Ansatte}</td>
          </tr>
        `;
      });
      tbody.innerHTML = html;
    }

    // =========================================================================
    // PAGE 6: EVM FREMDRIFT & S-KURVE
    // =========================================================================
    function renderPage6() {
      const container = document.getElementById('chart-p4-scurve');
      const width = 520;
      const height = 240;
      const padL = 50;
      const padR = 40;
      const padT = 20;
      const padB = 30;

      const innerW = width - padL - padR;
      const innerH = height - padT - padB;
      const maxVal = 145;

      let svg = `<svg class="tufte-chart" viewBox="0 0 ${width} ${height}">`;
      for (let i = 0; i <= 4; i++) {
        const val = (maxVal / 4) * i;
        const y = padT + innerH - (val / maxVal) * innerH;
        svg += `<line x1="${padL}" y1="${y}" x2="${width - padR}" y2="${y}" stroke="#f1f5f9" />`;
        svg += `<text x="${padL - 6}" y="${y + 3}" text-anchor="end" font-size="9" fill="#94a3b8">${val.toFixed(0)}M</text>`;
      }

      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Des'];
      let pvPts = [], evPts = [], acPts = [];

      DATA.evm.forEach((r, idx) => {
        const x = padL + (idx / 11) * innerW;
        const yPV = padT + innerH - ((r.PlannedValue_PV / 1000000) / maxVal) * innerH;
        const yEV = padT + innerH - ((r.EarnedValue_EV / 1000000) / maxVal) * innerH;
        const yAC = padT + innerH - ((r.ActualCost_AC / 1000000) / maxVal) * innerH;

        pvPts.push(`${x},${yPV}`);
        evPts.push(`${x},${yEV}`);
        acPts.push(`${x},${yAC}`);

        svg += `<text x="${x}" y="${padT + innerH + 16}" text-anchor="middle" font-size="9" fill="#64748b">${months[idx]}</text>`;
      });

      svg += `<polyline points="${pvPts.join(' ')}" fill="none" stroke="#64748b" stroke-width="2" stroke-dasharray="4,3" />`;
      svg += `<polyline points="${evPts.join(' ')}" fill="none" stroke="#0284c7" stroke-width="2.5" />`;
      svg += `<polyline points="${acPts.join(' ')}" fill="none" stroke="#ef4444" stroke-width="2" />`;

      const lastX = width - padR;
      const lastPV = padT + innerH - ((DATA.evm[11].PlannedValue_PV / 1000000) / maxVal) * innerH;
      const lastEV = padT + innerH - ((DATA.evm[11].EarnedValue_EV / 1000000) / maxVal) * innerH;
      const lastAC = padT + innerH - ((DATA.evm[11].ActualCost_AC / 1000000) / maxVal) * innerH;

      svg += `<text x="${lastX + 4}" y="${lastPV + 3}" font-size="9" font-weight="600" fill="#64748b">PV</text>`;
      svg += `<text x="${lastX + 4}" y="${lastEV + 3}" font-size="9" font-weight="700" fill="#0284c7">EV</text>`;
      svg += `<text x="${lastX + 4}" y="${lastAC + 3}" font-size="9" font-weight="700" fill="#ef4444">AC</text>`;

      svg += `</svg>`;
      container.innerHTML = svg;

      renderP4Indices();
      renderP4Table();
    }

    function renderP4Indices() {
      const container = document.getElementById('chart-p4-indices');
      const width = 450;
      const height = 240;
      const padL = 40;
      const padR = 30;
      const padT = 20;
      const padB = 30;

      const innerW = width - padL - padR;
      const innerH = height - padT - padB;
      const minVal = 0.90;
      const maxVal = 1.05;

      let svg = `<svg class="tufte-chart" viewBox="0 0 ${width} ${height}">`;
      const y1 = padT + innerH - ((1.00 - minVal) / (maxVal - minVal)) * innerH;
      svg += `<line x1="${padL}" y1="${y1}" x2="${width - padR}" y2="${y1}" stroke="#10b981" stroke-width="1.5" stroke-dasharray="3,3" />`;
      svg += `<text x="${width - padR + 4}" y="${y1 + 3}" font-size="9" font-weight="600" fill="#10b981">1.00</text>`;

      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Des'];
      let cpiPts = [], spiPts = [];

      DATA.evm.forEach((r, i) => {
        const x = padL + (i / 11) * innerW;
        const yCPI = padT + innerH - ((r.CostPerformanceIndex_CPI - minVal) / (maxVal - minVal)) * innerH;
        const ySPI = padT + innerH - ((r.SchedulePerformanceIndex_SPI - minVal) / (maxVal - minVal)) * innerH;

        cpiPts.push(`${x},${yCPI}`);
        spiPts.push(`${x},${ySPI}`);
        svg += `<text x="${x}" y="${padT + innerH + 16}" text-anchor="middle" font-size="9" fill="#64748b">${months[i]}</text>`;
      });

      svg += `<polyline points="${cpiPts.join(' ')}" fill="none" stroke="#f59e0b" stroke-width="2.2" />`;
      svg += `<polyline points="${spiPts.join(' ')}" fill="none" stroke="#0284c7" stroke-width="2.2" />`;

      svg += `
        <g transform="translate(${padL + 10}, ${padT + 4})">
          <line x1="0" y1="5" x2="15" y2="5" stroke="#f59e0b" stroke-width="2.5" />
          <text x="20" y="8" font-size="10" fill="#f59e0b">CPI (0,97)</text>
          <line x1="120" y1="5" x2="135" y2="5" stroke="#0284c7" stroke-width="2.5" />
          <text x="140" y="8" font-size="10" fill="#0284c7">SPI (0,98)</text>
        </g>
      `;
      svg += `</svg>`;
      container.innerHTML = svg;
    }

    function renderP4Table() {
      const tbody = document.getElementById('tbody-p4-evm');
      const months = ['Januar', 'Februar', 'Mars', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Desember'];

      let html = '';
      DATA.evm.forEach((r, idx) => {
        const cpiColor = r.CostPerformanceIndex_CPI >= 1.0 ? 'text-green' : (r.CostPerformanceIndex_CPI >= 0.95 ? 'text-amber' : 'text-red');
        const spiColor = r.SchedulePerformanceIndex_SPI >= 1.0 ? 'text-green' : 'text-amber';

        html += `
          <tr>
            <td><strong>${months[idx]} 2026</strong></td>
            <td class="num">${fmtNum(r.BAC_BudgetAtCompletion)}</td>
            <td class="num">${fmtNum(r.PlannedValue_PV)}</td>
            <td class="num">${fmtNum(r.EarnedValue_EV)}</td>
            <td class="num">${fmtNum(r.ActualCost_AC)}</td>
            <td class="num">${fmtNum(r.EstimateAtCompletion_EAC)}</td>
            <td class="num text-green">+${fmtNum(r.VarianceAtCompletion_VAC)}</td>
            <td class="num ${cpiColor}"><strong>${r.CostPerformanceIndex_CPI.toFixed(2)}</strong></td>
            <td class="num ${spiColor}"><strong>${r.SchedulePerformanceIndex_SPI.toFixed(2)}</strong></td>
            <td><span class="badge-rag badge-green">Planmessig</span></td>
          </tr>
        `;
      });
      tbody.innerHTML = html;
    }

    // =========================================================================
    // PAGE 7: STUDIEPRODUKSJON & KD
    // =========================================================================
    function renderPage7() {
      const container = document.getElementById('chart-p5-spe');
      const width = 500;
      const height = 220;
      const padL = 130;
      const padR = 40;
      const padT = 20;
      const padB = 25;

      const programs = [
        { name: 'Master Org. & Ledelse / MKT', base: 1040, target: 1050 },
        { name: 'Master & Bachelor Rettsvitenskap', base: 780, target: 788 },
        { name: 'Siviløkonom / Øk.Ad / Ph.D.', base: 1300, target: 1315 }
      ];

      const maxVal = 1500;
      const innerW = width - padL - padR;
      const innerH = height - padT - padB;
      const rowH = innerH / programs.length;

      let svg = `<svg class="tufte-chart" viewBox="0 0 ${width} ${height}">`;
      programs.forEach((p, i) => {
        const y = padT + i * rowH + 6;
        const bBase = (p.base / maxVal) * innerW;
        const bTarget = (p.target / maxVal) * innerW;

        svg += `<text x="${padL - 8}" y="${y + 12}" text-anchor="end" font-size="10" fill="#1e293b" font-weight="500">${p.name}</text>`;
        svg += `<rect x="${padL}" y="${y}" width="${bBase}" height="10" fill="#94a3b8" rx="2"
                  onmouseover="showTooltip(event, '${p.name}: 2025 Grunnlag ' + ${p.base} + ' SPE60')" onmouseout="hideTooltip()" />`;
        svg += `<rect x="${padL}" y="${y + 13}" width="${bTarget}" height="10" fill="#0284c7" rx="2"
                  onmouseover="showTooltip(event, '${p.name}: Mål 2026 ' + ${p.target} + ' SPE60')" onmouseout="hideTooltip()" />`;
        svg += `<text x="${padL + bTarget + 6}" y="${y + 22}" font-size="10" font-weight="600" fill="#0284c7">${p.target}</text>`;
      });

      svg += `
        <g transform="translate(${padL + 10}, ${height - 12})">
          <rect x="0" y="0" width="8" height="8" fill="#94a3b8" />
          <text x="12" y="7" font-size="9" fill="#64748b">2025 Grunnlag (Lag)</text>
          <rect x="120" y="0" width="8" height="8" fill="#0284c7" />
          <text x="132" y="7" font-size="9" fill="#0284c7">Mål 2026 (SPE60)</text>
        </g>
      `;
      svg += `</svg>`;
      container.innerHTML = svg;

      renderP5Ratio();
      renderP5Table();
    }

    function renderP5Ratio() {
      const container = document.getElementById('chart-p5-ratio');
      const width = 450;
      const height = 220;
      const padL = 130;
      const padR = 40;
      const padT = 20;
      const padB = 25;

      const ratios = [
        { name: 'Master Org. & Ledelse / MKT', ratio: 25.6 },
        { name: 'Master & Bachelor Rettsvitenskap', ratio: 22.4 },
        { name: 'Siviløkonom / Øk.Ad / Ph.D.', ratio: 21.6 }
      ];

      const maxVal = 30;
      const innerW = width - padL - padR;
      const innerH = height - padT - padB;
      const rowH = innerH / ratios.length;

      let svg = `<svg class="tufte-chart" viewBox="0 0 ${width} ${height}">`;
      ratios.forEach((r, i) => {
        const y = padT + i * rowH + (rowH - 18) / 2;
        const bLen = (r.ratio / maxVal) * innerW;

        svg += `<text x="${padL - 8}" y="${y + 13}" text-anchor="end" font-size="10" fill="#1e293b" font-weight="500">${r.name}</text>`;
        svg += `<rect x="${padL}" y="${y}" width="${bLen}" height="18" fill="#f59e0b" rx="2" 
                  onmouseover="showTooltip(event, '${r.name}: ${r.ratio} stud/UF')" onmouseout="hideTooltip()" />`;
        svg += `<text x="${padL + bLen + 6}" y="${y + 14}" font-size="10" font-weight="600" fill="#b45309">${r.ratio.toFixed(1)}</text>`;
      });
      svg += `</svg>`;
      container.innerHTML = svg;
    }

    function renderP5Table() {
      const tbody = document.getElementById('tbody-p5-students');
      const orgNames = {
        'K11000': 'Institutt for ledelse og innovasjon',
        'K12000': 'Institutt for rettsvitenskap',
        'K13000': 'Institutt for økonomi'
      };

      const progRows = [
        { prog: 'Master Org. & Ledelse / MKT', org: 'K11000', cat: 'Kategori 1', stud: 1150, base: 1040, target: 1050, rate: 54550, inc: 57277500, ratio: 25.6 },
        { prog: 'Master & Bachelor i Rettsvitenskap', org: 'K12000', cat: 'Kategori 1', stud: 850, base: 780, target: 788, rate: 54550, inc: 42985400, ratio: 22.4 },
        { prog: 'Siviløkonom / Øk.Ad / Ph.D.', org: 'K13000', cat: 'Kategori 1', stud: 1450, base: 1300, target: 1315, rate: 54550, inc: 71733250, ratio: 21.6 }
      ];

      let html = '';
      let totStud = 0, totBase = 0, totTarget = 0, totInc = 0;

      progRows.forEach(r => {
        totStud += r.stud;
        totBase += r.base;
        totTarget += r.target;
        totInc += r.inc;

        html += `
          <tr>
            <td><strong>${r.prog}</strong></td>
            <td>${orgNames[r.org]} (${r.org})</td>
            <td><span class="badge-rag badge-neutral">${r.cat}</span></td>
            <td class="num">${fmtNum(r.stud)}</td>
            <td class="num">${fmtNum(r.base)}</td>
            <td class="num">${fmtNum(r.target)}</td>
            <td class="num">${fmtNum(r.rate)} kr</td>
            <td class="num"><strong>${fmtNum(r.inc)} kr</strong></td>
            <td class="num">${r.ratio.toFixed(1)}</td>
          </tr>
        `;
      });

      const avgRatio = (totStud / 154).toFixed(1);
      html += `
        <tr class="total-row">
          <td>SAMLET HHU PRODUKSJON</td>
          <td>Alle Institutter</td>
          <td>Kategori 1</td>
          <td class="num">${fmtNum(totStud)}</td>
          <td class="num">${fmtNum(totBase)}</td>
          <td class="num">${fmtNum(totTarget)}</td>
          <td class="num">54 550 kr</td>
          <td class="num"><strong>${fmtNum(totInc)} kr</strong></td>
          <td class="num">${avgRatio}</td>
        </tr>
      `;
      tbody.innerHTML = html;
    }

    // =========================================================================
    // PAGE 8: BUDSJETT 2027 PLANRAPPORT
    // =========================================================================
    function renderPage8() {
      // 1. Units Table
      const tbodyUnits = document.getElementById('tbody-p27-units');
      let htmlUnits = '';
      let totRev = 0, totCost = 0, totNet = 0, totAV = 0, totUF = 0, totStud = 0, totSPE = 0;

      DATA.p27_units.forEach(u => {
        totRev += u.inntekter;
        totCost += u.kostnader;
        totNet += u.netto;
        totAV += u.aarsverk;
        totUF += u.uf;
        totStud += u.studenter;
        totSPE += u.spe60;

        htmlUnits += `
          <tr>
            <td><strong>${u.enhet}</strong> (${u.org})</td>
            <td class="num">${fmtNum(u.inntekter / 1000000, 2)} M</td>
            <td class="num">${fmtNum(u.kostnader / 1000000, 2)} M</td>
            <td class="num text-green"><strong>+${fmtNum(u.netto / 1000000, 2)} M</strong></td>
            <td class="num">${u.aarsverk.toFixed(1)}</td>
            <td class="num">${u.uf.toFixed(0)}</td>
            <td class="num">${fmtNum(u.studenter)}</td>
            <td class="num">${fmtNum(u.spe60)}</td>
          </tr>
        `;
      });

      htmlUnits += `
        <tr class="total-row">
          <td>SUM HHU 2027</td>
          <td class="num">${fmtNum(totRev / 1000000, 2)} M</td>
          <td class="num">${fmtNum(totCost / 1000000, 2)} M</td>
          <td class="num text-green"><strong>+${fmtNum(totNet / 1000000, 2)} M</strong></td>
          <td class="num">${totAV.toFixed(1)}</td>
          <td class="num">${totUF.toFixed(0)}</td>
          <td class="num">${fmtNum(totStud)}</td>
          <td class="num">${fmtNum(totSPE)}</td>
        </tr>
      `;
      tbodyUnits.innerHTML = htmlUnits;

      // 2. Actions Table 2027
      const tbodyActions = document.getElementById('tbody-p27-actions');
      let htmlActions = '';
      DATA.p27_actions.forEach(a => {
        htmlActions += `
          <tr>
            <td><strong>${a.tiltak}</strong></td>
            <td>${a.enhet}</td>
            <td class="num"><strong>${fmtNum(a.effekt)} kr</strong></td>
            <td><span class="badge-rag badge-green">${a.status}</span></td>
            <td>${a.driver}</td>
          </tr>
        `;
      });
      tbodyActions.innerHTML = htmlActions;

      // 3. Detailed 2027 Transactions
      const tbodyBudget = document.getElementById('tbody-p7-budget');
      const months = ['Januar', 'Februar', 'Mars', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Desember'];
      const orgNames = {
        'K10000': 'Admin & Felles', 'K11000': 'Ledelse & Innovasjon',
        'K12000': 'Rettsvitenskap', 'K13000': 'Økonomi'
      };
      const accDict = new Map(DATA.accounts.map(a => [a.Konto, a]));

      let htmlB = '';
      let totBudget = 0;
      let rows = DATA.budget27;
      if (state.org !== 'ALL') rows = rows.filter(r => r.OrgKode === state.org);

      rows.slice(0, 36).forEach(r => {
        const mIdx = (r.DatoNokkel % 100) - 1;
        const mNavn = months[mIdx] || 'Måned';
        const aInfo = accDict.get(r.Konto) || { Kontonavn: 'Diverse', SRS_regnskapslinje: 'Drift' };
        totBudget += r.BudsjettBelop;

        htmlB += `
          <tr>
            <td>${mNavn} 2027</td>
            <td>${orgNames[r.OrgKode] || r.OrgKode}</td>
            <td>${r.Konto}</td>
            <td>${aInfo.Kontonavn}</td>
            <td>${aInfo.SRS_regnskapslinje}</td>
            <td class="num"><strong>${fmtNum(r.BudsjettBelop)} kr</strong></td>
            <td>${r.Kommentar || 'Vedtatt budsjett'}</td>
          </tr>
        `;
      });

      htmlB += `
        <tr class="total-row">
          <td colspan="5">SUM VISNING (UTVALG)</td>
          <td class="num"><strong>${fmtNum(totBudget)} kr</strong></td>
          <td>Budsjettvedtak Note 15</td>
        </tr>
      `;
      tbodyBudget.innerHTML = htmlB;
    }

    // =========================================================================
    // PAGE 9: BUDSJETTPROSESS 2027 & LUKKEPLAN
    // =========================================================================
    function renderPage9() {
      // 1. Gates Pipeline Roadmap
      const containerPipeline = document.getElementById('gate-pipeline-container');
      let htmlP = '';
      DATA.gates.forEach(g => {
        let nodeClass = 'future';
        if (g.status.includes('Fullført')) nodeClass = 'passed';
        else if (g.status.includes('Pågår') || g.status.includes('Åpent')) nodeClass = 'in-progress';
        else if (g.status.includes('Ikke klar')) nodeClass = 'blocked';

        htmlP += `
          <div class="gate-node ${nodeClass}">
            <div class="gate-num">Port ${g.port} | ${g.periode}</div>
            <div class="gate-title">${g.sporsmaal}</div>
            <div class="gate-status">${g.rag_icon} ${g.status}</div>
          </div>
        `;
      });
      containerPipeline.innerHTML = htmlP;

      // 2. Gates Table
      const tbodyGates = document.getElementById('tbody-gates');
      let htmlG = '';
      DATA.gates.forEach(g => {
        const badgeClass = g.rag_icon.includes('🟢') ? 'badge-green' : (g.rag_icon.includes('🟡') ? 'badge-amber' : (g.rag_icon.includes('🔴') ? 'badge-red' : 'badge-neutral'));
        htmlG += `
          <tr>
            <td><strong>Port ${g.port}</strong></td>
            <td>${g.periode}</td>
            <td style="white-space: normal; font-weight: 500;">${g.sporsmaal}</td>
            <td style="white-space: normal; max-width: 240px;">${g.aktivitet}</td>
            <td>${g.ansvarlig}</td>
            <td>${g.leveranse}</td>
            <td>${g.arena}</td>
            <td><span class="badge-rag ${badgeClass}">${g.rag_icon} ${g.status}</span></td>
            <td>${g.frist}</td>
          </tr>
        `;
      });
      tbodyGates.innerHTML = htmlG;

      // 3. Driver Analysis Table
      const tbodyDrivers = document.getElementById('tbody-driver-analysis');
      let htmlD = '';
      DATA.driver_analysis.forEach(d => {
        const badgeClass = d.rag.includes('🟢') ? 'badge-green' : (d.rag.includes('🟡') ? 'badge-amber' : 'badge-red');
        htmlD += `
          <tr>
            <td><strong>${d.driver}</strong></td>
            <td style="white-space: normal;">${d.mekanisme}</td>
            <td>${d.kvantifisering}</td>
            <td>${d.effekt}</td>
            <td>${d.risiko}</td>
            <td>${d.kontroll}</td>
            <td>${d.eier}</td>
            <td>${d.avstemming}</td>
            <td class="num">${d.modellverdi > 0 ? (d.modellverdi > 1000 ? fmtNum(d.modellverdi / 1000000, 2) + ' M' : d.modellverdi) : '—'}</td>
            <td class="num">${d.referanse > 0 ? (d.referanse > 1000 ? fmtNum(d.referanse / 1000000, 2) + ' M' : d.referanse) : '—'}</td>
            <td class="num ${d.differanse < 0 ? 'text-red' : ''}">${d.differanse !== 0 ? (Math.abs(d.differanse) > 1000 ? fmtNum(d.differanse / 1000000, 2) + ' M' : d.differanse) : '0,0'}</td>
            <td><span class="badge-rag ${badgeClass}">${d.rag} ${d.konklusjon}</span></td>
          </tr>
        `;
      });
      tbodyDrivers.innerHTML = htmlD;

      // 4. Closure Plan Table
      const tbodyClosure = document.getElementById('tbody-closure-plan');
      let htmlC = '';
      DATA.closure_plan.forEach(c => {
        const badgeClass = c.rag.includes('🟢') ? 'badge-green' : (c.rag.includes('🟡') ? 'badge-amber' : 'badge-red');
        htmlC += `
          <tr>
            <td><strong>#${c.prio}</strong></td>
            <td><strong>${c.avvik_risiko}</strong></td>
            <td style="white-space: normal; max-width: 280px;">${c.handling}</td>
            <td>${c.eier}</td>
            <td>${c.frist}</td>
            <td style="white-space: normal;">${c.bevis}</td>
            <td style="white-space: normal; color: var(--rag-red-text);">${c.konsekvens}</td>
            <td><span class="badge-rag ${badgeClass}">${c.rag}</span></td>
          </tr>
        `;
      });
      tbodyClosure.innerHTML = htmlC;
    }

    // =========================================================================
    // PAGE 10: PROGNOSEMETODIKK 2027
    // =========================================================================
    function renderPage10() {
      // 1. Forecast Posts
      const tbodyPosts = document.getElementById('tbody-forecast-posts');
      let htmlP = '';
      DATA.forecast_posts.forEach(p => {
        const prioBadge = p.prio === 'Høy' ? 'badge-red' : (p.prio === 'Middels' ? 'badge-amber' : 'badge-neutral');
        htmlP += `
          <tr>
            <td><span class="badge-rag ${prioBadge}">${p.prio}</span></td>
            <td><strong>${p.post}</strong></td>
            <td>${p.konto}</td>
            <td class="num">${p.baseline > 0 ? (p.baseline > 1000 ? fmtNum(p.baseline / 1000000, 2) + ' M' : p.baseline) : '—'}</td>
            <td><strong>${p.metode}</strong></td>
            <td style="white-space: normal;">${p.driver}</td>
            <td style="white-space: normal; font-size: 11px;">${p.beregning}</td>
            <td>${p.oppdatering}</td>
          </tr>
        `;
      });
      tbodyPosts.innerHTML = htmlP;

      // 2. Routine Steps
      const tbodySteps = document.getElementById('tbody-routine-steps');
      let htmlS = '';
      DATA.routine_steps.forEach(s => {
        htmlS += `
          <tr>
            <td><strong>Trinn ${s.trinn}</strong></td>
            <td><strong>${s.formel}</strong></td>
            <td>${s.forklaring}</td>
            <td>${s.kontroll}</td>
            <td>${s.aktivitet} (${s.d1_3} | ${s.d4_5} | ${s.d6_7})</td>
          </tr>
        `;
      });
      tbodySteps.innerHTML = htmlS;
    }

    // =========================================================================
    // TABLE SORTING & EXPORT UTILITIES
    // =========================================================================
    function sortTable(tableId, colIdx, isNumeric = false) {
      const table = document.getElementById(tableId);
      const tbody = table.querySelector('tbody');
      const rows = Array.from(tbody.querySelectorAll('tr')).filter(r => !r.classList.contains('total-row'));

      const isAsc = table.getAttribute('data-sort-dir') !== 'asc';
      table.setAttribute('data-sort-dir', isAsc ? 'asc' : 'desc');

      rows.sort((a, b) => {
        if (isNumeric) {
          const rawA = a.children[colIdx].innerText.replace(/\\s+/g, '').replace(/,/g, '.').replace(/[^0-9.-]/g, '').trim();
          const rawB = b.children[colIdx].innerText.replace(/\\s+/g, '').replace(/,/g, '.').replace(/[^0-9.-]/g, '').trim();
          const valA = parseFloat(rawA) || 0;
          const valB = parseFloat(rawB) || 0;
          return isAsc ? valA - valB : valB - valA;
        } else {
          const valA = a.children[colIdx].innerText.toLowerCase();
          const valB = b.children[colIdx].innerText.toLowerCase();
          return isAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
        }
      });

      const totalRow = tbody.querySelector('.total-row');
      tbody.innerHTML = '';
      rows.forEach(r => tbody.appendChild(r));
      if (totalRow) tbody.appendChild(totalRow);
    }

    function exportActiveTableToCSV() {
      const activeSection = document.querySelector('.page-section.active');
      const table = activeSection.querySelector('table');
      if (!table) return alert('Ingen tabell funnet på aktiv side.');

      let csv = [];
      const rows = table.querySelectorAll('tr');
      rows.forEach(r => {
        const cols = r.querySelectorAll('th, td');
        const rowData = Array.from(cols).map(c => '"' + c.innerText.replace(/"/g, '""').trim() + '"');
        csv.push(rowData.join(';'));
      });

      const blob = new Blob(["\\ufeff" + csv.join('\\n')], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `HHU_Rapport_${state.activeTab}_${state.year}.csv`;
      a.click();
    }
  </script>
</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Successfully generated {OUTPUT_HTML} with {len(html)} bytes.")

if __name__ == '__main__':
    generate_html()
