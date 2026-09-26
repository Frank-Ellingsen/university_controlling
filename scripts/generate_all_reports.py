"""
Script: generate_all_reports.py
Generates the complete 3-page Power BI report suite for:
- Page 1: 'Virksomhets- og Prosjektoversikt 2026' (Rolled-up Executive KPI Overview)
- Page 2: 'Prosjektstyring & EVM Dybde' (Earned Value Management Deep Dive)
- Page 3: 'Bemanning & Studieproduksjon' (Faculty Staffing, Capacity & Education Production)
Strictly adheres to Edward Tufte's Data-Ink ratio principles.
"""

import json
import os
from pathlib import Path

BASE_DIR = Path(r"c:\Users\frank\Desktop\UIA2")
PAGES_META_FILE = BASE_DIR / "UIA-project-2026YTD.Report" / "definition" / "pages" / "pages.json"
PAGES_ROOT = BASE_DIR / "UIA-project-2026YTD.Report" / "definition" / "pages"

PAGE_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
CONTAINER_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json"
PAGES_META_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json"

def create_textbox_visual(name, x, y, width, height, z, paragraphs, tab_order=1):
    return {
        "$schema": CONTAINER_SCHEMA,
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": z,
            "width": width,
            "height": height,
            "tabOrder": tab_order
        },
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [
                    {
                        "properties": {
                            "paragraphs": paragraphs
                        }
                    }
                ]
            },
            "drillFilterOtherVisuals": False
        }
    }

def create_card_visual(name, x, y, width, height, z, measure_name, title_text, tab_order=1):
    return {
        "$schema": CONTAINER_SCHEMA,
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": z,
            "width": width,
            "height": height,
            "tabOrder": tab_order
        },
        "visual": {
            "visualType": "card",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "_Measures"}},
                                        "Property": measure_name
                                    }
                                },
                                "queryRef": f"_Measures.{measure_name}",
                                "nativeQueryRef": measure_name
                            }
                        ]
                    }
                }
            },
            "objects": {
                "title": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                        }
                    }
                ]
            },
            "drillFilterOtherVisuals": True
        }
    }

def create_slicer_visual(name, x, y, width, height, z, entity, column_name, title_text, tab_order=1):
    return {
        "$schema": CONTAINER_SCHEMA,
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": z,
            "width": width,
            "height": height,
            "tabOrder": tab_order
        },
        "visual": {
            "visualType": "slicer",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {
                                    "Column": {
                                        "Expression": {"SourceRef": {"Entity": entity}},
                                        "Property": column_name
                                    }
                                },
                                "queryRef": f"{entity}.{column_name}",
                                "nativeQueryRef": column_name,
                                "active": True
                            }
                        ]
                    }
                }
            },
            "objects": {
                "title": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                        }
                    }
                ]
            },
            "drillFilterOtherVisuals": True
        }
    }

def create_table_visual(name, x, y, width, height, z, columns_and_measures, title_text, tab_order=1):
    projections = []
    for item in columns_and_measures:
        if item["type"] == "Column":
            projections.append({
                "field": {
                    "Column": {
                        "Expression": {"SourceRef": {"Entity": item["entity"]}},
                        "Property": item["property"]
                    }
                },
                "queryRef": f"{item['entity']}.{item['property']}",
                "nativeQueryRef": item.get("label", item["property"]),
                "active": True
            })
        else:
            projections.append({
                "field": {
                    "Measure": {
                        "Expression": {"SourceRef": {"Entity": item["entity"]}},
                        "Property": item["property"]
                    }
                },
                "queryRef": f"{item['entity']}.{item['property']}",
                "nativeQueryRef": item.get("label", item["property"])
            })

    return {
        "$schema": CONTAINER_SCHEMA,
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": z,
            "width": width,
            "height": height,
            "tabOrder": tab_order
        },
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": projections
                    }
                }
            },
            "objects": {
                "title": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                        }
                    }
                ]
            },
            "drillFilterOtherVisuals": True
        }
    }

