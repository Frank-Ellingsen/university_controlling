"""
Script: generate_pbir_visuals.py
Generates the PBIR (Power BI Enhanced Report format) visual containers for:
Page 1: 'Virksomhets- og Prosjektoversikt 2026' (Rolled-up Executive Overview of Total KPIs)
Strictly adheres to Edward Tufte's Data-Ink ratio principles.
"""

import json
import os
from pathlib import Path

BASE_DIR = Path(r"c:\Users\frank\Desktop\UIA2")
PAGE_DIR = BASE_DIR / "UIA-project-2026YTD.Report" / "definition" / "pages" / "0a6c532bb128ac39b432"
VISUALS_DIR = PAGE_DIR / "visuals"

SCHEMA_URL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json"

def create_textbox_visual(name, x, y, width, height, z, paragraphs, tab_order=1):
    return {
        "$schema": SCHEMA_URL,
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
        "$schema": SCHEMA_URL,
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
            },
            "drillFilterOtherVisuals": True
        }
    }

def create_slicer_visual(name, x, y, width, height, z, entity, column_name, title_text, tab_order=1):
    return {
        "$schema": SCHEMA_URL,
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
        "$schema": SCHEMA_URL,
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
        "$schema": SCHEMA_URL,
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
        "$schema": SCHEMA_URL,
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

def build_all_visuals():
    VISUALS_DIR.mkdir(parents=True, exist_ok=True)
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

    # 2. Slicers
    visuals.append(create_slicer_visual("vis_slc_enhet", 1340, 20, 320, 75, 15, "DimOrganization", "Enhet", "Filtrer Enhet", 2))
    visuals.append(create_slicer_visual("vis_slc_kvartal", 1680, 20, 220, 75, 16, "DimDate", "Kvartal", "Kvartal", 3))

    # 3. KPI Cards Row (Y: 110 to 220, w: 364 each)
    kpis = [
        ("vis_kpi_actual_ytd", 20, "Actual YTD", "REGNSKAP YTD (MNOK)", 4),
        ("vis_kpi_eac", 399, "Forecast LE (EAC)", "PROGNOSE ÅRSSLUTT - EAC (MNOK)", 5),
        ("vis_kpi_vac", 778, "Sluttavvik (VAC)", "SLUTTAVVIK - VAC (MNOK)", 6),
        ("vis_kpi_cpi", 1157, "CPI", "EVM KOSTNADSINDEKS (CPI)", 7),
        ("vis_kpi_aarsverk", 1536, "Totale Årsverk", "AKTIVE ÅRSVERK (FTE)", 8),
    ]
    for vname, vx, mname, title, tab in kpis:
        visuals.append(create_card_visual(vname, vx, 110, 364, 100, 20, mname, title, tab))

    # 4. Middle Section:
    # 4a. Total KPI-Oversikt Table (tableEx)
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

    # 4b. EVM S-Curve (lineChart)
    scurve_cat = {"entity": "DimDate", "property": "MaanedNavn", "label": "Måned"}
    scurve_measures = [
        {"entity": "_Measures", "property": "Planned Value (PV)", "label": "PV (Planlagt)"},
        {"entity": "_Measures", "property": "Earned Value (EV)", "label": "EV (Opptjent)"},
        {"entity": "_Measures", "property": "Actual Cost (AC)", "label": "AC (Faktisk)"}
    ]
    visuals.append(create_line_chart_visual("vis_cht_evm_scurve", 1220, 230, 680, 430, 31, scurve_cat, scurve_measures, "EVM S-Kurve Trend 2026: Planlagt (PV) vs Opptjent (EV) vs Faktisk (AC)", 10))

    # 5. Lower Section:
    # 5a. Staffing Breakdown Bar Chart
    bemanning_cat = {"entity": "DimOrganization", "property": "Kortnavn", "label": "Enhet"}
    bemanning_measures = [
        {"entity": "_Measures", "property": "Faglige Årsverk (UF)", "label": "Faglige årsverk (UF)"},
        {"entity": "_Measures", "property": "Teknisk-Admin Årsverk (TA)", "label": "Teknisk-administrative (TA)"}
    ]
    visuals.append(create_bar_chart_visual("vis_cht_bemanning", 20, 680, 930, 370, 40, bemanning_cat, bemanning_measures, "Bemanningsfordeling: Faglige årsverk (UF) vs Teknisk-Administrative (TA)", 11))

    # 5b. Cost Variance Breakdown by Category
    cost_cat = {"entity": "DimAccountHierarchy", "property": "Nivaa1_Navn", "label": "Kontokategori"}
    cost_measures = [
        {"entity": "_Measures", "property": "Avvik YTD", "label": "Avvik YTD (MNOK)"}
    ]
    visuals.append(create_bar_chart_visual("vis_cht_avvik_art", 970, 680, 930, 370, 41, cost_cat, cost_measures, "Regnskapsavvik YTD fordelt på Hovedartskontoer (MNOK)", 12))

    # Write each visual to its own folder
    for vis in visuals:
        v_name = vis["name"]
        v_dir = VISUALS_DIR / v_name
        v_dir.mkdir(parents=True, exist_ok=True)
        v_file = v_dir / "visual.json"
        with open(v_file, "w", encoding="utf-8") as f:
            json.dump(vis, f, indent=2, ensure_ascii=False)
        print(f"Created visual: {v_name} -> {v_file}")

    # Update page.json displayName
    page_json_file = PAGE_DIR / "page.json"
    with open(page_json_file, "r", encoding="utf-8") as f:
        page_data = json.load(f)
    page_data["displayName"] = "Virksomhets- og Prosjektoversikt 2026"
    with open(page_json_file, "w", encoding="utf-8") as f:
        json.dump(page_data, f, indent=2, ensure_ascii=False)
    print(f"Updated page.json with displayName: {page_data['displayName']}")

if __name__ == "__main__":
    build_all_visuals()
