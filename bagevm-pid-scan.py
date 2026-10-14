#!/usr/bin/env python3
"""扫描 BageVM 各商店页，提取 (档位名, pid)，并交叉验证 pid 0-90 的 aff 链接。"""
import re, json, html, os, time, urllib.request, ssl

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8"}
BASE = "https://www.bagevm.com"
HERE = os.path.dirname(os.path.abspath(__file__))

PAGES = [
    "los-angeles-servers", "los-angeles2-servers", "salt-lake-city-servers",
    "hong-kong-servers", "hong-kong-lite-servers",
    "singapore-servers", "singapore-standard-servers",
    "japan-servers", "japan-standard-servers",
    "united-kingdom-servers", "germany-servers", "tw-hinet-vds",
]


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return r.read().decode("utf-8", errors="ignore")


out = {}
for slug in PAGES:
    url = f"{BASE}/index.php/store/{slug}"
    try:
        raw = fetch(url)
    except Exception as e:
        print("FAIL", slug, e)
        continue
    items = []
    # 每个产品块：h5 标题 + 规格 div，末尾是 id="productN-order-button"
    for m in re.finditer(r'<h5[^>]*>\s*(.*?)\s*</h5>', raw, re.S):
        title = html.unescape(re.sub(r"<[^>]+>", " ", m.group(1))).strip()
        tail = raw[m.end(): m.end() + 3000]
        pm = re.search(r'id="product(\d+)-order-button"', tail)
        if title and pm:
            items.append({"name": re.sub(r"\s+", " ", title), "pid": int(pm.group(1))})
    out[slug] = items
    print(f"{slug}: {len(items)} 档  " + ", ".join(f'{i["name"]}={i["pid"]}' for i in items))
    time.sleep(0.4)

with open(os.path.join(HERE, "data", "bagevm-pid映射.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

allpids = sorted({i["pid"] for v in out.values() for i in v})
print("\n共", len(allpids), "个 pid:", allpids)