def create_line_chart_visual(name, x, y, width, height, z, category_col, measures, title_text, tab_order=1):
    cat_projection = [{
        "field": {
            "Column": {
                "Expression": {"SourceRef": {"Entity": category_col["entity"]}},
                "Property": category_col["property"]
            }
        },
        "queryRef": f"{category_col['entity']}.{category_col['property']}",
        "nativeQueryRef": category_col.get("label", category_col["property"]),
        "active": True
    }]

    y_projections = []
    for m in measures:
        y_projections.append({
            "field": {
                "Measure": {
                    "Expression": {"SourceRef": {"Entity": m["entity"]}},
                    "Property": m["property"]
                }
            },
            "queryRef": f"{m['entity']}.{m['property']}",
            "nativeQueryRef": m.get("label", m["property"])
        })

    return {
        "$schema": CONTAINER_SCHEMA,
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": z,
            "width": width,
            "height": height,
            "tabOrder": tab_order
        },
        "visual": {
            "visualType": "lineChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": cat_projection
                    },
                    "Y": {
                        "projections": y_projections
                    }
                }
            },
            "objects": {
                "title": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                        }
                    }
                ]
            },
            "drillFilterOtherVisuals": True
        }
    }

def create_bar_chart_visual(name, x, y, width, height, z, category_col, measures, title_text, tab_order=1):
    cat_projection = [{
        "field": {
            "Column": {
                "Expression": {"SourceRef": {"Entity": category_col["entity"]}},
                "Property": category_col["property"]
            }
        },
        "queryRef": f"{category_col['entity']}.{category_col['property']}",
        "nativeQueryRef": category_col.get("label", category_col["property"]),
        "active": True
    }]

    y_projections = []
    for m in measures:
        y_projections.append({
            "field": {
                "Measure": {
                    "Expression": {"SourceRef": {"Entity": m["entity"]}},
                    "Property": m["property"]
                }
            },
            "queryRef": f"{m['entity']}.{m['property']}",
            "nativeQueryRef": m.get("label", m["property"])
        })

    return {
        "$schema": CONTAINER_SCHEMA,
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": z,
            "width": width,
            "height": height,
            "tabOrder": tab_order
        },
        "visual": {
            "visualType": "barChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": cat_projection
                    },
                    "Y": {
                        "projections": y_projections
                    }
                }
            },
            "objects": {
                "title": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                        }
                    }
                ]
            },
            "drillFilterOtherVisuals": True
        }
    }

def save_page_and_visuals(page_name, display_name, visuals):
    page_dir = PAGES_ROOT / page_name
    visuals_dir = page_dir / "visuals"
    visuals_dir.mkdir(parents=True, exist_ok=True)

    # page.json
    page_json = {
        "$schema": PAGE_SCHEMA,
        "name": page_name,
        "displayName": display_name,
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920
    }
    with open(page_dir / "page.json", "w", encoding="utf-8") as f:
        json.dump(page_json, f, indent=2, ensure_ascii=False)

    # visuals
    for vis in visuals:
        v_name = vis["name"]
        v_dir = visuals_dir / v_name
        v_dir.mkdir(parents=True, exist_ok=True)
        with open(v_dir / "visual.json", "w", encoding="utf-8") as f:
            json.dump(vis, f, indent=2, ensure_ascii=False)

    print(f"  [PAGE] '{display_name}' ({page_name}) saved with {len(visuals)} visuals.")

