import re
from pathlib import Path

content = Path("University-project-2026YTD.SemanticModel/definition/tables/_Measures.tmdl").read_text("utf-8")
lines = content.splitlines()

declared = set()
for l in lines:
    m = re.match(r"^\s*measure\s+['\"]?([^='\"\n\r]+)['\"]?\s*=", l)
    if m:
        declared.add(m.group(1).strip())

refs = set(re.findall(r"\[([^\]]+)\]", content))
undeclared = refs - declared

# Read all columns from all tables
all_columns = set()
for tf in Path("University-project-2026YTD.SemanticModel/definition/tables").glob("*.tmdl"):
    for l in tf.read_text("utf-8").splitlines():
        m = re.match(r"^\s*column\s+['\"]?([^='\"\n\r]+)['\"]?\s*$", l)
        if m:
            all_columns.add(m.group(1).strip())

print(f"Declared measures: {len(declared)}")
print(f"Total columns in model: {len(all_columns)}")

neither = undeclared - all_columns
print(f"References that are NEITHER a measure nor a column: {len(neither)}")
for n in sorted(neither):
    print("  ->", repr(n))
