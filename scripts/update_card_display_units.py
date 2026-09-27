import json
from pathlib import Path

pages_dir = Path(r"University-project-2026YTD.Report\definition\pages")

cards_updated = []
for v_file in sorted(pages_dir.glob("**/vis*kpi*/visual.json")):
    data = json.loads(v_file.read_text(encoding="utf-8"))
    v_type = data.get("visual", {}).get("visualType")
    
    if v_type == "card":
        if "objects" not in data["visual"]:
            data["visual"]["objects"] = {}
        
        data["visual"]["objects"]["labels"] = [
            {
                "properties": {
                    "displayUnits": {
                        "expr": {
                            "Literal": {
                                "Value": "0D"
                            }
                        }
                    }
                }
            }
        ]
        
        v_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        cards_updated.append(v_file.parent.name)

print(f"Updated {len(cards_updated)} classic card visuals with displayUnits: 0D:")
for c in cards_updated:
    print(" -", c)
