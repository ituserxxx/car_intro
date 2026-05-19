import shutil
import json
from pathlib import Path

BASE = Path("d:/DDD/xxx/code/wx_mini/car_intro/car_instr_rust/car_pdfs")
JSON_PATH = BASE.parent / "car_pdfs.json"

car_data = json.load(JSON_PATH.open("r", encoding="utf-8"))

# 为 changcheng_xi 构建精确映射：文件名 -> dir_name
filename_to_dir = {}
for item in car_data:
    if item.get("parten") == "changchang_xi":
        for child in item.get("chrild", []):
            dir_name = child["dir_name"]
            for pdf in child.get("pdfs", []):
                filename_to_dir[pdf] = dir_name

src_dir = BASE / "changcheng_xi" / "doc"
if not src_dir.exists():
    print("changcheng_xi/doc 不存在")
    exit(1)

for pdf_file in src_dir.glob("*.pdf"):
    dir_name = filename_to_dir.get(pdf_file.name)
    if dir_name:
        dst_dir = BASE / "changcheng_xi" / dir_name
        dst_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(pdf_file), str(dst_dir / pdf_file.name))
        print(f"[changcheng_xi] {pdf_file.name} -> {dir_name}/")
    else:
        print(f"[changcheng_xi] 未分类: {pdf_file.name}")

print("\nchangcheng_xi 整理完成！")
