import requests, os, json
from urllib.parse import unquote

BASE_API = 'https://cmsmanage-siteapi.gwm.com.cn'
DOC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'doc')
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Content-Type': 'application/json',
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


def fetch_classify():
    url = BASE_API + '/content/classify'
    payload = {
        'site_id': '1000042',
        'parent_id': '1102882',
        'is_all': '1'
    }
    r = requests.post(url, headers=HEADERS, json=payload, timeout=20)
    r.raise_for_status()
    data = r.json()
    if data.get('code') != 0:
        print(f'[ERROR] 获取分类失败: {data}')
        return []
    return data.get('data', [])


def fetch_docs(classify_id):
    url = BASE_API + '/content/list'
    payload = {
        'site_id': '1000042',
        'classify_id': classify_id,
        'limit': 100
    }
    r = requests.post(url, headers=HEADERS, json=payload, timeout=20)
    r.raise_for_status()
    data = r.json()
    if data.get('code') != 0:
        return []
    return data.get('data', {}).get('list', [])


def clean_filename(name):
    invalid = '\\/:*?"<>|'
    for c in invalid:
        name = name.replace(c, '_')
    return name.strip()


def extract_name_from_url(url):
    # 从URL中提取文件名
    try:
        parts = url.split('/')
        fname = unquote(parts[-1])
        if fname.endswith('.pdf'):
            return fname
    except Exception:
        pass
    return None


def main():
    ensure_dir(DOC_DIR)
    existing = get_existing_files()
    print(f'已有PDF文件: {len(existing)} 个')

    classify_list = fetch_classify()
    print(f'获取到 {len(classify_list)} 个车型分类')

    total = 0
    skipped = 0
    downloaded = 0

    for cls in classify_list:
        car_name = cls.get('name', '未知车型')
        cid = cls.get('id')
        if not cid:
            continue

        docs = fetch_docs(cid)
        print(f'\n[{car_name}] 找到 {len(docs)} 个文档')

        for doc in docs:
            title = doc.get('title', '')
            pdf_url = doc.get('url_pdf', '')
            if not pdf_url:
                continue

            # 优先使用title作为文件名，如果title为空则从URL提取
            if title:
                fname = clean_filename(title) + '.pdf'
            else:
                extracted = extract_name_from_url(pdf_url)
                if extracted:
                    fname = clean_filename(extracted)
                else:
                    fname = clean_filename(f'doc_{doc.get("id")}') + '.pdf'

            total += 1
            if fname in existing:
                print(f'  [SKIP] {fname}')
                skipped += 1
                continue

            filepath = os.path.join(DOC_DIR, fname)
            print(f'  [DOWNLOAD] {fname}')
            if download_file(pdf_url, filepath):
                downloaded += 1
                existing.add(fname)

    print(f'\n===== 完成 =====')
    print(f'总计: {total} | 已存在跳过: {skipped} | 新下载: {downloaded}')


if __name__ == '__main__':
    main()
