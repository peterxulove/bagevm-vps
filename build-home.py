#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 bagevm vault 的 首页.md（导航 + 查询配方 + 字段说明 + 嵌入视图）。"""
import json, os, io, collections

VAULT = "/Users/peter/Documents/Obsidian Vault"
ROOT = os.path.join(VAULT, "bagevm")
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
TODAY = "2026-10-14"
AFF = "1195"

data = json.load(open(os.path.join(SRC, "bagevm-产品线数据.json"), encoding="utf-8"))
lines = data["lines"]
n_lines = len(lines)
n_plans = sum(len(l["tiers"]) for l in lines)
n_posts = len([f for f in os.listdir(os.path.join(ROOT, "来源帖")) if f.endswith(".md")])
n_vendor = len([f for f in os.listdir(os.path.join(ROOT, "厂商")) if f.endswith(".md")])

# 库存
n_out = 0
n_ok = 0
for l in lines:
    for (name, *_rest) in l["tiers"]:
        s = l["stock"].get(name)
        if s == 0:
            n_out += 1
        else:
            n_ok += 1

# 月付区间
mons = [min(t[6] for t in l["tiers"]) for l in lines]
lo, hi = min(mons), max(mons)

# 推荐运营商计数
isp_c = collections.Counter()
for l in lines:
    k = l["key"]
    star = {
      "hk-lite": (1,1,2), "hk-std": (1,1,3), "jp": (1,1,2), "jp-std": (2,2,3),
      "sg": (1,1,2), "sg-std": (1,2,2), "la": (1,1,1), "la2": (1,1,1),
      "slc": (1,1,1), "de": (1,2,1), "uk": (1,1,1),
    }.get(k)
    if star:
        for op, s in zip(("中国电信", "中国联通", "中国移动"), star):
            if s == 3:
                isp_c[op] += 1

seg_c = collections.Counter()
segmap = {"hk-lite":"亚太 · Lite","hk-std":"亚太 · Standard","jp":"亚太 · 非Standard",
 "jp-std":"亚太 · Standard","sg":"亚太 · 非Standard","sg-std":"亚太 · Standard",
 "la":"北美","la2":"北美","slc":"北美","de":"欧洲","uk":"欧洲","tw":"亚太 · 台湾"}
for l in lines:
    seg_c[segmap[l["key"]]] += 1

