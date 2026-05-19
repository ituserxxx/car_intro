import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
CAR_JSON = BASE_DIR / "car.json"
OUTPUT = BASE_DIR.parent / "car_instr_rust" / "car_pdfs.json"

# parten -> 实际目录名映射
PARTEN_DIR_MAP = {
    "changchang_xi": "changcheng_xi",
    "byd_xi": "byd",
    "fengtian_xi": "toyota",
}


def get_pdfs_for_child(parten, child):
    dir_name = child["dir_name"]
    name = child["name"]

    # 长城系：子品牌有独立目录
    if parten == "changchang_xi":
        doc_path = BASE_DIR / "changcheng_xi" / dir_name / "doc"
        if doc_path.exists():
            return [f.name for f in doc_path.iterdir() if f.suffix.lower() == ".pdf"]
        return []

    # BYD：只有一个 doc 目录
    if parten == "byd_xi":
        doc_path = BASE_DIR / "byd" / "doc"
        if doc_path.exists():
            return [f.name for f in doc_path.iterdir() if f.suffix.lower() == ".pdf"]
        return []

    # 丰田：所有 PDF 在 toyota/doc 下，按车型名匹配
    if parten == "fengtian_xi":
        doc_path = BASE_DIR / "toyota" / "doc"
        if not doc_path.exists():
            return []
        all_pdfs = [f.name for f in doc_path.iterdir() if f.suffix.lower() == ".pdf"]

        # 按车型名关键词匹配
        matched = []
        for pdf in all_pdfs:
            # 简单关键词匹配
            if name in pdf:
                matched.append(pdf)
                continue
            # 特殊处理
            if name == "铂智4X" and "bZ4X" in pdf:
                matched.append(pdf)
                continue
            if name == "铂智3X" and "铂智3X" in pdf:
                matched.append(pdf)
                continue
            if name == "iA5" and "iA5" in pdf:
                matched.append(pdf)
                continue

        # 如果直接匹配不到，尝试用更宽松的关键词
        if not matched:
            keywords = {
                "汉兰达": ["汉兰达"],
                "赛那": ["赛那"],
                "凯美瑞": ["凯美瑞"],
                "凯美瑞智能电混双擎": ["凯美瑞", "电混双擎"],
                "威飒": ["威飒"],
                "威飒智能电混双擎": ["威飒", "HEV"],
                "威兰达": ["威兰达", "汽油版"],
                "威兰达智能电混双擎": ["威兰达", "HEV"],
                "威兰达智能插电双擎": ["威兰达", "PHEV"],
                "雷凌": ["雷凌", "汽油版"],
                "雷凌智能电混双擎": ["雷凌", "HEV"],
                "锋兰达": ["锋兰达", "汽油版"],
                "锋兰达智能电混双擎": ["锋兰达", "HEV"],
                "凌尚": ["凌尚", "汽油版"],
                "凌尚智能电混双擎": ["凌尚", "HEV"],
                "埃尔法": ["埃尔法"],
                "致享": ["致享"],
            }
            if name in keywords:
                kws = keywords[name]
                for pdf in all_pdfs:
                    if all(kw in pdf for kw in kws):
                        matched.append(pdf)

        return matched

    return []


def main():
    with open(CAR_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 为每个 child 添加 pdfs
    for group in data:
        parten = group["parten"]
        for child in group["chrild"]:
            child["pdfs"] = get_pdfs_for_child(parten, child)

    # 添加 dazhong（大众）
    dazhong_doc = BASE_DIR / "dazhong" / "doc"
    if dazhong_doc.exists():
        dazhong_pdfs = [f.name for f in dazhong_doc.iterdir() if f.suffix.lower() == ".pdf"]
        data.append({
            "parten": "dazhong_xi",
            "chrild": [
                {
                    "name": "大众",
                    "dir_name": "dazhong",
                    "url": "https://techcare.svw-volkswagen.com/khgg-sywh.html",
                    "pdfs": dazhong_pdfs
                }
            ]
        })

    # 保存
    OUTPUT.parent.mkdir(exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    total = sum(len(c["pdfs"]) for g in data for c in g["chrild"])
    print(f"生成完成: {OUTPUT}")
    print(f"共 {len(data)} 个系列, {sum(len(g['chrild']) for g in data)} 个品牌/车型, {total} 个 PDF")


if __name__ == "__main__":
    main()
