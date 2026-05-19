import requests
import re
import os
import json

base_url = "https://www.gac-toyota.com.cn"
js_url = base_url + "/2022/src/assets/json/usermanual.js"
doc_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "doc")
os.makedirs(doc_dir, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.gac-toyota.com.cn/enjoy-service/usermanual",
}

print(f"正在下载数据源: {js_url}")
resp = requests.get(js_url, headers=headers, timeout=30)
print(f"Status: {resp.status_code}")
text = resp.text

# 提取数组
m = re.search(r'_baseData\.usermanualModle\s*=\s*(\[.*?\])\s*(?:;|$)', text, re.DOTALL)
if not m:
    print("未找到数据")
    exit(1)

js_array = m.group(1)

# 提取每个车型的 carName 和 manualData 块
car_blocks = re.findall(
    r'carName\s*:\s*[\'\"]([^\'\"]+)[\'\"].*?manualData\s*:\s*(\[[^\]]*\])',
    js_array, re.DOTALL
)

print(f"找到 {len(car_blocks)} 个车型")

# 如果上面的正则因为嵌套问题失败，换种方式：先把整个数组拆成单个对象
if not car_blocks:
    print("尝试按对象拆分...")
    # 找到每个 { } 块，但注意 manualData 内部也有 {}
    # 用更精确的方式：匹配从 { 到 },{ 或 }] 的块
    raw_blocks = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', js_array)
    car_blocks = []
    for block in raw_blocks:
        car_name_match = re.search(r"carName\s*:\s*['\"]([^'\"]+)['\"]", block)
        if car_name_match:
            car_name = car_name_match.group(1)
            # 提取 manualData 数组
            md_match = re.search(r'manualData\s*:\s*(\[.*?\])', block, re.DOTALL)
            if md_match:
                car_blocks.append((car_name, md_match.group(1)))

print(f"共 {len(car_blocks)} 个车型有手册数据")

total = 0
skipped = 0
downloaded = 0

for car_name, manual_data_str in car_blocks:
    # 从 manualData 数组中提取每个手册的 title 和 downloadUrl
    # manualData 格式: [{ title:'...', viewUrl:'...', downloadUrl:'...' },{...}]
    
    # 提取每个 {} 块
    items = re.findall(r'\{[^{}]*\}', manual_data_str)
    
    for item in items:
        title_match = re.search(r"title\s*:\s*['\"]([^'\"]+)['\"]", item)
        url_match = re.search(r"downloadUrl\s*:\s*['\"]([^'\"]+)['\"]", item)
        
        if not title_match or not url_match:
            continue
        
        title = title_match.group(1).strip()
        pdf_path = url_match.group(1).strip()
        
        if not pdf_path or not title:
            continue
        
        # 构建完整URL
        if pdf_path.startswith("http"):
            pdf_url = pdf_path
        else:
            pdf_url = base_url + pdf_path
        
        # 文件名：使用title，去掉.pdf后缀（如果有的话），再加上.pdf
        filename = title if title.endswith(".pdf") else title + ".pdf"
        # 清理非法字符
        filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
        filepath = os.path.join(doc_dir, filename)
        
        total += 1
        
        if os.path.exists(filepath):
            print(f"[跳过] {filename}")
            skipped += 1
            continue
        
        print(f"[下载] {car_name} -> {filename}")
        try:
            r = requests.get(pdf_url, headers=headers, timeout=120, stream=True)
            r.raise_for_status()
            with open(filepath, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            downloaded += 1
            print(f"  完成 ({os.path.getsize(filepath)} bytes)")
        except Exception as e:
            print(f"  失败: {e}")

print(f"\n总计: {total} 个文件, 下载 {downloaded} 个, 跳过 {skipped} 个")
print(f"保存目录: {doc_dir}")
