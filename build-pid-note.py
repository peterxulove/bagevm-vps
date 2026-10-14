#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 Obsidian 笔记：BageVM pid 对照表（厂商/ 下）。"""
import json, os, io

VAULT = "/Users/peter/Documents/Obsidian Vault"
ROOT = os.path.join(VAULT, "bagevm")
HERE = os.path.dirname(os.path.abspath(__file__))
TODAY = "2026-10-14"
AFF = "1195"
AFF_BASE = f"https://www.bagevm.com/aff.php?aff={AFF}"

data = json.load(open(os.path.join(HERE, "data", "bagevm-产品线数据.json"), encoding="utf-8"))
full = json.load(open(os.path.join(HERE, "data", "bagevm-pid全量映射.json"), encoding="utf-8"))

# 53 个在售档位（来自产品线数据）
tier_rows = []
for l in data["lines"]:
    for t in l["tiers"]:
        name, c, r, d, bw, tf, mo = t[0], t[1], t[2], t[3], t[4], t[5], t[6]
        pid = t[9] if len(t) > 9 else None
        st = l["stock"].get(name)
        stock = "缺货" if st == 0 else ("在售" if st is not None else "在售")
        tier_rows.append((pid or 0, f'{l["name"]} - {name}', f"{c}C/{r}G/{d}G", f"{tf}@{bw}Mbps", mo, stock, l["name"]))
tier_rows.sort()

# 额外产品（有货但不在 53 档里）
KNOWN = {t[0] for t in tier_rows}
extra_instock = []
extra_oos = []
for k, v in sorted(full.items(), key=lambda kv: int(kv[0])):
    pid = int(k)
    if pid in KNOWN:
        continue
    if v["kind"] == "instock":
        extra_instock.append((pid, v.get("name", "").strip()[:70]))
    elif v["kind"] == "oos":
        extra_oos.append((pid, v.get("slug", "")))


def fm(d):
    out = []
    for k, v in d.items():
        if isinstance(v, list):
            out.append(f"{k}:")
            for i in v:
                out.append(f"  - {i}")
        else:
            out.append(f"{k}: {v}")
    return "---\n" + "\n".join(out) + "\n---\n"


rows_md = "\n".join(
    f'| {pid} | [[BageVM-{name.replace(" - ", "-")}\\|{name}]] | {spec} | {tr} | ${mo} | {stock} | <{AFF_BASE}&pid={pid}> |'
    for pid, name, spec, tr, mo, stock, _ln in tier_rows)

text = fm({
    "type": "vendor_info",
    "name": "BageVM pid 对照表",
    "vendor": "[[BageVM]]",
    "kind": "pid_map",
    "collected_at": TODAY,
    "aff_base": AFF_BASE,
    "aff_template": f"{AFF_BASE}&pid={{pid}}",
    "tags": ["vps", "vps/vendor"],
}) + f"""
# BageVM pid 对照表

BageVM 面板是 WHMCS，**推广链接支持档位级 `pid` 参数**：

```
通用链接：{AFF_BASE}
档位级  ：{AFF_BASE}&pid=<pid>     # 302 到 cart.php?a=add&pid=<pid>，直达该档位
```

pid 来源：{TODAY} 遍历 1–110，用「加入购物车 → 配置页」读出的**真实产品名**（`cart.php?a=add&pid=N`
命中时跳 `confproduct` 且页面显示产品名；缺货时 302 回 `/store/<分类>/<档位>`；无效 pid 回落到分类首页）。

## 一、在售 53 档（与 [[03 套餐价格表.base|套餐价格表]] 一一对应）

| pid | 档位 | 规格 | 流量/带宽 | 月付 | 库存 | 推广链接 |
|-----|------|------|-----------|------|------|----------|
{rows_md}

> 每篇 [[02 产品线库.base|产品线]] / [[03 套餐价格表.base|套餐]] 笔记的 `aff_link` 字段已带对应 pid。

## 二、其他在售产品（不在上面 53 档里）

| pid | 产品 | 说明 |
|-----|------|------|
{chr(10).join(f'| {p} | {n} | <{AFF_BASE}&pid={p}> |' for p, n in extra_instock) or '| — | — | — |'}

## 三、已下架 / 缺货的历史产品（保留 pid 备查）

这些 pid 仍有效但当前缺货，多为**隐藏档位**与**闪购（flash-sales）**产品，历史上架过，
适合盯补货 / 对比价格时参考：

| pid | 产品（官网 slug） |
|-----|------------------|
{chr(10).join(f'| {p} | `{s}` |' for p, s in extra_oos)}

> 其中 `flash-sales/*` 是节日闪购档（双十一、黑五、新年等），`*/min`、`*/min-1`、`*/min-2`
> 是比 TINY 更低的隐藏小档，`germany-servers-strong-*` 是德国「Strong」隐藏线。
> 这些产品**不出现在官网分类页**，只能通过 pid 直达。

## 四、抓取方法（可复跑）

```bash
cd outputs/bagevm-vps
python3 bagevm-pid-full.py        # 遍历 pid 1-110，读真实产品名 -> data/bagevm-pid全量映射.json
python3 bagevm-pid-scan.py        # 从各商店页 Order Now 按钮的 id="productN-order-button" 提取 pid
```

## 相关

- 厂商资料 → [[BageVM]]
- 套餐价格表 → [[03 套餐价格表.base|套餐价格表]]（含「pid 对照」视图）
"""

with io.open(os.path.join(ROOT, "厂商", "BageVM-pid对照表.md"), "w", encoding="utf-8") as f:
    f.write(text)
print("已生成 厂商/BageVM-pid对照表.md", len(text), "字符")
print(f"在售 {len(tier_rows)} 档 · 其他在售 {len(extra_instock)} · 历史/缺货 {len(extra_oos)}")
