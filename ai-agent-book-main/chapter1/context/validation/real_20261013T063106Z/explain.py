import json

with open("evidence.json", encoding="utf-8") as f:
    data = json.load(f)
with open("evidence_output.txt", "w", encoding="utf-8") as f:
    # ensure_ascii=False 保留中文，indent=2 美化
    json.dump(data, f, ensure_ascii=False, indent=2)