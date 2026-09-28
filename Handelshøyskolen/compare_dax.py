import re, csv

with open('Controller-Handelshøyskolen.SemanticModel/definition/tables/_Measures.tmdl', 'r', encoding='utf-8') as f:
    tmdl = f.read()

tmdl_measures = set(m.strip().strip("'") for m in re.findall(r'measure\s+([^\=]+?)\s*=', tmdl))

with open('DimDAXLibrary.csv', 'r', encoding='utf-8') as f:
    dax_md_measures = [r['MeasureName'].strip().strip("'") for r in csv.DictReader(f)]

print(f"TMDL measures count: {len(tmdl_measures)}")
print(f"DAX.md measures count: {len(dax_md_measures)}")

missing = [m for m in dax_md_measures if m not in tmdl_measures]
print(f"Missing from TMDL ({len(missing)}):")
for m in missing:
    print(f"  - {m}")
