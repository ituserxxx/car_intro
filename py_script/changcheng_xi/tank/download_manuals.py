#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载坦克官网所有随车手册 PDF
保存到 tank/doc/ 目录，按文档名称（含车型信息）命名
"""

import os
import re
import json
import requests

BASE_API = "https://cmsmanage-siteapi.gwm.com.cn"
DOC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "doc")
os.makedirs(DOC_DIR, exist_ok=True)

HEADERS_FORM = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
}
HEADERS_JSON = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/json",
}
SITE_ID = 1000076


def sanitize(name: str) -> str:
    """去除文件名中的非法字符"""
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    return name.strip() or "unknown"


def get_channels():
    url = f"{BASE_API}/downloadcenter/getchannelnew"
    r = requests.post(url, data={"site_id": SITE_ID}, headers=HEADERS_FORM, timeout=20)
    r.raise_for_status()
    data = r.json()
    if data.get("code") != 0:
        raise RuntimeError(f"getchannelnew 失败: {data}")
    return data.get("data", [])


def get_manual_channel(channels):
    for ch in channels:
        if "随车手册" in ch.get("label", ""):
            return ch
    labels = [ch.get("label") for ch in channels]
    raise RuntimeError(f"未找到'随车手册'频道，可用频道: {labels}")


def get_docs(fid: str, cid: str):
    url = f"{BASE_API}/downloadcenter/getallnew"
    payload = {
        "site_id": SITE_ID,
        "fid": fid,
        "cid": cid,
        "page": 1,
        "infosize": 10000,
        "userauth": 1,
    }
    r = requests.post(url, data=payload, headers=HEADERS_FORM, timeout=20)
    r.raise_for_status()
    data = r.json()
    if data.get("code") != 0:
        raise RuntimeError(f"getallnew 失败: {data}")
    return data.get("data", [])


def get_pdf_url(dirid: str, filetype: str) -> str:
    url = f"{BASE_API}/downloadcenter/getdirinfov2"
    payload = {"dirid": dirid, "filetype": filetype, "site_id": SITE_ID}
    r = requests.post(url, json=payload, headers=HEADERS_JSON, timeout=20)
    r.raise_for_status()
    data = r.json()
    if data.get("code") != 0:
        raise RuntimeError(f"getdirinfov2 失败: {data}")
    items = data.get("data", [])
    if not items:
        raise RuntimeError("getdirinfov2 返回空列表")
    return items[0]["obs_path"]


def download_pdf(url: str, name: str):
    safe_name = sanitize(name)
    path = os.path.join(DOC_DIR, f"{safe_name}.pdf")

    try:
        r = requests.get(url, headers=HEADERS_FORM, timeout=60, stream=True)
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"  [OK] {name}")
        return True
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        return False


def main():
    print("=== 坦克随车手册 PDF 下载工具 ===\n")

    print("1. 获取频道列表...")
    channels = get_channels()

    manual_ch = get_manual_channel(channels)
    fid = manual_ch["value"]
    cars = manual_ch.get("child", [])
    print(f"2. 找到频道: {manual_ch['label']} (fid={fid})")
    print(f"   共 {len(cars)} 个分类/车型\n")

    success = 0
    fail = 0

    for car in cars:
        car_name = car.get("label", "")
        cid = car.get("value", "")
        count = int(car.get("count", 0) or 0)

        if count == 0:
            print(f"[{car_name}] 无文档，跳过")
            continue

        print(f"[{car_name}] 查询文档列表...")
        try:
            docs = get_docs(fid, cid)
        except Exception as e:
            print(f"  [FAIL] 获取文档列表失败: {e}")
            fail += 1
            continue

        if not docs:
            print(f"  [SKIP] 文档列表为空")
            continue

        for doc in docs:
            doc_name = doc.get("bucket_name", "")
            dirid = doc.get("id")
            filetype = doc.get("bucket_file_type", "17")

            if not dirid:
                print(f"  [SKIP] 文档缺少 id")
                continue

            try:
                pdf_url = get_pdf_url(dirid, filetype)
            except Exception as e:
                print(f"  [FAIL] 获取 PDF 链接失败 [{doc_name}]: {e}")
                fail += 1
                continue

            if download_pdf(pdf_url, doc_name):
                success += 1
            else:
                fail += 1

    print(f"\n=== 完成 ===")
    print(f"成功: {success} 个")
    print(f"失败: {fail} 个")
    print(f"保存目录: {DOC_DIR}")


if __name__ == "__main__":
    main()
