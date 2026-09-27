import re
from pathlib import Path

p = Path("University-project-2026YTD.SemanticModel/definition/tables/_Measures.tmdl")
content = p.read_text(encoding="utf-8")
lines = content.splitlines()

declared = set()
for l in lines:
    m = re.match(r"^\s*measure\s+['\"]?([^='\"\n\r]+)['\"]?\s*=", l)
    if m:
        declared.add(m.group(1).strip())

print(f"Total declared measures: {len(declared)}")

# Check File.Contents in all tables
tables_dir = Path("University-project-2026YTD.SemanticModel/definition/tables")
print("\n--- Checking File.Contents paths ---")
for tf in tables_dir.glob("*.tmdl"):
    txt = tf.read_text("utf-8")
    for match in re.finditer(r'File\.Contents\("([^"]+)"\)', txt):
        fpath = Path(match.group(1))
        print(f"{tf.stem}: {fpath} -> exists: {fpath.exists()}")


# Check references in _Measures.tmdl
refs = set(re.findall(r"\[([^\]]+)\]", content))
print("\n--- Checking references inside _Measures.tmdl ---")
for r in sorted(refs):
    if r not in declared:
        # Check if it has a close match
        r_clean = r.lower().replace("å", "").replace("ø", "").replace("æ", "").replace(" ", "")
        for d in declared:
            d_clean = d.lower().replace("\ufffd", "").replace("å", "").replace("ø", "").replace("æ", "").replace(" ", "")
            if r_clean == d_clean and r != d:
                print(f"BROKEN DAX REF: [{r}] is used in DAX, but declared measure is [{d}]")

# Now check visual.json files across all pages!
print("\n--- Checking visual.json projections & objects ---")
pages_dir = Path("University-project-2026YTD.Report/definition/pages")
for vfile in pages_dir.glob("**/visual.json"):
    vcontent = vfile.read_text(encoding="utf-8")
    # find all "Property": "..."
    props = re.findall(r'"Property":\s*"([^"]+)"', vcontent)
    for pr in props:
        if pr not in declared:
            pr_clean = pr.lower().replace("\ufffd", "").replace("å", "").replace("ø", "").replace("æ", "").replace(" ", "")
            for d in declared:
                d_clean = d.lower().replace("\ufffd", "").replace("å", "").replace("ø", "").replace("æ", "").replace(" ", "")
                if pr_clean == d_clean and pr != d:
                    print(f"BROKEN VISUAL REF in {vfile.parent.name}: visual requests Property '{pr}', but declared is '{d}'")
