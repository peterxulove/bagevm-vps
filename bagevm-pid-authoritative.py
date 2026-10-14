#!/usr/bin/env python3
"""用 add-to-cart 重定向目标，建立权威的 pid -> 产品 映射（BageVM）。

判据：
  - 302/落点 = cart.php?a=confproduct&i=0  -> 该 pid 有效且**有货**（已加入购物车）
  - 落点 = /index.php/store/<slug>/<tier> -> 该 pid 有效但**缺货**（跳回产品页）
  - 落点 = /index.php/store/<slug>（无 tier） -> pid 无效
"""
import re, json, os, time, ssl, http.cookiejar, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"}
HERE = os.path.dirname(os.path.abspath(__file__))


def add(pid):
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj),
                                     urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    try:
        r = op.open(urllib.request.Request(f"https://www.bagevm.com/cart.php?a=add&pid={pid}", headers=UA), timeout=30)
        return r.geturl()
    except Exception as e:
        return f"ERR:{e}"


rows = {}
for pid in range(1, 111):
    final = add(pid)
    tail = final.split("bagevm.com")[-1]
    if "confproduct" in tail:
        kind, slug = "instock", ""
    elif re.search(r"/index\.php/store/([^/]+)/([^/?#]+)", tail):
        m = re.search(r"/index\.php/store/([^/]+)/([^/?#]+)", tail)
        kind, slug = "oos", f"{m.group(1)}/{m.group(2)}"
    elif "/index.php/store/" in tail:
        kind, slug = "invalid", ""
    else:
        kind, slug = "other", tail
    rows[pid] = {"kind": kind, "slug": slug, "final": tail}
    if kind != "invalid":
        print(f"pid={pid:>3}  {kind:8s} {slug}")
    time.sleep(0.1)

with open(os.path.join(HERE, "data", "bagevm-pid权威映射.json"), "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=1)

valid = {p: v for p, v in rows.items() if v["kind"] in ("instock", "oos")}
print(f"\n有效 pid {len(valid)} 个：", sorted(valid))
print("有货:", sorted(p for p, v in valid.items() if v["kind"] == "instock"))
