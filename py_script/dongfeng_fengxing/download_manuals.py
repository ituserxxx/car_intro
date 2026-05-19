import urllib.request
import urllib.parse
import os
from pathlib import Path

doc_dir = Path(__file__).parent / 'doc'
os.makedirs(doc_dir, exist_ok=True)

manuals = [
    "http://www.fxauto.com.cn/html/instruction/%E8%8F%B1%E6%99%BAM5%E4%BD%BF%E7%94%A8%E5%8F%8A%E4%B8%89%E5%8C%85%E6%89%8B%E5%86%8C%EF%BC%88%E9%80%82%E7%94%A8%E8%BD%A6%E5%9E%8B%EF%BC%9A%E8%8F%B1%E6%99%BAM5%E3%80%81V3%EF%BC%89.pdf",
    "http://www.fxauto.com.cn/html/instruction/%E8%8F%B1%E6%99%BAPLUS%E4%BD%BF%E7%94%A8%E5%8F%8A%E4%B8%89%E5%8C%85%E6%89%8B%E5%86%8C.pdf",
    "http://www.fxauto.com.cn/html/instruction/%E8%8F%B1%E6%99%BA%E6%96%B0%E8%83%BD%E6%BA%90%E4%BD%BF%E7%94%A8%E5%8F%8A%E4%B8%89%E5%8C%85%E6%89%8B%E5%86%8C.pdf",
    "http://www.fxauto.com.cn/html/instruction/%E9%A3%8E%E8%A1%8CM7%E4%BD%BF%E7%94%A8%E5%8F%8A%E4%B8%89%E5%8C%85%E6%89%8B%E5%86%8C.pdf",
    "http://www.fxauto.com.cn/html/instruction/%E9%A3%8E%E8%A1%8CS50EV%E4%BD%BF%E7%94%A8%E5%8F%8A%E4%B8%89%E5%8C%85%E6%89%8B%E5%86%8C.pdf",
    "http://www.fxauto.com.cn/html/instruction/%E9%A3%8E%E8%A1%8CT5%20EVO%E4%BD%BF%E7%94%A8%E5%8F%8A%E4%B8%89%E5%8C%85%E6%89%8B%E5%86%8C%EF%BC%88%E9%80%82%E7%94%A8%E8%BD%A6%E5%9E%8B%EF%BC%9A%E9%A3%8E%E8%A1%8CT5%20EVO%E3%80%81%E7%8B%82%E9%A3%99%E7%89%88%EF%BC%89.pdf",
    "http://www.fxauto.com.cn/html/instruction/%E9%A3%8E%E8%A1%8C%E6%B8%B8%E8%89%87%E4%BD%BF%E7%94%A8%E5%8F%8A%E4%B8%89%E5%8C%85%E6%89%8B%E5%86%8C.pdf",
    "http://www.fxauto.com.cn/html/instruction/%E9%A3%8E%E8%A1%8C%E9%9B%B7%E9%9C%86%E4%BD%BF%E7%94%A8%E5%8F%8A%E4%B8%89%E5%8C%85%E6%89%8B%E5%86%8C.pdf",
    "http://www.fxauto.com.cn/html/instruction/%E9%A3%8E%E8%A1%8CT5%E4%BD%BF%E7%94%A8%E5%8F%8A%E4%B8%89%E5%8C%85%E6%89%8B%E5%86%8C%EF%BC%88%E9%80%82%E7%94%A8%E8%BD%A6%E5%9E%8B%EF%BC%9A%E9%A3%8E%E8%A1%8CT5%E9%A9%AC%E8%B5%AB%E7%89%88%E3%80%81%E7%9B%9B%E4%B8%96%E6%AC%BE%EF%BC%89.pdf",
]

for url in manuals:
    name = os.path.basename(urllib.parse.urlparse(url).path)
    filepath = doc_dir / name
    if filepath.exists():
        print(f'Skip {name}')
        continue
    try:
        print(f'Downloading {name} ...')
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/pdf,application/octet-stream,*/*',
            'Referer': 'http://www.fxauto.com.cn/',
        })
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(filepath, 'wb') as f:
                f.write(resp.read())
        print(f'Saved {name}')
    except Exception as e:
        print(f'Error downloading {name}: {e}')
