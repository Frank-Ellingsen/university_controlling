"""
Script to add additional measures and generate complete PBIR report pages
for Controller-Handelshøyskolen.
"""
import os
import json
import uuid
import shutil

BASE_DIR = r"c:\Users\frank\Desktop\UIA2\Handelshøyskolen"
SEMANTIC_DIR = os.path.join(BASE_DIR, "Controller-Handelshøyskolen.SemanticModel", "definition")
REPORT_DIR = os.path.join(BASE_DIR, "Controller-Handelshøyskolen.Report", "definition")
PAGES_DIR = os.path.join(REPORT_DIR, "pages")

def gen_guid():
    return str(uuid.uuid4())

def append_additional_measures():
    measures_path = os.path.join(SEMANTIC_DIR, "tables", "_Measures.tmdl")
    with open(measures_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "Actual/FC Lønn" in content:
        print("Measures already present in _Measures.tmdl")
        return

    extra_measures = f"""
\tmeasure 'Actual/FC Lønn' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactGL'[Belop_signert]),
\t\t\t    'DimAccountHierarchy'[Nivaa1_Navn] = "Lønnskostnad"
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: {gen_guid()}

\tmeasure 'Actual/FC Drift' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactGL'[Belop_signert]),
\t\t\t    'DimAccountHierarchy'[Nivaa1_Navn] IN {{"Annen driftskostnad", "Andre driftskostnader"}}
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: {gen_guid()}

\tmeasure 'Actual/FC Capex' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactGL'[Belop_signert]),
\t\t\t    'DimAccountHierarchy'[Kontotype] = "Investeringer"
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: {gen_guid()}

\tmeasure 'Faktiske & Prognostiserte Driftskostnader' =
\t\t\tCALCULATE(
\t\t\t    SUM('FactGL'[Belop_signert]),
\t\t\t    'DimAccountHierarchy'[Kontotype] = "Kostnad"
\t\t\t)
\t\tformatString: #,##0.0
\t\tdisplayFolder: _02 Prognose & EAC
\t\tlineageTag: {gen_guid()}

\tmeasure 'Forecast RAG Status' =
\t\t\tVAR Vac = [Sluttavvik (VAC)]
\t\t\tVAR VacPct = [VAC %]
\t\t\tRETURN
\t\t\tSWITCH(
\t\t\t    TRUE(),
\t\t\t    Vac >= 0, "🟢 Planmessig",
\t\t\t    VacPct >= -0.05, "🟡 Moderat avvik",
\t\t\t    "🔴 Vesentlig avvik"
\t\t\t)
\t\tdisplayFolder: _07 RAG & Formatering
\t\tlineageTag: {gen_guid()}

\tmeasure 'Diagnose og Drivere' =
\t\t\tVAR Org = SELECTEDVALUE('DimOrganization'[OrgKode])
\t\t\tRETURN
\t\t\tSWITCH(
\t\t\t    Org,
\t\t\t    "HHU_I001", "Høy SPE-produksjon (86,7/mnd). KD Kat 1 sats. T003 EVU-ekspansjon pågår.",
\t\t\t    "HHU_I002", "Stabil drift. Rettsvitenskap. 21,3 stud/UF. Lav vakansgrad.",
\t\t\t    "HHU_I003", "Høy studenttetthet (23,3 stud/UF). T002 faglige årsverk omdisponert.",
\t\t\t    "HHU_ADM", "T001 administrativ ansettelsesstopp. AACSB akkrediteringskostnad M03/M09.",
\t\t\t    "TEK_001", "Laboratoriekostnader og IKT-investeringer. Merforbruk -1,9 MNOK.",
\t\t\t    "HEL_001", "Klinisk praksis og turnusavtaler. Merforbruk -5,3 MNOK.",
\t\t\t    "SAM_001", "Mindreforbruk på drift +3,0 MNOK. Frikjøp på samfunnsprosjekter.",
\t\t\t    "HUM_001", "Stabil drift, marginalt avvik -0,3 MNOK.",
\t\t\t    "ADM_001", "Sentral vakansstopp T006. Felles konsulentkutt. Merforbruk -8,7 MNOK.",
\t\t\t    "Handelshøyskolen har et samlet netto overskudd på +2,2 MNOK som bidrar til å dempe universitetets sentrale underskudd."
\t\t\t)
\t\tdisplayFolder: _07 RAG & Formatering
\t\tlineageTag: {gen_guid()}
"""
    idx = content.find("\tcolumn Column1")
    if idx != -1:
        new_content = content[:idx] + extra_measures + "\n" + content[idx:]
        with open(measures_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Appended additional measures to _Measures.tmdl")

def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

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

def create_textbox_visual(vis_name, x, y, width, height, tab_order, p1_text, p2_text=None):
    runs = [{"value": p1_text, "textStyle": {"fontFamily": "Segoe UI", "fontSize": "15pt", "fontWeight": "bold", "color": "#1E293B"}}]
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

def build_all_pages():
    for item in os.listdir(PAGES_DIR):
        p = os.path.join(PAGES_DIR, item)
        if os.path.isdir(p):
            shutil.rmtree(p)

    pages_metadata = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
        "pageOrder": [
            "page_dekan_cockpit",
            "page_hhu_drivere",
            "page_evm_prosjekt",
            "page_tiltakslogg"
        ],
        "activePageName": "page_dekan_cockpit"
    }
    write_json(os.path.join(PAGES_DIR, "pages.json"), pages_metadata)

    # =========================================================================
    # PAGE 1: Dekanens Ledelsesdashboard (3-30-300)
    # =========================================================================
    p1_dir = os.path.join(PAGES_DIR, "page_dekan_cockpit")
    p1_vis_dir = os.path.join(p1_dir, "visuals")
    write_json(os.path.join(p1_dir, "page.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": "page_dekan_cockpit",
        "displayName": "Dekanens Ledelsesdashboard (3-30-300)",
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920
    })

    # Header & Slicers
    write_json(os.path.join(p1_vis_dir, "vis_hdr_board_title", "visual.json"), create_textbox_visual(
        "vis_hdr_board_title", 20, 15, 1180, 75, 1,
        "Handelshøyskolen ved UiA (HHU) — Dekanens Ledelsesdashboard & Helårsprognose 2026",
        "Cutoff: 30. september 2026 (M09 YTD) | KD 2025 Kategori 1 (54 550 NOK/SPE) | SRS 9 & 10 | 3-30-300 Styringsmodell"
    ))
    write_json(os.path.join(p1_vis_dir, "vis_slc_aar", "visual.json"), create_slicer_visual(
        "vis_slc_aar", 1220, 15, 160, 75, 2, "DimDate", "Aar", "Regnskapsår", "Single"
    ))
    write_json(os.path.join(p1_vis_dir, "vis_slc_maaned", "visual.json"), create_slicer_visual(
        "vis_slc_maaned", 1400, 15, 220, 75, 3, "DimDate", "MaanedNavnKort", "Rapporteringsperiode", "Single"
    ))
    write_json(os.path.join(p1_vis_dir, "vis_slc_fakultet", "visual.json"), create_slicer_visual(
        "vis_slc_fakultet", 1640, 15, 260, 75, 4, "DimOrganization", "Fakultetsnavn", "Fakultet / Enhet", "Dropdown"
    ))

    # Top 5 KPI Cards
    write_json(os.path.join(p1_vis_dir, "vis_kpi_total_revenue", "visual.json"), create_card_visual(
        "vis_kpi_total_revenue", 20, 105, 360, 115, 5, "Total Inntekt MNOK", "TOTAL INNTEKT (RAMME 2026)",
        "🟢 Budsj: ▲ +0,0 % | 🟢 YoY: ▲ +2,8 % | MoM: ▲ +0,4 %", accent_color="#10B981"
    ))
    write_json(os.path.join(p1_vis_dir, "vis_kpi_net_result_vac", "visual.json"), create_card_visual(
        "vis_kpi_net_result_vac", 400, 105, 360, 115, 6, "Sluttavvik (VAC)", "NETTO SLUTTAVVIK (VAC)",
        "🟢 HHU: +2,2 MNOK (+0,8%) | UiA samlet: -11,0 MNOK (F-05-20)", accent_color="#10B981"
    ))
    write_json(os.path.join(p1_vis_dir, "vis_kpi_staffing_fte", "visual.json"), create_card_visual(
        "vis_kpi_staffing_fte", 780, 105, 360, 115, 7, "Totale Årsverk", "BEMANNING & LØNNSANDEL",
        "🟢 Lønnsandel: 65,4% | 155 UF / 95 TA | Vakanser: 9,3 ÅV", accent_color="#F59E0B"
    ))
    write_json(os.path.join(p1_vis_dir, "vis_kpi_evm_cpi", "visual.json"), create_card_visual(
        "vis_kpi_evm_cpi", 1160, 105, 360, 115, 8, "CPI", "EVM EFFEKTIVITETSINDEKS",
        "🟡 CPI: 0,95 | SPI: 0,92 (Tidsfremdrift) | 5% Kostnadsoverskridelse", accent_color="#F59E0B"
    ))
    write_json(os.path.join(p1_vis_dir, "vis_kpi_students_spe", "visual.json"), create_card_visual(
        "vis_kpi_students_spe", 1540, 105, 360, 115, 9, "Registrerte Studenter", "STUDENTER & PRODUKSJON",
        "🟢 3 120 SPE60 | 22,3 Studenter/UF-ÅV (KD Kat 1: 54 550 kr)", accent_color="#10B981"
    ))

    # Middle Left
    write_json(os.path.join(p1_vis_dir, "vis_cht_revenue_cost_monthly", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "vis_cht_revenue_cost_monthly",
        "position": {"x": 20, "y": 235, "z": 30, "width": 1120, "height": 400, "tabOrder": 10},
        "visual": {
            "visualType": "lineClusteredColumnComboChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimDate"}}, "Property": "MaanedNavn"}}, "queryRef": "DimDate.MaanedNavn", "nativeQueryRef": "Måned", "active": True}]},
                    "Y": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Faktiske & Prognostiserte Driftskostnader"}}, "queryRef": "_Measures.Faktiske & Prognostiserte Driftskostnader", "nativeQueryRef": "Faktisk/Prognose Driftskostnad"}]},
                    "Y2": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Budsjett YTD"}}, "queryRef": "_Measures.Budsjett YTD", "nativeQueryRef": "Månedlig Budsjett"}]},
                    "Tooltips": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Avvik YTD"}}, "queryRef": "_Measures.Avvik YTD", "nativeQueryRef": "Avvik YTD"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Avvik YTD %"}}, "queryRef": "_Measures.Avvik YTD %", "nativeQueryRef": "Avvik %"}
                    ]}
                }
            },
            "objects": {
                "legend": make_legend("'Top'"),
                "lineStyles": [{"properties": {"lineStyle": {"expr": {"Literal": {"Value": "'dashed'"}}}, "strokeWidth": {"expr": {"Literal": {"Value": "2D"}}}}, "selector": {"metadata": "_Measures.Budsjett YTD"}}]
            },
            "visualContainerObjects": {
                "title": make_title("Månedlig Kostnadsutvikling vs. Budsjett M01–M12 (T3 Cutoff pr 30.09)")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # Middle Right
    write_json(os.path.join(p1_vis_dir, "vis_cht_faculty_net_result", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "vis_cht_faculty_net_result",
        "position": {"x": 1160, "y": 235, "z": 31, "width": 740, "height": 400, "tabOrder": 11},
        "visual": {
            "visualType": "barChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimOrganization"}}, "Property": "Instituttnavn"}}, "queryRef": "DimOrganization.Instituttnavn", "nativeQueryRef": "Enhet / Institutt", "active": True}]},
                    "Y": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Sluttavvik (VAC)"}}, "queryRef": "_Measures.Sluttavvik (VAC)", "nativeQueryRef": "Sluttavvik (VAC MNOK)"}]},
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
            "objects": {
                "legend": make_legend("'Top'")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # Bottom Matrix
    write_json(os.path.join(p1_vis_dir, "vis_tbl_faculty_summary_matrix", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "vis_tbl_faculty_summary_matrix",
        "position": {"x": 20, "y": 650, "z": 40, "height": 410, "width": 1880, "tabOrder": 12},
        "visual": {
            "visualType": "pivotTable",
            "query": {
                "queryState": {
                    "Rows": {"projections": [
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimOrganization"}}, "Property": "Fakultetsnavn"}}, "queryRef": "DimOrganization.Fakultetsnavn", "nativeQueryRef": "Fakultet", "active": True},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimOrganization"}}, "Property": "Instituttnavn"}}, "queryRef": "DimOrganization.Instituttnavn", "nativeQueryRef": "Institutt", "active": True}
                    ]},
                    "Values": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Total Inntekt MNOK"}}, "queryRef": "_Measures.Total Inntekt MNOK", "nativeQueryRef": "Total Inntekt (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Actual/FC Lønn"}}, "queryRef": "_Measures.Actual/FC Lønn", "nativeQueryRef": "Lønnskostnad (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Actual/FC Drift"}}, "queryRef": "_Measures.Actual/FC Drift", "nativeQueryRef": "Driftskostnad (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Actual/FC Capex"}}, "queryRef": "_Measures.Actual/FC Capex", "nativeQueryRef": "Investeringer Capex (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Sluttavvik (VAC)"}}, "queryRef": "_Measures.Sluttavvik (VAC)", "nativeQueryRef": "Netto Resultat VAC (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Faglige Årsverk (UF)"}}, "queryRef": "_Measures.Faglige Årsverk (UF)", "nativeQueryRef": "UF-Årsverk"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Studenter pr UF-Årsverk"}}, "queryRef": "_Measures.Studenter pr UF-Årsverk", "nativeQueryRef": "Studenter / UF-ÅV"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Forecast RAG Status"}}, "queryRef": "_Measures.Forecast RAG Status", "nativeQueryRef": "RAG Status"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Diagnose og Drivere"}}, "queryRef": "_Measures.Diagnose og Drivere", "nativeQueryRef": "Strategisk Diagnose"}
                    ]}
                }
            },
            "visualContainerObjects": {
                "stylePreset": [{"properties": {"name": {"expr": {"Literal": {"Value": "'None'"}}}}}],
                "title": make_title("Fakultets- og Instituttoversikt: Totalregnskap, Stillingsstruktur og Styringsdiagnose (300-sekunders dybdeanalyse)")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # =========================================================================
    # PAGE 2: Handelshøyskolen Fag- & Driveranalyse
    # =========================================================================
    p2_dir = os.path.join(PAGES_DIR, "page_hhu_drivere")
    p2_vis_dir = os.path.join(p2_dir, "visuals")
    write_json(os.path.join(p2_dir, "page.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": "page_hhu_drivere",
        "displayName": "Handelshøyskolen Fag- & Driveranalyse",
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920
    })

    write_json(os.path.join(p2_vis_dir, "vis_hdr_hhu_title", "visual.json"), create_textbox_visual(
        "vis_hdr_hhu_title", 20, 15, 1880, 75, 1,
        "Handelshøyskolen ved UiA (HHU) — Operasjonell Styring, Fag- & Driveranalyse 2026",
        "AACSB-akkreditert | KDs Finansieringsmodell 2025 Kategori 1 (54 550 NOK/60 SPE) | SRS 10 Frikjøp (BOA/TDI) & SRS 9 Kontraktstap"
    ))

    write_json(os.path.join(p2_vis_dir, "vis_kpi_hhu_rev", "visual.json"), create_card_visual(
        "vis_kpi_hhu_rev", 20, 105, 360, 115, 2, "HHU Total Revenue", "HHU HELÅRSINNTEKT (LE)",
        "🟢 282,6 MNOK | Budsjett: 282,6 MNOK (100% realisering)", accent_color="#10B981"
    ))
    write_json(os.path.join(p2_vis_dir, "vis_kpi_hhu_margin", "visual.json"), create_card_visual(
        "vis_kpi_hhu_margin", 400, 105, 360, 115, 3, "HHU Netto Resultat", "HHU NETTO DRIFTSMARGIN",
        "🟢 +2,2 MNOK (Overskudd bidrar positivt til UiAs balanse)", accent_color="#10B981"
    ))
    write_json(os.path.join(p2_vis_dir, "vis_kpi_hhu_spe", "visual.json"), create_card_visual(
        "vis_kpi_hhu_spe", 780, 105, 360, 115, 4, "Avlagte SPE60", "PRODUSERTE STUDIEPOENG (SPE60)",
        "🟢 3 120 SPE60 | KD Kategori 1 Inntekt: 170,2 MNOK", accent_color="#10B981"
    ))
    write_json(os.path.join(p2_vis_dir, "vis_kpi_hhu_density", "visual.json"), create_card_visual(
        "vis_kpi_hhu_density", 1160, 105, 360, 115, 5, "HHU Studenter pr UF-Årsverk", "LÆRERTETTHET (STUDENTER/UF)",
        "🟡 22,3 Studenter/UF-ÅV (Maksgrense i sektornorm)", accent_color="#F59E0B"
    ))
    write_json(os.path.join(p2_vis_dir, "vis_kpi_hhu_lonnspct", "visual.json"), create_card_visual(
        "vis_kpi_hhu_lonnspct", 1540, 105, 360, 115, 6, "HHU Lønnsandel %", "LØNNSANDEL DRIFTSKOSTNADER",
        "🟢 65,4% av kostnader (64,9% av inntekt) | Sektormål: <= 65%", accent_color="#10B981"
    ))

    write_json(os.path.join(p2_vis_dir, "vis_cht_hhu_spe_institutt", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "vis_cht_hhu_spe_institutt",
        "position": {"x": 20, "y": 235, "z": 20, "width": 920, "height": 380, "tabOrder": 7},
        "visual": {
            "visualType": "clusteredColumnChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimOrganization"}}, "Property": "Instituttnavn"}}, "queryRef": "DimOrganization.Instituttnavn", "nativeQueryRef": "Institutt", "active": True}]},
                    "Y": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Registrerte Studenter"}}, "queryRef": "_Measures.Registrerte Studenter", "nativeQueryRef": "Studenter"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Avlagte SPE60"}}, "queryRef": "_Measures.Avlagte SPE60", "nativeQueryRef": "SPE60 Helår"}
                    ]}
                }
            },
            "visualContainerObjects": {
                "title": make_title("HHU Instituttfordeling: Registrerte Studenter vs. Avlagte SPE60 (KD Kat 1)")
            },
            "drillFilterOtherVisuals": True
        }
    })

    write_json(os.path.join(p2_vis_dir, "vis_cht_hhu_bemanning", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "vis_cht_hhu_bemanning",
        "position": {"x": 960, "y": 235, "z": 20, "width": 940, "height": 380, "tabOrder": 8},
        "visual": {
            "visualType": "clusteredBarChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimOrganization"}}, "Property": "Instituttnavn"}}, "queryRef": "DimOrganization.Instituttnavn", "nativeQueryRef": "Institutt", "active": True}]},
                    "Y": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Faglige Årsverk (UF)"}}, "queryRef": "_Measures.Faglige Årsverk (UF)", "nativeQueryRef": "UF Faglige Årsverk"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Teknisk-Admin Årsverk (TA)"}}, "queryRef": "_Measures.Teknisk-Admin Årsverk (TA)", "nativeQueryRef": "TA Administrative Årsverk"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Vakanser"}}, "queryRef": "_Measures.Vakanser", "nativeQueryRef": "Ledige Vakanser"}
                    ]}
                }
            },
            "visualContainerObjects": {
                "title": make_title("Stillingsstruktur og Vakanser (UF, TA & Vakansfaktor) pr HHU-Enhet")
            },
            "drillFilterOtherVisuals": True
        }
    })

    write_json(os.path.join(p2_vis_dir, "vis_tbl_hhu_prosjekt_srs", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "vis_tbl_hhu_prosjekt_srs",
        "position": {"x": 20, "y": 630, "z": 25, "width": 1880, "height": 430, "tabOrder": 9},
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {"projections": [
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimOrganization"}}, "Property": "Instituttnavn"}}, "queryRef": "DimOrganization.Instituttnavn", "nativeQueryRef": "Enhet"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactGL"}}, "Property": "ProsjektKode"}}, "queryRef": "FactGL.ProsjektKode", "nativeQueryRef": "Prosjekt"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimAccountHierarchy"}}, "Property": "Kontonavn"}}, "queryRef": "DimAccountHierarchy.Kontonavn", "nativeQueryRef": "Kontonavn"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimAccountHierarchy"}}, "Property": "SRS_regnskapslinje"}}, "queryRef": "DimAccountHierarchy.SRS_regnskapslinje", "nativeQueryRef": "SRS Standard"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Actual YTD Kostnad"}}, "queryRef": "_Measures.Actual YTD Kostnad", "nativeQueryRef": "Påløpt M01-M09 (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Forecast LE Kostnad"}}, "queryRef": "_Measures.Forecast LE Kostnad", "nativeQueryRef": "Helår LE (MNOK)"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactGL"}}, "Property": "Beskrivelse"}}, "queryRef": "FactGL.Beskrivelse", "nativeQueryRef": "Merknad / Regulatorisk Hjemmel"}
                    ]}
                }
            },
            "visualContainerObjects": {
                "title": make_title("Sentrale HHU Transaksjoner og Prosjekter: AACSB Akkreditering, SRS 9 EVU-avsetning & SRS 10 NFR-frikjøp")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # =========================================================================
    # PAGE 3: Prosjektcontrolling & EVM (TDI & S-Kurve)
    # =========================================================================
    p3_dir = os.path.join(PAGES_DIR, "page_evm_prosjekt")
    p3_vis_dir = os.path.join(p3_dir, "visuals")
    write_json(os.path.join(p3_dir, "page.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": "page_evm_prosjekt",
        "displayName": "Prosjektcontrolling & EVM (TDI & S-Kurve)",
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920
    })

    write_json(os.path.join(p3_vis_dir, "vis_hdr_evm_title", "visual.json"), create_textbox_visual(
        "vis_hdr_evm_title", 20, 15, 1880, 75, 1,
        "Prosjektcontrolling & Earned Value Management (EVM) — S-Kurve & TDI-Modell 2026",
        "Standard: Edward Tufte Data-Ink | Direkte Etikettering | Note 15 & Rundskriv F-05-20 (5 %-regelen) | BAC 1 433,0 MNOK / EAC 1 444,0 MNOK"
    ))

    write_json(os.path.join(p3_vis_dir, "vis_kpi_pv", "visual.json"), create_card_visual(
        "vis_kpi_pv", 20, 105, 300, 115, 2, "Planned Value (PV)", "PLANNED VALUE (PV)", "Planlagt budsjett til nå", accent_color="#64748B"
    ))
    write_json(os.path.join(p3_vis_dir, "vis_kpi_ev", "visual.json"), create_card_visual(
        "vis_kpi_ev", 335, 105, 300, 115, 3, "Earned Value (EV)", "EARNED VALUE (EV)", "Opptjent produksjonsverdi", accent_color="#10B981"
    ))
    write_json(os.path.join(p3_vis_dir, "vis_kpi_ac", "visual.json"), create_card_visual(
        "vis_kpi_ac", 650, 105, 300, 115, 4, "Actual Cost (AC)", "ACTUAL COST (AC)", "Faktisk bokførte kostnader", accent_color="#EF4444"
    ))
    write_json(os.path.join(p3_vis_dir, "vis_kpi_cpi_big", "visual.json"), create_card_visual(
        "vis_kpi_cpi_big", 965, 105, 300, 115, 5, "CPI", "COST EFFICIENCY (CPI)", "0,95 | 5% Kostnadsoverskridelse", accent_color="#F59E0B"
    ))
    write_json(os.path.join(p3_vis_dir, "vis_kpi_spi_big", "visual.json"), create_card_visual(
        "vis_kpi_spi_big", 1280, 105, 300, 115, 6, "SPI", "SCHEDULE INDEX (SPI)", "0,92 | Moderat fremdriftsavvik", accent_color="#F59E0B"
    ))
    write_json(os.path.join(p3_vis_dir, "vis_kpi_tcpi_big", "visual.json"), create_card_visual(
        "vis_kpi_tcpi_big", 1595, 105, 305, 115, 7, "TCPI", "TO-COMPLETE INDEX (TCPI)", "Krevd effektivitet reståret", accent_color="#EF4444"
    ))

    write_json(os.path.join(p3_vis_dir, "vis_cht_scurve", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "vis_cht_scurve",
        "position": {"x": 20, "y": 235, "z": 30, "height": 430, "width": 1200, "tabOrder": 8},
        "visual": {
            "visualType": "lineChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimDate"}}, "Property": "MaanedNavn"}}, "queryRef": "DimDate.MaanedNavn", "nativeQueryRef": "Måned", "active": True}]},
                    "Y": {"projections": [
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Planned Value (PV)"}}, "queryRef": "_Measures.Planned Value (PV)", "nativeQueryRef": "PV (Planlagt)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Earned Value (EV)"}}, "queryRef": "_Measures.Earned Value (EV)", "nativeQueryRef": "EV (Opptjent)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Actual Cost (AC)"}}, "queryRef": "_Measures.Actual Cost (AC)", "nativeQueryRef": "AC (Faktisk)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Årsbudsjett (BAC)"}}, "queryRef": "_Measures.Årsbudsjett (BAC)", "nativeQueryRef": "BAC (Ramme)"}
                    ]}
                }
            },
            "objects": {
                "legend": make_legend("'Top'")
            },
            "visualContainerObjects": {
                "title": make_title("EVM S-Kurve: Kumulativ PV, EV, AC og Totalbudsjett (BAC 1 433,0 MNOK)")
            },
            "drillFilterOtherVisuals": True
        }
    })

    write_json(os.path.join(p3_vis_dir, "vis_txt_tdi_note15", "visual.json"), create_textbox_visual(
        "vis_txt_tdi_note15", 1240, 235, 660, 430, 9,
        "BOA & TDI-Modellen (Tid, Direkte, Indirekte Kostnader / Overhead)\n"
        "• SRS 10 Bidrag (NFR/EU): Inntekt = Påløpte kostnader. Ingen fortjeneste. Full balanseføring på konto 2180 ved forskuddsutbetaling.\n"
        "• SRS 9 Oppdrag (EVU): Faktureres etter fullføringsgrad / leverte milepæler. Onerøse kontrakter tapsavsettes umiddelbart (konto 7790).\n"
        "• 5 %-regelen (Rundskriv F-05-20): Ubrukte bevilgningsmidler over 5,0% (71,7 MNOK) må begrunnes særskilt i Note 15 med bindende investeringsplaner.",
        "Veilederkrav: Controller sikrer full overhead-dekning (TDI) og overvåker instituttvise frikjøpsgrader for vitenskapelig ansatte."
    ))

    write_json(os.path.join(p3_vis_dir, "vis_tbl_evm_matrix", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "vis_tbl_evm_matrix",
        "position": {"x": 20, "y": 680, "z": 35, "height": 380, "width": 1880, "tabOrder": 10},
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {"projections": [
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "DimDate"}}, "Property": "MaanedNavn"}}, "queryRef": "DimDate.MaanedNavn", "nativeQueryRef": "Måned"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Planned Value (PV)"}}, "queryRef": "_Measures.Planned Value (PV)", "nativeQueryRef": "PV (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Earned Value (EV)"}}, "queryRef": "_Measures.Earned Value (EV)", "nativeQueryRef": "EV (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Actual Cost (AC)"}}, "queryRef": "_Measures.Actual Cost (AC)", "nativeQueryRef": "AC (MNOK)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Cost Variance (CV)"}}, "queryRef": "_Measures.Cost Variance (CV)", "nativeQueryRef": "CV (Kostnadsavvik)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Schedule Variance (SV)"}}, "queryRef": "_Measures.Schedule Variance (SV)", "nativeQueryRef": "SV (Tidsavvik)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "CPI"}}, "queryRef": "_Measures.CPI", "nativeQueryRef": "CPI"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "SPI"}}, "queryRef": "_Measures.SPI", "nativeQueryRef": "SPI"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "EAC (EVM)"}}, "queryRef": "_Measures.EAC (EVM)", "nativeQueryRef": "EAC (Sluttkostnad)"},
                        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "VAC (EVM)"}}, "queryRef": "_Measures.VAC (EVM)", "nativeQueryRef": "VAC (Sluttavvik)"}
                    ]}
                }
            },
            "visualContainerObjects": {
                "title": make_title("Månedlige EVM-Nøkkeltall: Kumulativ utvikling og fremdriftsindekser 2026 (M01-M12)")
            },
            "drillFilterOtherVisuals": True
        }
    })

    # =========================================================================
    # PAGE 4: Tiltakslogg & Handlingsplan (FactAction)
    # =========================================================================
    p4_dir = os.path.join(PAGES_DIR, "page_tiltakslogg")
    p4_vis_dir = os.path.join(p4_dir, "visuals")
    write_json(os.path.join(p4_dir, "page.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": "page_tiltakslogg",
        "displayName": "Tiltakslogg & Handlingsplan (FactAction)",
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920
    })

    write_json(os.path.join(p4_vis_dir, "vis_hdr_action_title", "visual.json"), create_textbox_visual(
        "vis_hdr_action_title", 20, 15, 1880, 75, 1,
        "Omstillings- og Tiltaksoppfølging (FactAction) — Gap-lukking mot Budsjett 2026",
        "Risikostyrt porteføljeoppfølging (RAG) | Forventet helårseffekt: -7,6 MNOK | Realisert per T3: -5,85 MNOK (77,0 % realiseringsgrad)"
    ))

    write_json(os.path.join(p4_vis_dir, "vis_kpi_action_forventet", "visual.json"), create_card_visual(
        "vis_kpi_action_forventet", 20, 105, 450, 115, 2, "Forventet Tiltakseffekt", "FORVENTET HELÅRSEFFEKT",
        "Total planlagt kostnadsreduksjon", accent_color="#64748B"
    ))
    write_json(os.path.join(p4_vis_dir, "vis_kpi_action_realisert", "visual.json"), create_card_visual(
        "vis_kpi_action_realisert", 495, 105, 450, 115, 3, "Realisert Tiltakseffekt", "REALISERT EFFEKT PR. 30.09",
        "Bokførte innsparinger YTD", accent_color="#10B981"
    ))
    write_json(os.path.join(p4_vis_dir, "vis_kpi_action_gjenstaende", "visual.json"), create_card_visual(
        "vis_kpi_action_gjenstaende", 970, 105, 450, 115, 4, "Gjenstående Tiltakseffekt", "GJENSTÅENDE EFFEKT Q4",
        "Innsparinger som må realiseres i Q4", accent_color="#F59E0B"
    ))
    write_json(os.path.join(p4_vis_dir, "vis_kpi_action_grad", "visual.json"), create_card_visual(
        "vis_kpi_action_grad", 1445, 105, 455, 115, 5, "Tiltaksdekning %", "REALISERINGSGRAD",
        "🟢 77,0% | Planmessig fremdrift", accent_color="#10B981"
    ))

    write_json(os.path.join(p4_vis_dir, "vis_tbl_factaction", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "vis_tbl_factaction",
        "position": {"x": 20, "y": 235, "z": 25, "height": 450, "width": 1880, "tabOrder": 6},
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {"projections": [
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction"}}, "Property": "TiltakID"}}, "queryRef": "FactAction.TiltakID", "nativeQueryRef": "ID"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction"}}, "Property": "Enhet"}}, "queryRef": "FactAction.Enhet", "nativeQueryRef": "Enhet"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction"}}, "Property": "TiltakNavn"}}, "queryRef": "FactAction.TiltakNavn", "nativeQueryRef": "Tiltaksnavn"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction"}}, "Property": "AnsvarligRolle"}}, "queryRef": "FactAction.AnsvarligRolle", "nativeQueryRef": "Ansvarlig Rolle"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction"}}, "Property": "StartDato"}}, "queryRef": "FactAction.StartDato", "nativeQueryRef": "Startdato"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction"}}, "Property": "FristDato"}}, "queryRef": "FactAction.FristDato", "nativeQueryRef": "Frist"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction"}}, "Property": "ForventetEffektMNOK"}}, "queryRef": "FactAction.ForventetEffektMNOK", "nativeQueryRef": "Forventet (MNOK)"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction"}}, "Property": "RealisertEffektMNOK"}}, "queryRef": "FactAction.RealisertEffektMNOK", "nativeQueryRef": "Realisert (MNOK)"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction"}}, "Property": "Prioritet"}}, "queryRef": "FactAction.Prioritet", "nativeQueryRef": "Prioritet"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "FactAction"}}, "Property": "Status"}}, "queryRef": "FactAction.Status", "nativeQueryRef": "RAG Status"}
                    ]}
                }
            },
            "visualContainerObjects": {
                "title": make_title("Handlingsplan og Omstillingstiltak (FactAction): Status, Ansvar og Finansiell Effekt 2026")
            },
            "drillFilterOtherVisuals": True
        }
    })

    write_json(os.path.join(p4_vis_dir, "vis_txt_gap_bridge", "visual.json"), create_textbox_visual(
        "vis_txt_gap_bridge", 20, 705, 1880, 350, 7,
        "Senior Controller Vurdering & Strategiske Handlingsalternativer for Fakultetsledelsen (HHU)\n"
        "• HHU bidrar med +2,2 MNOK i positivt driftsresultat: Dette demper UiAs samlede helårsavvik (-11,0 MNOK som må dekkes av formålskapital iht. F-05-20).\n"
        "• Tiltak T001 (Administrativ ansettelsesstopp på HHU ADM): Har allerede levert -0,9 MNOK av forventet -1,2 MNOK.\n"
        "• Tiltak T002 (Omdisponering faglige årsverk): Fullført med 100% måloppnåelse (-0,85 MNOK) og styrket undervisningskapasitet på Økonomi.\n"
        "• Tiltak T003 (EVU porteføljeekspansjon): Pågår mot Agder-næringslivet med -0,8 MNOK realisert av -1,5 MNOK målsetting.\n"
        "• Strategisk Anbefaling: Opprettholde vakansbrems i Q4, prioritere NFR-frikjøp (SRS 10) for vitenskapelige ansatte, og overvåke EVU001 nøye for å unngå ytterligere kontraktstap etter SRS 9."
    ))

    print("All PBIR pages and visual containers created successfully!")

if __name__ == "__main__":
    append_additional_measures()
    build_all_pages()