def build_page_1():
    visuals = []
    # 1. Header Textbox
    header_paragraphs = [
        {
            "textRuns": [
                {
                    "value": "UNIVERSITETET I AGDER — VIRKSOMHETS- OG PROSJEKTOVERSIKT 2026",
                    "textStyle": {
                        "fontFamily": "Segoe UI",
                        "fontSize": "16pt",
                        "fontWeight": "bold",
                        "color": "#0f172a"
                    }
                }
            ]
        },
        {
            "textRuns": [
                {
                    "value": "Rullet lederoversikt pr. 30.09.2026 (YTD Q3) | Regnskap, Prognose (EAC), EVM Prosjektkontroll, Bemanning & Studieproduksjon",
                    "textStyle": {
                        "fontFamily": "Segoe UI",
                        "fontSize": "10pt",
                        "color": "#64748b"
                    }
                }
            ]
        }
    ]
    visuals.append(create_textbox_visual("vis_hdr_title", 20, 20, 1300, 75, 10, header_paragraphs, 1))
    visuals.append(create_slicer_visual("vis_slc_enhet", 1340, 20, 320, 75, 15, "DimOrganization", "Enhet", "Filtrer Enhet", 2))
    visuals.append(create_slicer_visual("vis_slc_kvartal", 1680, 20, 220, 75, 16, "DimDate", "Kvartal", "Kvartal", 3))

    # 2. KPI Cards Row
    kpis = [
        ("vis_kpi_actual_ytd", 20, "Actual YTD", "REGNSKAP YTD (MNOK)", 4),
        ("vis_kpi_eac", 399, "Forecast LE (EAC)", "PROGNOSE ÅRSSLUTT - EAC (MNOK)", 5),
        ("vis_kpi_vac", 778, "Sluttavvik (VAC)", "SLUTTAVVIK - VAC (MNOK)", 6),
        ("vis_kpi_cpi", 1157, "CPI", "EVM KOSTNADSINDEKS (CPI)", 7),
        ("vis_kpi_aarsverk", 1536, "Totale Årsverk", "AKTIVE ÅRSVERK (FTE)", 8),
    ]
    for vname, vx, mname, title, tab in kpis:
        visuals.append(create_card_visual(vname, vx, 110, 364, 100, 20, mname, title, tab))

    # 3. Middle Section: Table & EVM S-Curve
    table_fields = [
        {"type": "Column", "entity": "DimOrganization", "property": "Kortnavn", "label": "Enhet"},
        {"type": "Measure", "entity": "_Measures", "property": "Budsjett YTD", "label": "Budsjett YTD (MNOK)"},
        {"type": "Measure", "entity": "_Measures", "property": "Actual YTD", "label": "Regnskap YTD (MNOK)"},
        {"type": "Measure", "entity": "_Measures", "property": "Avvik YTD", "label": "Avvik YTD (MNOK)"},
        {"type": "Measure", "entity": "_Measures", "property": "Avvik YTD %", "label": "Avvik %"},
        {"type": "Measure", "entity": "_Measures", "property": "Årsbudsjett (BAC)", "label": "Årsbudsjett BAC"},
        {"type": "Measure", "entity": "_Measures", "property": "Forecast LE (EAC)", "label": "Prognose EAC"},
        {"type": "Measure", "entity": "_Measures", "property": "Sluttavvik (VAC)", "label": "Sluttavvik VAC"},
        {"type": "Measure", "entity": "_Measures", "property": "CPI", "label": "CPI"},
        {"type": "Measure", "entity": "_Measures", "property": "SPI", "label": "SPI"},
        {"type": "Measure", "entity": "_Measures", "property": "Forecast RAG Status", "label": "Status"}
    ]
    visuals.append(create_table_visual("vis_tbl_hovedoversikt", 20, 230, 1180, 430, 30, table_fields, "Total KPI-Oversikt per Fakultet og Enhet (MNOK / Indeks)", 9))

    scurve_cat = {"entity": "DimDate", "property": "MaanedNavn", "label": "Måned"}
    scurve_measures = [
        {"entity": "_Measures", "property": "Planned Value (PV)", "label": "PV (Planlagt)"},
        {"entity": "_Measures", "property": "Earned Value (EV)", "label": "EV (Opptjent)"},
        {"entity": "_Measures", "property": "Actual Cost (AC)", "label": "AC (Faktisk)"}
    ]
    visuals.append(create_line_chart_visual("vis_cht_evm_scurve", 1220, 230, 680, 430, 31, scurve_cat, scurve_measures, "EVM S-Kurve Trend 2026: Planlagt (PV) vs Opptjent (EV) vs Faktisk (AC)", 10))

    # 4. Lower Section
    bemanning_cat = {"entity": "DimOrganization", "property": "Kortnavn", "label": "Enhet"}
    bemanning_measures = [
        {"entity": "_Measures", "property": "Faglige Årsverk (UF)", "label": "Faglige årsverk (UF)"},
        {"entity": "_Measures", "property": "Teknisk-Admin Årsverk (TA)", "label": "Teknisk-administrative (TA)"}
    ]
    visuals.append(create_bar_chart_visual("vis_cht_bemanning", 20, 680, 930, 370, 40, bemanning_cat, bemanning_measures, "Bemanningsfordeling: Faglige årsverk (UF) vs Teknisk-Administrative (TA)", 11))

    cost_cat = {"entity": "DimAccountHierarchy", "property": "Nivaa1_Navn", "label": "Kontokategori"}
    cost_measures = [
        {"entity": "_Measures", "property": "Avvik YTD", "label": "Avvik YTD (MNOK)"}
    ]
    visuals.append(create_bar_chart_visual("vis_cht_avvik_art", 970, 680, 930, 370, 41, cost_cat, cost_measures, "Regnskapsavvik YTD fordelt på Hovedartskontoer (MNOK)", 12))

    save_page_and_visuals("0a6c532bb128ac39b432", "Virksomhets- og Prosjektoversikt 2026", visuals)

