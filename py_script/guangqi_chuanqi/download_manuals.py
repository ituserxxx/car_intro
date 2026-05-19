"""
广汽传祺车型用户手册下载脚本
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
    {"car": "向往S9", "url": "https://www.gacmotor.com/static/upload/explanation/%E5%90%91%E5%BE%80S9_T60-M__%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_20260320.pdf"},
    {"car": "向往M8乾崑", "url": "https://www.gacmotor.com/static/upload/explanation/%E5%90%91%E5%BE%80M8%E4%B9%BE%E5%B4%91_T9M%E9%95%BF%E7%BB%AD%E8%88%AA__%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6_20260319.pdf"},
    {"car": "向往M8宗师（T9M短续航智驾）", "url": "https://www.gacmotor.com/static/upload/explanation/%E5%90%91%E5%BE%80M8%E5%AE%97%E5%B8%88%EF%BC%88T9M%E7%9F%AD%E7%BB%AD%E8%88%AA%E6%99%BA%E9%A9%BE%EF%BC%89_%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_20251111.pdf"},
    {"car": "向往M8宗师尊享版（非智驾版）", "url": "https://www.gacmotor.com/static/upload/explanation/%E5%90%91%E5%BE%80M8%E5%AE%97%E5%B8%88%E5%B0%8A%E4%BA%AB%E7%89%88%EF%BC%88%E9%9D%9E%E6%99%BA%E9%A9%BE%E7%89%88%EF%BC%89_%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6_20251219.pdf"},
    {"car": "S7（T68）", "url": "https://www.gacmotor.com/static/upload/explanation/S7%EF%BC%88T68%EF%BC%89_%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_20260105.pdf"},
    {"car": "E8（A09 HEV）", "url": "https://www.gacmotor.com/static/upload/explanation/%28E8A09%20HEV%29_%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6%E5%AE%8C%E6%95%B4%E7%89%88_20250118.pdf"},
    {"car": "E8（T09-Y）", "url": "https://www.gacmotor.com/static/upload/explanation/E8%EF%BC%88T09-Y%EF%BC%89_%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6_20251231.pdf"},
    {"car": "E9（T9M 第一阶段）", "url": "https://www.gacmotor.com/static/upload/explanation/E9%28T9M%20%E7%AC%AC%E4%B8%80%E9%98%B6%E6%AE%B5%29_%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6%E5%AE%8C%E6%95%B4%E7%89%88_20250220.pdf"},
    {"car": "E9电动福祉版", "url": "https://www.gacmotor.com/static/upload/explanation/E9%E7%94%B5%E5%8A%A8%E7%A6%8F%E7%A5%89%E7%89%88%28A8E%E7%A6%8F%E7%A5%89%E7%89%88%29_%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6%28%E5%90%88%E5%B9%B6%E4%BF%9D%E4%BF%AE%E4%BF%9D%E5%85%BB%E6%89%8B%E5%86%8C%29_20250225.pdf"},
    {"car": "E9国宾定制版", "url": "https://www.gacmotor.com/static/upload/explanation/E9%E5%9B%BD%E5%AE%BE%E5%AE%9A%E5%88%B6%E7%89%88%28A8E%E6%AE%BF%E5%A0%82%E7%89%88%29_%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6%28%E5%90%88%E5%B9%B6%E4%BF%9D%E4%BF%AE%E4%BF%9D%E5%85%BB%E6%89%8B%E5%86%8C%29_20250225.pdf"},
    {"car": "E8（A09 PHEV）", "url": "https://www.gacmotor.com/static/upload/explanation/E8%EF%BC%88A09%20PHEV%EF%BC%89_%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6_20251231.pdf"},
    {"car": "E9（T9M短续航）", "url": "https://www.gacmotor.com/static/upload/explanation/E9%EF%BC%88T9M%E7%9F%AD%E7%BB%AD%E8%88%AA%EF%BC%89_%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_20251106.pdf"},
    {"car": "ES9", "url": "https://www.gacmotor.com/static/upload/explanation/ES9_T6E%E5%90%AB%E9%A1%B6%E9%85%8D__%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6_20260121.pdf"},
    {"car": "GS4 MAX", "url": "https://www.gacmotor.com/static/upload/explanation/GS4%20MAX%EF%BC%88T58-X%20%E7%87%83%E6%B2%B9%EF%BC%89_%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6_20251229.pdf"},
    {"car": "M6 MAX", "url": "https://www.gacmotor.com/static/upload/explanation/M6%20MAX%EF%BC%88T08-Y%EF%BC%8C%E5%90%AB2024%E6%AC%BE%E3%80%812025%E6%AC%BE%EF%BC%89_%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6_20250621.pdf"},
    {"car": "M8 HYBRID", "url": "https://www.gacmotor.com/static/upload/explanation/M8%20HYBRID%28T88-Y%20GMC400%29_%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6%E5%AE%8C%E6%95%B4%E7%89%88_20250220.pdf"},
    {"car": "M8燃油", "url": "https://www.gacmotor.com/static/upload/explanation/M8%28T88-Y%20%E7%87%83%E6%B2%B9%29_%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6%E5%AE%8C%E6%95%B4%E7%89%88%28%E5%90%88%E5%B9%B6%E4%BF%9D%E4%BF%AE%E4%BF%9D%E5%85%BB%E6%89%8B%E5%86%8C%29_20250222.pdf"},
    {"car": "M8双擎", "url": "https://www.gacmotor.com/static/upload/explanation/M8%E5%8F%8C%E6%93%8E%28T88-Y%20THS%29_%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6_20250220.pdf"},
    {"car": "M8宗师科技关爱版", "url": "https://www.gacmotor.com/static/upload/explanation/M8%E5%AE%97%E5%B8%88%E7%A7%91%E6%8A%80%E5%85%B3%E7%88%B1%E7%89%88%28T88-Y%20%E7%A6%8F%E7%A5%89%E7%89%88%29_%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6%E5%AE%8C%E6%95%B4%E7%89%88%28%E5%90%88%E5%B9%B6%E4%BF%9D%E4%BF%AE%E4%BF%9D%E5%85%BB%E6%89%8B%E5%86%8C%29_20250222.pdf"},
    {"car": "全新第二代GS8", "url": "https://www.gacmotor.com/static/upload/explanation/%E5%85%A8%E6%96%B0%E7%AC%AC%E4%BA%8C%E4%BB%A3GS8%28T60-Y%E7%87%83%E6%B2%B9%E5%90%AB2024%E6%AC%BE%E3%80%812025%E6%AC%BE%E3%80%81T60-Y1%E5%9B%9B%E9%A9%B1%E4%BA%94%E5%BA%A7%29_%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6%28%E5%90%88%E5%B9%B6%E4%BF%9D%E4%BF%AE%E4%BF%9D%E5%85%BB%E6%89%8B%E5%86%8C%29_20250225.pdf"},
    {"car": "影豹", "url": "https://www.gacmotor.com/static/upload/explanation/%E5%BD%B1%E8%B1%B9%28A5X%29_%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6%E5%AE%8C%E6%95%B4%E7%89%88_20250220.pdf"},
    {"car": "影酷", "url": "https://www.gacmotor.com/static/upload/explanation/%E5%BD%B1%E9%85%B7%28A9E%29_%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6%E5%AE%8C%E6%95%B4%E7%89%88_20250220.pdf"},
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
    print("广汽传祺 Vehicle Manual Downloader")
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

        print(f"\n车型: {car_name}")
        if save_path.exists():
            print(f"  SKIP (已存在): {filename}")
            total_skipped += 1
            continue

        print(f"  下载: {filename}")
        if download_file(url, save_path):
            print(f"  成功 -> {save_path}")
            total_downloaded += 1
        else:
            print(f"  失败")

        time.sleep(0.5)

    print("\n" + "=" * 60)
    print(f"完成: 下载 {total_downloaded} 个, 跳过 {total_skipped} 个")
    print(f"保存目录: {DOC_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
