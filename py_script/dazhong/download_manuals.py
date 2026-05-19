"""
大众车型用户手册下载脚本
根据 car.json 中的页面抓取所有车型手册并下载到 doc/<车型>/ 目录下
"""
import os
import re
import json
import time
import urllib.request
from pathlib import Path
from urllib.parse import quote

BASE_DIR = Path(__file__).parent
DOC_DIR = BASE_DIR / "doc"
DOC_DIR.mkdir(exist_ok=True)

# 手动整理从页面 HTML 中提取的各车型 PDF 链接
# 这些链接来自 https://techcare.svw-volkswagen.com/khgg-sywh.html
MANUALS = [
    {"car": "ID.3", "url": "https://techcare.svw-volkswagen.com/pdf-1/sywh/2023/03/ID.3%20%E4%BD%BF%E7%94%A8%E7%BB%B4%E6%8A%A4%E8%AF%B4%E6%98%8E%E4%B9%A6-202303.pdf"},
    {"car": "ID.4 X", "url": "https://techcare.svw-volkswagen.com/pdf-1/sywh/2023/03/ID.4%20X%20%20%E4%BD%BF%E7%94%A8%E7%BB%B4%E6%8A%A4%E8%AF%B4%E6%98%8E%E4%B9%A6-202303.pdf"},
    {"car": "ID.6 X", "url": "https://techcare.svw-volkswagen.com/pdf-1/sywh/2023/03/ID.6%20X%20%E4%BD%BF%E7%94%A8%E7%BB%B4%E6%8A%A4%E8%AF%B4%E6%98%8E%E4%B9%A6-202303.pdf"},
    {"car": "全新桑塔纳", "url": "https://techcare.svw-volkswagen.com/pdf-1/sywh/0919/%E6%A1%91%E5%A1%94%E7%BA%B3%20%E4%BD%BF%E7%94%A8%E7%BB%B4%E6%8A%A4%E8%AF%B4%E6%98%8E%E4%B9%A6-202209.pdf"},
    {"car": "途观X", "url": "https://techcare.svw-volkswagen.com/pdf-1/sywh/2023/%E9%80%94%E8%A7%82X%20%E4%BD%BF%E7%94%A8%E7%BB%B4%E6%8A%A4%E8%AF%B4%E6%98%8E%E4%B9%A6-202302.pdf"},
    {"car": "途观L", "url": "https://techcare.svw-volkswagen.com/pdf-1/sywh/2023/03/%E9%80%94%E8%A7%82L%20%E4%BD%BF%E7%94%A8%E7%BB%B4%E6%8A%A4%E8%AF%B4%E6%98%8E%E4%B9%A6-202303.pdf"},
    {"car": "途观L插电混动", "url": "https://techcare.svw-volkswagen.com/pdf-1/sywh/0919/%E9%80%94%E8%A7%82L%E6%8F%92%E7%94%B5%E6%B7%B7%E5%8A%A8%20%E4%BD%BF%E7%94%A8%E7%BB%B4%E6%8A%A4%E8%AF%B4%E6%98%8E%E4%B9%A6-202209.pdf"},
    {"car": "途安L", "url": "https://techcare.svw-volkswagen.com/pdf-1/sywh/2023/%E9%80%94%E5%AE%89L%20%E4%BD%BF%E7%94%A8%E7%BB%B4%E6%8A%A4%E8%AF%B4%E6%98%8E%E4%B9%A6-202302.pdf"},
    {"car": "凌渡L", "url": "https://techcare.svw-volkswagen.com/pdf-1/sywh/2023/03/%E5%87%8C%E6%B8%A1L%20%E4%BD%BF%E7%94%A8%E7%BB%B4%E6%8A%A4%E8%AF%B4%E6%98%8E%E4%B9%A6-202302.pdf"},
    {"car": "朗逸", "url": "https://techcare.svw-volkswagen.com/pdf-1/sywh/2023/03/%E6%9C%97%E9%80%B8%20%E4%BD%BF%E7%94%A8%E7%BB%B4%E6%8A%A4%E8%AF%B4%E6%98%8E%E4%B9%A6-202303.pdf"},
    {"car": "帕萨特", "url": "https://techcare.svw-volkswagen.com/pdf-1/sywh/2023/03/%E5%B8%95%E8%90%A8%E7%89%B9%20%E4%BD%BF%E7%94%A8%E7%BB%B4%E6%8A%A4%E8%AF%B4%E6%98%8E%E4%B9%A6-202303.pdf"},
    {"car": "帕萨特插电混动", "url": "https://techcare.svw-volkswagen.com/pdf-1/sywh/0919/%E5%B8%95%E8%90%A8%E7%89%B9%E6%8F%92%E7%94%B5%E6%B7%B7%E5%8A%A8%20%E4%BD%BF%E7%94%A8%E7%BB%B4%E6%8A%A4%E8%AF%B4%E6%98%8E%E4%B9%A6-202210.pdf"},
    {"car": "新辉昂", "url": "https://techcare.svw-volkswagen.com/pdf-1/sywh/0919/%E6%96%B0%E8%BE%89%E6%98%82%20%E4%BD%BF%E7%94%A8%E7%BB%B4%E6%8A%A4%E8%AF%B4%E6%98%8E%E4%B9%A6-202207.pdf"},
    {"car": "全新途昂家族", "url": "https://techcare.svw-volkswagen.com/pdf-1/sywh/0919/%E5%85%A8%E6%96%B0%E9%80%94%E6%98%82%E5%AE%B6%E6%97%8F%20%E4%BD%BF%E7%94%A8%E7%BB%B4%E6%8A%A4%E8%AF%B4%E6%98%8E%E4%B9%A6-202209.pdf"},
    {"car": "新途岳", "url": "https://techcare.svw-volkswagen.com/pdf-1/sywh/2023/03/%E6%96%B0%E9%80%94%E5%B2%B3%20%E4%BD%BF%E7%94%A8%E7%BB%B4%E6%8A%A4%E8%AF%B4%E6%98%8E%E4%B9%A6-202303.pdf"},
    {"car": "途铠", "url": "https://techcare.svw-volkswagen.com/pdf-1/sywh/2023/03/%E9%80%94%E9%93%A0%20%E4%BD%BF%E7%94%A8%E7%BB%B4%E6%8A%A4%E8%AF%B4%E6%98%8E%E4%B9%A6-202302.pdf"},
    {"car": "朗逸纯电", "url": "https://techcare.svw-volkswagen.com/pdf-1/sywh/0406/%E6%9C%97%E9%80%B8%E7%BA%AF%E7%94%B5%20%E4%BD%BF%E7%94%A8%E7%BB%B4%E6%8A%A4%E8%AF%B4%E6%98%8E%E4%B9%A6-202110.pdf"},
    {"car": "新威然", "url": "https://techcare.svw-volkswagen.com/pdf-1/sywh/2023/03/%E5%A8%81%E7%84%B6%20%E4%BD%BF%E7%94%A8%E7%BB%B4%E6%8A%A4%E8%AF%B4%E6%98%8E%E4%B9%A6-202303.pdf"},
    {"car": "全新一代Polo", "url": "https://techcare.svw-volkswagen.com/pdf-1/sywh/2023/03/POLO%20%E4%BD%BF%E7%94%A8%E7%BB%B4%E6%8A%A4%E8%AF%B4%E6%98%8E%E4%B9%A6-202302.pdf"},
    {"car": "途岳纯电", "url": "https://techcare.svw-volkswagen.com/pdf-1/sywh/0406/%E9%80%94%E5%B2%B3%E7%BA%AF%E7%94%B5%20%E4%BD%BF%E7%94%A8%E7%BB%B4%E6%8A%A4%E8%AF%B4%E6%98%8E%E4%B9%A6-202202.pdf"},
    {"car": "朗逸启航", "url": "https://techcare.svw-volkswagen.com/pdf-1/sywh/0406/%E6%9C%97%E9%80%B8%E5%90%AF%E8%88%AA%20%E4%BD%BF%E7%94%A8%E7%BB%B4%E6%8A%A4%E8%AF%B4%E6%98%8E%E4%B9%A6-202203.pdf"},
    {"car": "朗逸新锐", "url": "https://techcare.svw-volkswagen.com/pdf-1/sywh/0616/%E6%9C%97%E9%80%B8%E6%96%B0%E9%94%90%20%E4%BD%BF%E7%94%A8%E7%BB%B4%E6%8A%A4%E8%AF%B4%E6%98%8E%E4%B9%A6-202306.pdf"},
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
    print("大众 Vehicle Manual Downloader")
    print("=" * 60)

    total_downloaded = 0
    total_skipped = 0

    for item in MANUALS:
        car_name = item["car"]
        url = item["url"]

        car_dir = DOC_DIR / safe_name(car_name)
        car_dir.mkdir(exist_ok=True)

        # 从 URL 中提取文件名
        filename = url.split('/')[-1]
        # URL decode
        try:
            from urllib.parse import unquote
            filename = unquote(filename)
        except Exception:
            pass

        # 安全化文件名
        filename = safe_name(filename)
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'

        save_path = car_dir / filename

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
