import requests, os
from urllib.parse import unquote

DOC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'doc')
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

MANUALS = [
    {"name": "欧拉5 混动版", "url": "https://res.gwm.com.cn/2026/04/24/1853164_223_%E6%AC%A7%E6%8B%895-%E6%B7%B7%E5%8A%A8%E7%89%88-%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6-2026.02-V1.pdf"},
    {"name": "欧拉5 燃油版", "url": "https://res.gwm.com.cn/2026/04/24/1853162_223_%E6%AC%A7%E6%8B%895-%E7%87%83%E6%B2%B9%E7%89%88-%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6-2026.02-V1.pdf"},
    {"name": "欧拉5 纯电版", "url": "https://res.gwm.com.cn/2026/04/03/1852817_223_%E6%AC%A7%E6%8B%895-%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6(1)(1).pdf"},
    {"name": "欧拉好猫-2025款（经典型）", "url": "https://res.gwm.com.cn/2026/03/13/1852440_223_%E6%AC%A7%E6%8B%89%E5%A5%BD%E7%8C%AB-25%E6%AC%BE(%E4%BD%8E%E9%85%8D-%E7%BB%8F%E5%85%B8%E5%9E%8B%EF%BC%89-%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6.pdf"},
    {"name": "欧拉好猫-2025款（豪华型、尊荣型）", "url": "https://res.gwm.com.cn/2026/03/13/1852441_223_%E6%AC%A7%E6%8B%89%E5%A5%BD%E7%8C%AB-25%E6%AC%BE%EF%BC%88%E8%B1%AA%E5%8D%8E%E5%9E%8B%E5%B0%8A%E8%8D%A3%E5%9E%8B%EF%BC%89-%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6.pdf"},
    {"name": "欧拉好猫GT木兰版-2025款", "url": "https://res.gwm.com.cn/2026/03/13/1852443_223_%E6%AC%A7%E6%8B%89%E5%A5%BD%E7%8C%AB-%E8%BF%90%E5%8A%A8%E7%89%882025%E6%AC%BE-%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6.pdf"},
    {"name": "欧拉闪电猫", "url": "https://res.gwm.com.cn/2025/12/23/1851561_223_%E6%AC%A7%E6%8B%89%E9%97%AA%E7%94%B5%E7%8C%AB-%E5%9F%BA%E7%A1%80%E6%AC%BE-%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6.pdf"},
    {"name": "欧拉芭蕾猫", "url": "https://res.gwm.com.cn/2025/11/06/1850649_223_%E6%AC%A7%E6%8B%89%E8%8A%AD%E8%95%BE%E7%8C%AB-2023%E6%AC%BE-%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6.pdf"},
]


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def download_file(url, filepath):
    try:
        r = requests.get(url, headers=HEADERS, stream=True, timeout=60)
        r.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f'  [ERROR] 下载失败: {e}')
        if os.path.exists(filepath):
            os.remove(filepath)
        return False


def clean_filename(name):
    invalid = '\\/:*?"<>|'
    for c in invalid:
        name = name.replace(c, '_')
    return name.strip()


def main():
    ensure_dir(DOC_DIR)
    existing = set(os.listdir(DOC_DIR))
    print(f'已有PDF文件: {len(existing)} 个\n')

    total = len(MANUALS)
    skipped = 0
    downloaded = 0

    for item in MANUALS:
        model_name = item['name']
        url = item['url']
        fname = clean_filename(model_name) + '.pdf'

        if fname in existing:
            print(f'[SKIP] {fname}')
            skipped += 1
            continue

        filepath = os.path.join(DOC_DIR, fname)
        print(f'[DOWNLOAD] {fname}')
        if download_file(url, filepath):
            downloaded += 1
            existing.add(fname)

    print(f'\n===== 完成 =====')
    print(f'总计: {total} | 已存在跳过: {skipped} | 新下载: {downloaded}')


if __name__ == '__main__':
    main()
