import re
from pathlib import Path

BASE_DIR = Path(r"c:\Users\frank\Desktop\UIA2")
measures_file = BASE_DIR / "UIA-project-2026YTD.SemanticModel" / "definition" / "tables" / "_Measures.tmdl"

content = measures_file.read_text(encoding="utf-8")

# Parse measures
measures = {}
current_m = None
current_lines = []

for line in content.splitlines():
    m = re.match(r"^\tmeasure\s+['\"]?([^'\"=]+?)['\"]?\s*=\s*(.*)$", line)
    if m:
        if current_m:
            measures[current_m] = "\n".join(current_lines)
        current_m = m.group(1).strip()
        current_lines = [m.group(2).strip()] if m.group(2).strip() else []
    elif current_m:
        if line.startswith("\t\t") and not line.strip().startswith(("formatString:", "displayFolder:", "lineageTag:", "annotation")):
            current_lines.append(line.strip())
        elif line.startswith("\t") and not line.startswith("\t\t"):
            # next measure or property
            if current_m:
                measures[current_m] = "\n".join(current_lines)
                current_m = None
                current_lines = []

if current_m:
    measures[current_m] = "\n".join(current_lines)

print(f"Parsed {len(measures)} measures.")

# Check parentheses and brackets balance
errors = []
for name, dax in measures.items():
    open_paren = dax.count("(")
    close_paren = dax.count(")")
    if open_paren != close_paren:
        errors.append((name, f"Parentheses mismatch: {open_paren} '(' vs {close_paren} ')'", dax))
    
    # Check square brackets in measures (excluding inside strings)
    # Simple check
    open_bracket = dax.count("[")
    close_bracket = dax.count("]")
    if open_bracket != close_bracket:
        errors.append((name, f"Bracket mismatch: {open_bracket} '[' vs {close_bracket} ']'", dax))

print(f"DAX syntax balance errors: {len(errors)}")
for err in errors:
    print("  [ERROR]", err[0], ":", err[1])

# Check references inside measures
all_declared = set(measures.keys())
all_tables = {}
tables_dir = BASE_DIR / "UIA-project-2026YTD.SemanticModel" / "definition" / "tables"
for t_file in tables_dir.glob("*.tmdl"):
    t_name = t_file.stem
    cols = set()
    for line in t_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("column "):
            m = re.match(r"^column\s+['\"]?([^'\"=]+?)['\"]?$", line)
            if m:
                cols.add(m.group(1).strip())
    all_tables[t_name] = cols

missing_refs = []
for name, dax in measures.items():
    # Find table[column] references
    table_col_refs = re.findall(r"['\"]?([A-Za-z0-9_]+)['\"]?\[([^\]]+)\]", dax)
    for t, c in table_col_refs:
        if t in all_tables:
            if c not in all_tables[t]:
                missing_refs.append((name, f"Column '{c}' not in table '{t}'"))
        elif t == "":
            # Bare [Measure]
            if c not in all_declared:
                missing_refs.append((name, f"Measure '[{c}]' not declared"))

print(f"Missing references inside measures: {len(missing_refs)}")
for err in missing_refs:
    print("  [REF ERROR]", err[0], ":", err[1])
