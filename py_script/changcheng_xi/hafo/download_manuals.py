#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载哈弗官网所有车型的随车手册 PDF
保存到 hafo/doc/ 目录，按车型名称命名
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


def sanitize_filename(name: str) -> str:
    """去除文件名中的非法字符"""
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    return name.strip() or "unknown"


def get_channels():
    """获取所有频道列表"""
    url = f"{BASE_API}/downloadcenter/getchannelnew"
    r = requests.post(url, data={"site_id": 183}, headers=HEADERS_FORM, timeout=20)
    r.raise_for_status()
    data = r.json()
    if data.get("code") != 0:
        raise RuntimeError(f"getchannelnew 失败: {data}")
    return data.get("data", [])


def get_manual_channel(channels):
    """从频道列表中找到'随车手册'"""
    for ch in channels:
        if "随车手册" in ch.get("label", ""):
            return ch
    labels = [ch.get("label") for ch in channels]
    raise RuntimeError(f"未找到'随车手册'频道，可用频道: {labels}")


def get_all_docs(fid: str, cid: str):
    """获取某个车型下的所有文档列表"""
    url = f"{BASE_API}/downloadcenter/getallnew"
    payload = {
        "site_id": 183,
        "fid": fid,
        "cid": cid,
        "page": 1,
        "infosize": 10000,
        "userauth": 2,
    }
    r = requests.post(url, data=payload, headers=HEADERS_FORM, timeout=20)
    r.raise_for_status()
    data = r.json()
    if data.get("code") != 0:
        raise RuntimeError(f"getallnew 失败: {data}")
    return data.get("data", [])


def get_pdf_url(dirid: str) -> str:
    """根据文档 ID 获取真实的 PDF 下载链接"""
    url = f"{BASE_API}/downloadcenter/getdirinfo"
    payload = {"dirid": dirid, "filetype": 2, "site_id": 183}
    r = requests.post(url, json=payload, headers=HEADERS_JSON, timeout=20)
    r.raise_for_status()
    data = r.json()
    if data.get("code") != 0:
        raise RuntimeError(f"getdirinfo 失败: {data}")
    items = data.get("data", [])
    if not items:
        raise RuntimeError("getdirinfo 返回空列表")
    return items[0]["obs_path"]


def download_pdf(url: str, name: str):
    """下载 PDF 并保存"""
    safe_name = sanitize_filename(name)
    path = os.path.join(DOC_DIR, f"{safe_name}.pdf")

    try:
        r = requests.get(url, headers=HEADERS_FORM, timeout=60, stream=True)
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"  [OK] {name} -> {os.path.basename(path)}")
        return True
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        return False


def main():
    print("=== 哈弗随车手册 PDF 下载工具 ===\n")

    # 1. 获取频道列表
    print("1. 获取频道列表...")
    channels = get_channels()

    # 2. 找到随车手册频道
    manual_ch = get_manual_channel(channels)
    fid = manual_ch["value"]
    cars = manual_ch.get("child", [])
    print(f"2. 找到频道: {manual_ch['label']} (fid={fid})")
    print(f"   共 {len(cars)} 个车型\n")

    # 3. 遍历每个车型下载
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
            docs = get_all_docs(fid, cid)
        except Exception as e:
            print(f"  [FAIL] 获取文档列表失败: {e}")
            fail += 1
            continue

        if not docs:
            print(f"  [SKIP] 文档列表为空")
            continue

        # 通常一个车型只有一份随车手册，取第一个
        doc = docs[0]
        dirid = doc.get("id")
        if not dirid:
            print(f"  [SKIP] 文档缺少 id")
            continue

        try:
            pdf_url = get_pdf_url(dirid)
        except Exception as e:
            print(f"  [FAIL] 获取 PDF 链接失败: {e}")
            fail += 1
            continue

        if download_pdf(pdf_url, car_name):
            success += 1
        else:
            fail += 1

    print(f"\n=== 完成 ===")
    print(f"成功: {success} 个")
    print(f"失败: {fail} 个")
    print(f"保存目录: {DOC_DIR}")


if __name__ == "__main__":
    main()
