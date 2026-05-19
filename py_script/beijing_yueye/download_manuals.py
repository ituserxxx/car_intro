"""
北京越野车型用户手册下载脚本
"""
import os
import re
import json
import time
import urllib.request
from pathlib import Path
from urllib.parse import quote, unquote

BASE_DIR = Path(__file__).parent
DOC_DIR = BASE_DIR / "doc"
DOC_DIR.mkdir(exist_ok=True)

MANUALS = [
    {"car": "BJ80 2020款", "url": "https://www.beijingauto.com.cn/pdf/BJ80%202020%E6%AC%BE%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6.pdf"},
    {"car": "BJ60", "url": "https://www.beijingauto.com.cn/pdf/BJ60%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6.pdf"},
    {"car": "BJ60增程", "url": "https://www.beijingauto.com.cn/pdf/BJ60%E5%A2%9E%E7%A8%8B%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A620251204.pdf"},
    {"car": "BJ40探险家", "url": "https://www.beijingauto.com.cn/pdf/bj40txjsms20260115.pdf"},
    {"car": "BJ40增程", "url": "https://www.beijingauto.com.cn/pdf/B41VS%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A620250813.pdf"},
    {"car": "BJ40增程赤兔版", "url": "https://www.beijingauto.com.cn/pdf/B41VS%E5%A2%9E%E7%A8%8B%E8%B5%A4%E5%85%94%E7%89%88%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A620260303.pdf"},
    {"car": "全新BJ40环塔冠军版", "url": "https://www.beijingauto.com.cn/pdf/%E5%85%A8%E6%96%B0BJ40%E7%8E%AF%E5%A1%94%E5%86%A0%E5%86%9B%E7%89%88%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A620250809.pdf"},
    {"car": "全新BJ40刀锋英雄版", "url": "https://www.beijingauto.com.cn/pdf/%E5%85%A8%E6%96%B0BJ40%E5%88%80%E9%94%8B%E8%8B%B1%E9%9B%84%E7%89%88%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A620260204.pdf"},
    {"car": "全新BJ40刀锋英雄巨幕版", "url": "https://www.beijingauto.com.cn/pdf/%E5%85%A8%E6%96%B0BJ40%E5%88%80%E9%94%8B%E8%8B%B1%E9%9B%84%E5%B7%A8%E5%B9%95%E7%89%88%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A620260204.pdf"},
    {"car": "全新BJ40城市猎人版", "url": "https://www.beijingauto.com.cn/pdf/%E5%85%A8%E6%96%B0BJ40%E5%9F%8E%E5%B8%82%E7%8C%8E%E4%BA%BA%E7%89%88%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A620260204.pdf"},
    {"car": "全新BJ40城市猎人巨幕版", "url": "https://www.beijingauto.com.cn/pdf/%E5%85%A8%E6%96%B0BJ40%E5%9F%8E%E5%B8%82%E7%8C%8E%E4%BA%BA%E5%B7%A8%E5%B9%95%E7%89%88%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A620260204.pdf"},
    {"car": "BJ40 2024款雨林穿越版", "url": "https://www.beijingauto.com.cn/pdf/BJ40%202024%E6%AC%BE%E9%9B%A8%E6%9E%97%E7%A9%BF%E8%B6%8A%E7%89%88%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A62024.pdf"},
    {"car": "BJ40 2023款环塔冠军版", "url": "https://www.beijingauto.com.cn/pdf/BJ40%E7%B3%BB%E5%88%97%E8%BD%A6%E5%9E%8B%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C.pdf"},
    {"car": "BJ40 2020款城市猎人版", "url": "https://www.beijingauto.com.cn/pdf/BJ40%E7%B3%BB%E5%88%97%E8%BD%A6%E5%9E%8B%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C.pdf"},
    {"car": "BJ40 2023款城市猎人版", "url": "https://www.beijingauto.com.cn/pdf/BJ40%E7%B3%BB%E5%88%97%E8%BD%A6%E5%9E%8B%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C.pdf"},
    {"car": "BJ40刀锋英雄版", "url": "https://www.beijingauto.com.cn/pdf/BJ40%E7%B3%BB%E5%88%97%E8%BD%A6%E5%9E%8B%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C.pdf"},
    {"car": "BJ40 2023款刀锋英雄版", "url": "https://www.beijingauto.com.cn/pdf/BJ40%E7%B3%BB%E5%88%97%E8%BD%A6%E5%9E%8B%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C.pdf"},
    {"car": "BJ40致敬2020版", "url": "https://www.beijingauto.com.cn/pdf/BJ40%E7%B3%BB%E5%88%97%E8%BD%A6%E5%9E%8B%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C.pdf"},
    {"car": "F40", "url": "https://www.beijingauto.com.cn/pdf/F40%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6.pdf"},
    {"car": "新魔方", "url": "https://www.beijingauto.com.cn/pdf/BEIJING%E9%AD%94%E6%96%B9%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6-20230721.pdf"},
    {"car": "新X7", "url": "https://www.beijingauto.com.cn/pdf/X7%E7%94%A8%E6%88%B7%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A62023.7.pdf"},
    {"car": "X5", "url": "https://www.beijingauto.com.cn/pdf/X5%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A620230720.pdf"},
    {"car": "X3", "url": "https://www.beijingauto.com.cn/pdf/X3%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A620211019.pdf"},
    {"car": "U7", "url": "https://www.beijingauto.com.cn/pdf/U7%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A62023.7.pdf"},
    {"car": "U5 PLUS", "url": "https://www.beijingauto.com.cn/pdf/U5PLUS%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C20230721.pdf"},
    {"car": "EU7", "url": "https://www.beijingauto.com.cn/pdf/EU7%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A62023.7.pdf"},
    {"car": "EU5", "url": "https://www.beijingauto.com.cn/pdf/EU5%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6%2020230718.pdf"},
    {"car": "新EU5 PLUS", "url": "https://www.beijingauto.com.cn/pdf/EU5PLUS%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A620230719.pdf"},
    {"car": "BJ30燃油", "url": "https://www.beijingauto.com.cn/pdf/B30X%E7%87%83%E6%B2%B9%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A620240524.pdf"},
    {"car": "BJ30混动", "url": "https://www.beijingauto.com.cn/pdf/B30X%E6%B7%B7%E5%8A%A8%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A620240524.pdf"},
]


