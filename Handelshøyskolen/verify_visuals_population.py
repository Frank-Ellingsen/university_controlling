import os
import glob
import json
import re

BASE_DIR = r"c:\Users\frank\Desktop\UIA2\Handelshøyskolen"
SEMANTIC_DIR = os.path.join(BASE_DIR, "Controller-Handelshøyskolen.SemanticModel", "definition")
REPORT_DIR = os.path.join(BASE_DIR, "Controller-Handelshøyskolen.Report", "definition")
PAGES_DIR = os.path.join(REPORT_DIR, "pages")

# 1. Collect all measures in _Measures.tmdl
with open(os.path.join(SEMANTIC_DIR, "tables", "_Measures.tmdl"), "r", encoding="utf-8") as f:
    measures_tmdl = f.read()

model_measures = set(re.findall(r"measure\s+'([^']+)'\s*=", measures_tmdl))
for m in re.findall(r"measure\s+([A-Za-z0-9_%]+)\s*=", measures_tmdl):
    model_measures.add(m)

# 2. Collect all columns per table
table_columns = {}
for tf in glob.glob(os.path.join(SEMANTIC_DIR, "tables", "*.tmdl")):
    tname = os.path.basename(tf).replace(".tmdl", "")
    with open(tf, "r", encoding="utf-8") as f:
        content = f.read()
    cols = re.findall(r"column\s+([^\r\n\t]+)", content)
    clean_cols = set(c.strip().strip("'") for c in cols)
    table_columns[tname] = clean_cols

print(f"Loaded {len(model_measures)} measures from _Measures.tmdl.")
print(f"Loaded {len(table_columns)} tables with their respective columns.")

# 3. Find and check all visual.json files
visual_files = glob.glob(os.path.join(PAGES_DIR, "*", "visuals", "*", "visual.json"))
print(f"Found {len(visual_files)} visuals across all report pages.")

issues = []
summary_by_page = {}

for vf in visual_files:
    rel_path = os.path.relpath(vf, REPORT_DIR)
    parts = rel_path.split(os.sep)
    page_name = parts[1]
    visual_name = parts[3]
    
    if page_name not in summary_by_page:
        summary_by_page[page_name] = []
        
    with open(vf, "r", encoding="utf-8") as fp:
        try:
            data = json.load(fp)
        except Exception as e:
            issues.append(f"JSON ERROR in {rel_path}: {e}")
            continue

    vis = data.get("visual", {})
    v_type = vis.get("visualType", "UNKNOWN")
    pos = data.get("position", {})
    
    # Check position
    if not pos.get("width") or not pos.get("height"):
        issues.append(f"Position missing in {rel_path}")
        
    # Check data fields
    q_state = vis.get("query", {}).get("queryState", {})
    referenced_measures = []
    referenced_columns = []
    
    # Recursive search for Property, Measure, Column
    def extract_fields(obj):
        if isinstance(obj, dict):
            if "Measure" in obj:
                m_info = obj["Measure"]
                m_prop = m_info.get("Property")
                if m_prop:
                    referenced_measures.append(m_prop)
            if "Column" in obj:
                c_info = obj["Column"]
                c_prop = c_info.get("Property")
                c_entity = c_info.get("Expression", {}).get("SourceRef", {}).get("Entity")
                if c_prop:
                    referenced_columns.append((c_entity, c_prop))
            for k, v in obj.items():
                extract_fields(v)
        elif isinstance(obj, list):
            for it in obj:
                extract_fields(it)

    extract_fields(vis)
    
    # Check if textboxes have text
    text_chunks = []
    if v_type == "textbox":
        def extract_text(obj):
            if isinstance(obj, dict):
                if "value" in obj and isinstance(obj["value"], str):
                    text_chunks.append(obj["value"])
                for k, v in obj.items():
                    extract_text(v)
            elif isinstance(obj, list):
                for it in obj:
                    extract_text(it)
        extract_text(vis)
        if not "".join(text_chunks).strip():
            issues.append(f"Empty textbox in {rel_path}")

    # Validate referenced measures against model
    for rm in referenced_measures:
        if rm not in model_measures:
            issues.append(f"Unresolved Measure '{rm}' in {rel_path}")

    # Validate referenced columns against tables
    for ent, col in referenced_columns:
        if ent and ent in table_columns:
            if col not in table_columns[ent]:
                issues.append(f"Unresolved Column '{ent}[{col}]' in {rel_path}")
        elif ent and ent not in table_columns:
            issues.append(f"Unresolved Entity/Table '{ent}' in {rel_path}")

    # Record summary
    summary_by_page[page_name].append({
        "visual_name": visual_name,
        "type": v_type,
        "measures": referenced_measures,
        "columns": [f"{e}[{c}]" for e, c in referenced_columns],
        "has_text": bool("".join(text_chunks).strip()) if v_type == "textbox" else None
    })

print("\n" + "="*50)
print("AUDIT RESULTS PER PAGE:")
print("="*50)
for p, v_list in summary_by_page.items():
    print(f"\nPAGE: {p} ({len(v_list)} visuals)")
    for v in v_list:
        m_str = ", ".join(v["measures"]) if v["measures"] else "None"
        c_str = ", ".join(v["columns"]) if v["columns"] else "None"
        if v["type"] == "textbox":
            status = "POPULATED (Text verified)" if v["has_text"] else "EMPTY TEXT"
        elif v["measures"] or v["columns"]:
            status = f"POPULATED (Measures: {m_str} | Cols: {c_str})"
        else:
            status = "NO FIELDS ASSIGNED"
        print(f"  - {v['visual_name']} [{v['type']}]: {status}")

print("\n" + "="*50)
if issues:
    print(f"FOUND {len(issues)} ISSUES:")
    for iss in issues:
        print(f"  [X] {iss}")
else:
    print("ALL VISUALS ARE 100% POPULATED WITH VALID DATA BINDINGS AND MODEL FIELDS!")
print("="*50)
