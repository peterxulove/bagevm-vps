#!/usr/bin/env python3
"""遍历 pid 1-110，用 add-to-cart -> confproduct 页面读出真实产品名，建立权威 pid 对照表。"""
import re, json, os, time, ssl, http.cookiejar, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"}
HERE = os.path.dirname(os.path.abspath(__file__))


def probe(pid):
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj),
                                     urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    try:
        r = op.open(urllib.request.Request(f"https://www.bagevm.com/cart.php?a=add&pid={pid}", headers=UA), timeout=30)
        final = r.geturl()
        t = r.read().decode("utf-8", "ignore")
    except Exception as e:
        return {"pid": pid, "kind": "err", "err": str(e)[:80]}
    tail = final.split("bagevm.com")[-1]
    tt = re.sub(r"<script[\s\S]*?</script>", " ", t)
    tt = re.sub(r"<[^>]+>", " ", tt)
    tt = re.sub(r"\s+", " ", __import__("html").unescape(tt))
    i = tt.find("Configure your desired options")
    name, spec = "", ""
    if i >= 0:
        seg = tt[i + len("Configure your desired options and continue to checkout."):][:220].strip()
        # 产品名 + 规格
        name = seg.split("  ")[0][:60]
        spec = seg[:160]
        return {"pid": pid, "kind": "instock", "slug": "", "name": name, "spec": spec}
    m = re.search(r"/index\.php/store/([^/]+)/([^/?#]+)", tail)
    if m:
        return {"pid": pid, "kind": "oos", "slug": f"{m.group(1)}/{m.group(2)}", "name": "", "spec": ""}
    return {"pid": pid, "kind": "invalid", "slug": "", "name": "", "spec": ""}


rows = {}
for pid in range(1, 111):
    v = probe(pid)
    rows[pid] = v
    if v["kind"] != "invalid":
        print(f'pid={pid:>3}  {v["kind"]:7s}  {v.get("name","")[:45]:45s} {v.get("slug","")}', flush=True)
    time.sleep(0.05)

with open(os.path.join(HERE, "data", "bagevm-pid全量映射.json"), "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=1)
print("\n完成。有效 pid:", sorted(p for p, v in rows.items() if v["kind"] != "invalid"))
