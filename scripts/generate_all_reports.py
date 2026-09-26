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
    # 1. Header Textbox (Matching Styrenotat and PDF Title Slide)
    header_paragraphs = [
        {
            "textRuns": [
                {
                    "value": "ØKONOMISK STATUS OG HELÅRSPROGNOSE 2026 — BESLUTNINGSGRUNNLAG FOR UNIVERSITETSSTYRET",
                    "textStyle": {
                        "fontFamily": "Segoe UI",
                        "fontSize": "15pt",
                        "fontWeight": "bold",
                        "color": "#0f172a"
                    }
                }
            ]
        },
        {
            "textRuns": [
                {
                    "value": "En diagnostisk gjennomgang av faktisk innføring, ressursforbruk og iverksatte omstillingstiltak | Status pr. M09 (30.09.2026)",
                    "textStyle": {
                        "fontFamily": "Segoe UI",
                        "fontSize": "10pt",
                        "fontWeight": "bold",
                        "color": "#334155"
                    }
                }
            ]
        },
        {
            "textRuns": [
                {
                    "value": "Rapporteringsansvarlig: Virksomhetsstyring og Økonomi | Universitetet i Agder | Framlegg for: Universitetsstyret 15.10.2026",
                    "textStyle": {
                        "fontFamily": "Segoe UI",
                        "fontSize": "8.5pt",
                        "color": "#64748b"
                    }
                }
            ]
        }
    ]
    visuals.append(create_textbox_visual("vis_hdr_board_title", 20, 12, 1280, 80, 10, header_paragraphs, 1))
    visuals.append(create_slicer_visual("vis_slc_enhet", 1315, 12, 345, 80, 15, "DimOrganization", "Enhet", "Filtrer Enhet", 2))
    visuals.append(create_slicer_visual("vis_slc_kvartal", 1675, 12, 225, 80, 16, "DimDate", "Kvartal", "Kvartal", 3))

    # 2. Strategic Executive Summary Banner (Translating Section 1 of Styrenotat & Slide 2/3 of PDF)
    summary_paragraphs = [
        {
            "textRuns": [
                {
                    "value": "STRATEGISK DIAGNOSE M09: NETTO NEGATIVT SLUTTAVVIK PÅ -11,0 MNOK MOT BAC (VEDTATT RAMME 1 433 MNOK VS EAC 1 444 MNOK)",
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
                    "value": "• KD 2025 Ny Modell: Basisbevilgningen (1 234 MNOK) ligger fast. Statlig risiko er flyttet til UiA; marginale endringer i produksjon slår direkte inn i bunnlinjen.\n• Tre Kritiske Avviksdrivere: 1) Svikt i studiepoeng ved SAM (prosjekt I013BA). 2) Praksisunderfinansiering ved HEL (RETHOS overstiger marginal sats). 3) Fremdriftsavvik i BOA med TDI-overheadtap (CPI 0,95 / SPI 0,92 iht. SRS 10).\n• Iverksatte Omstillingstiltak (FactAction): -15,0 MNOK planlagt | -9,0 MNOK sikret per M09 | Udekket gap: 2,0 MNOK krever skjerpet vakansestyring i Q4.",
                    "textStyle": {
                        "fontFamily": "Segoe UI",
                        "fontSize": "8.5pt",
                        "color": "#1e293b"
                    }
                }
            ]
        }
    ]
    visuals.append(create_textbox_visual("vis_txt_exec_summary", 20, 98, 1880, 96, 18, summary_paragraphs, 4))

    # 3. Executive KPI Cards Row (The Board Big 5)
    kpis = [
        ("vis_kpi_bac", 20, "Årsbudsjett (BAC)", "BAC — VEDTATT ÅRSRAMME 2026 (MNOK)", 5),
        ("vis_kpi_eac", 400, "Forecast LE (EAC)", "EAC — PROGNOSE SLUTTKOSTNAD (MNOK)", 6),
        ("vis_kpi_vac", 780, "Sluttavvik (VAC)", "NETTO AVVIK / VAC (MNOK)", 7),
        ("vis_kpi_lonnsandel", 1160, "Lønnsandel %", "LØNNSANDEL % (SEKTORMÅL: 71,0 %)", 8),
        ("vis_kpi_omstilling_gap", 1540, "Omstilling Udekket Gap", "UDEKKET OMSTILLINGSGAP (MNOK)", 9),
    ]
    for vname, vx, mname, title, tab in kpis:
        visuals.append(create_card_visual(vname, vx, 202, 360, 96, 20, mname, title, tab))

    # 4. Middle Section: Strategic Faculty Diagnostic Table & EVM S-Curve
    table_fields = [
        {"type": "Column", "entity": "DimOrganization", "property": "Kortnavn", "label": "Enhet"},
        {"type": "Measure", "entity": "_Measures", "property": "Avvikstype", "label": "Avvikstype"},
        {"type": "Measure", "entity": "_Measures", "property": "Budsjett YTD", "label": "Budsjett YTD"},
        {"type": "Measure", "entity": "_Measures", "property": "Actual YTD", "label": "Regnskap YTD"},
        {"type": "Measure", "entity": "_Measures", "property": "Avvik YTD", "label": "Avvik YTD"},
        {"type": "Measure", "entity": "_Measures", "property": "Forecast LE (EAC)", "label": "Prognose EAC"},
        {"type": "Measure", "entity": "_Measures", "property": "Sluttavvik (VAC)", "label": "Sluttavvik VAC"},
        {"type": "Measure", "entity": "_Measures", "property": "Diagnose og Drivere", "label": "Analyse og Drivere (Styrenotat §3)"},
        {"type": "Measure", "entity": "_Measures", "property": "Styrenotat Status RAG", "label": "Status"}
    ]
    visuals.append(create_table_visual("vis_tbl_styrenotat_fakultet", 20, 306, 1190, 380, 30, table_fields, "Fakultetsvis Avviksanalyse & Status M09 (Styrenotat Tabell 3: Enhetsvis gjennomgang)", 10))

    scurve_cat = {"entity": "DimDate", "property": "MaanedNavn", "label": "Måned"}
    scurve_measures = [
        {"entity": "_Measures", "property": "Planned Value (PV)", "label": "PV (Planlagt)"},
        {"entity": "_Measures", "property": "Earned Value (EV)", "label": "EV (Opptjent)"},
        {"entity": "_Measures", "property": "Actual Cost (AC)", "label": "AC (Faktisk)"}
    ]
    visuals.append(create_line_chart_visual("vis_cht_evm_scurve", 1225, 306, 675, 380, 31, scurve_cat, scurve_measures, "EVM S-Kurve Trend 2026: BOA-portefølje [CPI: 0,95 TDI-fellen | SPI: 0,92 SRS 10 Risiko]", 11))

    # 5. Lower Section: Kapasitetsstyring & Action Tracker
    bemanning_cat = {"entity": "DimOrganization", "property": "Kortnavn", "label": "Enhet"}
    bemanning_measures = [
        {"entity": "_Measures", "property": "Faglige Årsverk (UF)", "label": "Faglige årsverk (UF)"},
        {"entity": "_Measures", "property": "Teknisk-Admin Årsverk (TA)", "label": "Teknisk-administrative (TA)"}
    ]
    visuals.append(create_bar_chart_visual("vis_cht_bemanning", 20, 694, 910, 374, 40, bemanning_cat, bemanning_measures, "Kapasitetsstyring: Faglige årsverk (UF: 57,1 % / Mål >50 %) vs Teknisk-Administrative (TA)", 12))

    action_table_fields = [
        {"type": "Column", "entity": "FactAction", "property": "TiltakID", "label": "ID"},
        {"type": "Column", "entity": "FactAction", "property": "TiltakNavn", "label": "Tiltak (Beskrivelse)"},
        {"type": "Column", "entity": "FactAction", "property": "ForventetEffekt_MNOK", "label": "Planlagt (MNOK)"},
        {"type": "Column", "entity": "FactAction", "property": "RealisertEffekt_MNOK", "label": "Realisert (MNOK)"},
        {"type": "Column", "entity": "FactAction", "property": "Frist", "label": "Frist"},
        {"type": "Column", "entity": "FactAction", "property": "Status", "label": "Status"},
        {"type": "Column", "entity": "FactAction", "property": "Ansvarlig", "label": "Ansvarlig"},
        {"type": "Column", "entity": "FactAction", "property": "RAG_Status", "label": "RAG"}
    ]
    visuals.append(create_table_visual("vis_tbl_action_tracker", 945, 694, 955, 374, 41, action_table_fields, "Handlingsplan og Omstillingstiltak (Action Tracker iht. Styrenotat §6 & Slide 10: -15M planlagt / -9M realisert)", 13))

    save_page_and_visuals("0a6c532bb128ac39b432", "Økonomisk Status og Helårsprognose 2026", visuals)

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

    # 2. Executive KPI Cards Row (Unit focus pr 30.09.2026)
    kpis = [
        ("vis4_kpi_actual", 20, "Actual YTD", "FAKTISK REGNSKAP YTD (MNOK)", 3),
        ("vis4_kpi_budget", 399, "Budsjett YTD", "PERIODISERT BUDSJETT YTD (MNOK)", 4),
        ("vis4_kpi_avvik", 778, "Avvik YTD", "NETTO AVVIK YTD (MNOK)", 5),
        ("vis4_kpi_eac", 1157, "Forecast LE (EAC)", "PROGNOSE ÅRSSLUTT - EAC (MNOK)", 6),
        ("vis4_kpi_5pct", 1536, "5% Regel Status", "5%-REGEL STATUS (F-05-20)", 7),
    ]
    for vname, vx, mname, title, tab in kpis:
        visuals.append(create_card_visual(vname, vx, 110, 364, 100, 20, mname, title, tab))

    # 3. Middle Section:
    # 3a. Account structure & cost breakdown for the unit
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

    # 3b. Staffing Breakdown for Unit
    bemanning_cat = {"entity": "DimOrganization", "property": "Kortnavn", "label": "Enhet"}
    bemanning_measures = [
        {"entity": "_Measures", "property": "Faglige Årsverk (UF)", "label": "Faglig (UF)"},
        {"entity": "_Measures", "property": "Teknisk-Admin Årsverk (TA)", "label": "Teknisk-Admin (TA)"},
        {"entity": "_Measures", "property": "Vakanser (Ubesatte stillinger)", "label": "Ubesatte Vakanser"}
    ]
    visuals.append(create_bar_chart_visual("vis4_cht_bemanning", 1220, 230, 680, 430, 31, bemanning_cat, bemanning_measures, "Enhetens Stillingsstruktur: UF vs TA vs Vakanser", 9))

    # 4. Lower Section:
    # 4a. Monthly actual vs budget profile
    month_cat = {"entity": "DimDate", "property": "MaanedNavn", "label": "Måned"}
    month_measures = [
        {"entity": "_Measures", "property": "Actual YTD", "label": "Faktisk kostnad YTD"},
        {"entity": "_Measures", "property": "Budsjett YTD", "label": "Budsjett YTD"}
    ]
    visuals.append(create_bar_chart_visual("vis4_cht_month_profile", 20, 680, 930, 370, 40, month_cat, month_measures, "Månedlig Kostnadsprofil vs Budsjett (MNOK)", 10))

    # 4b. Education & BOA Grant Table
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

def update_pages_metadata():
    pages_meta = {
        "$schema": PAGES_META_SCHEMA,
        "pageOrder": [
            "0a6c532bb128ac39b432",
            "page_evm_deepdive",
            "page_faculty_education",
            "page_role_portal"
        ],
        "activePageName": "0a6c532bb128ac39b432"
    }
    with open(PAGES_META_FILE, "w", encoding="utf-8") as f:
        json.dump(pages_meta, f, indent=2, ensure_ascii=False)
    print(f"\n[METADATA] Updated {PAGES_META_FILE} with 4 pages in sequence.")

if __name__ == "__main__":
    print("=" * 80)
    print("BYGGER ALLE POWER BI RAPPORTSIDER (PBIR FORMAT)...")
    print("=" * 80)
    build_page_1()
    build_page_2()
    build_page_3()
    build_page_4()
    update_pages_metadata()
    print("=" * 80)
    print("ALLE RAPPORTSIDER FULLFØRT UTEN AVBRUDD!")
    print("=" * 80)
