#!/usr/bin/env python3
"""交叉验证：pid 1-100 的 aff 链接落点状态（有货=返回分类页 / 缺货=Out of Stock / 无效）。"""
import re, json, os, time, urllib.request, ssl

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"}
HERE = os.path.dirname(os.path.abspath(__file__))


def get(url, follow=True):
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None
    handlers = [] if follow else [NoRedirect]
    ctx = ssl.create_default_context()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(), *handlers)
    try:
        with op.open(urllib.request.Request(url, headers=UA), timeout=30) as r:
            return r.status, r.headers.get("Location"), r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location"), ""


res = {}
for pid in range(1, 101):
    st, loc, body = get(f"https://www.bagevm.com/aff.php?aff=1195&pid={pid}", follow=True)
    txt = re.sub(r"<[^>]+>", " ", body)
    oos = "Out of Stock" in txt
    # 判断是否落到某个分类页（有 "View Cart" 说明有效产品页）
    valid = "View Cart" in txt
    res[pid] = {"status": st, "valid": valid, "out_of_stock": oos}
    print(f"pid={pid:>3}  valid={valid}  oos={oos}")
    time.sleep(0.15)

with open(os.path.join(HERE, "data", "bagevm-pid验证.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
valid = [p for p, v in res.items() if v["valid"]]
print("\n有效 pid 数:", len(valid))
print("有效 pid:", valid)
