#!/usr/bin/env python3
"""BageVM 官网商店页扫描：产品线 / 档位 / 价格 / 库存 / 订购链接。"""
import re, json, html, os, time, urllib.request, ssl

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8"}
BASE = "https://www.bagevm.com"

PAGES = {
    "los-angeles-servers":   "Los Angeles Servers",
    "los-angeles2-servers":  "Los Angeles2 Servers",
    "salt-lake-city-servers":"Salt Lake City Servers",
    "hong-kong-servers":     "Hong Kong Standard Servers",
    "hong-kong-lite-servers":"Hong Kong Lite Servers",
    "singapore-servers":     "Singapore Servers",
    "singapore-standard-servers": "Singapore Standard Servers",
    "japan-servers":         "Japan Servers",
    "japan-standard-servers":"Japan Standard Servers",
    "united-kingdom-servers":"United Kingdom Servers",
    "germany-servers":       "Germany Servers",
    "tw-hinet-vds":          "TW HINET VDS",
}

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return r.read().decode("utf-8", errors="ignore")

def text_of(t):
    t = re.sub(r"<script[\s\S]*?</script>", " ", t)
    t = re.sub(r"<style[\s\S]*?</style>", " ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    return re.sub(r"\s+", " ", t)

def fetch_deps(raw):
    """fetchDependencies 列表，包含各产品 order 按钮的 pid"""
    pids = re.findall(r'href="[^"]*cart\.php\?a=add&(?:pid|pid=\d+)[^"]*"', raw)
    # 直接找 pid
    pids = re.findall(r'pid=(\d+)', raw)
    return sorted(set(pids), key=int)

out = {}
for slug, label in PAGES.items():
    url = f"{BASE}/index.php/store/{slug}"
    try:
        raw = fetch(url)
    except Exception as e:
        print(f"FAIL {slug}: {e}")
        continue
    txt = text_of(raw)
    # 找 "View Cart" 之后的产品区
    i = txt.find("View Cart")
    body = txt[i:] if i >= 0 else txt
    # 截断到 footer
    j = body.find("Based on this product")
    if j > 0: body = body[:j]
    pids = fetch_deps(raw)
    out[slug] = {"label": label, "url": url, "pids": pids, "text": body.strip()}
    print(f"OK {slug}: {len(body)} chars, pids={pids}")
    time.sleep(0.5)

with open(os.path.join(os.path.dirname(__file__), "bagevm-store扫描.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("saved", len(out), "pages")
