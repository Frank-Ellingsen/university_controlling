"""
PBIR Report Generator for HHU-Rapport.Report
Generates 7 production-grade PBIR report pages adhering to Edward Tufte Data-Ink Ratio rules
and Frank Ellingsen's Project Controlling standards.
"""
import os
import shutil
import json

HHU_DIR = r"c:\Users\frank\Desktop\UIA2\HHU"
REPORT_DIR = os.path.join(HHU_DIR, "HHU-Rapport.Report")
DEFINITION_DIR = os.path.join(REPORT_DIR, "definition")
PAGES_DIR = os.path.join(DEFINITION_DIR, "pages")
THEME_SRC = r"c:\Users\frank\Desktop\UIA2\powerbi\themes\tufte_minimalist_theme.json"
THEME_DST = os.path.join(REPORT_DIR, "StaticResources", "RegisteredResources", "University-Tufte-Minimalist-20260926.json")

def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def setup_theme_and_report_json():
    os.makedirs(os.path.dirname(THEME_DST), exist_ok=True)
    if os.path.exists(THEME_SRC):
        shutil.copy2(THEME_SRC, THEME_DST)
        print("Copied Tufte Minimalist theme.")

    report_json = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.3.0/schema.json",
        "themeCollection": {
            "baseTheme": {
                "name": "User",
                "reportVersionAtImport": {
                    "visual": "2.12.0",
                    "report": "3.4.0",
                    "page": "2.3.1"
                },
                "type": "RegisteredResources"
            },
            "customTheme": {
                "name": "University-Tufte-Minimalist-20260926",
                "reportVersionAtImport": {
                    "visual": "2.12.0",
                    "report": "3.4.0",
                    "page": "2.3.1"
                },
                "type": "RegisteredResources"
            }
        },
        "objects": {
            "section": [
                {
                    "properties": {
                        "verticalAlignment": {
                            "expr": {
                                "Literal": {
                                    "Value": "'Top'"
                                }
                            }
                        }
                    }
                }
            ]
        },
        "resourcePackages": [
            {
                "name": "RegisteredResources",
                "type": "RegisteredResources",
                "items": [
                    {
                        "name": "University-Tufte-Minimalist-20260926",
                        "path": "University-Tufte-Minimalist-20260926.json",
                        "type": "CustomTheme"
                    }
                ]
            }
        ],
        "settings": {
            "useStylableVisualContainerHeader": True,
            "exportDataMode": "AllowSummarized",
            "defaultDrillFilterOtherVisuals": True,
            "allowChangeFilterTypes": True,
            "useEnhancedTooltips": True,
            "useDefaultAggregateDisplayName": True
        }
    }
    write_json(os.path.join(DEFINITION_DIR, "report.json"), report_json)

def make_title(text):
    return [
        {
            "properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "text": {"expr": {"Literal": {"Value": f"'{text}'"}}}
            }
        }
    ]

def make_legend(position="'Top'"):
    return [
        {
            "properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "position": {"expr": {"Literal": {"Value": position}}}
            }
        }
    ]

def create_textbox_visual(vis_name, x, y, width, height, tab_order, p1_text, p2_text=None):
    runs = [{"value": p1_text, "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "14pt", "fontWeight": "bold", "color": "#0F172A"}}]
    paragraphs = [{"textRuns": runs}]
    if p2_text:
        paragraphs.append({"textRuns": [{"value": p2_text, "textStyle": {"fontFamily": "Segoe UI", "fontSize": "9pt", "color": "#64748B"}}]})
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": vis_name,
        "position": {
            "x": x,
            "y": y,
            "z": 10,
            "height": height,
            "width": width,
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
            }
        }
    }

def create_slicer_visual(vis_name, x, y, width, height, tab_order, entity, column_name, title, mode="Single"):
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": vis_name,
        "position": {
            "x": x,
            "y": y,
            "z": 15,
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
                                        "Expression": {
                                            "SourceRef": {
                                                "Entity": entity
                                            }
                                        },
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
                "data": [
                    {
                        "properties": {
                            "mode": {"expr": {"Literal": {"Value": f"'{mode}'"}}}
                        }
                    }
                ],
                "header": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}
                        }
                    }
                ]
            },
            "drillFilterOtherVisuals": True
        }
    }

def create_card_visual(vis_name, x, y, width, height, tab_order, measure_name, title, subtitle_text=None, accent_color="#10B981"):
    vis = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": vis_name,
        "position": {
            "x": x,
            "y": y,
            "z": 20,
            "height": height,
            "width": width,
            "tabOrder": tab_order
        },
        "visual": {
            "visualType": "cardVisual",
            "query": {
                "queryState": {
                    "Data": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Entity": "_Measures"
                                            }
                                        },
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
                "accentBar": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "position": {"expr": {"Literal": {"Value": "'Left'"}}},
                            "width": {"expr": {"Literal": {"Value": "4D"}}},
                            "color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{accent_color}'"}}}}}
                        },
                        "selector": {"id": "default"}
                    }
                ]
            },
            "visualContainerObjects": {
                "title": make_title(title)
            },
            "drillFilterOtherVisuals": True
        }
    }
    if subtitle_text:
        vis["visual"]["visualContainerObjects"]["subTitle"] = [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": f"'{subtitle_text}'"}}}
                }
            }
        ]
    return vis