def build_page_2():
    visuals = []
    # 1. Header Textbox
    header_paragraphs = [
        {
            "textRuns": [
                {
                    "value": "UNIVERSITETET I AGDER — PROSJEKTSTYRING & EVM DYBDEANALYSE 2026",
                    "textStyle": {
                        "fontFamily": "Segoe UI",
                        "fontSize": "16pt",
                        "fontWeight": "bold",
                        "color": "#0f172a"
                    }
                }
            ]
        },
        {
            "textRuns": [
                {
                    "value": "Earned Value Management (EVM), kumulativ fremdrift, kostnads- og tidsavvik (CV/SV) og SRS 10 BOA-oppfølging",
                    "textStyle": {
                        "fontFamily": "Segoe UI",
                        "fontSize": "10pt",
                        "color": "#64748b"
                    }
                }
            ]
        }
    ]
    visuals.append(create_textbox_visual("vis2_hdr_title", 20, 20, 1300, 75, 10, header_paragraphs, 1))
    visuals.append(create_slicer_visual("vis2_slc_enhet", 1340, 20, 320, 75, 15, "DimOrganization", "Enhet", "Filtrer Enhet", 2))
    visuals.append(create_slicer_visual("vis2_slc_kvartal", 1680, 20, 220, 75, 16, "DimDate", "Kvartal", "Kvartal", 3))

    # 2. EVM KPI Cards Row
    kpis = [
        ("vis2_kpi_ev", 20, "Earned Value (EV)", "OPPTJENT VERDI - EV (MNOK)", 4),
        ("vis2_kpi_ac", 399, "Actual Cost (AC)", "FAKTISK KOSTNAD - AC (MNOK)", 5),
        ("vis2_kpi_cv", 778, "Cost Variance (CV)", "KOSTNADSAVVIK - CV (MNOK)", 6),
        ("vis2_kpi_sv", 1157, "Schedule Variance (SV)", "TIDSAVVIK - SV (MNOK)", 7),
        ("vis2_kpi_tcpi", 1536, "TCPI (To-Complete Performance Index)", "TCPI (INDEKS FOR Å NÅ BUDSJETT)", 8),
    ]
    for vname, vx, mname, title, tab in kpis:
        visuals.append(create_card_visual(vname, vx, 110, 364, 100, 20, mname, title, tab))

    # 3. Middle Section: Full S-Curve and Index Trend
    scurve_cat = {"entity": "DimDate", "property": "MaanedNavn", "label": "Måned"}
    scurve_measures = [
        {"entity": "_Measures", "property": "Planned Value (PV)", "label": "PV (Planlagt)"},
        {"entity": "_Measures", "property": "Earned Value (EV)", "label": "EV (Opptjent)"},
        {"entity": "_Measures", "property": "Actual Cost (AC)", "label": "AC (Faktisk)"},
        {"entity": "_Measures", "property": "Årsbudsjett (BAC)", "label": "BAC (Totalramme)"}
    ]
    visuals.append(create_line_chart_visual("vis2_cht_scurve_full", 20, 230, 1180, 430, 30, scurve_cat, scurve_measures, "Kumulativ EVM S-Kurve 2026: Planlagt (PV) vs Opptjent (EV) vs Faktisk (AC) vs BAC", 9))

    index_cat = {"entity": "DimDate", "property": "MaanedNavn", "label": "Måned"}
    index_measures = [
        {"entity": "_Measures", "property": "CPI", "label": "CPI (Kostnadseffektivitet)"},
        {"entity": "_Measures", "property": "SPI", "label": "SPI (Fremdriftseffektivitet)"}
    ]
    visuals.append(create_line_chart_visual("vis2_cht_index_trend", 1220, 230, 680, 430, 31, index_cat, index_measures, "Prestasjonsindekser over tid: CPI & SPI (Mål: >= 1.00)", 10))

    # 4. Lower Section: Variance Trend & Month Matrix Table
    var_cat = {"entity": "DimDate", "property": "MaanedNavn", "label": "Måned"}
    var_measures = [
        {"entity": "_Measures", "property": "Cost Variance (CV)", "label": "Kostnadsavvik CV (MNOK)"},
        {"entity": "_Measures", "property": "Schedule Variance (SV)", "label": "Tidsavvik SV (MNOK)"}
    ]
    visuals.append(create_bar_chart_visual("vis2_cht_var_trend", 20, 680, 930, 370, 40, var_cat, var_measures, "Månedlig avviksutvikling: Kostnadsavvik (CV) vs Tidsavvik (SV)", 11))

    matrix_fields = [
        {"type": "Column", "entity": "DimDate", "property": "MaanedNavn", "label": "Måned"},
        {"type": "Measure", "entity": "_Measures", "property": "Planned Value (PV)", "label": "PV (MNOK)"},
        {"type": "Measure", "entity": "_Measures", "property": "Earned Value (EV)", "label": "EV (MNOK)"},
        {"type": "Measure", "entity": "_Measures", "property": "Actual Cost (AC)", "label": "AC (MNOK)"},
        {"type": "Measure", "entity": "_Measures", "property": "Cost Variance (CV)", "label": "CV (MNOK)"},
        {"type": "Measure", "entity": "_Measures", "property": "Schedule Variance (SV)", "label": "SV (MNOK)"},
        {"type": "Measure", "entity": "_Measures", "property": "CPI", "label": "CPI"},
        {"type": "Measure", "entity": "_Measures", "property": "SPI", "label": "SPI"},
        {"type": "Measure", "entity": "_Measures", "property": "EAC (EVM)", "label": "EAC (MNOK)"},
        {"type": "Measure", "entity": "_Measures", "property": "VAC (EVM)", "label": "VAC (MNOK)"}
    ]
    visuals.append(create_table_visual("vis2_tbl_evm_matrix", 970, 680, 930, 370, 41, matrix_fields, "Månedlig EVM Styringsmatrise (MNOK og Indekser)", 12))

    save_page_and_visuals("page_evm_deepdive", "Prosjektstyring & EVM Dybde", visuals)

