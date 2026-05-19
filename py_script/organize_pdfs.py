import os
import shutil
import json
from pathlib import Path

BASE = Path("d:/DDD/xxx/code/wx_mini/car_intro/car_instr_rust/car_pdfs")
JSON_PATH = BASE.parent / "car_pdfs.json"

# 加载 car_pdfs.json
car_data = json.load(JSON_PATH.open("r", encoding="utf-8"))

# 分类规则：品牌 -> {子目录: [关键词列表]}
# 关键词越长越优先匹配
RULES = {
    "beijing_yueye": {
        "B30X": ["B30X"],
        "B41VS": ["B41VS"],
        "魔方": ["魔方"],
        "BJ40": ["BJ40", "bj40txjsms", "全新BJ40"],
        "BJ60": ["BJ60"],
        "BJ80": ["BJ80"],
        "EU5": ["EU5"],
        "EU7": ["EU7"],
        "F40": ["F40"],
        "U5PLUS": ["U5PLUS"],
        "U7": ["U7"],
        "X3": ["X3"],
        "X5": ["X5"],
        "X7": ["X7"],
    },
    "byd": {
        "唐": ["唐", "tang-", "tang100"],
        "宋": ["宋", "song-", "songdm", "song-ev", "宋电动", "宋经典", "宋Ultra"],
        "汉": ["汉"],
        "秦": ["秦", "qinev"],
        "元": ["元", "yuan-"],
        "海豹": ["海豹"],
        "海豚": ["海豚"],
        "海鸥": ["海鸥"],
        "海狮": ["海狮"],
        "护卫舰": ["护卫舰"],
        "驱逐舰": ["驱逐舰"],
        "e系列": ["e5300", "e6-", "E2", "E5", "EL用户手册"],
        "f系列": ["f0-", "f3-", "F6", "F3DM"],
        "g系列": ["g5-"],
        "s系列": ["s6-", "s7-"],
        "其他": ["byd3s", "SAFG", "比亚迪", "surui"],
    },
    "dazhong": {
        "ID.3": ["ID.3"],
        "ID.4": ["ID.4"],
        "ID.6": ["ID.6"],
        "POLO": ["POLO"],
        "途昂": ["途昂"],
        "凌渡": ["凌渡"],
        "威然": ["威然"],
        "帕萨特": ["帕萨特"],
        "辉昂": ["辉昂"],
        "途岳": ["途岳"],
        "朗逸": ["朗逸"],
        "桑塔纳": ["桑塔纳"],
        "途安": ["途安"],
        "途观": ["途观"],
        "途铠": ["途铠"],
    },
    "guangqi_chuanqi": {
        "E8": ["E8"],
        "E9": ["E9"],
        "ES9": ["ES9"],
        "GS4": ["GS4"],
        "GS8": ["GS8"],
        "M6": ["M6"],
        "M8": ["M8", "向往M8"],
        "S7": ["S7"],
        "S9": ["向往S9"],
    }
}


def classify_by_rules(brand, filename):
    """根据规则返回子目录名，优先匹配最长关键词"""
    if brand not in RULES:
        return None

    best_match = None
    best_len = 0
    fname_lower = filename.lower()
    for subdir, keywords in RULES[brand].items():
        for kw in keywords:
            if kw.lower() in fname_lower:
                if len(kw) > best_len:
                    best_len = len(kw)
                    best_match = subdir
    return best_match


def organize_toyota():
    """toyota 使用 car_pdfs.json 中的精确映射"""
    filename_to_dir = {}
    for item in car_data:
        if item.get("parten") == "fengtian_xi":
            for child in item.get("chrild", []):
                dir_name = child["dir_name"]
                for pdf in child.get("pdfs", []):
                    filename_to_dir[pdf] = dir_name

    src_dir = BASE / "toyota" / "doc"
    if not src_dir.exists():
        print("toyota/doc 不存在")
        return

    for pdf_file in src_dir.glob("*.pdf"):
        dir_name = filename_to_dir.get(pdf_file.name)
        if dir_name:
            dst_dir = BASE / "toyota" / dir_name
            dst_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(pdf_file), str(dst_dir / pdf_file.name))
            print(f"[toyota] {pdf_file.name} -> {dir_name}/")
        else:
            print(f"[toyota] 未分类: {pdf_file.name}")


def organize_brand(brand_name):
    """根据规则整理其他品牌"""
    src_dir = BASE / brand_name / "doc"
    if not src_dir.exists():
        print(f"{brand_name}/doc 不存在")
        return

    for pdf_file in src_dir.glob("*.pdf"):
        subdir = classify_by_rules(brand_name, pdf_file.name)
        if subdir:
            dst_dir = BASE / brand_name / subdir
            dst_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(pdf_file), str(dst_dir / pdf_file.name))
            print(f"[{brand_name}] {pdf_file.name} -> {subdir}/")
        else:
            print(f"[{brand_name}] 未分类: {pdf_file.name}")


if __name__ == "__main__":
    # 先处理 toyota（精确映射）
    organize_toyota()

    # 再处理其他品牌
    for brand in ["beijing_yueye", "byd", "dazhong", "guangqi_chuanqi"]:
        organize_brand(brand)

    print("\n整理完成！")
