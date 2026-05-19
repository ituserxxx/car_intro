import requests, os
from urllib.parse import unquote

BASE_API = 'https://cmsmanage-siteapi.gwm.com.cn'
DOC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'doc')
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def get_existing_files():
    if not os.path.exists(DOC_DIR):
        return set()
    return set(os.listdir(DOC_DIR))


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


def fetch_manuals():
    url = BASE_API + '/wey/manual-and-folding/get-manual-and-folding'
    r = requests.post(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    data = r.json()
    if data.get('code') != '0':
        print(f'[ERROR] 获取手册列表失败: {data}')
        return []
    return data.get('data', [])


def clean_filename(name):
    invalid = '\\/:*?"<>|'
    for c in invalid:
        name = name.replace(c, '_')
    return name.strip()


def extract_name_from_url(url):
    try:
        parts = url.split('/')
        fname = unquote(parts[-1])
        if fname.endswith('.pdf'):
            # 去掉可能的前缀哈希
            if '_' in fname:
                parts_name = fname.split('_')
                # 找最后一个以 .pdf 结尾的部分
                for p in reversed(parts_name):
                    if p.endswith('.pdf'):
                        return p
            return fname
    except Exception:
        pass
    return None


def main():
    ensure_dir(DOC_DIR)
    existing = get_existing_files()
    print(f'已有PDF文件: {len(existing)} 个')

    manuals = fetch_manuals()
    print(f'获取到 {len(manuals)} 个车型手册')

    total = 0
    skipped = 0
    downloaded = 0

    for item in manuals:
        model_name = item.get('model_name', '')
        pdf_url = item.get('manual_rel', '')
        if not pdf_url:
            continue

        # 优先使用 model_name 作为文件名，否则从URL提取
        if model_name:
            fname = clean_filename(model_name) + '.pdf'
        else:
            extracted = extract_name_from_url(pdf_url)
            if extracted:
                fname = clean_filename(extracted)
            else:
                fname = clean_filename(f'doc_{item.get("model_id")}') + '.pdf'

        total += 1
        if fname in existing:
            print(f'[SKIP] {fname}')
            skipped += 1
            continue

        filepath = os.path.join(DOC_DIR, fname)
        print(f'[DOWNLOAD] {fname}')
        if download_file(pdf_url, filepath):
            downloaded += 1
            existing.add(fname)

    print(f'\n===== 完成 =====')
    print(f'总计: {total} | 已存在跳过: {skipped} | 新下载: {downloaded}')


if __name__ == '__main__':
    main()