def build_page_3():
    visuals = []
    # 1. Header Textbox
    header_paragraphs = [
        {
            "textRuns": [
                {
                    "value": "UNIVERSITETET I AGDER — FAKULTETSANALYSE: BEMANNING & STUDIEPRODUKSJON",
                    "textStyle": {
                        "fontFamily": "Segoe UI",
                        "fontSize": "16pt",
                        "fontWeight": "bold",
                        "color": "#0f172a"
                    }
                }
            ]
        },
        {
            "textRuns": [
                {
                    "value": "Stillingsstruktur (UF/TA), kapasitetsutnyttelse, studentproduksjon (SPE60) og KD Resultatfinansiering",
                    "textStyle": {
                        "fontFamily": "Segoe UI",
                        "fontSize": "10pt",
                        "color": "#64748b"
                    }
                }
            ]
        }
    ]
    visuals.append(create_textbox_visual("vis3_hdr_title", 20, 20, 1540, 75, 10, header_paragraphs, 1))
    visuals.append(create_slicer_visual("vis3_slc_enhet", 1580, 20, 320, 75, 15, "DimOrganization", "Enhet", "Filtrer Enhet", 2))

    # 2. Staffing & Production KPI Cards Row
    kpis = [
        ("vis3_kpi_total_fte", 20, "Totale Årsverk", "TOTALE ÅRSVERK (FTE)", 3),
        ("vis3_kpi_uf_fte", 399, "Faglige Årsverk (UF)", "FAGLIGE ÅRSVERK (UF)", 4),
        ("vis3_kpi_uf_pct", 778, "Faglig Andel %", "FAGLIG ANDEL (MÅL: >= 60%)", 5),
        ("vis3_kpi_students", 1157, "Registrerte Studenter", "REGISTRERTE STUDENTER", 6),
        ("vis3_kpi_spe60", 1536, "Avlagte SPE60", "AVLAGTE SPE60 (HELÅRSSTUDENTER)", 7),
    ]
    for vname, vx, mname, title, tab in kpis:
        visuals.append(create_card_visual(vname, vx, 110, 364, 100, 20, mname, title, tab))

    # 3. Middle Section: Faculty Matrix Table & Student/UF Ratio Chart
    fac_table_fields = [
        {"type": "Column", "entity": "DimOrganization", "property": "Kortnavn", "label": "Enhet"},
        {"type": "Measure", "entity": "_Measures", "property": "Totale Årsverk", "label": "Totale Årsverk"},
        {"type": "Measure", "entity": "_Measures", "property": "Faglige Årsverk (UF)", "label": "Faglig (UF)"},
        {"type": "Measure", "entity": "_Measures", "property": "Teknisk-Admin Årsverk (TA)", "label": "Teknisk-Admin (TA)"},
        {"type": "Measure", "entity": "_Measures", "property": "Faglig Andel %", "label": "Faglig Andel %"},
        {"type": "Measure", "entity": "_Measures", "property": "Registrerte Studenter", "label": "Studenter"},
        {"type": "Measure", "entity": "_Measures", "property": "Avlagte SPE60", "label": "SPE60"},
        {"type": "Measure", "entity": "_Measures", "property": "Studenter pr UF-Årsverk", "label": "Studenter / UF"},
        {"type": "Measure", "entity": "_Measures", "property": "Enhetskostnad pr SPE60", "label": "Kr / SPE60"},
        {"type": "Measure", "entity": "_Measures", "property": "KD Resultatbevilgning MNOK", "label": "KD Bevilgning (MNOK)"}
    ]
    visuals.append(create_table_visual("vis3_tbl_faculty_kpi", 20, 230, 1180, 430, 30, fac_table_fields, "Fakultetsoversikt: Bemanning, Produksjon og Finansiering", 8))

    ratio_cat = {"entity": "DimOrganization", "property": "Kortnavn", "label": "Enhet"}
    ratio_measures = [
        {"entity": "_Measures", "property": "Studenter pr UF-Årsverk", "label": "Studenter pr UF-årsverk"}
    ]
    visuals.append(create_bar_chart_visual("vis3_cht_student_ratio", 1220, 230, 680, 430, 31, ratio_cat, ratio_measures, "Studenter pr. Faglig Årsverk (UF-ratio) per Fakultet", 9))

    # 4. Lower Section: KD Grant & Unit Cost
    kd_cat = {"entity": "DimOrganization", "property": "Kortnavn", "label": "Enhet"}
    kd_measures = [
        {"entity": "_Measures", "property": "KD Resultatbevilgning MNOK", "label": "KD Resultatfinansiering (MNOK)"}
    ]
    visuals.append(create_bar_chart_visual("vis3_cht_kd_bevilgning", 20, 680, 930, 370, 40, kd_cat, kd_measures, "Estimert KD Resultatbevilgning 2025/2026 (MNOK)", 10))

    cost_cat = {"entity": "DimOrganization", "property": "Kortnavn", "label": "Enhet"}
    cost_measures = [
        {"entity": "_Measures", "property": "Enhetskostnad pr SPE60", "label": "Enhetskostnad pr SPE60 (NOK)"}
    ]
    visuals.append(create_bar_chart_visual("vis3_cht_unit_cost", 970, 680, 930, 370, 41, cost_cat, cost_measures, "Beregnet Enhetskostnad pr. Avlagt SPE60 (Kroner)", 11))

    save_page_and_visuals("page_faculty_education", "Bemanning & Studieproduksjon", visuals)

def update_pages_metadata():
    pages_meta = {
        "$schema": PAGES_META_SCHEMA,
        "pageOrder": [
            "0a6c532bb128ac39b432",
            "page_evm_deepdive",
            "page_faculty_education"
        ],
        "activePageName": "0a6c532bb128ac39b432"
    }
    with open(PAGES_META_FILE, "w", encoding="utf-8") as f:
        json.dump(pages_meta, f, indent=2, ensure_ascii=False)
    print(f"\n[METADATA] Updated {PAGES_META_FILE} with 3 pages in sequence.")

if __name__ == "__main__":
    print("=" * 80)
    print("BYGGER ALLE POWER BI RAPPORTSIDER (PBIR FORMAT)...")
    print("=" * 80)
    build_page_1()
    build_page_2()
    build_page_3()
    update_pages_metadata()
    print("=" * 80)
    print("ALLE RAPPORTSIDER FULLFØRT UTEN AVBRUDD!")
    print("=" * 80)