def safe_name(name):
    return re.sub(r'[\\/:*?"<>|]', '_', name).strip()


def download_file(url, save_path):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/pdf,application/octet-stream,*/*",
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=120) as response:
            with open(save_path, "wb") as f:
                f.write(response.read())
        return True
    except Exception as e:
        print(f"    ERROR: {e}")
        return False


def main():
    print("=" * 60)
    print("Beijing Yueye Vehicle Manual Downloader")
    print("=" * 60)

    total_downloaded = 0
    total_skipped = 0

    for item in MANUALS:
        car_name = item["car"]
        url = item["url"]

        filename = url.split('/')[-1]
        try:
            filename = unquote(filename)
        except Exception:
            pass
        filename = safe_name(filename)
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'

        save_path = DOC_DIR / filename

        print(f"\nCar: {car_name}")
        safe_filename = filename.encode('gbk', errors='replace').decode('gbk')
        if save_path.exists():
            print(f"  SKIP (exists): {safe_filename}")
            total_skipped += 1
            continue

        print(f"  DOWNLOAD: {safe_filename}")
        if download_file(url, save_path):
            print(f"  OK -> {save_path}")
            total_downloaded += 1
        else:
            print(f"  FAILED")

        time.sleep(0.5)

    print("\n" + "=" * 60)
    print(f"Done: downloaded {total_downloaded}, skipped {total_skipped}")
    print(f"Save dir: {DOC_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
