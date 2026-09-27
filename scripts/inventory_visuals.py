import json
from pathlib import Path

pages_dir = Path("University-project-2026YTD.Report/definition/pages")
pages_json = json.loads((pages_dir / "pages.json").read_text("utf-8"))

for page_name in pages_json.get("pageOrder", []):
    p_path = pages_dir / page_name
    meta_file = p_path / "page.json"
    p_display = page_name
    if meta_file.exists():
        p_data = json.loads(meta_file.read_text("utf-8"))
        p_display = f"{p_data.get('displayName')} ({page_name})"
    
    print(f"\n==========================================")
    print(f"PAGE: {p_display}")
    print(f"==========================================")
    
    vis_dir = p_path / "visuals"
    if not vis_dir.exists():
        continue
    for vdir in sorted(vis_dir.iterdir()):
        vfile = vdir / "visual.json"
        if not vfile.exists():
            continue
        vdata = json.loads(vfile.read_text("utf-8"))
        vtype = vdata.get("visual", {}).get("visualType", "unknown")
        qs = vdata.get("visual", {}).get("query", {}).get("queryState", {})
        
        fields = []
        for bname, bdata in qs.items():
            for proj in bdata.get("projections", []):
                qref = proj.get("queryRef")
                fields.append(f"{bname}:{qref}")
        
        print(f"  Visual: {vdir.name:<32} Type: {vtype:<28} Fields: {', '.join(fields)}")
