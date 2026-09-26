"""
Script: generate_all_reports.py
Generates the complete 5-page Power BI report suite (PBIR format):
- Page 1: 'Virksomhets- og Prosjektoversikt 2026' (Rolled-up Executive KPI Overview & Styrenotat Status)
- Page 2: 'Prosjektstyring & EVM Dybde' (Earned Value Management Deep Dive)
- Page 3: 'Bemanning & Studieproduksjon' (Faculty Staffing, Capacity & Education Production)
- Page 4: 'Rollebasert Lederportal' (Role-based Management Portal with RLS)
- Page 5: 'KPI Katalog & Styringsregler' (Master KPI Catalog, Content Definitions, YoY, MoM & RAG Guide)

Strictly adheres to:
- Edward Tufte's Data-Ink ratio principles (clean fonts, no vertical gridlines, colors for active RAG variances).
- KD 2025 Ny Modell, SRS 10 BOA-opptjening, and F-05-20 5%-avsetningsregel.
- Rich tooltips, explicit Top legends, and card subtitles (YoY, MoM, Content, RAG).
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

def create_card_visual(name, x, y, width, height, z, measure_name, title_text, tab_order=1, subtitle_text=None):
    objects = {
        "title": [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                }
            }
        ],
        "labels": [
            {
                "properties": {
                    "displayUnits": {
                        "expr": {
                            "Literal": {
                                "Value": "0D"
                            }
                        }
                    }
                }
            }
        ]
    }
    if subtitle_text:
        objects["subTitle"] = [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": f"'{subtitle_text}'"}}}
                }
            }
        ]

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
            "objects": objects,
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

def create_line_chart_visual(name, x, y, width, height, z, category_col, measures, title_text, tab_order=1, tooltips=None):
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

    query_state = {
        "Category": {
            "projections": cat_projection
        },
        "Y": {
            "projections": y_projections
        }
    }

    if tooltips:
        tooltip_projections = []
        for t in tooltips:
            if t.get("type") == "Column":
                tooltip_projections.append({
                    "field": {
                        "Column": {
                            "Expression": {"SourceRef": {"Entity": t["entity"]}},
                            "Property": t["property"]
                        }
                    },
                    "queryRef": f"{t['entity']}.{t['property']}",
                    "nativeQueryRef": t.get("label", t["property"]),
                    "active": True
                })
            else:
                tooltip_projections.append({
                    "field": {
                        "Measure": {
                            "Expression": {"SourceRef": {"Entity": t["entity"]}},
                            "Property": t["property"]
                        }
                    },
                    "queryRef": f"{t['entity']}.{t['property']}",
                    "nativeQueryRef": t.get("label", t["property"])
                })
        query_state["Tooltips"] = {"projections": tooltip_projections}

    objects = {
        "title": [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                }
            }
        ],
        "legend": [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "position": {"expr": {"Literal": {"Value": "'Top'"}}}
                }
            }
        ]
    }

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
                "queryState": query_state
            },
            "objects": objects,
            "drillFilterOtherVisuals": True
        }
    }

def create_bar_chart_visual(name, x, y, width, height, z, category_col, measures, title_text, tab_order=1, tooltips=None):
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

    query_state = {
        "Category": {
            "projections": cat_projection
        },
        "Y": {
            "projections": y_projections
        }
    }

    if tooltips:
        tooltip_projections = []
        for t in tooltips:
            if t.get("type") == "Column":
                tooltip_projections.append({
                    "field": {
                        "Column": {
                            "Expression": {"SourceRef": {"Entity": t["entity"]}},
                            "Property": t["property"]
                        }
                    },
                    "queryRef": f"{t['entity']}.{t['property']}",
                    "nativeQueryRef": t.get("label", t["property"]),
                    "active": True
                })
            else:
                tooltip_projections.append({
                    "field": {
                        "Measure": {
                            "Expression": {"SourceRef": {"Entity": t["entity"]}},
                            "Property": t["property"]
                        }
                    },
                    "queryRef": f"{t['entity']}.{t['property']}",
                    "nativeQueryRef": t.get("label", t["property"])
                })
        query_state["Tooltips"] = {"projections": tooltip_projections}

    objects = {
        "title": [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                }
            }
        ],
        "legend": [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "position": {"expr": {"Literal": {"Value": "'Top'"}}}
                }
            }
        ]
    }

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
                "queryState": query_state
            },
            "objects": objects,
            "drillFilterOtherVisuals": True
        }
    }

def save_page_and_visuals(page_name, display_name, visuals):
    page_dir = PAGES_ROOT / page_name
    visuals_dir = page_dir / "visuals"
    visuals_dir.mkdir(parents=True, exist_ok=True)

    # Clean obsolete visual folders
    active_visual_names = {vis["name"] for vis in visuals}
    for existing_item in visuals_dir.iterdir():
        if existing_item.is_dir() and existing_item.name not in active_visual_names:
            import shutil
            shutil.rmtree(existing_item)

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
    # 1. Header Textbox (Matching dashboard_skills.md: UiA Board Executive Dashboard 2026 | Cutoff: 30. Sept 2026)
    header_paragraphs = [
        {
            "textRuns": [
                {
                    "value": "UiA Board Executive Dashboard 2026 — Helårsstatus & Prognose",
                    "textStyle": {
                        "fontFamily": "Segoe UI",
                        "fontSize": "15pt",
                        "fontWeight": "bold",
                        "color": "#1E293B"
                    }
                }
            ]
        },
        {
            "textRuns": [
                {
                    "value": "Cutoff: 30. september 2026 (M09) | Status iht. KD 2025, SRS 10 BOA og F-05-20 (5 %-regelen) | 3-30-300 Styringsmodell",
                    "textStyle": {
                        "fontFamily": "Segoe UI",
                        "fontSize": "9pt",
                        "color": "#64748B"
                    }
                }
            ]
        }
    ]
    visuals.append(create_textbox_visual("vis_hdr_board_title", 20, 15, 1180, 75, 10, header_paragraphs, 1))
    
    # Slicers (Top Right Header as defined in dashboard_skills.md)
    visuals.append(create_slicer_visual("vis_slc_aar", 1220, 15, 200, 75, 15, "DimDate", "Aar", "Regnskapsår", 2))
    visuals.append(create_slicer_visual("vis_slc_maaned", 1440, 15, 220, 75, 16, "DimDate", "MaanedNavn", "Rapporteringsperiode", 3))
    visuals.append(create_slicer_visual("vis_slc_fakultet", 1680, 15, 220, 75, 17, "DimOrganization", "Enhet", "Enhet / Fakultet", 4))

    # 2. Top Section: 5 KPI Cards (3-Second Snapshot, Y = 105 px, Height = 115 px, Width = 360 px each)
    kpis = [
        ("vis_kpi_total_revenue", 20, "Total Inntekt MNOK", "TOTAL INNTEKT (RAMME 2026)", "🟢 Budsj: ▲ +0,0 % | 🟢 YoY: ▲ +3,2 % | MoM: ▲ +2,8 %", 5),
        ("vis_kpi_net_result_vac", 400, "Sluttavvik (VAC)", "NETTO DRIFTSRESULTAT (VAC)", "🔴 Sluttavvik: -11,0 MNOK (-0,8 %) | YTD: -11,0 MNOK (Dekkes av F-05-20)", 6),
        ("vis_kpi_staffing_fte", 780, "Totale Årsverk", "ÅRSVERK & LØNNSANDEL", "🟢 Lønnsandel: 65,4 % | 948 UF / 292 TA | YoY: +12 ÅV", 7),
        ("vis_kpi_evm_cpi", 1160, "CPI", "EVM EFFEKTIVITET (CPI / SPI)", "🟡 CPI: 0,95 | SPI: 0,92 (Tidsfremdrift) | 🔴 5 % Kostnadsoverskridelse", 8),
        ("vis_kpi_students_spe", 1540, "Registrerte Studenter", "STUDENTER & PRODUKSJON (SPE60)", "🟢 10 850 SPE60 | 🟡 14,8 Studenter/UF-ÅV | YoY: ▲ +1,8 %", 9),
    ]
    for vname, vx, mname, title, subtitle, tab in kpis:
        visuals.append(create_card_visual(vname, vx, 105, 360, 115, 20, mname, title, tab, subtitle_text=subtitle))

    # 3. Middle Section: Core Trends & Segmental Analysis (30-Second Insight, Y = 235 px, Height = 400 px)
    # Middle Left (60%, Width = 1120 px, x = 20)
    rev_cost_cat = {"entity": "DimDate", "property": "MaanedNavn", "label": "Måned"}
    rev_cost_measures = [
        {"entity": "_Measures", "property": "Faktiske & Prognostiserte Driftskostnader", "label": "Faktisk/Prognose Kostnad"},
        {"entity": "_Measures", "property": "Budsjett YTD", "label": "Periodisert Budsjett"},
        {"entity": "_Measures", "property": "Cumulative Actual & Forecast", "label": "Kumulativ Faktisk/Prognose"},
        {"entity": "_Measures", "property": "Cumulative Budget", "label": "Kumulativt Budsjett"}
    ]
    rev_cost_tooltips = [
        {"entity": "_Measures", "property": "Avvik YTD", "label": "Avvik YTD"},
        {"entity": "_Measures", "property": "Avvik YTD %", "label": "Avvik %"},
        {"entity": "_Measures", "property": "Actual MoM Endring MNOK", "label": "MoM Endring MNOK"}
    ]
    visuals.append(create_bar_chart_visual("vis_cht_revenue_cost_monthly", 20, 235, 1120, 400, 30, rev_cost_cat, rev_cost_measures, "Månedlig Kostnadsutvikling vs. Budsjett M01–M12 (Faktisk M01-M09 / Q4 Prognose)", 10, tooltips=rev_cost_tooltips))

    # Middle Right (40%, Width = 740 px, x = 1160)
    fac_var_cat = {"entity": "DimOrganization", "property": "Kortnavn", "label": "Fakultet"}
    fac_var_measures = [
        {"entity": "_Measures", "property": "Sluttavvik (VAC)", "label": "Sluttavvik (VAC MNOK)"}
    ]
    fac_var_tooltips = [
        {"entity": "_Measures", "property": "Total Inntekt MNOK", "label": "Total Inntekt"},
        {"entity": "_Measures", "property": "Forecast LE (EAC)", "label": "Prognose (EAC)"},
        {"entity": "_Measures", "property": "Årsbudsjett (BAC)", "label": "Årsbudsjett (BAC)"},
        {"entity": "_Measures", "property": "Forecast RAG Status", "label": "RAG Status"}
    ]
    visuals.append(create_bar_chart_visual("vis_cht_faculty_net_result", 1160, 235, 740, 400, 31, fac_var_cat, fac_var_measures, "Fakultetsvis Netto Sluttavvik (VAC MNOK) — Merforbruk vs. Mindreforbruk", 11, tooltips=fac_var_tooltips))

    # 4. Bottom Section: Detailed Summary & Risk Table (300-Second Deep Dive, Y = 650 px, Height = 410 px, Width = 1880 px)
    matrix_fields = [
        {"type": "Column", "entity": "DimOrganization", "property": "Enhet", "label": "Fakultet / Enhet"},
        {"type": "Measure", "entity": "_Measures", "property": "Total Inntekt MNOK", "label": "Total Inntekt (MNOK)"},
        {"type": "Measure", "entity": "_Measures", "property": "Actual/FC Lønn", "label": "Lønnskostnad (MNOK)"},
        {"type": "Measure", "entity": "_Measures", "property": "Actual/FC Drift", "label": "Driftskostnad (MNOK)"},
        {"type": "Measure", "entity": "_Measures", "property": "Actual/FC Capex", "label": "Investeringer Capex (MNOK)"},
        {"type": "Measure", "entity": "_Measures", "property": "Sluttavvik (VAC)", "label": "Netto Resultat VAC (MNOK)"},
        {"type": "Measure", "entity": "_Measures", "property": "Faglige Årsverk (UF)", "label": "UF-Årsverk"},
        {"type": "Measure", "entity": "_Measures", "property": "Studenter pr UF-Årsverk", "label": "Studenter / UF-ÅV"},
        {"type": "Measure", "entity": "_Measures", "property": "Forecast RAG Status", "label": "RAG Status"},
        {"type": "Measure", "entity": "_Measures", "property": "Diagnose og Drivere", "label": "Strategisk Diagnose"}
    ]
    visuals.append(create_table_visual("vis_tbl_faculty_summary_matrix", 20, 650, 1880, 410, 40, matrix_fields, "Fakultetsoversikt: Totalregnskap, Stillingsstruktur og Styringsdiagnose (300-sekunders dybdeanalyse)", 12))

    save_page_and_visuals("0a6c532bb128ac39b432", "UiA Board Executive Dashboard 2026", visuals)

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

    # 2. EVM KPI Cards Row with Subtitles
    kpis = [
        ("vis2_kpi_ev", 20, "Earned Value (EV)", "OPPTJENT VERDI - EV (MNOK)", "Opptjent produksjon | MoM: +122.5M | SRS 10 BOA | RAG: 🟡", 4),
        ("vis2_kpi_ac", 399, "Actual Cost (AC)", "FAKTISK KOSTNAD - AC (MNOK)", "Faktisk ressursforbruk | MoM: +126.0M | YoY: +5.2% | RAG: 🔴", 5),
        ("vis2_kpi_cv", 778, "Cost Variance (CV)", "KOSTNADSAVVIK - CV (MNOK)", "Kostnadsavvik (EV - AC) | MoM: -3.5M | RAG: 🔴 TDI-tap", 6),
        ("vis2_kpi_sv", 1157, "Schedule Variance (SV)", "TIDSAVVIK - SV (MNOK)", "Fremdriftsavvik (EV - PV) | MoM: -2.0M | RAG: 🔴 Forsinkelse", 7),
        ("vis2_kpi_tcpi", 1536, "TCPI (To-Complete Performance Index)", "TCPI (INDEKS FOR Å NÅ BUDSJETT)", "Nødvendig effektivitet for å nå BAC | Mål: <= 1.00 | RAG: 🔴", 8),
    ]
    for vname, vx, mname, title, subtitle, tab in kpis:
        visuals.append(create_card_visual(vname, vx, 110, 364, 100, 20, mname, title, tab, subtitle_text=subtitle))

    # 3. Middle Section: Full S-Curve and Index Trend
    scurve_cat = {"entity": "DimDate", "property": "MaanedNavn", "label": "Måned"}
    scurve_measures = [
        {"entity": "_Measures", "property": "Planned Value (PV)", "label": "PV (Planlagt)"},
        {"entity": "_Measures", "property": "Earned Value (EV)", "label": "EV (Opptjent)"},
        {"entity": "_Measures", "property": "Actual Cost (AC)", "label": "AC (Faktisk)"},
        {"entity": "_Measures", "property": "Årsbudsjett (BAC)", "label": "BAC (Totalramme)"}
    ]
    scurve_tooltips = [
        {"entity": "_Measures", "property": "Cost Variance (CV)", "label": "Cost Variance (CV)"},
        {"entity": "_Measures", "property": "Schedule Variance (SV)", "label": "Schedule Variance (SV)"},
        {"entity": "_Measures", "property": "CPI", "label": "CPI"},
        {"entity": "_Measures", "property": "SPI", "label": "SPI"},
        {"entity": "_Measures", "property": "EAC (EVM)", "label": "EAC (EVM)"},
        {"entity": "_Measures", "property": "VAC (EVM)", "label": "VAC (EVM)"}
    ]
    visuals.append(create_line_chart_visual("vis2_cht_scurve_full", 20, 230, 1180, 430, 30, scurve_cat, scurve_measures, "Kumulativ EVM S-Kurve 2026: Planlagt (PV) vs Opptjent (EV) vs Faktisk (AC) vs BAC", 9, tooltips=scurve_tooltips))

    index_cat = {"entity": "DimDate", "property": "MaanedNavn", "label": "Måned"}
    index_measures = [
        {"entity": "_Measures", "property": "CPI", "label": "CPI (Kostnadseffektivitet)"},
        {"entity": "_Measures", "property": "SPI", "label": "SPI (Fremdriftseffektivitet)"}
    ]
    index_tooltips = [
        {"entity": "_Measures", "property": "CPI MoM Endring", "label": "CPI MoM Endring"},
        {"entity": "_Measures", "property": "SPI MoM Endring", "label": "SPI MoM Endring"},
        {"entity": "_Measures", "property": "CPI RAG Status", "label": "CPI RAG Status"},
        {"entity": "_Measures", "property": "SPI RAG Status", "label": "SPI RAG Status"}
    ]
    visuals.append(create_line_chart_visual("vis2_cht_index_trend", 1220, 230, 680, 430, 31, index_cat, index_measures, "Prestasjonsindekser over tid: CPI & SPI (Mål: >= 1.00)", 10, tooltips=index_tooltips))

    # 4. Lower Section: Variance Trend & Month Matrix Table
    var_cat = {"entity": "DimDate", "property": "MaanedNavn", "label": "Måned"}
    var_measures = [
        {"entity": "_Measures", "property": "Cost Variance (CV)", "label": "Kostnadsavvik CV (MNOK)"},
        {"entity": "_Measures", "property": "Schedule Variance (SV)", "label": "Tidsavvik SV (MNOK)"}
    ]
    var_tooltips = [
        {"entity": "_Measures", "property": "CPI", "label": "CPI"},
        {"entity": "_Measures", "property": "SPI", "label": "SPI"}
    ]
    visuals.append(create_bar_chart_visual("vis2_cht_var_trend", 20, 680, 930, 370, 40, var_cat, var_measures, "Månedlig avviksutvikling: Kostnadsavvik (CV) vs Tidsavvik (SV)", 11, tooltips=var_tooltips))

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

    # 2. Staffing & Production KPI Cards Row with Subtitles
    kpis = [
        ("vis3_kpi_total_fte", 20, "Totale Årsverk", "TOTALE ÅRSVERK (FTE)", "MoM: +3.0 FTE | YoY: +1.2% | Sektormål: Stramhet | RAG: 🟢", 3),
        ("vis3_kpi_uf_fte", 399, "Faglige Årsverk (UF)", "FAGLIGE ÅRSVERK (UF)", "Vitenskapelig bemanning | MoM: +2.0 FTE | RAG: 🟢", 4),
        ("vis3_kpi_uf_pct", 778, "Faglig Andel %", "FAGLIG ANDEL (MÅL: >= 60%)", "Kapasitetsandel UF | UiA Mål: >= 60.0% | Status: 57.1% | RAG: 🟡", 5),
        ("vis3_kpi_students", 1157, "Registrerte Studenter", "REGISTRERTE STUDENTER", "Total studentmasse | YoY: +0.8% | RAG: 🟢", 6),
        ("vis3_kpi_spe60", 1536, "Avlagte SPE60", "AVLAGTE SPE60 (HELÅRSSTUDENTER)", "Helårsstudiepoeng | YoY: -1.5% svikt SAM/I013BA | RAG: 🔴", 7),
    ]
    for vname, vx, mname, title, subtitle, tab in kpis:
        visuals.append(create_card_visual(vname, vx, 110, 364, 100, 20, mname, title, tab, subtitle_text=subtitle))

    # 3. Middle Section: Faculty Matrix Table & Student/UF Ratio Chart
    fac_table_fields = [
        {"type": "Column", "entity": "DimOrganization", "property": "Kortnavn", "label": "Enhet"},
        {"type": "Measure", "entity": "_Measures", "property": "Totale Årsverk", "label": "Totale Årsverk"},
        {"type": "Measure", "entity": "_Measures", "property": "Faglige Årsverk (UF)", "label": "Faglig (UF)"},
        {"type": "Measure", "entity": "_Measures", "property": "Teknisk-Admin Årsverk (TA)", "label": "Teknisk-Admin (TA)"},
        {"type": "Measure", "entity": "_Measures", "property": "Faglig Andel %", "label": "Faglig Andel %"},
        {"type": "Measure", "entity": "_Measures", "property": "Vakanser (Ubesatte stillinger)", "label": "Vakanser"},
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
    ratio_tooltips = [
        {"entity": "_Measures", "property": "Registrerte Studenter", "label": "Studenter"},
        {"entity": "_Measures", "property": "Faglige Årsverk (UF)", "label": "UF-årsverk"},
        {"entity": "_Measures", "property": "Avlagte SPE60", "label": "Avlagte SPE60"}
    ]
    visuals.append(create_bar_chart_visual("vis3_cht_student_ratio", 1220, 230, 680, 430, 31, ratio_cat, ratio_measures, "Studenter pr. Faglig Årsverk (UF-ratio) per Fakultet", 9, tooltips=ratio_tooltips))

    # 4. Lower Section: KD Grant & Unit Cost
    kd_cat = {"entity": "DimOrganization", "property": "Kortnavn", "label": "Enhet"}
    kd_measures = [
        {"entity": "_Measures", "property": "KD Resultatbevilgning MNOK", "label": "KD Resultatfinansiering (MNOK)"}
    ]
    kd_tooltips = [
        {"entity": "_Measures", "property": "Avlagte SPE60", "label": "Avlagte SPE60"},
        {"entity": "_Measures", "property": "Enhetskostnad pr SPE60", "label": "Kr/SPE60"}
    ]
    visuals.append(create_bar_chart_visual("vis3_cht_kd_bevilgning", 20, 680, 930, 370, 40, kd_cat, kd_measures, "Estimert KD Resultatbevilgning 2025/2026 (MNOK)", 10, tooltips=kd_tooltips))

    cost_cat = {"entity": "DimOrganization", "property": "Kortnavn", "label": "Enhet"}
    cost_measures = [
        {"entity": "_Measures", "property": "Enhetskostnad pr SPE60", "label": "Enhetskostnad pr SPE60 (NOK)"}
    ]
    cost_tooltips = [
        {"entity": "_Measures", "property": "Totale Årsverk", "label": "Totale Årsverk"},
        {"entity": "_Measures", "property": "Avlagte SPE60", "label": "Avlagte SPE60"},
        {"entity": "_Measures", "property": "KD Resultatbevilgning MNOK", "label": "KD Bevilgning"}
    ]
    visuals.append(create_bar_chart_visual("vis3_cht_unit_cost", 970, 680, 930, 370, 41, cost_cat, cost_measures, "Beregnet Enhetskostnad pr. Avlagt SPE60 (Kroner)", 11, tooltips=cost_tooltips))

    save_page_and_visuals("page_faculty_education", "Bemanning & Studieproduksjon", visuals)

def build_page_4():
    visuals = []
    # 1. Header Textbox with Role Context
    header_paragraphs = [
        {
            "textRuns": [
                {
                    "value": "UNIVERSITETET I AGDER — ROLLEBASERT LEDERPORTAL & FAKULTETSSTYRING",
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
                    "value": "Målrettet virksomhets- og økonomioppfølging tilpasset dekaner, fakultetsdirektører og prosjektledere (RLS)",
                    "textStyle": {
                        "fontFamily": "Segoe UI",
                        "fontSize": "10pt",
                        "color": "#64748b"
                    }
                }
            ]
        }
    ]
    visuals.append(create_textbox_visual("vis4_hdr_title", 20, 20, 1400, 75, 10, header_paragraphs, 1))
    visuals.append(create_slicer_visual("vis4_slc_enhet", 1440, 20, 460, 75, 15, "DimOrganization", "Enhet", "Aktiv Enhet (RLS)", 2))

    # 2. Executive KPI Cards Row (Unit focus pr 30.09.2026) with Subtitles
    kpis = [
        ("vis4_kpi_actual", 20, "Actual YTD", "FAKTISK REGNSKAP YTD (MNOK)", "Faktisk regnskap pr M09 | MoM: +3.5M | YoY: +5.2% | RAG: 🔴", 3),
        ("vis4_kpi_budget", 399, "Budsjett YTD", "PERIODISERT BUDSJETT YTD (MNOK)", "Periodisert årsbudsjett pr M09 (75% framdrift) | RAG: 🟢", 4),
        ("vis4_kpi_avvik", 778, "Avvik YTD", "NETTO AVVIK YTD (MNOK)", "Netto forbruksavvik YTD mot ramme | RAG: 🔴 Merforbruk", 5),
        ("vis4_kpi_eac", 1157, "Forecast LE (EAC)", "PROGNOSE ÅRSSLUTT - EAC (MNOK)", "Styrets prognose helår 2026 | VAC: -11.0M | RAG: 🔴", 6),
        ("vis4_kpi_5pct", 1536, "5% Regel Status", "5%-REGEL STATUS (F-05-20)", "Departementets avsetningsgrense | F-05-20 | RAG: 🟢 Innenfor", 7),
    ]
    for vname, vx, mname, title, subtitle, tab in kpis:
        visuals.append(create_card_visual(vname, vx, 110, 364, 100, 20, mname, title, tab, subtitle_text=subtitle))

    # 3. Middle Section:
    cost_table_fields = [
        {"type": "Column", "entity": "DimAccountHierarchy", "property": "Nivaa1_Navn", "label": "Hovedartskonto"},
        {"type": "Column", "entity": "DimAccountHierarchy", "property": "Nivaa2_Navn", "label": "Kontogruppe"},
        {"type": "Measure", "entity": "_Measures", "property": "Budsjett YTD", "label": "Budsjett YTD (MNOK)"},
        {"type": "Measure", "entity": "_Measures", "property": "Actual YTD", "label": "Regnskap YTD (MNOK)"},
        {"type": "Measure", "entity": "_Measures", "property": "Avvik YTD", "label": "Avvik YTD (MNOK)"},
        {"type": "Measure", "entity": "_Measures", "property": "Avvik YTD %", "label": "Avvik %"},
        {"type": "Measure", "entity": "_Measures", "property": "Årsbudsjett (BAC)", "label": "Årsbudsjett BAC"},
        {"type": "Measure", "entity": "_Measures", "property": "Forecast LE (EAC)", "label": "Prognose EAC"},
        {"type": "Measure", "entity": "_Measures", "property": "Sluttavvik (VAC)", "label": "Sluttavvik VAC"}
    ]
    visuals.append(create_table_visual("vis4_tbl_kontostruktur", 20, 230, 1180, 430, 30, cost_table_fields, "Enhetens Kontostruktur og Avviksfordeling (MNOK)", 8))

    bemanning_cat = {"entity": "DimOrganization", "property": "Kortnavn", "label": "Enhet"}
    bemanning_measures = [
        {"entity": "_Measures", "property": "Faglige Årsverk (UF)", "label": "Faglig (UF)"},
        {"entity": "_Measures", "property": "Teknisk-Admin Årsverk (TA)", "label": "Teknisk-Admin (TA)"},
        {"entity": "_Measures", "property": "Vakanser (Ubesatte stillinger)", "label": "Ubesatte Vakanser"}
    ]
    bemanning_tooltips = [
        {"entity": "_Measures", "property": "Totale Årsverk", "label": "Totale Årsverk"},
        {"entity": "_Measures", "property": "Faglig Andel %", "label": "Faglig Andel %"},
        {"entity": "_Measures", "property": "Studenter pr UF-Årsverk", "label": "Studenter / UF"}
    ]
    visuals.append(create_bar_chart_visual("vis4_cht_bemanning", 1220, 230, 680, 430, 31, bemanning_cat, bemanning_measures, "Enhetens Stillingsstruktur: UF vs TA vs Vakanser", 9, tooltips=bemanning_tooltips))

    # 4. Lower Section:
    month_cat = {"entity": "DimDate", "property": "MaanedNavn", "label": "Måned"}
    month_measures = [
        {"entity": "_Measures", "property": "Actual YTD", "label": "Faktisk kostnad YTD"},
        {"entity": "_Measures", "property": "Budsjett YTD", "label": "Budsjett YTD"}
    ]
    month_tooltips = [
        {"entity": "_Measures", "property": "Avvik YTD", "label": "Avvik YTD"},
        {"entity": "_Measures", "property": "Avvik YTD %", "label": "Avvik %"},
        {"entity": "_Measures", "property": "Actual MoM Endring MNOK", "label": "MoM Endring MNOK"}
    ]
    visuals.append(create_bar_chart_visual("vis4_cht_month_profile", 20, 680, 930, 370, 40, month_cat, month_measures, "Månedlig Kostnadsprofil vs Budsjett (MNOK)", 10, tooltips=month_tooltips))

    edu_table_fields = [
        {"type": "Column", "entity": "DimOrganization", "property": "Kortnavn", "label": "Enhet"},
        {"type": "Measure", "entity": "_Measures", "property": "Registrerte Studenter", "label": "Studenter"},
        {"type": "Measure", "entity": "_Measures", "property": "Avlagte SPE60", "label": "Avlagte SPE60"},
        {"type": "Measure", "entity": "_Measures", "property": "Studenter pr UF-Årsverk", "label": "Studenter / UF"},
        {"type": "Measure", "entity": "_Measures", "property": "Enhetskostnad pr SPE60", "label": "Kr / SPE60"},
        {"type": "Measure", "entity": "_Measures", "property": "KD Resultatbevilgning MNOK", "label": "KD Bevilgning (MNOK)"},
        {"type": "Measure", "entity": "_Measures", "property": "BOA Inntekt (NFR/EU)", "label": "BOA Inntekt (MNOK)"}
    ]
    visuals.append(create_table_visual("vis4_tbl_produksjon_boa", 970, 680, 930, 370, 41, edu_table_fields, "Studieproduksjon, Enhetskostnad & BOA Tilskudd (MNOK)", 11))

    save_page_and_visuals("page_role_portal", "Rollebasert Lederportal", visuals)

def build_page_5_kpi_dictionary():
    visuals = []
    # 1. Header Textbox
    header_paragraphs = [
        {
            "textRuns": [
                {
                    "value": "UNIVERSITETET I AGDER — KPI METADATAGUIDE, INNHOLDSDEFINISJONER & STYRINGSREGLER",
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
                    "value": "Fullstendig katalog over samtlige 24 styrings-KPIer: Innhold/formel, KD 2025 regelverk, SRS 10, MoM/YoY referanser og RAG-terskler",
                    "textStyle": {
                        "fontFamily": "Segoe UI",
                        "fontSize": "10pt",
                        "color": "#64748b"
                    }
                }
            ]
        }
    ]
    visuals.append(create_textbox_visual("vis5_hdr_title", 20, 20, 1300, 75, 10, header_paragraphs, 1))
    visuals.append(create_slicer_visual("vis5_slc_gruppe", 1340, 20, 320, 75, 15, "DimKPI", "KPI_Gruppe", "Filtrer Gruppe", 2))
    visuals.append(create_slicer_visual("vis5_slc_rag", 1680, 20, 220, 75, 16, "DimKPI", "RAG_Status", "RAG Filter", 3))

    # 2. Methodology & Regulatory Reference Box
    methodology_paragraphs = [
        {
            "textRuns": [
                {
                    "value": "LOVPÅLAGT RAMMEVERK & DEFINISJONSBASIS FOR ØKONOMISTYRING VED UNIVERSITETET I AGDER",
                    "textStyle": {
                        "fontFamily": "Segoe UI",
                        "fontSize": "10.5pt",
                        "fontWeight": "bold",
                        "color": "#0f172a"
                    }
                }
            ]
        },
        {
            "textRuns": [
                {
                    "value": "• KD 2025 Finansieringsmodell: Ny resultatmodell med faste satser pr. avlagt studiepoeng (SPE60). Historiske overgangsordninger er faset ut; statlig risiko er overført til UiA. Produksjonssvikt i SAM/I013BA gir umiddelbart inntektstap i rammebevilgningen.\n• SRS 10 Opptjeningsprinsipp: Inntektsføring av bidrags- og oppdragsfinansiert aktivitet (BOA) baseres på faktisk prosjektfremdrift (Earned Value). Prosjekter med fremdriftshefte (SPI < 1.00) utløser TDI-overheadsvikt og marginunderskudd.\n• F-05-20 Finansdepartementets 5%-Regel: Netto overføring av ubrukte bevilgninger til påfølgende år kan ikke overskride 5 % av samlet statstilskudd. Netto akkumulerte avsetninger ved UiA utgjør 3,4 % (41,4 MNOK) — tilfredsstillende margin (🟢).\n• RAG-kriterier iht. Edward Tufte: 🟢 Normal drift/iht. ramme | 🟡 Observasjonspost/omstilling under oppfølging | 🔴 Kritisk avvik som krever umiddelbar dekan- og styreaksjon.",
                    "textStyle": {
                        "fontFamily": "Segoe UI",
                        "fontSize": "8.5pt",
                        "color": "#1e293b"
                    }
                }
            ]
        }
    ]
    visuals.append(create_textbox_visual("vis5_txt_regulations", 20, 105, 1880, 100, 18, methodology_paragraphs, 4))

    # 3. Master KPI Catalog Table (Displaying all 12 columns from DimKPI)
    kpi_table_fields = [
        {"type": "Column", "entity": "DimKPI", "property": "KPI_Navn", "label": "KPI Navn"},
        {"type": "Column", "entity": "DimKPI", "property": "KPI_Gruppe", "label": "Gruppe"},
        {"type": "Column", "entity": "DimKPI", "property": "Enhet", "label": "Enhet"},
        {"type": "Column", "entity": "DimKPI", "property": "Innhold_Definisjon", "label": "Innhold & Beregningsmetode (Definisjon)"},
        {"type": "Column", "entity": "DimKPI", "property": "Styringsregel_Maal", "label": "Lovhjemmel / Målverdi"},
        {"type": "Column", "entity": "DimKPI", "property": "MoM_Utvikling", "label": "Måned-til-måned (MoM M09 vs M08)"},
        {"type": "Column", "entity": "DimKPI", "property": "YoY_Vekst", "label": "År-til-år (YoY 2026 vs 2025)"},
        {"type": "Column", "entity": "DimKPI", "property": "RAG_Status", "label": "RAG Status"}
    ]
    visuals.append(create_table_visual("vis5_tbl_master_kpi", 20, 220, 1880, 840, 30, kpi_table_fields, "Master KPI Katalog: Samtlige 24 styringsindikatorer med formler, regler, MoM og YoY referanser", 5))

    save_page_and_visuals("page_kpi_dictionary", "KPI Katalog & Styringsregler", visuals)

def update_pages_metadata():
    pages_meta = {
        "$schema": PAGES_META_SCHEMA,
        "pageOrder": [
            "0a6c532bb128ac39b432",
            "page_evm_deepdive",
            "page_faculty_education",
            "page_role_portal",
            "page_kpi_dictionary"
        ],
        "activePageName": "0a6c532bb128ac39b432"
    }
    with open(PAGES_META_FILE, "w", encoding="utf-8") as f:
        json.dump(pages_meta, f, indent=2, ensure_ascii=False)
    print(f"\n[METADATA] Updated {PAGES_META_FILE} with 5 pages in sequence.")

if __name__ == "__main__":
    print("=" * 80)
    print("BYGGER ALLE 5 POWER BI RAPPORTSIDER (PBIR FORMAT)...")
    print("=" * 80)
    build_page_1()
    build_page_2()
    build_page_3()
    build_page_4()
    build_page_5_kpi_dictionary()
    update_pages_metadata()
    print("=" * 80)
    print("ALLE 5 RAPPORTSIDER FULLFØRT UTEN AVBRUDD!")
    print("=" * 80)
