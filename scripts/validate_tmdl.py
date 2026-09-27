import os
import re
from collections import Counter, defaultdict

def validate():
    base_dir = r"University-project-2026YTD.SemanticModel\definition"
    
    measures = defaultdict(list)
    columns_per_table = defaultdict(lambda: defaultdict(list))
    lineage_tags = defaultdict(list)
    current_table = None
    
    tables_dir = os.path.join(base_dir, "tables")
    for fname in os.listdir(tables_dir):
        if not fname.endswith(".tmdl"):
            continue
        tpath = os.path.join(tables_dir, fname)
        tname = fname[:-5]
        
        with open(tpath, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f, 1):
                # measure
                m_meas = re.match(r"^\s*measure\s+(.+?)\s*=", line)
                if m_meas:
                    mname = m_meas.group(1).strip("' ")
                    measures[mname].append((fname, idx))
                    
                # column
                m_col = re.match(r"^\s*column\s+(.+?)$", line)
                if m_col:
                    cname = m_col.group(1).strip("' ")
                    columns_per_table[tname][cname].append((fname, idx))
                    
                # lineageTag
                m_tag = re.match(r"^\s*lineageTag:\s*([a-f0-9\-]+)", line, re.I)
                if m_tag:
                    ltag = m_tag.group(1).strip().lower()
                    lineage_tags[ltag].append((fname, idx))

    print(f"=== TMDL VALIDATION REPORT ===")
    
    dup_measures = {k: v for k, v in measures.items() if len(v) > 1}
    if dup_measures:
        print(f"\n[ERROR] Duplicate measures found ({len(dup_measures)}):")
        for m, locs in dup_measures.items():
            print(f"  - '{m}':")
            for f, l in locs:
                print(f"      {f}:{l}")
    else:
        print("\n[OK] No duplicate measures found.")
        
    dup_cols = {}
    for tname, cols in columns_per_table.items():
        dups = {k: v for k, v in cols.items() if len(v) > 1}
        if dups:
            dup_cols[tname] = dups
            
    if dup_cols:
        print(f"\n[ERROR] Duplicate columns found in tables:")
        for t, cols in dup_cols.items():
            print(f"  Table '{t}':")
            for c, locs in cols.items():
                print(f"    - Column '{c}': {locs}")
    else:
        print("[OK] No duplicate columns within any table.")
        
    dup_tags = {k: v for k, v in lineage_tags.items() if len(v) > 1}
    if dup_tags:
        print(f"\n[ERROR] Duplicate lineageTags found ({len(dup_tags)}):")
        for tag, locs in dup_tags.items():
            print(f"  - Tag '{tag}': {locs}")
    else:
        print("[OK] All lineageTags are unique.")

if __name__ == "__main__":
    validate()