def build_all_report_pages():
    setup_theme_and_report_json()

    # Clear existing pages
    if os.path.exists(PAGES_DIR):
        for item in os.listdir(PAGES_DIR):
            p = os.path.join(PAGES_DIR, item)
            if os.path.isdir(p):
                shutil.rmtree(p)
            elif item.endswith(".json") and item != "pages.json":
                os.remove(p)

    pages = [
        {"id": "page_p1_summary", "name": "1. Ledelsessammendrag 2026"},
        {"id": "page_p2_institutter", "name": "2. Institutter & Rammer"},
        {"id": "page_p3_staffing", "name": "3. Bemanningsanalyse & Årsverk"},
        {"id": "page_p4_evm", "name": "4. EVM Fremdrift & S-Kurve"},
        {"id": "page_p5_students", "name": "5. Studieproduksjon & KD"},
        {"id": "page_p6_action", "name": "6. Omstillingstiltak (T001-T004)"},
        {"id": "page_p7_budget2027", "name": "7. Budsjett 2027 & Note 15"}
    ]

    pages_metadata = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
        "pageOrder": [p["id"] for p in pages],
        "activePageName": "page_p1_summary"
    }
    write_json(os.path.join(PAGES_DIR, "pages.json"), pages_metadata)

    # =========================================================================
    # PAGE 1: Ledelsessammendrag 2026
    # =========================================================================
    p1_dir = os.path.join(PAGES_DIR, "page_p1_summary")
    p1_vis = os.path.join(p1_dir, "visuals")
    write_json(os.path.join(p1_dir, "page.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": "page_p1_summary",
        "displayName": "1. Ledelsessammendrag 2026",
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920
    })

    # Header & Slicers
    write_json(os.path.join(p1_vis, "hdr_title", "visual.json"), create_textbox_visual(
        "hdr_title", 20, 15, 1180, 75, 1,
        "Handelshøyskolen ved UiA (HHU) — Ledelsessammendrag & Helårsprognose 2026",
        "Vedtatt ramme 130 153 825 kr | Cutoff: 30.09.2026 (M01-M09 Actuals, M10-M12 Q4 Forecast) | Tufte Minimalist Standard"
    ))
    write_json(os.path.join(p1_vis, "slc_aar", "visual.json"), create_slicer_visual(
        "slc_aar", 1220, 15, 210, 75, 2, "DimDate", "Aar", "Regnskapsår", "Single"
    ))
    write_json(os.path.join(p1_vis, "slc_maaned", "visual.json"), create_slicer_visual(
        "slc_maaned", 1450, 15, 220, 75, 3, "DimDate", "MaanedNavnKort", "Rapporteringsmåned", "Dropdown"
    ))
    write_json(os.path.join(p1_vis, "slc_org", "visual.json"), create_slicer_visual(
        "slc_org", 1690, 15, 210, 75, 4, "DimOrganization", "Enhetsnavn", "Enhet / Institutt", "Dropdown"
    ))

    # KPI Cards (Top Row - 3-Second Snapshot, 5 New Cards, width 360px each)
    write_json(os.path.join(p1_vis, "kpi_rev", "visual.json"), create_card_visual(
        "kpi_rev", 20, 105, 360, 120, 5, "Total Inntekt MNOK", "TOTAL INNTEKT (RAMME 2026)",
        "Budsjett: 130,2 MNOK | ▲ +0,0%", accent_color="#10B981"
    ))
    write_json(os.path.join(p1_vis, "kpi_vac", "visual.json"), create_card_visual(
        "kpi_vac", 400, 105, 360, 120, 6, "Sluttavvik (VAC)", "HELÅRSAVVIK / RESULTAT (VAC)",
        "Dekkes av formålskapital (F-05-20) | YTD: 67,7 MNOK", accent_color="#EF4444"
    ))
    write_json(os.path.join(p1_vis, "kpi_fte", "visual.json"), create_card_visual(
        "kpi_fte", 780, 105, 360, 120, 7, "Totale Årsverk", "BEMANNING TOTALT (FTE)",
        "82 UF / 40 TA | Lønnsandel: 65,4%", accent_color="#F59E0B"
    ))
    write_json(os.path.join(p1_vis, "kpi_cpi", "visual.json"), create_card_visual(
        "kpi_cpi", 1160, 105, 360, 120, 8, "CPI", "EVM KOSTNADSEFFEKTIVITET (CPI)",
        "SPI (Fremdrift): 1,00 | Kostnadskontroll", accent_color="#10B981"
    ))
    write_json(os.path.join(p1_vis, "kpi_students", "visual.json"), create_card_visual(
        "kpi_students", 1540, 105, 360, 120, 9, "Registrerte Studenter", "STUDIEPRODUKSJON & SPE60",
        "Avlagte SPE60 | 22,6 Studenter/UF-ÅV", accent_color="#3B82F6"
    ))

    # Middle Section: Core Trends & Segmental Analysis (30-Second Insight)
    # Visual 10: Clustered Column + Line Chart (Combo Chart)
    write_json(os.path.join(p1_vis, "cht_monthly_actuals_fc", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "cht_monthly_actuals_fc",
        "position": {"x": 20, "y": 240, "z": 30, "width": 1120, "height": 400, "tabOrder": 10},
        "visual": {
            "visualType": "lineClusteredColumnComboChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimDate"}}, "Property": "MaanedNavnKort"}}, "queryRef": "DimDate.MaanedNavnKort", "nativeQueryRef": "Måned", "active": True}]},
                    "Y": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Faktiske & Prognostiserte Driftskostnader"}}, "queryRef": "_Measures.Faktiske & Prognostiserte Driftskostnader", "nativeQueryRef": "Faktiske & Prognostiserte Driftskostnader"}
                    ]},
                    "Y2": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Budsjett YTD"}}, "queryRef": "_Measures.Budsjett YTD", "nativeQueryRef": "Budsjett YTD"}
                    ]},
                    "Tooltips": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Avvik YTD"}}, "queryRef": "_Measures.Avvik YTD", "nativeQueryRef": "Avvik YTD"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Avvik YTD %"}}, "queryRef": "_Measures.Avvik YTD %", "nativeQueryRef": "Avvik YTD %"}
                    ]}
                }
            },
            "objects": {
                "legend": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "position": {"expr": {"Literal": {"Value": "'Top'"}}}
                    }
                }],
                "lineStyles": [{
                    "properties": {
                        "lineStyle": {"expr": {"Literal": {"Value": "'dashed'"}}},
                        "strokeWidth": {"expr": {"Literal": {"Value": "2D"}}}
                    },
                    "selector": {"metadata": "_Measures.Budsjett YTD"}
                }]
            },
            "visualContainerObjects": {
                "title": make_title("Månedlig Kostnadsutvikling vs. Budsjett M01–M12 (T3 Cutoff pr 30.09)")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # Visual 11: Diverging Bar Chart
    write_json(os.path.join(p1_vis, "cht_dept_variance", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "cht_dept_variance",
        "position": {"x": 1160, "y": 240, "z": 31, "width": 740, "height": 400, "tabOrder": 11},
        "visual": {
            "visualType": "barChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimOrganization"}}, "Property": "Enhetsnavn"}}, "queryRef": "DimOrganization.Enhetsnavn", "nativeQueryRef": "Institutt / Enhet", "active": True}]},
                    "Y": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Sluttavvik (VAC)"}}, "queryRef": "_Measures.Sluttavvik (VAC)", "nativeQueryRef": "Sluttavvik (VAC)"}
                    ]},
                    "Tooltips": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Total Inntekt MNOK"}}, "queryRef": "_Measures.Total Inntekt MNOK", "nativeQueryRef": "Total Inntekt"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Forecast LE (EAC)"}}, "queryRef": "_Measures.Forecast LE (EAC)", "nativeQueryRef": "Prognose (EAC)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Forecast RAG Status"}}, "queryRef": "_Measures.Forecast RAG Status", "nativeQueryRef": "RAG Status"}
                    ]}
                }
            },
            "visualContainerObjects": {
                "title": make_title("Enhetsvis Netto Sluttavvik (VAC MNOK) — Merforbruk vs. Mindreforbruk")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # Visual 12: Matrix Table (Bottom - 300-Second Deep Dive)
    write_json(os.path.join(p1_vis, "tbl_institute_matrix", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "tbl_institute_matrix",
        "position": {"x": 20, "y": 655, "z": 40, "height": 410, "width": 1880, "tabOrder": 12},
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {"projections": [
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimOrganization"}}, "Property": "OrgKode"}}, "queryRef": "DimOrganization.OrgKode", "nativeQueryRef": "OrgKode"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimOrganization"}}, "Property": "Enhetsnavn"}}, "queryRef": "DimOrganization.Enhetsnavn", "nativeQueryRef": "Enhetsnavn"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Total Inntekt MNOK"}}, "queryRef": "_Measures.Total Inntekt MNOK", "nativeQueryRef": "Total Inntekt (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Actual/FC Lønn"}}, "queryRef": "_Measures.Actual/FC Lønn", "nativeQueryRef": "Lønnskostnad (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Actual/FC Drift"}}, "queryRef": "_Measures.Actual/FC Drift", "nativeQueryRef": "Driftskostnad (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Actual/FC Capex"}}, "queryRef": "_Measures.Actual/FC Capex", "nativeQueryRef": "Investeringer Capex (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Sluttavvik (VAC)"}}, "queryRef": "_Measures.Sluttavvik (VAC)", "nativeQueryRef": "Netto Resultat VAC"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Faglige Årsverk (UF)"}}, "queryRef": "_Measures.Faglige Årsverk (UF)", "nativeQueryRef": "UF-Årsverk"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Studenter pr UF-Årsverk"}}, "queryRef": "_Measures.Studenter pr UF-Årsverk", "nativeQueryRef": "Studenter / UF-ÅV"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Forecast RAG Status"}}, "queryRef": "_Measures.Forecast RAG Status", "nativeQueryRef": "RAG Status"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Diagnose og Drivere"}}, "queryRef": "_Measures.Diagnose og Drivere", "nativeQueryRef": "Strategisk Diagnose"}
                    ]}
                }
            },
            "objects": {
                "grid": [
                    {
                        "properties": {
                            "gridVertical": {"expr": {"Literal": {"Value": "false"}}},
                            "gridHorizontal": {"expr": {"Literal": {"Value": "true"}}}
                        }
                    }
                ]
            },
            "visualContainerObjects": {
                "title": make_title("Fakultets- og Instituttoversikt: Totalregnskap, Stillingsstruktur og Styringsdiagnose (300-sekunders dybdeanalyse)")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # =========================================================================
    # PAGE 2: Institutter & Ansvarsområder
    # =========================================================================
    p2_dir = os.path.join(PAGES_DIR, "page_p2_institutter")
    p2_vis = os.path.join(p2_dir, "visuals")
    write_json(os.path.join(p2_dir, "page.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": "page_p2_institutter",
        "displayName": "2. Institutter & Rammer",
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920
    })
    write_json(os.path.join(p2_vis, "hdr_title", "visual.json"), create_textbox_visual(
        "hdr_title", 20, 15, 1200, 75, 1,
        "HHU Ansvarsområder & Instituttoppfølging 2026",
        "K10000 Admin (14,0 MNOK) | K11000 Ledelse (38,5 MNOK) | K12000 Rettsvitenskap (29,25 MNOK) | K13000 Økonomi (48,40 MNOK)"
    ))
    write_json(os.path.join(p2_vis, "slc_org", "visual.json"), create_slicer_visual(
        "slc_org", 1240, 15, 320, 75, 2, "DimOrganization", "Enhetsnavn", "Velg Institutt", "Dropdown"
    ))
    write_json(os.path.join(p2_vis, "slc_kontotype", "visual.json"), create_slicer_visual(
        "slc_kontotype", 1580, 15, 320, 75, 3, "DimAccountHierarchy", "Kontotype", "Kontotype", "Dropdown"
    ))

    # KPI Cards for 4 units
    write_json(os.path.join(p2_vis, "kpi_k10000", "visual.json"), create_card_visual(
        "kpi_k10000", 20, 105, 460, 115, 4, "HHU K10000 Admin Budsjett", "K10000 FAKULTETSADMIN & FELLES",
        "Budsjett: 14 000 000 NOK", accent_color="#334155"
    ))
    write_json(os.path.join(p2_vis, "kpi_k11000", "visual.json"), create_card_visual(
        "kpi_k11000", 495, 105, 460, 115, 5, "HHU K11000 Ledelse Budsjett", "K11000 LEDELSE & INNOVASJON",
        "Budsjett: 38 500 000 NOK", accent_color="#0284C7"
    ))
    write_json(os.path.join(p2_vis, "kpi_k12000", "visual.json"), create_card_visual(
        "kpi_k12000", 970, 105, 460, 115, 6, "HHU K12000 Rettsvitenskap Budsjett", "K12000 RETTSVITENSKAP",
        "Budsjett: 29 250 000 NOK", accent_color="#475569"
    ))
    write_json(os.path.join(p2_vis, "kpi_k13000", "visual.json"), create_card_visual(
        "kpi_k13000", 1445, 105, 455, 115, 7, "HHU K13000 Økonomi Budsjett", "K13000 ØKONOMI",
        "Budsjett: 48 403 825 NOK", accent_color="#10B981"
    ))

    # Visual 8: Account Hierarchy Matrix
    write_json(os.path.join(p2_vis, "tbl_account_matrix", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "tbl_account_matrix",
        "position": {"x": 20, "y": 235, "z": 30, "height": 825, "width": 1880, "tabOrder": 8},
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {"projections": [
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimAccountHierarchy"}}, "Property": "Konto"}}, "queryRef": "DimAccountHierarchy.Konto", "nativeQueryRef": "Konto"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimAccountHierarchy"}}, "Property": "Kontonavn"}}, "queryRef": "DimAccountHierarchy.Kontonavn", "nativeQueryRef": "Kontonavn"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimAccountHierarchy"}}, "Property": "Nivaa1_Navn"}}, "queryRef": "DimAccountHierarchy.Nivaa1_Navn", "nativeQueryRef": "Kontogruppe"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimAccountHierarchy"}}, "Property": "SRS_regnskapslinje"}}, "queryRef": "DimAccountHierarchy.SRS_regnskapslinje", "nativeQueryRef": "SRS Regnskapslinje"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Årsbudsjett (BAC)"}}, "queryRef": "_Measures.Årsbudsjett (BAC)", "nativeQueryRef": "Vedtatt Budsjett"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Actual YTD"}}, "queryRef": "_Measures.Actual YTD", "nativeQueryRef": "Bokført YTD"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Forecast Q4 (ETC)"}}, "queryRef": "_Measures.Forecast Q4 (ETC)", "nativeQueryRef": "Prognose Q4"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Forecast LE (EAC)"}}, "queryRef": "_Measures.Forecast LE (EAC)", "nativeQueryRef": "Sluttprognose EAC"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Sluttavvik (VAC)"}}, "queryRef": "_Measures.Sluttavvik (VAC)", "nativeQueryRef": "Sluttavvik VAC"}
                    ]}
                }
            },
            "objects": {
                "grid": [
                    {
                        "properties": {
                            "gridVertical": {"expr": {"Literal": {"Value": "false"}}},
                            "gridHorizontal": {"expr": {"Literal": {"Value": "true"}}}
                        }
                    }
                ]
            },
            "visualContainerObjects": {
                "title": make_title("Detaljert Kontooppfølging iht. DFØ R-102 Kontoplan & SRS Regnskapslinjer")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # =========================================================================
    # PAGE 3: Bemanningsanalyse & Årsverk
    # =========================================================================
    p3_dir = os.path.join(PAGES_DIR, "page_p3_staffing")
    p3_vis = os.path.join(p3_dir, "visuals")
    write_json(os.path.join(p3_dir, "page.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": "page_p3_staffing",
        "displayName": "3. Bemanningsanalyse & Årsverk",
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920
    })
    write_json(os.path.join(p3_vis, "hdr_title", "visual.json"), create_textbox_visual(
        "hdr_title", 20, 15, 1200, 75, 1,
        "Bemannings- og Årsverksanalyse — Handelshøyskolen ved UiA (HHU)",
        "UF-årsverk (vitenskapelige) vs. TA-årsverk (teknisk-administrative) | Vakansgrad & Rekrutteringskontroll"
    ))
    write_json(os.path.join(p3_vis, "slc_org", "visual.json"), create_slicer_visual(
        "slc_org", 1240, 15, 320, 75, 2, "DimOrganization", "Enhetsnavn", "Enhet / Institutt", "Dropdown"
    ))
    write_json(os.path.join(p3_vis, "slc_stilling", "visual.json"), create_slicer_visual(
        "slc_stilling", 1580, 15, 320, 75, 3, "FactFTE", "Stillingstype", "Stillingstype (UF / TA)", "Dropdown"
    ))

    # KPI Cards
    write_json(os.path.join(p3_vis, "kpi_totale_av", "visual.json"), create_card_visual(
        "kpi_totale_av", 20, 105, 300, 115, 4, "Totale Årsverk", "TOTALE ÅRSVERK (SNAPSHOT)",
        "Siste registrerte måned", accent_color="#334155"
    ))
    write_json(os.path.join(p3_vis, "kpi_uf_av", "visual.json"), create_card_visual(
        "kpi_uf_av", 335, 105, 300, 115, 5, "Faglige Årsverk (UF)", "FAGLIGE ÅRSVERK (UF)",
        "Undervisning & Forskning", accent_color="#0284C7"
    ))
    write_json(os.path.join(p3_vis, "kpi_ta_av", "visual.json"), create_card_visual(
        "kpi_ta_av", 650, 105, 300, 115, 6, "Teknisk-Admin Årsverk (TA)", "ADMIN. ÅRSVERK (TA)",
        "Teknisk-Administrativt", accent_color="#475569"
    ))
    write_json(os.path.join(p3_vis, "kpi_faglig_andel", "visual.json"), create_card_visual(
        "kpi_faglig_andel", 965, 105, 300, 115, 7, "Faglig Andel %", "FAGLIG ANDEL %",
        "Sektormål: > 50-55%", accent_color="#10B981"
    ))
    write_json(os.path.join(p3_vis, "kpi_vakansgrad", "visual.json"), create_card_visual(
        "kpi_vakansgrad", 1280, 105, 300, 115, 8, "Vakansgrad %", "VAKANSGRAD %",
        "Planlagte vs Faktiske ÅV", accent_color="#F59E0B"
    ))
    write_json(os.path.join(p3_vis, "kpi_lonnsandel_fte", "visual.json"), create_card_visual(
        "kpi_lonnsandel_fte", 1595, 105, 305, 115, 9, "Lønnsandel %", "LØNNSANDEL %",
        "Mål: < 65,0%", accent_color="#10B981"
    ))

    # Visual 10: Stacked Column Chart
    write_json(os.path.join(p3_vis, "cht_fte_by_month", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "cht_fte_by_month",
        "position": {"x": 20, "y": 235, "z": 30, "width": 1100, "height": 400, "tabOrder": 10},
        "visual": {
            "visualType": "stackedColumnChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimDate"}}, "Property": "MaanedNavnKort"}}, "queryRef": "DimDate.MaanedNavnKort", "nativeQueryRef": "Måned", "active": True}]},
                    "Series": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactFTE"}}, "Property": "Stillingstype"}}, "queryRef": "FactFTE.Stillingstype", "nativeQueryRef": "Stillingstype", "active": True}]},
                    "Y": {"projections": [
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactFTE"}}, "Property": "Aarsverk"}}, "queryRef": "FactFTE.Aarsverk", "nativeQueryRef": "Årsverk"}
                    ]}
                }
            },
            "visualContainerObjects": {
                "title": make_title("Månedlig Årsverksutvikling fordelt på UF og TA")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # Visual 11: Bar chart by Unit
    write_json(os.path.join(p3_vis, "cht_fte_by_unit", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "cht_fte_by_unit",
        "position": {"x": 1140, "y": 235, "z": 31, "width": 760, "height": 400, "tabOrder": 11},
        "visual": {
            "visualType": "barChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimOrganization"}}, "Property": "Enhetsnavn"}}, "queryRef": "DimOrganization.Enhetsnavn", "nativeQueryRef": "Enhetsnavn", "active": True}]},
                    "Y": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Totale Årsverk"}}, "queryRef": "_Measures.Totale Årsverk", "nativeQueryRef": "Totale Årsverk"}
                    ]}
                }
            },
            "visualContainerObjects": {
                "title": make_title("Bemanningsstørrelse (Totale Årsverk) per Enhet")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # Visual 12: FTE Detailed Table
    write_json(os.path.join(p3_vis, "tbl_fte_detail", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "tbl_fte_detail",
        "position": {"x": 20, "y": 650, "z": 40, "height": 410, "width": 1880, "tabOrder": 12},
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {"projections": [
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimDate"}}, "Property": "MaanedNavn"}}, "queryRef": "DimDate.MaanedNavn", "nativeQueryRef": "Måned"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimOrganization"}}, "Property": "Enhetsnavn"}}, "queryRef": "DimOrganization.Enhetsnavn", "nativeQueryRef": "Enhet"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactFTE"}}, "Property": "Aarsverk_UF"}}, "queryRef": "FactFTE.Aarsverk_UF", "nativeQueryRef": "UF Årsverk"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactFTE"}}, "Property": "Aarsverk_TA"}}, "queryRef": "FactFTE.Aarsverk_TA", "nativeQueryRef": "TA Årsverk"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactFTE"}}, "Property": "Aarsverk_Totalt"}}, "queryRef": "FactFTE.Aarsverk_Totalt", "nativeQueryRef": "Totalt Årsverk"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactFTE"}}, "Property": "Budsjettert_Aarsverk"}}, "queryRef": "FactFTE.Budsjettert_Aarsverk", "nativeQueryRef": "Budsjettert ÅV"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactFTE"}}, "Property": "Vakans_Aarsverk"}}, "queryRef": "FactFTE.Vakans_Aarsverk", "nativeQueryRef": "Vakanser ÅV"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactFTE"}}, "Property": "Vakansgrad_Pct"}}, "queryRef": "FactFTE.Vakansgrad_Pct", "nativeQueryRef": "Vakansgrad %"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactFTE"}}, "Property": "Antall_Ansatte"}}, "queryRef": "FactFTE.Antall_Ansatte", "nativeQueryRef": "Antall Ansatte"}
                    ]}
                }
            },
            "objects": {
                "grid": [
                    {
                        "properties": {
                            "gridVertical": {"expr": {"Literal": {"Value": "false"}}},
                            "gridHorizontal": {"expr": {"Literal": {"Value": "true"}}}
                        }
                    }
                ]
            },
            "visualContainerObjects": {
                "title": make_title("Detaljert Månedlig Bemannings- og Vakanslogg per Avdeling")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # =========================================================================
    # PAGE 4: EVM Fremdrift & S-Kurve
    # =========================================================================
    p4_dir = os.path.join(PAGES_DIR, "page_p4_evm")
    p4_vis = os.path.join(p4_dir, "visuals")
    write_json(os.path.join(p4_dir, "page.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": "page_p4_evm",
        "displayName": "4. EVM Fremdrift & S-Kurve",
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920
    })
    write_json(os.path.join(p4_vis, "hdr_title", "visual.json"), create_textbox_visual(
        "hdr_title", 20, 15, 1200, 75, 1,
        "Earned Value Management (EVM) — Kostnads- og Fremdriftsstyring",
        "S-Kurve sporing: Planlagt Verdi (PV), Opptjent Verdi (EV), Faktisk Kostnad (AC) | Kostnadsindeks CPI & Tidsindeks SPI"
    ))
    write_json(os.path.join(p4_vis, "slc_maaned", "visual.json"), create_slicer_visual(
        "slc_maaned", 1580, 15, 320, 75, 2, "DimDate", "MaanedNavnKort", "Periode", "Dropdown"
    ))

    # EVM KPI Cards
    write_json(os.path.join(p4_vis, "kpi_pv", "visual.json"), create_card_visual(
        "kpi_pv", 20, 105, 300, 115, 3, "Planned Value (PV)", "PLANLAGT VERDI (PV)",
        "Budsjettert fremdrift", accent_color="#334155"
    ))
    write_json(os.path.join(p4_vis, "kpi_ev", "visual.json"), create_card_visual(
        "kpi_ev", 335, 105, 300, 115, 4, "Earned Value (EV)", "OPPTJENT VERDI (EV)",
        "Realisert produksjon", accent_color="#0284C7"
    ))
    write_json(os.path.join(p4_vis, "kpi_ac", "visual.json"), create_card_visual(
        "kpi_ac", 650, 105, 300, 115, 5, "Actual Cost (AC)", "FAKTISK KOSTNAD (AC)",
        "Påløpte kostnader", accent_color="#475569"
    ))
    write_json(os.path.join(p4_vis, "kpi_cpi", "visual.json"), create_card_visual(
        "kpi_cpi", 965, 105, 300, 115, 6, "CPI", "KOSTNADSINDEKS (CPI)",
        "Mål >= 1.00 (Kostnadskontroll)", accent_color="#F59E0B"
    ))
    write_json(os.path.join(p4_vis, "kpi_spi", "visual.json"), create_card_visual(
        "kpi_spi", 1280, 105, 300, 115, 7, "SPI", "FREMDRIFTSINDEKS (SPI)",
        "Mål >= 1.00 (Tidsplan)", accent_color="#10B981"
    ))
    write_json(os.path.join(p4_vis, "kpi_status", "visual.json"), create_card_visual(
        "kpi_status", 1595, 105, 305, 115, 8, "EVM Status Subtitle", "EVM STATUSINDEKS",
        "Samlet prosjektstatus", accent_color="#10B981"
    ))

    # Visual 9: S-Curve Line Chart
    write_json(os.path.join(p4_vis, "cht_s_curve", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "cht_s_curve",
        "position": {"x": 20, "y": 235, "z": 30, "width": 1100, "height": 400, "tabOrder": 9},
        "visual": {
            "visualType": "lineChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimDate"}}, "Property": "MaanedNavnKort"}}, "queryRef": "DimDate.MaanedNavnKort", "nativeQueryRef": "Måned", "active": True}]},
                    "Y": {"projections": [
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactEVM"}}, "Property": "Planned_Value_PV_MNOK"}}, "queryRef": "FactEVM.Planned_Value_PV_MNOK", "nativeQueryRef": "Planned Value (PV MNOK)"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactEVM"}}, "Property": "Earned_Value_EV_MNOK"}}, "queryRef": "FactEVM.Earned_Value_EV_MNOK", "nativeQueryRef": "Earned Value (EV MNOK)"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactEVM"}}, "Property": "Actual_Cost_AC_MNOK"}}, "queryRef": "FactEVM.Actual_Cost_AC_MNOK", "nativeQueryRef": "Actual Cost (AC MNOK)"}
                    ]}
                }
            },
            "visualContainerObjects": {
                "title": make_title("EVM S-Kurve: PV, EV og AC per Måned (MNOK)")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # Visual 10: CPI/SPI Line Chart
    write_json(os.path.join(p4_vis, "cht_indices", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "cht_indices",
        "position": {"x": 1140, "y": 235, "z": 31, "width": 760, "height": 400, "tabOrder": 10},
        "visual": {
            "visualType": "lineChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimDate"}}, "Property": "MaanedNavnKort"}}, "queryRef": "DimDate.MaanedNavnKort", "nativeQueryRef": "Måned", "active": True}]},
                    "Y": {"projections": [
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactEVM"}}, "Property": "CostPerformanceIndex_CPI"}}, "queryRef": "FactEVM.CostPerformanceIndex_CPI", "nativeQueryRef": "CPI (Kostnad)"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactEVM"}}, "Property": "SchedulePerformanceIndex_SPI"}}, "queryRef": "FactEVM.SchedulePerformanceIndex_SPI", "nativeQueryRef": "SPI (Fremdrift)"}
                    ]}
                }
            },
            "visualContainerObjects": {
                "title": make_title("Månedlig Effektivitetsutvikling (CPI & SPI)")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # Visual 11: EVM Monthly Table
    write_json(os.path.join(p4_vis, "tbl_evm_matrix", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "tbl_evm_matrix",
        "position": {"x": 20, "y": 650, "z": 40, "height": 410, "width": 1880, "tabOrder": 11},
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {"projections": [
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimDate"}}, "Property": "MaanedNavn"}}, "queryRef": "DimDate.MaanedNavn", "nativeQueryRef": "Måned"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactEVM"}}, "Property": "BAC_BudgetAtCompletion"}}, "queryRef": "FactEVM.BAC_BudgetAtCompletion", "nativeQueryRef": "BAC (NOK)"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactEVM"}}, "Property": "PlannedValue_PV"}}, "queryRef": "FactEVM.PlannedValue_PV", "nativeQueryRef": "Planned Value (PV)"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactEVM"}}, "Property": "EarnedValue_EV"}}, "queryRef": "FactEVM.EarnedValue_EV", "nativeQueryRef": "Earned Value (EV)"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactEVM"}}, "Property": "ActualCost_AC"}}, "queryRef": "FactEVM.ActualCost_AC", "nativeQueryRef": "Actual Cost (AC)"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactEVM"}}, "Property": "EstimateAtCompletion_EAC"}}, "queryRef": "FactEVM.EstimateAtCompletion_EAC", "nativeQueryRef": "EAC (NOK)"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactEVM"}}, "Property": "VarianceAtCompletion_VAC"}}, "queryRef": "FactEVM.VarianceAtCompletion_VAC", "nativeQueryRef": "VAC (NOK)"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactEVM"}}, "Property": "CostPerformanceIndex_CPI"}}, "queryRef": "FactEVM.CostPerformanceIndex_CPI", "nativeQueryRef": "CPI"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactEVM"}}, "Property": "SchedulePerformanceIndex_SPI"}}, "queryRef": "FactEVM.SchedulePerformanceIndex_SPI", "nativeQueryRef": "SPI"}
                    ]}
                }
            },
            "objects": {
                "grid": [
                    {
                        "properties": {
                            "gridVertical": {"expr": {"Literal": {"Value": "false"}}},
                            "gridHorizontal": {"expr": {"Literal": {"Value": "true"}}}
                        }
                    }
                ]
            },
            "visualContainerObjects": {
                "title": make_title("Månedlig Earned Value Prosjektlogg (NOK og Nøkkeltall)")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # =========================================================================
    # PAGE 5: Studieproduksjon & KD Kategori 1
    # =========================================================================
    p5_dir = os.path.join(PAGES_DIR, "page_p5_students")
    p5_vis = os.path.join(p5_dir, "visuals")
    write_json(os.path.join(p5_dir, "page.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": "page_p5_students",
        "displayName": "5. Studieproduksjon & KD",
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920
    })
    write_json(os.path.join(p5_vis, "hdr_title", "visual.json"), create_textbox_visual(
        "hdr_title", 20, 15, 1200, 75, 1,
        "Studieproduksjon & Kunnskapsdepartementets Finansieringsmodell",
        "Kategori 1 finansiering @ 54 550 NOK/SPE60 | 2-års etterslep (lag) | Lærertetthet (Studenter / UF-Årsverk)"
    ))
    write_json(os.path.join(p5_vis, "slc_org", "visual.json"), create_slicer_visual(
        "slc_org", 1240, 15, 320, 75, 2, "DimOrganization", "Enhetsnavn", "Enhet / Institutt", "Dropdown"
    ))

    # KPI Cards
    write_json(os.path.join(p5_vis, "kpi_stud", "visual.json"), create_card_visual(
        "kpi_stud", 20, 105, 460, 115, 3, "Registrerte Studenter", "REGISTRERTE STUDENTER",
        "Totalt HHU: 3 450 studenter", accent_color="#334155"
    ))
    write_json(os.path.join(p5_vis, "kpi_spe", "visual.json"), create_card_visual(
        "kpi_spe", 495, 105, 460, 115, 4, "Avlagte SPE60", "AVLAGTE STUDIEPOENGEKVIVALENTER",
        "Total produksjon: 3 153 SPE60", accent_color="#0284C7"
    ))
    write_json(os.path.join(p5_vis, "kpi_tetthet", "visual.json"), create_card_visual(
        "kpi_tetthet", 970, 105, 460, 115, 5, "Studenter pr UF-Årsverk", "LÆRERTETTHET (STUD / UF-ÅV)",
        "Gjennomsnitt: 22,3 stud/UF", accent_color="#F59E0B"
    ))
    write_json(os.path.join(p5_vis, "kpi_kd", "visual.json"), create_card_visual(
        "kpi_kd", 1445, 105, 455, 115, 6, "KD Kat 1 Inntekt", "BEREGNET KD KATEGORI 1 INNTEKT",
        "Sats: 54 550 kr per SPE60", accent_color="#10B981"
    ))

    # Visual 7: Bar chart by study program
    write_json(os.path.join(p5_vis, "cht_program_spe", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "cht_program_spe",
        "position": {"x": 20, "y": 235, "z": 30, "width": 1100, "height": 400, "tabOrder": 7},
        "visual": {
            "visualType": "clusteredColumnChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactStudents"}}, "Property": "Studieprogram"}}, "queryRef": "FactStudents.Studieprogram", "nativeQueryRef": "Studieprogram", "active": True}]},
                    "Y": {"projections": [
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactStudents"}}, "Property": "SPE60_Baseline_2025"}}, "queryRef": "FactStudents.SPE60_Baseline_2025", "nativeQueryRef": "2025 Baseline SPE"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactStudents"}}, "Property": "SPE60"}}, "queryRef": "FactStudents.SPE60", "nativeQueryRef": "Mål SPE60"}
                    ]}
                }
            },
            "visualContainerObjects": {
                "title": make_title("Studiepoengproduksjon (SPE60) per Studieprogram: 2025 Grunnlag vs Mål")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # Visual 8: Student ratio bar chart
    write_json(os.path.join(p5_vis, "cht_student_ratio", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "cht_student_ratio",
        "position": {"x": 1140, "y": 235, "z": 31, "width": 760, "height": 400, "tabOrder": 8},
        "visual": {
            "visualType": "barChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactStudents"}}, "Property": "Studieprogram"}}, "queryRef": "FactStudents.Studieprogram", "nativeQueryRef": "Studieprogram", "active": True}]},
                    "Y": {"projections": [
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactStudents"}}, "Property": "Studenter_pr_UF"}}, "queryRef": "FactStudents.Studenter_pr_UF", "nativeQueryRef": "Studenter pr UF"}
                    ]}
                }
            },
            "visualContainerObjects": {
                "title": make_title("Lærertetthet (Studenter per UF-årsverk)")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # Visual 9: Detailed Student Matrix Table
    write_json(os.path.join(p5_vis, "tbl_students_matrix", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "tbl_students_matrix",
        "position": {"x": 20, "y": 650, "z": 40, "height": 410, "width": 1880, "tabOrder": 9},
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {"projections": [
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactStudents"}}, "Property": "Studieprogram"}}, "queryRef": "FactStudents.Studieprogram", "nativeQueryRef": "Studieprogram"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimOrganization"}}, "Property": "Enhetsnavn"}}, "queryRef": "DimOrganization.Enhetsnavn", "nativeQueryRef": "Institutt"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactStudents"}}, "Property": "KDKategori"}}, "queryRef": "FactStudents.KDKategori", "nativeQueryRef": "KD Kategori"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactStudents"}}, "Property": "RegistrerteStudenter"}}, "queryRef": "FactStudents.RegistrerteStudenter", "nativeQueryRef": "Registrerte Studenter"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactStudents"}}, "Property": "SPE60_Baseline_2025"}}, "queryRef": "FactStudents.SPE60_Baseline_2025", "nativeQueryRef": "2025 Lag (SPE60)"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactStudents"}}, "Property": "SPE60"}}, "queryRef": "FactStudents.SPE60", "nativeQueryRef": "Mål SPE60"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactStudents"}}, "Property": "KDSats_NOK"}}, "queryRef": "FactStudents.KDSats_NOK", "nativeQueryRef": "KD Sats (kr)"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactStudents"}}, "Property": "KD_Marginal_Inntekt_2027"}}, "queryRef": "FactStudents.KD_Marginal_Inntekt_2027", "nativeQueryRef": "Beregnet KD Inntekt (NOK)"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactStudents"}}, "Property": "Studenter_pr_UF"}}, "queryRef": "FactStudents.Studenter_pr_UF", "nativeQueryRef": "Stud/UF-ÅV"}
                    ]}
                }
            },
            "objects": {
                "grid": [
                    {
                        "properties": {
                            "gridVertical": {"expr": {"Literal": {"Value": "false"}}},
                            "gridHorizontal": {"expr": {"Literal": {"Value": "true"}}}
                        }
                    }
                ]
            },
            "visualContainerObjects": {
                "title": make_title("Utdannings- og Studiepoengmodell: Kategori 1 Satser, 2-års Etterslep og Lærertetthet")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # =========================================================================
    # PAGE 6: Omstillingstiltak (T001–T004)
    # =========================================================================
    p6_dir = os.path.join(PAGES_DIR, "page_p6_action")
    p6_vis = os.path.join(p6_dir, "visuals")
    write_json(os.path.join(p6_dir, "page.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": "page_p6_action",
        "displayName": "6. Omstillingstiltak (T001-T004)",
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920
    })
    write_json(os.path.join(p6_vis, "hdr_title", "visual.json"), create_textbox_visual(
        "hdr_title", 20, 15, 1200, 75, 1,
        "Omstillingstiltak & Innsparingslogg (T001–T004) — HHU 2026/2027",
        "Planlagte tiltak: Stillingsfrys (T001), BOA frikjøp (T002), Prosjektlønnsomhet (T003), Vakanshold professorat (T004)"
    ))
    write_json(os.path.join(p6_vis, "slc_status", "visual.json"), create_slicer_visual(
        "slc_status", 1580, 15, 320, 75, 2, "FactAction", "Status", "Tiltaksstatus", "Dropdown"
    ))

    # KPI Cards
    write_json(os.path.join(p6_vis, "kpi_forventet", "visual.json"), create_card_visual(
        "kpi_forventet", 20, 105, 460, 115, 3, "Forventet Tiltakseffekt", "FORVENTET TILTAKSEFFEKT",
        "Planlagt samlet innsparing (NOK)", accent_color="#334155"
    ))
    write_json(os.path.join(p6_vis, "kpi_realisert", "visual.json"), create_card_visual(
        "kpi_realisert", 495, 105, 460, 115, 4, "Realisert Tiltakseffekt", "REALISERT TILTAKSEFFEKT",
        "Bokført innsparing hittil (NOK)", accent_color="#10B981"
    ))
    write_json(os.path.join(p6_vis, "kpi_realiseringsgrad", "visual.json"), create_card_visual(
        "kpi_realiseringsgrad", 970, 105, 460, 115, 5, "Tiltak Realiseringsgrad %", "REALISERINGSGRAD %",
        "Oppnådd andel av planlagt innsparing", accent_color="#F59E0B"
    ))
    write_json(os.path.join(p6_vis, "kpi_fc_etter", "visual.json"), create_card_visual(
        "kpi_fc_etter", 1445, 105, 455, 115, 6, "Forecast etter Tiltak", "PROGNOSE ETTER TILTAK",
        "EAC korrigert for tiltakseffekter", accent_color="#0284C7"
    ))

    # Visual 7: Bar chart of Action Effects
    write_json(os.path.join(p6_vis, "cht_action_savings", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "cht_action_savings",
        "position": {"x": 20, "y": 235, "z": 30, "width": 1880, "height": 380, "tabOrder": 7},
        "visual": {
            "visualType": "clusteredColumnChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction"}}, "Property": "TiltakNavn"}}, "queryRef": "FactAction.TiltakNavn", "nativeQueryRef": "Tiltak", "active": True}]},
                    "Y": {"projections": [
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction"}}, "Property": "ForventetInnsparingNOK"}}, "queryRef": "FactAction.ForventetInnsparingNOK", "nativeQueryRef": "Forventet Innsparing"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction"}}, "Property": "RealisertInnsparingNOK"}}, "queryRef": "FactAction.RealisertInnsparingNOK", "nativeQueryRef": "Realisert Innsparing"}
                    ]}
                }
            },
            "visualContainerObjects": {
                "title": make_title("Planlagt vs. Realisert Innsparingseffekt per Omstillingstiltak (NOK)")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # Visual 8: Action Log Table
    write_json(os.path.join(p6_vis, "tbl_action_log", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "tbl_action_log",
        "position": {"x": 20, "y": 635, "z": 40, "height": 425, "width": 1880, "tabOrder": 8},
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {"projections": [
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction"}}, "Property": "TiltakID"}}, "queryRef": "FactAction.TiltakID", "nativeQueryRef": "TiltakID"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction"}}, "Property": "TiltakNavn"}}, "queryRef": "FactAction.TiltakNavn", "nativeQueryRef": "Tiltaksnavn"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction"}}, "Property": "Budsjettansvarsområde"}}, "queryRef": "FactAction.Budsjettansvarsområde", "nativeQueryRef": "Ansvarsområde"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction"}}, "Property": "AnsvarligLeder"}}, "queryRef": "FactAction.AnsvarligLeder", "nativeQueryRef": "Ansvarlig Leder"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction"}}, "Property": "Status"}}, "queryRef": "FactAction.Status", "nativeQueryRef": "Status"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction"}}, "Property": "ForventetInnsparingNOK"}}, "queryRef": "FactAction.ForventetInnsparingNOK", "nativeQueryRef": "Forventet (kr)"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction"}}, "Property": "RealisertInnsparingNOK"}}, "queryRef": "FactAction.RealisertInnsparingNOK", "nativeQueryRef": "Realisert (kr)"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction"}}, "Property": "FristDato"}}, "queryRef": "FactAction.FristDato", "nativeQueryRef": "Frist"}
                    ]}
                }
            },
            "objects": {
                "grid": [
                    {
                        "properties": {
                            "gridVertical": {"expr": {"Literal": {"Value": "false"}}},
                            "gridHorizontal": {"expr": {"Literal": {"Value": "true"}}}
                        }
                    }
                ]
            },
            "visualContainerObjects": {
                "title": make_title("Styringstabell: Omstillingstiltak, Ansvarsfordeling og Gjennomføringsstatus")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # =========================================================================
    # PAGE 7: Budsjett 2027 & Note 15
    # =========================================================================
    p7_dir = os.path.join(PAGES_DIR, "page_p7_budget2027")
    p7_vis = os.path.join(p7_dir, "visuals")
    write_json(os.path.join(p7_dir, "page.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": "page_p7_budget2027",
        "displayName": "7. Budsjett 2027 & Note 15",
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920
    })
    write_json(os.path.join(p7_vis, "hdr_title", "visual.json"), create_textbox_visual(
        "hdr_title", 20, 15, 1200, 75, 1,
        "Budsjett 2027 — Handelshøyskolen ved UiA (HHU)",
        "Vedtatt ramme BUD2027: 288,07 MNOK Inntekt / 282,00 MNOK Kostnad (+6,07 MNOK Netto overskudd til Note 15 Formålskapital)"
    ))
    write_json(os.path.join(p7_vis, "slc_org", "visual.json"), create_slicer_visual(
        "slc_org", 1240, 15, 320, 75, 2, "DimOrganization", "Enhetsnavn", "Enhet / Institutt", "Dropdown"
    ))
    write_json(os.path.join(p7_vis, "slc_konto", "visual.json"), create_slicer_visual(
        "slc_konto", 1580, 15, 320, 75, 3, "DimAccountHierarchy", "Kontotype", "Kontotype", "Dropdown"
    ))

    # KPI Cards
    write_json(os.path.join(p7_vis, "kpi_bud27_rev", "visual.json"), create_card_visual(
        "kpi_bud27_rev", 20, 105, 300, 115, 4, "BUD2027 Inntekter HHU", "BUD2027 INNTEKTER",
        "HHU Ramme: 288,07 MNOK", accent_color="#10B981"
    ))
    write_json(os.path.join(p7_vis, "kpi_bud27_cost", "visual.json"), create_card_visual(
        "kpi_bud27_cost", 335, 105, 300, 115, 5, "BUD2027 Kostnader HHU", "BUD2027 KOSTNADER",
        "HHU Driftskostnad: 282,00 MNOK", accent_color="#EF4444"
    ))
    write_json(os.path.join(p7_vis, "kpi_bud27_net", "visual.json"), create_card_visual(
        "kpi_bud27_net", 650, 105, 300, 115, 6, "BUD2027 Netto Resultat HHU", "NETTO DRIFTSRESULTAT",
        "Avsetning Note 15: +6,07 MNOK", accent_color="#10B981"
    ))
    write_json(os.path.join(p7_vis, "kpi_bud27_kd", "visual.json"), create_card_visual(
        "kpi_bud27_kd", 965, 105, 300, 115, 7, "KD Kat 1 Resultatutbetaling 2027", "KD RESULTATUTBETALING",
        "Kategori 1 (2-års etterslep)", accent_color="#0284C7"
    ))
    write_json(os.path.join(p7_vis, "kpi_bud27_lonn", "visual.json"), create_card_visual(
        "kpi_bud27_lonn", 1280, 105, 300, 115, 8, "HHU Lønnsandel 2027 %", "LØNNSANDEL 2027 %",
        "Mål: < 64,5%", accent_color="#10B981"
    ))
    write_json(os.path.join(p7_vis, "kpi_bud27_rag", "visual.json"), create_card_visual(
        "kpi_bud27_rag", 1595, 105, 305, 115, 9, "HHU 2027 RAG Status Badge", "BUDSJETTSTATUS RAG",
        "Styringsstatus BUD2027", accent_color="#10B981"
    ))

    # Visual 10: Column Chart 2027 by department
    write_json(os.path.join(p7_vis, "cht_bud2027_by_dept", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "cht_bud2027_by_dept",
        "position": {"x": 20, "y": 235, "z": 30, "width": 1100, "height": 400, "tabOrder": 10},
        "visual": {
            "visualType": "clusteredColumnChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimOrganization"}}, "Property": "Enhetsnavn"}}, "queryRef": "DimOrganization.Enhetsnavn", "nativeQueryRef": "Institutt / Enhet", "active": True}]},
                    "Y": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "BUD2027 Inntekter HHU"}}, "queryRef": "_Measures.BUD2027 Inntekter HHU", "nativeQueryRef": "Budsjett Inntekter"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "BUD2027 Kostnader HHU"}}, "queryRef": "_Measures.BUD2027 Kostnader HHU", "nativeQueryRef": "Budsjett Kostnader"}
                    ]}
                }
            },
            "visualContainerObjects": {
                "title": make_title("Budsjett 2027: Inntekter vs. Kostnader per Institutt (NOK)")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # Visual 11: Bar chart 2027 accounts
    write_json(os.path.join(p7_vis, "cht_bud2027_by_srs", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "cht_bud2027_by_srs",
        "position": {"x": 1140, "y": 235, "z": 31, "width": 760, "height": 400, "tabOrder": 11},
        "visual": {
            "visualType": "barChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimAccountHierarchy"}}, "Property": "SRS_regnskapslinje"}}, "queryRef": "DimAccountHierarchy.SRS_regnskapslinje", "nativeQueryRef": "SRS Regnskapslinje", "active": True}]},
                    "Y": {"projections": [
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactBudget_2027"}}, "Property": "BudsjettBelop"}}, "queryRef": "FactBudget_2027.BudsjettBelop", "nativeQueryRef": "Budsjettbeløp"}
                    ]}
                }
            },
            "visualContainerObjects": {
                "title": make_title("Budsjett 2027 fordelt på SRS-regnskapslinjer")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # Visual 12: 2027 Detailed Budget Table
    write_json(os.path.join(p7_vis, "tbl_bud2027_matrix", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "tbl_bud2027_matrix",
        "position": {"x": 20, "y": 650, "z": 40, "height": 410, "width": 1880, "tabOrder": 12},
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {"projections": [
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimDate_2027"}}, "Property": "MaanedNavn"}}, "queryRef": "DimDate_2027.MaanedNavn", "nativeQueryRef": "Måned"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimOrganization"}}, "Property": "Enhetsnavn"}}, "queryRef": "DimOrganization.Enhetsnavn", "nativeQueryRef": "Enhet"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimAccountHierarchy"}}, "Property": "Konto"}}, "queryRef": "DimAccountHierarchy.Konto", "nativeQueryRef": "Konto"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimAccountHierarchy"}}, "Property": "Kontonavn"}}, "queryRef": "DimAccountHierarchy.Kontonavn", "nativeQueryRef": "Kontonavn"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimAccountHierarchy"}}, "Property": "SRS_regnskapslinje"}}, "queryRef": "DimAccountHierarchy.SRS_regnskapslinje", "nativeQueryRef": "SRS Regnskapslinje"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactBudget_2027"}}, "Property": "BudsjettBelop"}}, "queryRef": "FactBudget_2027.BudsjettBelop", "nativeQueryRef": "Budsjettbeløp (NOK)"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactBudget_2027"}}, "Property": "Kommentar"}}, "queryRef": "FactBudget_2027.Kommentar", "nativeQueryRef": "Kommentar"}
                    ]}
                }
            },
            "objects": {
                "grid": [
                    {
                        "properties": {
                            "gridVertical": {"expr": {"Literal": {"Value": "false"}}},
                            "gridHorizontal": {"expr": {"Literal": {"Value": "true"}}}
                        }
                    }
                ]
            },
            "visualContainerObjects": {
                "title": make_title("Periodisert Budsjett 2027 per Måned, Konto og Enhet (M01-M12)")
            },
            "drillFilterOtherVisuals": True
        }
    })

    print(f"Successfully generated {len(pages)} PBIR report pages with Tufte Minimalist layout.")

if __name__ == "__main__":
    build_all_report_pages()
