import os
import re
from collections import defaultdict

def check_all_tmdl():
    base_dir = r'University-project-2026YTD.SemanticModel'
    measures = defaultdict(list)
    
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.endswith('.tmdl'):
                fpath = os.path.join(root, f)
                with open(fpath, 'r', encoding='utf-8') as file:
                    for idx, line in enumerate(file, 1):
                        m = re.match(r'^\s*measure\s+(.+?)\s*=', line)
                        if m:
                            name = m.group(1).strip("' ")
                            measures[name].append((fpath, idx))
                            
    dups = {k: v for k, v in measures.items() if len(v) > 1}
    print(f"Total distinct measures across all TMDL: {len(measures)}")
    if dups:
        print(f"DUPLICATE MEASURES ACROSS FILES:")
        for name, occurrences in dups.items():
            print(f"  Measure: '{name}'")
            for path, line in occurrences:
                print(f"    - {path}:{line}")
    else:
        print("No duplicate measures found across all TMDL files.")

if __name__ == "__main__":
    check_all_tmdl()