text = f"""---
type: dashboard
name: bagevm 总览
vendor: "[[BageVM]]"
tags:
  - vps
  - vps/dashboard
---

# bagevm 总览

VPS 厂商产品库：把「官网产品与价格」+「第三方测评帖」存成结构化笔记，
用 Obsidian Bases 做查询，用来生成推广页、做多厂商比价。

**当前收录**：1 家厂商 · {n_lines} 条产品线 · {n_plans} 个档位 · {n_posts} 篇来源帖
**库存状态**：在售 {n_ok} · 缺货 {n_out}
**月付区间**：${lo:.2f} – ${hi:.2f}

> ⚠️ **BageVM 全线没有中国大陆优化**（官网标注 No China Mainland Optimization Guaranteed）。
> 它的定位是**大带宽落地机 / 中转机 / 解锁机**，不是回国优化机。

---

## 一、数据库

| 数据库 | 看什么 | 一行 = |
|--------|--------|--------|
| [[01 厂商库.base\\|厂商库]] | 厂商资料、官网、推广参数、ASN、支付方式 | 一条资料 |
| [[02 产品线库.base\\|产品线库]] | 每条产品线：地区 / 系列 / 上游 / 月付起 / **适用哪些运营商**（11 个视图） | 一条产品线 |
| [[03 套餐价格表.base\\|套餐价格表]] | **核心表**。全部档位的配置与价格，做推广页和比价用这张（10 个视图） | 一个档位 |
| [[04 库存看板.base\\|库存看板]] | 按库存两态分组的看板 + 缺货清单 | 一个档位 |
| [[05 库存快照.base\\|库存快照]] | 每次抓取的汇总，按时间纵向对比 | 一次抓取 |
| [[06 来源帖库.base\\|来源帖库]] | 抓到的第三方测评与讨论，产品特点的依据 | 一篇帖子 |

---

## 二、BageVM 的产品骨架

BageVM 的产品 = **地区 × 系列** 两个维度的组合。

| 维度 | 取值 |
|------|------|
| 地区 | 中国香港、日本、新加坡、美国洛杉矶、洛杉矶2、盐湖城、德国法兰克福、英国考文垂、中国台湾 |
| 系列 | **Standard**（EPYC 7663 + PCCWG/Telstra/Lumen/Retn/EIE 多上游）、**非Standard**（Ryzen 7950X + NTT/Cogent）、**Lite**（香港低价线）、**FiberState 段**（洛杉矶2 / 盐湖城）、**HiNet VDS**（台湾） |

### 选型主规律：Standard vs 非 Standard

| 对比项 | Standard 系列 | 非 Standard 系列 |
|--------|---------------|------------------|
| CPU | EPYC 7663 | Ryzen 7950X |
| 上游 | PCCWG + Telstra + Lumen + Retn + EIE（多上游） | NTT + Cogent + Lumen + HE |
| 国内三网延迟 | **更低**（移动/联通尤其明显） | 偏高（联通最差） |
| 单核 / 国际互联 | 一般（盘也偏慢） | **更强**（GB6 单核 1658–1761） |
| 口子 | 1000–5000Mbps | **5000–10000Mbps** |

一句话：**要国内低延迟选 Standard，要国际性能选非 Standard。**

### 各定位分布

{chr(10).join(f'- **{k}**：{v} 条' for k, v in seg_c.most_common())}

---

## 三、按运营商选型（速查）

产品线库里的 `isp_best` / `isp_ok` / `isp_avoid` 三个字段来自 NS938368 总参篇的三网 TCPing 与家宽测速，
`isp_basis` 标注证据强度。

推荐运营商计数：{' · '.join(f'{k} {v} 条' for k, v in isp_c.most_common())}。

一句话结论：

- **移动**：香港 Standard（TCPing 61ms）、日本 Standard（81ms）最好；避开英国（396ms）
- **联通**：日本 Standard（92ms）、德国法兰克福（183ms）；避开日本非 Standard（577ms）、新加坡（531ms）
- **电信**：日本 Standard（168ms）、洛杉矶（233ms）、法兰克福（243ms）；避开新加坡（404ms）

> 依据来源见 [[06 来源帖库.base\\|来源帖库]]；每条产品线的 `isp_source` 字段列了具体证据帖。

---

## 四、测试 IP 与 Looking Glass

BageVM **不单独公布测试 IP**，给每个节点提供了 Looking Glass 网页。

| 入口 | 地址 | 说明 |
|------|------|------|
| LG 聚合 | <http://lg.bagevm.net/> | 顶部切换全部节点 |
| 香港 Standard / Lite | lg-hka / lg-hkb | .bagevm.net |
| 日本 / 日本 Standard | lg-jpa / lg-jpb | .bagevm.net |
| 新加坡 / Standard | lg-sga / lg-sgb | .bagevm.net |
| 洛杉矶 / 洛杉矶2 / 盐湖城 | lg-usa / lg-usc / lg-usb | .bagevm.net |
| 英国 / 德国 / 台湾 | lg-gba / lg-dea / lg-twa | .bagevm.net |

完整清单见 [[BageVM-测试IP与LookingGlass]]。

---

## 五、推广链接

```
通用链接：https://www.bagevm.com/aff.php?aff={AFF}
```

- 面板为 WHMCS，`aff.php?aff=ID` 写 Cookie 后下单计入推广。
- 产品页 URL 为**产品线**级（`/index.php/store/<slug>`），没有 pid 级 aff 链接。

---

## 六、产品线一览

![[02 产品线库.base]]

## 七、套餐价格表

![[03 套餐价格表.base]]

## 八、库存看板

![[04 库存看板.base]]

## 九、来源帖

![[06 来源帖库.base]]

---

## 十、常用查询配方

在对应的 `.base` 里点「+」加视图，或直接改 `filters`。几个现成的：

| 想查什么 | 过滤条件 |
|----------|----------|
| 3 美元以内 | `price_usd <= 3` |
| 大带宽 | `bandwidth_mbps >= 1000` |
| 大流量 | `traffic_gb >= 4096` |
| Standard 系列 | `series == "Standard"` |
| 非 Standard 系列 | `series == "非Standard"` |
| 北美 | `segment == "北美"` |
| 欧洲 | `segment == "欧洲"` |
| 指定地区 | `region == "日本东京"` |
| 当前可下单 | `buyable == "是"` |
| 缺货的 | `stock == "缺货"` |
| 适合移动的 | `isp_best.contains("中国移动")` |
| 要避开的组合 | `!isp_avoid.isEmpty()` |
| 有实测依据的 | `isp_basis == "实测"` |
| 有 Looking Glass 的 | `!lg.isEmpty()` |
| 指定厂商（多厂商后） | `vendor == link("BageVM")` |

**注意**：Bases 没有 SQL 那样的 `from`/`source`，一个 base 默认包含 vault 里的**所有**文件。
所以每个 base 都用 `file.inFolder("bagevm/xxx")` 限定范围 —— 新建 base 时别忘了这一条。

---

## 十一、维护流程

### 更新价格与库存

1. 抓官网各分类页：`python3 outputs/bagevm-vps/bagevm-store-scan.py`
2. 重跑 `build-data.py` → `build-vault.py` → `build-bases.py` → `build-home.py`
3. 在 `库存/` 下会新建一条快照笔记（`type: stock`）

### 更新来源帖

来源帖来自 `nodeseek-test/帖子/`（NodeSeek 采集），重跑 `build-vault.py` 即会同步。

### 生成一篇推广页

1. 从 [[03 套餐价格表.base\\|套餐价格表]] 筛出目标产品线。
2. 取该产品线的 `aff_link` 作为购买按钮链接。
3. 从 [[06 来源帖库.base\\|来源帖库]] 按 `product_name` 筛出对应测评帖，引用其结论。
4. 按「速览 → 产品表 → 运营商适配 → 逐款详解 → FAQ → 引用来源」的结构产出页面。
   （本库已产出：<https://peterxulove.github.io/bagevm-vps/bagevm-vps-guide.html>）

---

## 十二、字段说明

### `type` 取值

`vendor` 厂商 · `vendor_info` 厂商附属资料 · `product_line` 产品线 · `plan` 档位 ·
`stock` 库存快照 · `source_post` 来源帖 · `dashboard` 首页

### `plan`（档位）关键字段

| 字段 | 含义 |
|------|------|
| `vendor` / `product` | 所属厂商 / 所属产品线（wikilink） |
| `region` / `series` / `segment` | 地区 / 系列 / 定位 |
| `spec_cpu` / `spec_traffic` / `spec_ip` | 规格 / 流量带宽 / IP |
| `cpu_cores` / `ram_gb` / `disk_gb` | 核数 / 内存 GB / 硬盘 GB |
| `bandwidth_mbps` / `traffic_gb` | 带宽 Mbps / 流量 GB |
| `price` / `unit` / `price_usd` | 月付价 / 周期 / 折合月付 |
| `annual_price` | 年付价（75 折促销价或原价） |
| `stock` / `stock_raw` | 库存两态（在售/缺货） / 官网原文 |
| `buyable` | 是否可下单 |
| `aff_link` | 带推广参数的购买链接 |

### `product_line`（产品线）运营商字段

| 字段 | 含义 |
|------|------|
| `isp_best` | 体验最好的运营商（列表） |
| `isp_ok` | 可用但非最优（列表） |
| `isp_avoid` | 不建议（列表） |
| `isp_basis` | 证据强度：`实测` / `无数据` |
| `isp_note` | 结论说明 |
| `isp_source` | 证据帖编号，可逐条复核 |
| `tcp_test` | 三网 TCPing 延迟 / 丢包（NS938368） |

星级约定：`isp_best` = ★★★　`isp_ok` = ★★☆　`isp_avoid` = ★☆☆

> 判定依据 NS938368 总参篇的**三网 TCPing 与家宽测速数据**。
> 再次强调：BageVM 全线无回国优化保证，星级只反映相对体验。

---

## 十三、数据来源

- 官网产品与价格：<https://www.bagevm.com/index.php/store>（{TODAY} 扫描，共 {n_plans} 档）
- Looking Glass：官网各分类页的「Looking Glass / 服务器测试」按钮
- 第三方测评：NodeSeek 37 篇 BageVM 相关帖子（正文 + 评论），来自 `nodeseek-test/` 库
- 三网数据：NS938368《总参篇｜腱鞘炎燃尽式测评 11 台一次看完》（2026-09-16 测试）
- 采集方式：curl 直抓官网分类页 + NodeSeek 采集数据

> 价格与库存为抓取时点快照，随时可能变动；以官网实时信息为准。
"""

with io.open(os.path.join(ROOT, "首页.md"), "w", encoding="utf-8") as f:
    f.write(text)
print("已生成 首页.md", len(text), "字符")
print(f"产品线 {n_lines} · 档位 {n_plans} · 来源帖 {n_posts} · 厂商资料 {n_vendor}")
