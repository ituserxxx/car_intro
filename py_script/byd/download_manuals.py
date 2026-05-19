"""
比亚迪车型手册下载脚本
"""
import os
import re
import json
import time
import hmac
import hashlib
import zipfile
import urllib.request
from pathlib import Path
from urllib.parse import urljoin, quote

SGK = "4a3688a5gcd88g443fga6b7fcb"
SK = "fcb8f0ddg5c92g45b7g9d33g04cc55d3be3b"
BASE_URL = "https://www.byd.com"
API_URL = "https://cms-api.byd.com/es/search"
DOC_DIR = Path(__file__).parent / "doc"
DOC_DIR.mkdir(exist_ok=True)

def sign(sgk, sk):
    timestamp = str(int(time.time()))
    message = f"{sgk}\n{sk}\n{timestamp}"
    signature = hmac.new(sk.encode(), message.encode(), hashlib.sha256).hexdigest()
    return {
        "X-HMAC-SIGNATURE": signature,
        "X-HMAC-TIMESTAMP": timestamp,
        "X-HMAC-SIGNKEY": sgk,
    }

def post_json(url, data):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Referer": "https://www.byd.com/",
        "Origin": "https://www.byd.com",
    }
    headers.update(sign(SGK, SK))
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return None

def fetch_all_records():
    all_records = []
    page = 1
    while True:
        data = {
            "brandName": "byd",
            "siteName": "cn",
            "type": "user-manual",
            "page": page,
            "size": 100,
            "sortField": "date",
            "text": "",
        }
        result = post_json(API_URL, data)
        if not result or result.get("code") != 0:
            break
        records = result.get("data", {}).get("records", [])
        if not records:
            break
        all_records.extend(records)
        total = result.get("data", {}).get("total", 0)
        print(f"  Page {page}: {len(records)} records (total {len(all_records)}/{total})")
        if len(all_records) >= total:
            break
        page += 1
    return all_records

def download_file(url_path, save_path):
    encoded_path = quote(url_path, safe='/')
    url = urljoin(BASE_URL, encoded_path)
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
        print(f"    ERROR: download failed")
        return False

def extract_zip(zip_path, extract_dir):
    pdf_files = []
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for member in zf.namelist():
                zf.extract(member, extract_dir)
                extracted_path = Path(extract_dir) / member
                if extracted_path.suffix.lower() == '.pdf':
                    pdf_files.append(extracted_path)
        return pdf_files
    except Exception as e:
        print(f"    ERROR: extract failed")
        return []

def safe_name(name):
    return re.sub(r'[\\/:*?"<>|]', '_', name).strip()

def main():
    print("=" * 60)
    print("BYD Vehicle Manual Downloader")
    print("=" * 60)
    
    print("\n1. Fetching manual list...")
    records = fetch_all_records()
    print(f"Total {len(records)} records")
    
    with open("manuals_data.json", "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    
    cars = {}
    for r in records:
        title = r.get("title", "unknown")
        car_name = title
        car_name = re.sub(r'^\d{4}款', '', car_name).strip()
        car_name = re.sub(r'用户手册.*$', '', car_name).strip()
        
        if car_name not in cars:
            cars[car_name] = []
        cars[car_name].append(r)
    
    print(f"\n2. Total {len(cars)} car categories")
    
    print("\n3. Starting download...")
    total_downloaded = 0
    total_skipped = 0
    total_extracted = 0
    
    for car_name, car_records in sorted(cars.items()):
        print(f"\n  Car: {car_name} ({len(car_records)} files)")
        
        for idx, r in enumerate(car_records, 1):
            title = r.get("title", "unknown")
            url_path = r.get("url", "")
            if not url_path:
                continue
            
            ext = Path(url_path).suffix.lower()
            if not ext:
                ext = ".pdf"
            
            safe_title = safe_name(title)
            filename = f"{safe_title}{ext}"
            save_path = DOC_DIR / filename
            
            if save_path.exists():
                print(f"    [{idx}/{len(car_records)}] SKIP (exists)")
                total_skipped += 1
                continue
            
            print(f"    [{idx}/{len(car_records)}] DL: {filename[:50]}")
            if download_file(url_path, save_path):
                total_downloaded += 1
                
                if ext == ".zip":
                    print(f"      Extracting...")
                    extract_dir = DOC_DIR / f"_extract_{idx}"
                    extract_dir.mkdir(exist_ok=True)
                    pdf_files = extract_zip(save_path, extract_dir)
                    if pdf_files:
                        for pdf in pdf_files:
                            pdf_name = safe_name(pdf.name)
                            pdf_dest = DOC_DIR / pdf_name
                            counter = 1
                            original_dest = pdf_dest
                            while pdf_dest.exists():
                                stem = original_dest.stem
                                pdf_dest = DOC_DIR / f"{stem}_{counter}{original_dest.suffix}"
                                counter += 1
                            os.replace(pdf, pdf_dest)
                            print(f"      -> PDF extracted")
                            total_extracted += 1
                        os.remove(save_path)
                        import shutil
                        shutil.rmtree(extract_dir, ignore_errors=True)
                    else:
                        print(f"      No PDF in zip")
            else:
                print(f"      FAILED")
            
            time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print(f"Done: downloaded {total_downloaded}, skipped {total_skipped}, extracted {total_extracted}")
    print(f"Files saved to: {DOC_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
