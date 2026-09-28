"""
PBIR Report Generator for HHU-Rapport.Report
Generates 11 production-grade PBIR report pages adhering to Edward Tufte Data-Ink Ratio rules
and Frank Ellingsen's Project Controlling standards, incorporating all reporting from UIA-Handelshøyskolen USE-CASE.xlsx.
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

def col_proj(entity, prop, native=None):
    return {
        "field": {
            "Column": {
                "Expression": {"SourceRef": {"Entity": entity}},
                "Property": prop
            }
        },
        "queryRef": f"{entity}.{prop}",
        "nativeQueryRef": native or prop,
        "active": True
    }

def meas_proj(meas, native=None):
    return {
        "field": {
            "Measure": {
                "Expression": {"SourceRef": {"Entity": "_Measures"}},
                "Property": meas
            }
        },
        "queryRef": f"_Measures.{meas}",
        "nativeQueryRef": native or meas
    }

def create_textbox_visual(vis_name, x, y, width, height, tab_order, p1_text, p2_text=None):
    runs = [{"value": p1_text, "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "13pt", "fontWeight": "bold", "color": "#0F172A"}}]
    paragraphs = [{"textRuns": runs}]
    if p2_text:
        paragraphs.append({"textRuns": [{"value": p2_text, "textStyle": {"fontFamily": "Segoe UI", "fontSize": "9pt", "color": "#64748B"}}]})
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": vis_name,
        "position": {
            "x": x, "y": y, "z": 10, "height": height, "width": width, "tabOrder": tab_order
        },
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [{"properties": {"paragraphs": paragraphs}}]
            }
        }
    }

def create_callout_box_visual(vis_name, x, y, width, height, tab_order, title_text, body_text, accent_color="#0F172A"):
    paragraphs = [
        {"textRuns": [{"value": title_text, "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "11pt", "fontWeight": "bold", "color": accent_color}}]},
        {"textRuns": [{"value": " ", "textStyle": {"fontSize": "4pt"}}]},
        {"textRuns": [{"value": body_text, "textStyle": {"fontFamily": "Segoe UI", "fontSize": "9pt", "color": "#334155"}}]}
    ]
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": vis_name,
        "position": {
            "x": x, "y": y, "z": 10, "height": height, "width": width, "tabOrder": tab_order
        },
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [{"properties": {"paragraphs": paragraphs}}]
            }
        }
    }

def create_slicer_visual(vis_name, x, y, width, height, tab_order, entity, column_name, title, mode="Single"):
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": vis_name,
        "position": {
            "x": x, "y": y, "z": 15, "width": width, "height": height, "tabOrder": tab_order
        },
        "visual": {
            "visualType": "slicer",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [col_proj(entity, column_name, title)]
                    }
                }
            },
            "objects": {
                "data": [{"properties": {"mode": {"expr": {"Literal": {"Value": f"'{mode}'"}}}}}],
                "header": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}}}]
            },
            "drillFilterOtherVisuals": True
        }
    }

def create_card_visual(vis_name, x, y, width, height, tab_order, measure_name, title, subtitle_text=None, accent_color="#10B981"):
    vis = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": vis_name,
        "position": {
            "x": x, "y": y, "z": 20, "height": height, "width": width, "tabOrder": tab_order
        },
        "visual": {
            "visualType": "cardVisual",
            "query": {
                "queryState": {
                    "Data": {
                        "projections": [meas_proj(measure_name, title)]
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

def create_table_visual(vis_name, x, y, width, height, tab_order, projections, title):
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": vis_name,
        "position": {
            "x": x, "y": y, "z": 30, "height": height, "width": width, "tabOrder": tab_order
        },
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {"projections": projections}
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
                "title": make_title(title)
            },
            "drillFilterOtherVisuals": True
        }
    }

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
        {"id": "page_p2_institutter", "name": "2. Enhets- & Kontooppfølging"},
        {"id": "page_p3_variance", "name": "3. Avviks- & Rotårsaksanalyse"},
        {"id": "page_p4_actionplan", "name": "4. Prioritert Handlingsplan"},
        {"id": "page_p5_staffing", "name": "5. Bemanningsanalyse & Årsverk"},
        {"id": "page_p6_evm", "name": "6. EVM Fremdrift & S-Kurve"},
        {"id": "page_p7_students", "name": "7. Studieproduksjon & KD"},
        {"id": "page_p8_budget2027", "name": "8. Budsjett 2027 Planrapport"},
        {"id": "page_p9_process", "name": "9. Budsjettprosess & Lukkeplan"},
        {"id": "page_p10_methods", "name": "10. Prognosemetodikk 2027"},
        {"id": "page_p11_modelguide", "name": "11. Datamodell & Kvalitetskontroll"}
    ]

    pages_metadata = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
        "pageOrder": [p["id"] for p in pages],
        "activePageName": "page_p1_summary"
    }
    write_json(os.path.join(PAGES_DIR, "pages.json"), pages_metadata)

    def init_page(page_id, display_name):
        pdir = os.path.join(PAGES_DIR, page_id)
        vdir = os.path.join(pdir, "visuals")
        os.makedirs(vdir, exist_ok=True)
        write_json(os.path.join(pdir, "page.json"), {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
            "name": page_id,
            "displayName": display_name,
            "displayOption": "FitToPage",
            "height": 1080,
            "width": 1920
        })
        return vdir

    # =========================================================================
    # PAGE 1: LEDELSESSAMMENDRAG 2026 (page_p1_summary)
    # =========================================================================
    p1_vis = init_page("page_p1_summary", "1. Ledelsessammendrag 2026")
    write_json(os.path.join(p1_vis, "hdr_title", "visual.json"), create_textbox_visual(
        "hdr_title", 20, 15, 1180, 75, 1,
        "Handelshøyskolen ved UiA (HHU) — Ledelsessammendrag & Helårsprognose 2026",
        "Vedtatt ramme 130,2 MNOK | Cutoff: 30.09.2026 (M01-M09 Actuals, M10-M12 Q4 Forecast) | Tufte Minimalist Standard"
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

    # Top KPI Cards
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

    # Middle Left: Combo Chart
    write_json(os.path.join(p1_vis, "cht_monthly_actuals_fc", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "cht_monthly_actuals_fc",
        "position": {"x": 20, "y": 240, "z": 30, "width": 1120, "height": 380, "tabOrder": 10},
        "visual": {
            "visualType": "lineClusteredColumnComboChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [col_proj("DimDate", "MaanedNavnKort", "Måned")]},
                    "Y": {"projections": [meas_proj("Faktiske & Prognostiserte Driftskostnader", "Faktiske & Prognose (MNOK)")]},
                    "Y2": {"projections": [meas_proj("Budsjett YTD", "Budsjett (MNOK)")]}
                }
            },
            "objects": {
                "legend": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "position": {"expr": {"Literal": {"Value": "'Top'"}}}}}]
            },
            "visualContainerObjects": {"title": make_title("Månedlig Driftskostnad: M01-M09 Faktisk, M10-M12 Q4 Prognose vs. Budsjett")},
            "drillFilterOtherVisuals": True
        }
    })

    # Middle Right: Horizontal Bar Chart
    write_json(os.path.join(p1_vis, "cht_faculty_vac", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "cht_faculty_vac",
        "position": {"x": 1160, "y": 240, "z": 30, "width": 740, "height": 380, "tabOrder": 11},
        "visual": {
            "visualType": "clusteredBarChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [col_proj("DimOrganization", "Enhetsnavn", "Enhet")]},
                    "Y": {"projections": [meas_proj("Sluttavvik (VAC)", "Sluttavvik (VAC)")]}
                }
            },
            "visualContainerObjects": {"title": make_title("Helårsavvik per Institutt (MNOK) — Favorable vs. Unfavorable")},
            "drillFilterOtherVisuals": True
        }
    })

    # Bottom Left: Matrix Table
    p1_matrix_projs = [
        col_proj("DimOrganization", "OrgKode", "OrgKode"),
        col_proj("DimOrganization", "Enhetsnavn", "Enhet"),
        meas_proj("Total Inntekt MNOK", "Total Inntekt (MNOK)"),
        meas_proj("Actual/FC Lønn", "Lønnskostnad (MNOK)"),
        meas_proj("Actual/FC Drift", "Driftskostnad (MNOK)"),
        meas_proj("Actual/FC Capex", "Investeringer Capex"),
        meas_proj("Sluttavvik (VAC)", "Netto Resultat VAC"),
        meas_proj("Faglige Årsverk (UF)", "UF-Årsverk"),
        meas_proj("Studenter pr UF-Årsverk", "Studenter/UF"),
        meas_proj("Forecast RAG Status", "RAG Status")
    ]
    write_json(os.path.join(p1_vis, "tbl_institute_matrix", "visual.json"), create_table_visual(
        "tbl_institute_matrix", 20, 635, 1260, 425, 12, p1_matrix_projs,
        "Fakultets- og Instituttoversikt: Totalregnskap, Stillingsstruktur og Styringsstatus (300-sekunders dybdeanalyse)"
    ))

    # Bottom Right: Executive Callout Textbox
    write_json(os.path.join(p1_vis, "callout_p1_conclusion", "visual.json"), create_callout_box_visual(
        "callout_p1_conclusion", 1300, 635, 600, 425, 13,
        "📌 LEDELSESKONKLUSJON (3–30–300 Beslutningsvisning)",
        "September YTD + Q4-prognose viser 4,1 MNOK mindreforbruk mot budsjett, men resultatet drives av midlertidige forsinkelser i ansettelser (K12000) og økt ekstern prosjektaktivitet.\n\n"
        "1. Kritiske flaskehalser: Månedlig prognoseavvik på 1,2 MNOK må lukkes før UBW-systemfrys 15.11.2026.\n\n"
        "2. Bemanningsrisiko: Konto-basert lønnsandel (66,8 %) overskrider målet på 64,5 % med 2,3 prosentpoeng.\n\n"
        "3. Omstilling 2027: Tiltakene T001–T003 må realisere planlagt helårseffekt på 3,8 MNOK for å sikre balanse.",
        accent_color="#0369A1"
    ))

    # =========================================================================
    # PAGE 2: ENHETS- & KONTOOPPFØLGING (page_p2_institutter)
    # =========================================================================
    p2_vis = init_page("page_p2_institutter", "2. Enhets- & Kontooppfølging")
    write_json(os.path.join(p2_vis, "hdr_title", "visual.json"), create_textbox_visual(
        "hdr_title", 20, 15, 1280, 75, 1,
        "2. Enhets- & Kontooppfølging — Økonomiske Rammer og Kontostruktur",
        "Granulær oppfølging av inntekter, lønn og drift per institutt og SRS-kontoart | M01-M09 Faktisk, M10-M12 Prognose"
    ))
    write_json(os.path.join(p2_vis, "slc_org", "visual.json"), create_slicer_visual(
        "slc_org", 1320, 15, 280, 75, 2, "DimOrganization", "Enhetsnavn", "Enhet / Institutt", "Dropdown"
    ))
    write_json(os.path.join(p2_vis, "slc_kontotype", "visual.json"), create_slicer_visual(
        "slc_kontotype", 1620, 15, 280, 75, 3, "DimAccountHierarchy", "Kontotype", "Kontotype", "Dropdown"
    ))

    write_json(os.path.join(p2_vis, "kpi_k10", "visual.json"), create_card_visual("kpi_k10", 20, 105, 450, 120, 4, "HHU K10000 Admin Budsjett", "K10000 FAKULTETSADMINISTRASJON", "Vedtatt årsramme", accent_color="#334155"))
    write_json(os.path.join(p2_vis, "kpi_k11", "visual.json"), create_card_visual("kpi_k11", 490, 105, 450, 120, 5, "HHU K11000 Ledelse Budsjett", "K11000 LEDELSE OG INNOVASJON", "Vedtatt årsramme", accent_color="#0284C7"))
    write_json(os.path.join(p2_vis, "kpi_k12", "visual.json"), create_card_visual("kpi_k12", 960, 105, 450, 120, 6, "HHU K12000 Rettsvitenskap Budsjett", "K12000 RETTSVITENSKAP", "Vedtatt årsramme", accent_color="#10B981"))
    write_json(os.path.join(p2_vis, "kpi_k13", "visual.json"), create_card_visual("kpi_k13", 1430, 105, 470, 120, 7, "HHU K13000 Økonomi Budsjett", "K13000 ØKONOMI (SIVILØKONOM)", "Vedtatt årsramme", accent_color="#F59E0B"))

    p2_acc_projs = [
        col_proj("DimAccountHierarchy", "Konto", "Konto"),
        col_proj("DimAccountHierarchy", "Kontonavn", "Kontonavn"),
        col_proj("DimAccountHierarchy", "SRS_regnskapslinje", "SRS-Linje"),
        meas_proj("Actual YTD", "Regnskap YTD"),
        meas_proj("Budsjett YTD", "Budsjett YTD"),
        meas_proj("Avvik YTD", "Avvik YTD"),
        meas_proj("Forecast LE (EAC)", "Helårsprognose (LE)"),
        meas_proj("Årsbudsjett (BAC)", "Årsbudsjett (BAC)"),
        meas_proj("Sluttavvik (VAC)", "Sluttavvik (VAC)")
    ]
    write_json(os.path.join(p2_vis, "tbl_kontooppfoelging", "visual.json"), create_table_visual(
        "tbl_kontooppfoelging", 20, 240, 1260, 480, 8, p2_acc_projs,
        "Kontooppfølging: Regnskap, Budsjett og Sluttavvik per Hovedbokskonto (SRS)"
    ))

    write_json(os.path.join(p2_vis, "callout_p2_analytical", "visual.json"), create_callout_box_visual(
        "callout_p2_analytical", 1300, 240, 600, 480, 9,
        "📋 ANALYTISK KONKLUSJON (Fra Unit Analysis)",
        "Enhetsanalysen avdekker tre vesentlige styringsforhold for Handelshøyskolen:\n\n"
        "• K13000 Økonomi er fakultetets største enhet med 1 450 studenter og 129,3 MNOK i inntekter. Høy aktivitet gir stram kostnadsstyring, spesielt innen pensjonsreguleringer.\n\n"
        "• K11000 Ledelse har marginal lønnsomhet på etter- og videreutdanning (EVU). Kontraktsmarginer må gjennomgås før nye leveranser igangsettes.\n\n"
        "• K12000 Rettsvitenskap har et midlertidig regnskapsmessig overskudd på 1,8 MNOK, men dette skyldes forsinkelser i ansettelser av førsteamanuenser og representerer en faglig kapasitetsrisiko.",
        accent_color="#0F172A"
    ))

    p2_org_projs = [
        col_proj("DimOrganization", "OrgKode", "OrgKode"),
        col_proj("DimOrganization", "Enhetsnavn", "Enhetsnavn"),
        meas_proj("Total Inntekt MNOK", "Total Inntekt"),
        meas_proj("Actual/FC Lønn", "Lønnskostnad"),
        meas_proj("Actual/FC Drift", "Driftskostnad"),
        meas_proj("Sluttavvik (VAC)", "Netto Sluttavvik (VAC)")
    ]
    write_json(os.path.join(p2_vis, "tbl_enhetsfordeling", "visual.json"), create_table_visual(
        "tbl_enhetsfordeling", 20, 735, 1880, 325, 10, p2_org_projs,
        "Enhetsfordeling: Samlet Kostnads- og Inntektsbilde per Institutt"
    ))

    # =========================================================================
    # PAGE 3: AVVIKS- & ROTÅRSAKSANALYSE (page_p3_variance)
    # =========================================================================
    p3_vis = init_page("page_p3_variance", "3. Avviks- & Rotårsaksanalyse")
    write_json(os.path.join(p3_vis, "hdr_title", "visual.json"), create_textbox_visual(
        "hdr_title", 20, 15, 1400, 75, 1,
        "3. Avviks- og Rotårsaksanalyse — Kritiske Avviksdrivere og Månedshotspots",
        "Kvantifisering av vesentlige budsjettavvik, underliggende årsaker og tidsmessige hotspots | Kilde: Variance Actions Sheet"
    ))
    write_json(os.path.join(p3_vis, "slc_org", "visual.json"), create_slicer_visual(
        "slc_org", 1440, 15, 460, 75, 2, "DimOrganization", "Enhetsnavn", "Enhet / Institutt", "Dropdown"
    ))

    write_json(os.path.join(p3_vis, "kpi_tot_avvik", "visual.json"), create_card_visual("kpi_tot_avvik", 20, 105, 450, 120, 3, "Sluttavvik (VAC)", "SAMLET SLUTTAVVIK (VAC)", "Netto mindreforbruk", accent_color="#10B981"))
    write_json(os.path.join(p3_vis, "kpi_max_avvik", "visual.json"), create_card_visual("kpi_max_avvik", 490, 105, 450, 120, 4, "Største Enkeltavvik MNOK", "STØRSTE ENKELTAVVIK", "Pensjonspremieavvik K13000", accent_color="#EF4444"))
    write_json(os.path.join(p3_vis, "kpi_driver_count", "visual.json"), create_card_visual("kpi_driver_count", 960, 105, 450, 120, 5, "Antall Avviksdrivere", "IDENTIFISERTE DRIVERE", "11 vesentlige poster", accent_color="#0284C7"))
    write_json(os.path.join(p3_vis, "kpi_vac_pct", "visual.json"), create_card_visual("kpi_vac_pct", 1430, 105, 470, 120, 6, "VAC %", "AVVIKSPROSENT %", "Normalisert mot budsjett", accent_color="#F59E0B"))

    p3_vd_projs = [
        col_proj("FactVarianceDriver", "OrgKode", "Org"),
        col_proj("FactVarianceDriver", "Konto", "Konto"),
        col_proj("FactVarianceDriver", "Avviksdriver", "Avviksdriver / Årsak"),
        col_proj("FactVarianceDriver", "BudsjettBelop", "Budsjett (kr)"),
        col_proj("FactVarianceDriver", "PrognoseLE", "Prognose LE (kr)"),
        col_proj("FactVarianceDriver", "AvvikBelop", "Avvik (kr)"),
        col_proj("FactVarianceDriver", "AvvikProsent", "Avvik %"),
        col_proj("FactVarianceDriver", "RAG_Status", "RAG Status")
    ]
    write_json(os.path.join(p3_vis, "tbl_variance_drivers", "visual.json"), create_table_visual(
        "tbl_variance_drivers", 20, 240, 1260, 500, 7, p3_vd_projs,
        "Topp 11 Avviksdrivere: Kvantifisering av Vesentlige Avvik og Årsakssammenhenger"
    ))

    p3_mh_projs = [
        col_proj("FactMonthHotspot", "Maaned", "Måned"),
        col_proj("FactMonthHotspot", "AvvikBelop", "Avvik (kr)"),
        col_proj("FactMonthHotspot", "Forklaring", "Årsaksforklaring & Sesongmønster")
    ]
    write_json(os.path.join(p3_vis, "tbl_month_hotspots", "visual.json"), create_table_visual(
        "tbl_month_hotspots", 1300, 240, 600, 500, 8, p3_mh_projs,
        "4 Månedshotspots (Sesongmessige Avvik)"
    ))

    write_json(os.path.join(p3_vis, "callout_p3_management", "visual.json"), create_callout_box_visual(
        "callout_p3_management", 20, 755, 1880, 305, 9,
        "⚠️ LEDELSESVURDERING OG ROBUSTHETSANALYSE",
        "Ledelsens gjennomgang viser at fakultetets positive helårsavvik (+4,1 MNOK) skjuler strukturelle sårbarheter:\n\n"
        "1. Pensjonsreguleringsrisiko: Pensjonspremieavviket ved K13000 (-1,8 MNOK) inntreffer i M03 og må håndteres med faste kvartalsvise avsetninger.\n"
        "2. EVU-inntektssvikt: K11000 har 1,5 MNOK lavere kursinntekter enn budsjettert, noe som krever umiddelbar stopp i leveranser uten positiv kontraktsmargin.\n"
        "3. Vakanser ved K12000: Besparelsen på 1,8 MNOK skyldes forsinket rekruttering av vitenskapelig ansatte, som må beskyttes mot permanente budsjettkutt.",
        accent_color="#B91C1C"
    ))

    # =========================================================================
    # PAGE 4: PRIORITERT HANDLINGSPLAN (page_p4_actionplan)
    # =========================================================================
    p4_vis = init_page("page_p4_actionplan", "4. Prioritert Handlingsplan")
    write_json(os.path.join(p4_vis, "hdr_title", "visual.json"), create_textbox_visual(
        "hdr_title", 20, 15, 1880, 75, 1,
        "4. Prioritert Handlingsplan — Tiltaksoppfølging, Eierskap og Beslutninger",
        "5 prioriterte tiltak for å lukke gap og omstillingsprogram T001–T004 | Kilde: Variance Actions Sheet Del 3"
    ))

    write_json(os.path.join(p4_vis, "kpi_brutto_gap", "visual.json"), create_card_visual("kpi_brutto_gap", 20, 105, 450, 120, 2, "Samlet Brutto Gap Handlingsplan", "SAMLET BRUTTO GAP", "Identifisert risikobeløp", accent_color="#EF4444"))
    write_json(os.path.join(p4_vis, "kpi_tiltak_effekt", "visual.json"), create_card_visual("kpi_tiltak_effekt", 490, 105, 450, 120, 3, "Samlet Tiltakseffekt Handlingsplan", "PLANLAGT TILTAKSEFFEKT", "Forventet innsparing", accent_color="#10B981"))
    write_json(os.path.join(p4_vis, "kpi_netto_restrisiko", "visual.json"), create_card_visual("kpi_netto_restrisiko", 960, 105, 450, 120, 4, "Netto Restrisiko Handlingsplan", "NETTO RESTRISIKO", "Gjenværende gap etter tiltak", accent_color="#F59E0B"))
    write_json(os.path.join(p4_vis, "kpi_antall_tiltak", "visual.json"), create_card_visual("kpi_antall_tiltak", 1430, 105, 470, 120, 5, "Antall Tiltak i Handlingsplan", "PRIORITERTE TILTAK", "Kritiske omstillingsløp", accent_color="#0284C7"))

    p4_ap_projs = [
        col_proj("FactActionPlan", "Prio", "Prio"),
        col_proj("FactActionPlan", "Omraade", "Område"),
        col_proj("FactActionPlan", "Rotaarsak", "Rotårsak / Observasjon"),
        col_proj("FactActionPlan", "AnbefaltHandling", "Anbefalt Handling"),
        col_proj("FactActionPlan", "AnsvarligEier", "Eier"),
        col_proj("FactActionPlan", "FristDato", "Frist"),
        col_proj("FactActionPlan", "BruttoGapNOK", "Brutto Gap (kr)"),
        col_proj("FactActionPlan", "ForventetEffektNOK", "Effekt (kr)"),
        col_proj("FactActionPlan", "KPI_Kontrollpunkt", "KPI / Kontroll"),
        col_proj("FactActionPlan", "RAG_Status", "RAG"),
        col_proj("FactActionPlan", "BeslutningNaa", "Beslutning Nå"),
        col_proj("FactActionPlan", "Oppfoelging", "Oppfølgingsarena")
    ]
    write_json(os.path.join(p4_vis, "tbl_action_plan", "visual.json"), create_table_visual(
        "tbl_action_plan", 20, 240, 1880, 480, 6, p4_ap_projs,
        "Prioritert Handlingsplan: 5 Kritiske Tiltak for Budsjettbalanse og Risikohåndtering"
    ))

    p4_act_projs = [
        col_proj("FactAction", "TiltakID", "TiltakID"),
        col_proj("FactAction", "OrgKode", "Enhet"),
        col_proj("FactAction", "TiltakNavn", "Tiltakstittel"),
        col_proj("FactAction", "ForventetEffekt", "Forventet Effekt (kr)"),
        col_proj("FactAction", "RealisertEffekt", "Realisert (kr)"),
        col_proj("FactAction", "Status", "Status"),
        col_proj("FactAction", "FristDato", "Frist")
    ]
    write_json(os.path.join(p4_vis, "tbl_actions_t001_t004", "visual.json"), create_table_visual(
        "tbl_actions_t001_t004", 20, 735, 1200, 325, 7, p4_act_projs,
        "Omstillingsportefølje T001–T004 (Gjennomføring & Realisering)"
    ))

    write_json(os.path.join(p4_vis, "callout_p4_escalation", "visual.json"), create_callout_box_visual(
        "callout_p4_escalation", 1240, 735, 660, 325, 8,
        "📋 ESKALERING OG BESLUTNINGSKRAV (Tiltaksportefølje)",
        "For å sikre realisering av tiltakseffekten på 3,8 MNOK gjelder følgende styringskrav:\n\n"
        "• Prio 1 (K13000): Ansettelsesstopp for stillinger uten ekstern finansiering gjelder med umiddelbar virkning.\n"
        "• Prio 2 (K11000): EVU-marginanalyse ferdigstilles innen 15.10.2026; ulønnsomme moduler avvikles.\n"
        "• Prio 5 (Portefølje): Ukentlig statusrapportering til fakultetsdirektør; avvik > 10 % eskaleres til dekanen.",
        accent_color="#0F172A"
    ))

    # =========================================================================
    # PAGE 5: BEMANNINGSANALYSE & ÅRSVERK (page_p5_staffing)
    # =========================================================================
    p5_vis = init_page("page_p5_staffing", "5. Bemanningsanalyse & Årsverk")
    write_json(os.path.join(p5_vis, "hdr_title", "visual.json"), create_textbox_visual(
        "hdr_title", 20, 15, 1400, 75, 1,
        "5. Bemanningsanalyse & Årsverk (FTE) — Stillingsstruktur og Lønnsandel",
        "Analyse av faglige årsverk (UF), teknisk-administrative årsverk (TA) og lønnskostnadsandel mot målkrav"
    ))
    write_json(os.path.join(p5_vis, "slc_org", "visual.json"), create_slicer_visual(
        "slc_org", 1440, 15, 460, 75, 2, "DimOrganization", "Enhetsnavn", "Enhet / Institutt", "Dropdown"
    ))

    write_json(os.path.join(p5_vis, "kpi_fte_total", "visual.json"), create_card_visual("kpi_fte_total", 20, 105, 450, 120, 3, "Totale Årsverk", "TOTALE ÅRSVERK (FTE)", "229,0 ÅV per M12", accent_color="#334155"))
    write_json(os.path.join(p5_vis, "kpi_fte_uf", "visual.json"), create_card_visual("kpi_fte_uf", 490, 105, 450, 120, 4, "Faglige Årsverk (UF)", "FAGLIGE ÅRSVERK (UF)", "Undervisning & forskning", accent_color="#0284C7"))
    write_json(os.path.join(p5_vis, "kpi_fte_ta", "visual.json"), create_card_visual("kpi_fte_ta", 960, 105, 450, 120, 5, "Teknisk-Admin Årsverk (TA)", "ADMIN. ÅRSVERK (TA)", "Drift & fakultetsstøtte", accent_color="#475569"))
    write_json(os.path.join(p5_vis, "kpi_fte_andel", "visual.json"), create_card_visual("kpi_fte_andel", 1430, 105, 470, 120, 6, "Faglig Andel %", "FAGLIG ANDEL %", "Målkrav: > 50–55 %", accent_color="#10B981"))

    p5_fte_projs = [
        col_proj("FactFTE", "OrgKode", "Enhet"),
        col_proj("FactFTE", "Stillingstype", "Stillingstype"),
        col_proj("FactFTE", "Aarsverk", "Årsverk"),
        col_proj("FactFTE", "Aarsverk_UF", "UF-Årsverk"),
        col_proj("FactFTE", "Aarsverk_TA", "TA-Årsverk"),
        col_proj("FactFTE", "Budsjettert_Aarsverk", "Budsjettert ÅV")
    ]
    write_json(os.path.join(p5_vis, "tbl_fte_breakdown", "visual.json"), create_table_visual(
        "tbl_fte_breakdown", 20, 240, 1260, 480, 7, p5_fte_projs,
        "Stillingsstruktur per Institutt: Årsverksfordeling og Bemanningskategorier"
    ))

    write_json(os.path.join(p5_vis, "callout_p5_staffing_diag", "visual.json"), create_callout_box_visual(
        "callout_p5_staffing_diag", 1300, 240, 600, 480, 8,
        "📋 BEMANNINGSDIAGNOSE & LØNNSANDEL",
        "• Faglig andel på 67,2 % er godt over sektormålet på 50–55 %, noe som sikrer kjerneleveransen innen forskning og utdanning.\n\n"
        "• Konto-basert lønnsandel (66,8 %) overskrider målet på 64,5 % (+2,27 pp). Dette representerer en strukturell kostnadsutfordring for 2027-budsjettet.\n\n"
        "• Avstemming mot UBW: Det er identifisert en differanse mellom FTE-filens lønnsandel (63,9 %) og hovedbokens lønnskonti (66,8 %) som må avstemmes før systemfrys.",
        accent_color="#0369A1"
    ))

    p5_hist_projs = [
        col_proj("DimOrganization", "OrgKode", "Org"),
        col_proj("DimOrganization", "Enhetsnavn", "Enhetsnavn"),
        meas_proj("Totale Årsverk", "Totale Årsverk"),
        meas_proj("Faglige Årsverk (UF)", "UF-Årsverk"),
        meas_proj("Teknisk-Admin Årsverk (TA)", "TA-Årsverk"),
        meas_proj("Lønnsandel %", "Lønnsandel %")
    ]
    write_json(os.path.join(p5_vis, "tbl_org_staffing_summary", "visual.json"), create_table_visual(
        "tbl_org_staffing_summary", 20, 735, 1880, 325, 9, p5_hist_projs,
        "Aggregert Bemanningssammendrag per Institutt og Enhet"
    ))

    # =========================================================================
    # PAGE 6: EVM FREMDRIFT & S-KURVE (page_p6_evm)
    # =========================================================================
    p6_vis = init_page("page_p6_evm", "6. EVM Fremdrift & S-Kurve")
    write_json(os.path.join(p6_vis, "hdr_title", "visual.json"), create_textbox_visual(
        "hdr_title", 20, 15, 1880, 75, 1,
        "6. Earned Value Management (EVM) — AACSB-Akkrediteringsprosjektet",
        "Objektiv styring av kostnadseffektivitet (CPI), tidsfremdrift (SPI), S-kurve og sluttprognose (EAC) | Kilde: FactEVM"
    ))

    write_json(os.path.join(p6_vis, "kpi_bac", "visual.json"), create_card_visual("kpi_bac", 20, 105, 360, 120, 2, "Årsbudsjett (BAC)", "PROSJEKTRAMME (BAC)", "8,5 MNOK totalbudsjett", accent_color="#334155"))
    write_json(os.path.join(p6_vis, "kpi_ev", "visual.json"), create_card_visual("kpi_ev", 400, 105, 360, 120, 3, "Earned Value (EV)", "OPPTJENT VERDI (EV)", "Faktisk fremdrift", accent_color="#0284C7"))
    write_json(os.path.join(p6_vis, "kpi_ac", "visual.json"), create_card_visual("kpi_ac", 780, 105, 360, 120, 4, "Actual Cost (AC)", "PÅLØPTE KOSTNADER (AC)", "Faktisk ressursbruk", accent_color="#EF4444"))
    write_json(os.path.join(p6_vis, "kpi_cpi", "visual.json"), create_card_visual("kpi_cpi", 1160, 105, 360, 120, 5, "CPI", "KOSTNADSEFFEKTIVITET (CPI)", "0,92 (Overskridelse)", accent_color="#F59E0B"))
    write_json(os.path.join(p6_vis, "kpi_spi", "visual.json"), create_card_visual("kpi_spi", 1540, 105, 360, 120, 6, "SPI", "TIDSFREMDRIFT (SPI)", "0,90 (Bak skjema)", accent_color="#F59E0B"))

    # S-Curve Line Chart
    write_json(os.path.join(p6_vis, "cht_evm_scurve", "visual.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": "cht_evm_scurve",
        "position": {"x": 20, "y": 240, "z": 30, "width": 1880, "height": 430, "tabOrder": 7},
        "visual": {
            "visualType": "lineChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [col_proj("DimDate", "MaanedNavnKort", "Måned")]},
                    "Y": {"projections": [
                        meas_proj("Planned Value (PV)", "Planlagt Verdi (PV)"),
                        meas_proj("Earned Value (EV)", "Opptjent Verdi (EV)"),
                        meas_proj("Actual Cost (AC)", "Påløpt Kostnad (AC)")
                    ]}
                }
            },
            "objects": {
                "legend": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "position": {"expr": {"Literal": {"Value": "'Top'"}}}}}]
            },
            "visualContainerObjects": {"title": make_title("EVM S-Kurve: Planlagt Verdi (PV), Opptjent Verdi (EV) og Faktisk Kostnad (AC) per Måned")},
            "drillFilterOtherVisuals": True
        }
    })

    p6_evm_projs = [
        col_proj("FactEVM", "DatoNokkel", "Periode"),
        col_proj("FactEVM", "PlannedValue_PV", "PV (kr)"),
        col_proj("FactEVM", "EarnedValue_EV", "EV (kr)"),
        col_proj("FactEVM", "ActualCost_AC", "AC (kr)"),
        col_proj("FactEVM", "BAC_BudgetAtCompletion", "BAC (kr)"),
        col_proj("FactEVM", "EstimateAtCompletion_EAC", "EAC (kr)"),
        col_proj("FactEVM", "VarianceAtCompletion_VAC", "VAC (kr)"),
        col_proj("FactEVM", "CostPerformanceIndex_CPI", "CPI"),
        col_proj("FactEVM", "SchedulePerformanceIndex_SPI", "SPI")
    ]
    write_json(os.path.join(p6_vis, "tbl_evm_metrics", "visual.json"), create_table_visual(
        "tbl_evm_metrics", 20, 685, 1880, 375, 8, p6_evm_projs,
        "EVM Månedstabell: Fullstendig Oversikt over Indekser, Varianser og Helårsprognoser"
    ))

    # =========================================================================
    # PAGE 7: STUDIEPRODUKSJON & KD (page_p7_students)
    # =========================================================================
    p7_vis = init_page("page_p7_students", "7. Studieproduksjon & KD")
    write_json(os.path.join(p7_vis, "hdr_title", "visual.json"), create_textbox_visual(
        "hdr_title", 20, 15, 1400, 75, 1,
        "7. Studieproduksjon & KD-Finansiering — Studiepoeng, Ekvivalenter og Kapasitet",
        "Kunnskapsdepartementets finansieringskategori 1 (54 550 kr/SPE60) og studenttetthet per faglig årsverk"
    ))
    write_json(os.path.join(p7_vis, "slc_org", "visual.json"), create_slicer_visual(
        "slc_org", 1440, 15, 460, 75, 2, "DimOrganization", "Enhetsnavn", "Enhet / Institutt", "Dropdown"
    ))

    write_json(os.path.join(p7_vis, "kpi_students_tot", "visual.json"), create_card_visual("kpi_students_tot", 20, 105, 450, 120, 3, "Registrerte Studenter", "REGISTRERTE STUDENTER", "3 450 studenter totalt", accent_color="#0284C7"))
    write_json(os.path.join(p7_vis, "kpi_spe_tot", "visual.json"), create_card_visual("kpi_spe_tot", 490, 105, 450, 120, 4, "Avlagte SPE60", "AVLAGTE SPE60 (EKVIVALENTER)", "3 120 SPE60 produksjon", accent_color="#10B981"))
    write_json(os.path.join(p7_vis, "kpi_kd_sats", "visual.json"), create_card_visual("kpi_kd_sats", 960, 105, 450, 120, 5, "KD Kat 1 Inntekt", "KD FINANSIERINGSSATS", "54 550 kr per SPE60", accent_color="#334155"))
    write_json(os.path.join(p7_vis, "kpi_ratio", "visual.json"), create_card_visual("kpi_ratio", 1430, 105, 470, 120, 6, "Studenter pr UF-Årsverk", "STUDENTTETTHET (RATIO)", "22,4 Studenter per UF-ÅV", accent_color="#F59E0B"))

    p7_stud_projs = [
        col_proj("FactStudents", "OrgKode", "Enhet"),
        col_proj("FactStudents", "Studieprogram", "Studieprogram"),
        col_proj("FactStudents", "KDKategori", "Kategori"),
        col_proj("FactStudents", "RegistrerteStudenter", "Studenter"),
        col_proj("FactStudents", "SPE60_Baseline_2025", "SPE60 Base"),
        col_proj("FactStudents", "SPE60", "SPE60 Mål"),
        col_proj("FactStudents", "KDSats_NOK", "KD Sats"),
        col_proj("FactStudents", "KD_Marginal_Inntekt_2027", "KD Inntekt (kr)"),
        col_proj("FactStudents", "StudenterPrUF", "Student/UF Ratio")
    ]
    write_json(os.path.join(p7_vis, "tbl_study_programs", "visual.json"), create_table_visual(
        "tbl_study_programs", 20, 240, 1260, 500, 7, p7_stud_projs,
        "Studieprogramoversikt: Produksjon, Satser og Beregnet KD-Bevilgning"
    ))

    write_json(os.path.join(p7_vis, "callout_p7_education", "visual.json"), create_callout_box_visual(
        "callout_p7_education", 1300, 240, 600, 500, 8,
        "📋 STUDIEPRODUKSJONSSTRATEGI & EFFEKTIVITET",
        "• K13000 har den høyeste studieproduksjonen med Siviløkonom- og bachelorprogrammene (71,7 MNOK inntekt, 21,6 stud/UF).\n\n"
        "• K11000 har høyeste studenttetthet (25,6 stud/UF) på masterprogrammene, men marginene på etterutdanning krever optimalisering.\n\n"
        "• Finansieringsmodellen: Endringer i SPE60-produksjon slår ut i KD-rammen med to års forsinkelse (t-2). Dagens overproduksjon sikrer inntektsgrunnlaget inn i 2028.",
        accent_color="#0F172A"
    ))

    p7_org_sum_projs = [
        col_proj("DimOrganization", "OrgKode", "OrgKode"),
        col_proj("DimOrganization", "Enhetsnavn", "Enhetsnavn"),
        meas_proj("Registrerte Studenter", "Studenter"),
        meas_proj("Avlagte SPE60", "SPE60"),
        meas_proj("Faglige Årsverk (UF)", "UF-Årsverk"),
        meas_proj("Studenter pr UF-Årsverk", "Ratio Stud/UF")
    ]
    write_json(os.path.join(p7_vis, "tbl_org_students_summary", "visual.json"), create_table_visual(
        "tbl_org_students_summary", 20, 755, 1880, 305, 9, p7_org_sum_projs,
        "Aggregert Studieproduksjon og Veiledningskapasitet per Institutt"
    ))

    # =========================================================================
    # PAGE 8: BUDSJETT 2027 PLANRAPPORT (page_p8_budget2027)
    # =========================================================================
    p8_vis = init_page("page_p8_budget2027", "8. Budsjett 2027 Planrapport")
    write_json(os.path.join(p8_vis, "hdr_title", "visual.json"), create_textbox_visual(
        "hdr_title", 20, 15, 1400, 75, 1,
        "8. Budsjett 2027 Planrapport — Økonomi, Kapasitet og Omstillingstiltak",
        "Konsolidert budsjett- og kapasitetsplan for 2027 per enhet, tiltaksportefølje og styringsbeslutninger | Kilde: 2027 Plan Report"
    ))
    write_json(os.path.join(p8_vis, "slc_org", "visual.json"), create_slicer_visual(
        "slc_org", 1440, 15, 460, 75, 2, "DimOrganization", "Enhetsnavn", "Enhet / Institutt", "Dropdown"
    ))

    write_json(os.path.join(p8_vis, "kpi_p27_rev", "visual.json"), create_card_visual("kpi_p27_rev", 20, 105, 450, 120, 3, "2027 Ramme Plan Inntekt MNOK", "PLANLAGTE INNTEKTER 2027", "286,1 MNOK konsolidert", accent_color="#10B981"))
    write_json(os.path.join(p8_vis, "kpi_p27_cost", "visual.json"), create_card_visual("kpi_p27_cost", 490, 105, 450, 120, 4, "2027 Ramme Plan Kostnad MNOK", "PLANLAGTE KOSTNADER 2027", "282,0 MNOK ramme", accent_color="#334155"))
    write_json(os.path.join(p8_vis, "kpi_p27_net", "visual.json"), create_card_visual("kpi_p27_net", 960, 105, 450, 120, 5, "2027 Ramme Plan Netto MNOK", "NETTO RESULTAT 2027", "+4,1 MNOK planlagt overskudd", accent_color="#10B981"))
    write_json(os.path.join(p8_vis, "kpi_p27_gap", "visual.json"), create_card_visual("kpi_p27_gap", 1430, 105, 470, 120, 6, "Budsjett 2027 Inntektsgap MNOK", "IDENTIFISERT RAMMEGAP", "🔴 2,0 MNOK under dokumentert mål", accent_color="#EF4444"))

    p8_u_projs = [
        col_proj("FactPlan2027Unit", "Enhetsnavn", "Enhetsnavn"),
        col_proj("FactPlan2027Unit", "OrgKode", "OrgKode"),
        col_proj("FactPlan2027Unit", "InntekterNOK", "Inntekter (kr)"),
        col_proj("FactPlan2027Unit", "KostnaderNOK", "Kostnader (kr)"),
        col_proj("FactPlan2027Unit", "NettoResultatNOK", "Netto Resultat (kr)"),
        col_proj("FactPlan2027Unit", "AarsverkTotalt", "Årsverk"),
        col_proj("FactPlan2027Unit", "UFAarsverk", "UF-ÅV"),
        col_proj("FactPlan2027Unit", "Studenter", "Studenter"),
        col_proj("FactPlan2027Unit", "SPE60", "SPE60")
    ]
    write_json(os.path.join(p8_vis, "tbl_p27_units", "visual.json"), create_table_visual(
        "tbl_p27_units", 20, 240, 1180, 460, 7, p8_u_projs,
        "Økonomi og Kapasitet per Enhet 2027 (Inntekter, Kostnader, Årsverk og Produksjon)"
    ))

    p8_act_projs = [
        col_proj("FactAction_2027", "TiltakID", "TiltakID"),
        col_proj("FactAction_2027", "OrgKode", "Enhet"),
        col_proj("FactAction_2027", "Tiltaksnavn", "Tiltakstittel"),
        col_proj("FactAction_2027", "ForventetEffekt", "Effekt (kr)"),
        col_proj("FactAction_2027", "Status", "Status"),
        col_proj("FactAction_2027", "Beskrivelse", "Beskrivelse")
    ]
    write_json(os.path.join(p8_vis, "tbl_p27_actions", "visual.json"), create_table_visual(
        "tbl_p27_actions", 1220, 240, 680, 460, 8, p8_act_projs,
        "2027 Strategiske Omstillingstiltak (T001–T003)"
    ))

    write_json(os.path.join(p8_vis, "callout_p8_decision", "visual.json"), create_callout_box_visual(
        "callout_p8_decision", 20, 715, 1880, 345, 9,
        "⚠️ STRATEGISK BESLUTNINGSSTØTTE 2027 & 2,0 MNOK INNTEKTSGAP",
        "Fakultetsstyrets behandling av 2027-rammen fordrer følgende strategiske avklaringer:\n\n"
        "1. Datakvalitetsavvik: FactBudget_2027 summerer til 286,07 MNOK, mens styringsdokumentene oppgir en ramme på 288,07 MNOK. Differansen på 2,0 MNOK skyldes manglende inntektsføring av sentral strategisk tildeling og må rettes i kilden før systemfrys.\n"
        "2. Lønnsandelens utvikling: Konto-basert lønnsandel (66,8 %) overskrider målet på 64,5 %. Lønnsveksten (3,7 %) spiser opp handlingsrommet og krever at ansettelsesstopp håndheves.\n"
        "3. Investeringsreserver: Det planlagte overskuddet på 4,1 MNOK må formålsbindes til flerårige investeringer i AACSB-akkreditering og digital læring.",
        accent_color="#B91C1C"
    ))

    # =========================================================================
    # PAGE 9: BUDSJETTPROSESS & LUKKEPLAN (page_p9_process)
    # =========================================================================
    p9_vis = init_page("page_p9_process", "9. Budsjettprosess & Lukkeplan")
    write_json(os.path.join(p9_vis, "hdr_title", "visual.json"), create_textbox_visual(
        "hdr_title", 20, 15, 1880, 75, 1,
        "9. Budsjettprosess 2027 — Beslutningsporter, Driveranalyse og Lukkeplan",
        "Styringsmodell med 6 beslutningsporter, kvantifiserte driveranalyser og prioritert lukkeplan før UBW-systemfrys"
    ))

    write_json(os.path.join(p9_vis, "kpi_gates_status", "visual.json"), create_card_visual("kpi_gates_status", 20, 105, 610, 120, 2, "Port 5 Flaskehals Status", "BESLUTNINGSPORT 5 STATUS", "Styringsavstemming", accent_color="#EF4444"))
    write_json(os.path.join(p9_vis, "kpi_closure_actions", "visual.json"), create_card_visual("kpi_closure_actions", 650, 105, 610, 120, 3, "Antall Tiltak i Handlingsplan", "PÅKREVDE LUKKEHANDLINGER", "6 tiltak før frys", accent_color="#F59E0B"))
    write_json(os.path.join(p9_vis, "kpi_net_vac", "visual.json"), create_card_visual("kpi_net_vac", 1280, 105, 620, 120, 4, "2027 Ramme Plan Netto MNOK", "PLANLAGT NETTO RESULTAT", "+4,1 MNOK balanse", accent_color="#10B981"))

    p9_dg_projs = [
        col_proj("FactDecisionGate", "PortNummer", "Port"),
        col_proj("FactDecisionGate", "Periode", "Periode"),
        col_proj("FactDecisionGate", "Hovedspoersmaal", "Hovedspørsmål"),
        col_proj("FactDecisionGate", "Aktivitet", "Hovedaktivitet"),
        col_proj("FactDecisionGate", "Leveranse", "Leveranse"),
        col_proj("FactDecisionGate", "Arena", "Beslutningsarena"),
        col_proj("FactDecisionGate", "Status", "Status"),
        col_proj("FactDecisionGate", "RAG_Ikon", "RAG"),
        col_proj("FactDecisionGate", "FristDato", "Frist")
    ]
    write_json(os.path.join(p9_vis, "tbl_decision_gates", "visual.json"), create_table_visual(
        "tbl_decision_gates", 20, 240, 1080, 440, 5, p9_dg_projs,
        "De 6 Beslutningsportene i Budsjettprosessen (Roadmap fra Rammevedtak til Endelig Låsing)"
    ))

    p9_da_projs = [
        col_proj("FactDriverAnalysis", "DriverNavn", "Driver"),
        col_proj("FactDriverAnalysis", "Kvantifisering", "Kvantifisering"),
        col_proj("FactDriverAnalysis", "Helaarseffekt", "Helårseffekt"),
        col_proj("FactDriverAnalysis", "Risiko", "Risiko"),
        col_proj("FactDriverAnalysis", "Kontroll", "Kontrollmekanisme"),
        col_proj("FactDriverAnalysis", "Differanse", "Diff"),
        col_proj("FactDriverAnalysis", "RAG_Status", "RAG")
    ]
    write_json(os.path.join(p9_vis, "tbl_driver_analysis", "visual.json"), create_table_visual(
        "tbl_driver_analysis", 1120, 240, 780, 440, 6, p9_da_projs,
        "Driveranalyse: Kritiske Forutsetninger for 2027"
    ))

    p9_cp_projs = [
        col_proj("FactClosurePlan", "Prio", "Prio"),
        col_proj("FactClosurePlan", "AvvikRisiko", "Avvik / Risiko"),
        col_proj("FactClosurePlan", "PaakrevdHandling", "Påkrevd Handling"),
        col_proj("FactClosurePlan", "AnsvarligEier", "Eier"),
        col_proj("FactClosurePlan", "FristDato", "Frist"),
        col_proj("FactClosurePlan", "BevisFerdigkriterium", "Ferdigkriterium"),
        col_proj("FactClosurePlan", "Konsekvens", "Konsekvens"),
        col_proj("FactClosurePlan", "RAG_Status", "RAG")
    ]
    write_json(os.path.join(p9_vis, "tbl_closure_plan", "visual.json"), create_table_visual(
        "tbl_closure_plan", 20, 695, 1180, 365, 7, p9_cp_projs,
        "Prioritert Lukkeplan før Systemfrys (UBW-låsing 15.11.2026)"
    ))

    write_json(os.path.join(p9_vis, "callout_p9_process", "visual.json"), create_callout_box_visual(
        "callout_p9_process", 1220, 695, 680, 365, 8,
        "📋 SAMLET PROSESSANALYSE OG ANBEFALING",
        "Budsjettprosessen er en moden, driverbasert styringsprosess, men Port 5 er flagget RØD (Ikke klar):\n\n"
        "1. Rammegapet på 2,0 MNOK og lønnsandelen på 66,8 % må avstemmes og godkjennes før systemfrys.\n"
        "2. Anbefaling: Stopp ved beslutningsport 5 til rammebrev og stillingsplaner er formelt signert.\n"
        "3. Lås BUD2027 sammen med flerårig investeringsplan, tiltakseiere og månedlig RAG-rapportering.",
        accent_color="#0F172A"
    ))

    # =========================================================================
    # PAGE 10: PROGNOSEMETODIKK 2027 (page_p10_methods)
    # =========================================================================
    p10_vis = init_page("page_p10_methods", "10. Prognosemetodikk 2027")
    write_json(os.path.join(p10_vis, "hdr_title", "visual.json"), create_textbox_visual(
        "hdr_title", 20, 15, 1880, 75, 1,
        "10. Prognosemetodikk 2027 — Formelverk, Metodebibliotek og Månedsrutine",
        "Standardmetodikk for løpende helårsprognostisering (Actual YTD + ETC = EAC) og årshjul for månedsslutt | Kilde: Forecast Methods 2027"
    ))

    write_json(os.path.join(p10_vis, "callout_p10_formula", "visual.json"), create_callout_box_visual(
        "callout_p10_formula", 20, 105, 1880, 110, 2,
        "📐 STANDARD PROGNOSEFORMEL: Actual YTD + ETC = EAC / Latest Estimate",
        "• Actual YTD (låst regnskap hittil i året) + ETC (driverbasert prognose for resterende måneder) = EAC / Latest Estimate (ny forventet helårsverdi).\n"
        "• Sluttavvik (VAC) = BUD2027 − EAC. Positivt tall er gunstig for kostnader (mindreforbruk). RAG-kriterier: Grønn ≥ 0 %; Gul 0 til −5 %; Rød < −5 %.",
        accent_color="#10B981"
    ))

    p10_fm_projs = [
        col_proj("FactForecastMethod", "Prio", "Prio"),
        col_proj("FactForecastMethod", "Budsjettpost", "Budsjettpost"),
        col_proj("FactForecastMethod", "KontoTabell", "Konto / Tabell"),
        col_proj("FactForecastMethod", "Baseline2027", "2027 Baseline (kr)"),
        col_proj("FactForecastMethod", "Prognosemetode", "Prognosemetode"),
        col_proj("FactForecastMethod", "DriverInput", "Driver / Inndata"),
        col_proj("FactForecastMethod", "OperativBeregning", "Operativ Beregning"),
        col_proj("FactForecastMethod", "Oppdateringsfrekvens", "Oppdatering")
    ]
    write_json(os.path.join(p10_vis, "tbl_forecast_methods", "visual.json"), create_table_visual(
        "tbl_forecast_methods", 20, 230, 1880, 500, 3, p10_fm_projs,
        "Metodebibliotek for 11 Budsjettsoster: Beregningsformler, Drivere og Oppdateringsrutiner"
    ))

    p10_rs_projs = [
        col_proj("FactRoutineStep", "TrinnNummer", "Trinn"),
        col_proj("FactRoutineStep", "FormelMetode", "Formel / Metode"),
        col_proj("FactRoutineStep", "Forklaring", "Forklaring & Hensikt"),
        col_proj("FactRoutineStep", "Kontrollaktivitet", "Kontrollaktivitet"),
        col_proj("FactRoutineStep", "MaanedligTidslinje", "Tidslinje & Leveranser (Dag 1–10)")
    ]
    write_json(os.path.join(p10_vis, "tbl_routine_steps", "visual.json"), create_table_visual(
        "tbl_routine_steps", 20, 745, 1880, 315, 4, p10_rs_projs,
        "Månedlig Rapporteringsrutine og Årshjul (Trinn 1–6 fra Periodelukking til Styringspublisering)"
    ))

    # =========================================================================
    # PAGE 11: DATAMODELL & KVALITETSKONTROLL (page_p11_modelguide)
    # =========================================================================
    p11_vis = init_page("page_p11_modelguide", "11. Datamodell & Kvalitetskontroll")
    write_json(os.path.join(p11_vis, "hdr_title", "visual.json"), create_textbox_visual(
        "hdr_title", 20, 15, 1880, 75, 1,
        "11. Datamodell & Kvalitetskontroll — Kildetabeller, Relasjoner og Datakvalitet",
        "Stjernemodell, TMDL-skjema, Power Query M-partisjoner og dokumentasjon av 2,0 MNOK rammegap | Kilde: Model Guide Sheet"
    ))

    write_json(os.path.join(p11_vis, "kpi_tables_cnt", "visual.json"), create_card_visual("kpi_tables_cnt", 20, 105, 450, 120, 2, "Total Inntekt MNOK", "KILDETABELLER", "25 Tabeller i modellen", accent_color="#10B981"))
    write_json(os.path.join(p11_vis, "kpi_rels_cnt", "visual.json"), create_card_visual("kpi_rels_cnt", 490, 105, 450, 120, 3, "Total Inntekt MNOK", "RELASJONER", "24 Relasjoner (100% verifisert)", accent_color="#0284C7"))
    write_json(os.path.join(p11_vis, "kpi_measures_cnt", "visual.json"), create_card_visual("kpi_measures_cnt", 960, 105, 450, 120, 4, "Total Inntekt MNOK", "DAX-MÅL", "92 Kalkulerte mål", accent_color="#334155"))
    write_json(os.path.join(p11_vis, "kpi_gap_status", "visual.json"), create_card_visual("kpi_gap_status", 1430, 105, 470, 120, 5, "Budsjett 2027 Inntektsgap MNOK", "DATAKVALITETSSTATUS", "🔴 2,0 MNOK Inntektsgap", accent_color="#EF4444"))

    p11_org_projs = [
        col_proj("DimOrganization", "OrgKode", "OrgKode"),
        col_proj("DimOrganization", "Enhetsnavn", "Enhetsnavn"),
        col_proj("DimOrganization", "Virksomhetstype", "Virksomhetstype"),
        col_proj("DimOrganization", "Budsjettansvarlig", "Budsjettansvarlig"),
        col_proj("DimOrganization", "LederTittel", "LederTittel"),
        col_proj("DimOrganization", "Nivaa2", "Fakultet"),
        col_proj("DimOrganization", "Nivaa3", "Institutt")
    ]
    write_json(os.path.join(p11_vis, "tbl_org_model", "visual.json"), create_table_visual(
        "tbl_org_model", 20, 240, 1880, 460, 6, p11_org_projs,
        "Organisasjonsstruktur (DimOrganization): Enhetshierarki, Virksomhetstype og Budsjettansvar"
    ))

    write_json(os.path.join(p11_vis, "callout_p11_dataquality", "visual.json"), create_callout_box_visual(
        "callout_p11_dataquality", 20, 715, 1880, 345, 7,
        "⚠️ VIKTIG DATAKVALITETSFUNN (2,0 MNOK Inntektsgap)",
        "Gjennomgang av kildetabellene avdekker et vesentlig datakvalitetsfunn i 2027-budsjettet:\n\n"
        "• Kildemodell FactBudget_2027 summerer til 286,07 MNOK, mens styringsdokumentene oppgir en vedtatt ramme på 288,07 MNOK.\n\n"
        "• Differansen på 2,0 MNOK reduserer nettoresultatet fra +6,07 MNOK til +4,07 MNOK.\n\n"
        "• Årsak: En strategisk tildelingslinje på 2,0 MNOK mangler i FactBudget_2027-kilden. Dette må korrigeres i UBW før endelig systemfrys ved Port 5.",
        accent_color="#B91C1C"
    ))

    print(f"Successfully generated all 11 production-grade PBIR report pages in {PAGES_DIR}.")

if __name__ == '__main__':
    build_all_report_pages()
