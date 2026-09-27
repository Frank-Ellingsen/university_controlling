import re
import json
from pathlib import Path

BASE_DIR = Path(r"c:\Users\frank\Desktop\UIA2")

# 1. Read all declared measures
measures_file = BASE_DIR / "University-project-2026YTD.SemanticModel" / "definition" / "tables" / "_Measures.tmdl"
lines = measures_file.read_text(encoding="utf-8").splitlines()
declared_measures = set()
for line in lines:
    line = line.strip()
    if line.startswith("measure "):
        # e.g. measure 'Actual YTD' = or measure CPI =
        m = re.match(r"^measure\s+['\"]?([^'\"=]+?)['\"]?\s*=", line)
        if m:
            declared_measures.add(m.group(1).strip())

print(f"Declared measures in TMDL: {len(declared_measures)}")

# 2. Read all column names in all TMDL tables
columns_by_table = {}
tables_dir = BASE_DIR / "University-project-2026YTD.SemanticModel" / "definition" / "tables"
for t_file in tables_dir.glob("*.tmdl"):
    t_name = t_file.stem
    columns = set()
    for line in t_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("column "):
            m = re.match(r"^column\s+['\"]?([^'\"=]+?)['\"]?$", line)
            if m:
                columns.add(m.group(1).strip())
    columns_by_table[t_name] = columns

print("Tables found:", list(columns_by_table.keys()))

# 3. Check every visual in every page in University-project-2026YTD.Report
report_pages_dir = BASE_DIR / "University-project-2026YTD.Report" / "definition" / "pages"
invalid_references = []

for v_file in report_pages_dir.glob("**/visual.json"):
    data = json.loads(v_file.read_text(encoding="utf-8"))
    v_name = data.get("name", v_file.parent.name)
    page_name = v_file.parent.parent.parent.name
    
    # Check projections
    query_state = data.get("visual", {}).get("query", {}).get("queryState", {})
    for bucket_name, bucket in query_state.items():
        projections = bucket.get("projections", [])
        for p in projections:
            field = p.get("field", {})
            if "Measure" in field:
                m_info = field["Measure"]
                entity = m_info.get("Expression", {}).get("SourceRef", {}).get("Entity")
                prop = m_info.get("Property")
                if prop not in declared_measures:
                    invalid_references.append((page_name, v_name, "Measure", entity, prop))
            elif "Column" in field:
                c_info = field["Column"]
                entity = c_info.get("Expression", {}).get("SourceRef", {}).get("Entity")
                prop = c_info.get("Property")
                table_cols = columns_by_table.get(entity, set())
                if prop not in table_cols:
                    invalid_references.append((page_name, v_name, "Column", entity, prop))

print(f"\nInvalid visual references found: {len(invalid_references)}")
for item in invalid_references:
    print(f"  [INVALID] Page: {item[0]} | Visual: {item[1]} | Type: {item[2]} | Entity: {item[3]} | Prop: {item[4]}")
