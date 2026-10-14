#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 BageVM 的整理结果写入 Obsidian 库（结构对齐 bytevirt vault）。

输入:
  outputs/bagevm-vps/data/bagevm-产品线数据.json     产品线 + 档位 + 库存 + 三网数据
  ~/Documents/Obsidian Vault/nodeseek-test/帖子/*     BageVM 来源帖（正文 + 评论）
输出:
  <vault>/bagevm/ 下的 厂商 / 产品线 / 套餐 / 库存 / 来源帖 / 数据库 / 首页.md
"""
import json, os, re, io, collections

VAULT = "/Users/peter/Documents/Obsidian Vault"
ROOT = os.path.join(VAULT, "bagevm")
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
POSTS_DIR = os.path.join(VAULT, "nodeseek-test", "帖子")

AFF = "1195"
VENDOR = "BageVM"
TODAY = "2026-10-14"

# ---------------- 产品线元数据（运营商适配 + 定位） ----------------
# star: (电信, 联通, 移动) 0-3；3=best 2=ok 1=avoid
META = {
 "hk-lite": dict(segment="亚太 · Lite", series="Lite", star=(1,1,2),
   note="比 Standard 便宜、流量更多（TINY 就给 4TB），国内延迟略高、带宽上限略低。社区实测用途是「跑 AI 用，流量也多，延迟也低，还能重置流量」。",
   src=["NS968629","NS960808","NS923398"]),
 "hk-std": dict(segment="亚太 · Standard", series="Standard", star=(1,1,3),
   note="全线对国内延迟最低的亚太节点：移动 TCPing 61ms，非晚高峰家宽单线程移动能跑到 855Mbps。原生 HK IP、解锁良好。代价是流量比 Lite 少（TINY 只有 2TB）。",
   src=["NS958987","NS967185","NS947804","NS929530"]),
 "jp": dict(segment="亚太 · 非Standard", series="非Standard", star=(1,1,2),
   note="Ryzen 7950X，GB6 单核 1658–1761，国际互联极强（到日本对端中位 4057Mbps）。但联通 TCPing 577ms 很差，晚高峰联通单线程归零。适合日本落地 / 国际中转 / 强单核。",
   src=["NS936936","NS937065","NS925802","NS920436"]),
 "jp-std": dict(segment="亚太 · Standard", series="Standard", star=(2,2,3),
   note="TCPing 三网 81/92/168ms 全线最低；晚高峰家宽测试是唯一三网单线程都没归零的节点。短板是 EPYC 7663 磁盘偏慢（4K 随机 45MB/s）。社区建议新购选 Standard。",
   src=["NS930864","NS940958","NS928577","NS946908","NS932145","NS928258"]),
 "sg": dict(segment="亚太 · 非Standard", series="非Standard", star=(1,1,2),
   note="与日本非 Standard 线同构（7950X，5000M/10000M 口）。IP 质量偏脏是通病，当前基本缺货。",
   src=[]),
 "sg-std": dict(segment="亚太 · Standard", series="Standard", star=(1,2,2),
   note="联通/电信延迟（284/321ms）明显优于非 Standard（531/404ms）。IP 质量偏脏但解锁优秀，移动方向延迟不错（106ms）。",
   src=["NS929735","NS929025","NS930216","NS946265","NS933606","NS929010","NS932211"]),
 "la": dict(segment="北美", series="BAGE 段", star=(1,1,1),
   note="GB6 单核 2273 全线最高，磁盘 SEQ1M 3216MB/s。商店页标称 AMD 7900，实测 9950X3D。三网 TCPing 233–242ms，无回国优化。",
   src=["NS922725","NS925025","NS955372"]),
 "la2": dict(segment="北美", series="FiberState 段", star=(1,1,1),
   note="上游 FiberState（AS26042），IP 质量报告显示流媒体/AI 全部原生解锁（非 DNS 解锁）。社区推荐作为美西落地 + 解锁首选。",
   src=["NS911593","NS922734","NS926112","NS930823","NS953936"]),
 "slc": dict(segment="北美", series="FiberState 段", star=(1,1,1),
   note="与 LA2 同上游同配置，可叠加折扣。缺点是位置偏：晚高峰移动单线程只有 25Mbps。",
   src=["NS942520"]),
 "de": dict(segment="欧洲", series="欧洲", star=(1,2,1),
   note="非晚高峰三网单线程 854/812/740 全线最均衡；欧洲对端中位 3860Mbps，适合欧洲大文件中转。晚高峰落差最大（电信 1 / 移动 49Mbps）。GB6 单核 2770。",
   src=["NS933135"]),
 "uk": dict(segment="欧洲", series="欧洲", star=(1,1,1),
   note="要英国原生 IP 就选它。缺点是 1Gbps 口封顶、盘偏慢（4K 69MB/s）、三网延迟都不好（移动 396ms）。不参加折扣码。",
   src=["NS952610","NS952760","NS939937","NS967037"]),
 "tw": dict(segment="亚太 · 台湾", series="HiNet VDS", star=None,
   note="唯一一条台湾线，卖点是中华电信 HiNet 动态 IP。当前缺货，下单页带专属促销码 7DEHA13B0O。",
   src=[]),
}

# 来源帖 → 产品线（按 ns_id）
POST_LINE = {
 "928577":"jp-std","940958":"jp-std","930864":"jp-std","946908":"jp-std","932145":"jp-std","928258":"jp-std",
 "936936":"jp","937065":"jp","925802":"jp","920436":"jp",
 "923398":"hk-lite","968629":"hk-lite","960808":"hk-lite","930620":"hk-lite","962368":"hk-lite",
 "967185":"hk-std","958987":"hk-std","959045":"hk-std","929530":"hk-std","947804":"hk-std",
 "929735":"sg-std","932211":"sg-std","929025":"sg-std","930216":"sg-std","946265":"sg-std",
 "933606":"sg-std","929010":"sg-std",
 "922725":"la","925025":"la","955372":"la",
 "911593":"la2","922734":"la2","926112":"la2","930823":"la2","953936":"la2",
 "942520":"slc",
 "933135":"de",
 "952610":"uk","952760":"uk","939937":"uk","967037":"uk",
 # 未关联单一产品线
 "938368":None,"920743":None,"947416":None,"913594":None,
}


def yaml_str(v):
    if v is None or v == "":
        return '""'
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        return str(v)
    s = str(v)
    if re.search(r'[:#\[\]{}",&*!|>%@`\'"]', s) or s != s.strip() or s.lower() in (
            "true", "false", "null", "yes", "no", "on", "off"):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def fm(d):
    out = []
    for k, v in d.items():
        if v is None or v == "":
            continue
        if isinstance(v, list):
            if not v:
                continue
            out.append(f"{k}:")
            for i in v:
                out.append(f"  - {yaml_str(i)}")
        else:
            out.append(f"{k}: {yaml_str(v)}")
    return "---\n" + "\n".join(out) + "\n---\n"


def wr(rel, text):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with io.open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def safe(s):
    return re.sub(r'[/\\:*?"<>|]', "-", s).strip()


def parse_post(path):
    t = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---", t, re.S)
    meta = {}
    if m:
        for line in m.group(1).split("\n"):
            mm = re.match(r"^([A-Za-z_]+):\s*(.*)$", line.strip())
            if mm:
                k, v = mm.group(1), mm.group(2).strip()
                if v.startswith('"') and v.endswith('"') and len(v) > 1:
                    v = v[1:-1]
                meta[k] = v
    body = t[m.end():] if m else t
    # 去掉“测试数据”结构化段落，只保留原帖正文 + 评论
    om = re.search(r"## 原帖正文\s*```text\s*([\s\S]*?)```", body)
    orig = om.group(1).strip() if om else ""
    cm = re.search(r"### 有信息量的评论\s*\n\s*([\s\S]*?)(?=<details>)", body)
    info_comments = cm.group(1).strip() if cm else ""
    return meta, orig, info_comments


# ---------------------------------------------------------------- 主流程
data = json.load(open(os.path.join(SRC, "bagevm-产品线数据.json"), encoding="utf-8"))
lines = data["lines"]

if os.path.isdir(ROOT):
    for d in ("厂商", "产品线", "套餐", "库存", "来源帖", "数据库"):
        p = os.path.join(ROOT, d)
        if os.path.isdir(p):
            for f in os.listdir(p):
                fp = os.path.join(p, f)
                if os.path.isfile(fp):
                    os.remove(fp)
os.makedirs(ROOT, exist_ok=True)

line_file = {l["key"]: safe(f"{VENDOR}-{l['name']}") for l in lines}
line_by_key = {l["key"]: l for l in lines}
stats = collections.Counter()
plan_rows = []
PLAN_FILE_BY_NAME = {}
PLAN_FILE_BY_NAME = {}

# ---- 1. 厂商
wr("厂商/BageVM.md", fm({
    "type": "vendor", "name": VENDOR, "title": VENDOR,
    "homepage": "https://www.bagevm.com/",
    "store_page": "https://www.bagevm.com/index.php/store",
    "classic_store": "https://www.bagevm.com/cart.php",
    "lg_entry": "http://lg.bagevm.net/",
    "affiliate_page": "https://www.bagevm.com/affiliates.php",
    "aff_param": AFF,
    "aff_link": f"https://www.bagevm.com/aff.php?aff={AFF}",
    "aff_template": f"https://www.bagevm.com/aff.php?aff={AFF}",
    "scrape_tool": "outputs/bagevm-vps/bagevm-store-scan.py",
    "scrape_note": "curl 直抓各 /index.php/store/<slug> 分类页；官网只公开月付价，年付价在购物车 JS 流里抓不到",
    "company": "BAGE CLOUD LLC",
    "asn": "AS63150（洛杉矶2 / 盐湖城 上游为 AS26042 FiberState）",
    "optimization": "全线无中国大陆优化（No China Mainland Optimization Guaranteed）",
    "payment": "支付宝 / PayPal / USDT（社区资料，以结账页为准）",
    "tags": ["vps", "vps/vendor"],
}) + f"""
# {VENDOR}

BageVM（**BAGE CLOUD LLC**）是一家全球大带宽云服务器提供商，主控面板为 **WHMCS + 自研 bage_cart 下单模板**。
覆盖 8 个国家/地区：中国香港、中国台湾、日本、新加坡、美国（洛杉矶 ×2 / 盐湖城）、德国、英国。

> **最重要的一条：BageVM 全线没有中国大陆优化**，官网每一条产品线都标注
> 「No China Mainland Optimization Guaranteed」。定位是**大带宽落地机 / 中转机 / 解锁机**，
> 不是回国优化机。社区（NS938368）评价：「国际优化的大带宽服务商，普遍提供 DNS 解锁，
> 长时间提供稳定服务，高质量回复工单，算得上小而美的 IDC」。

## 关键页面

| 用途 | 地址 |
|------|------|
| 首页 | <https://www.bagevm.com/> |
| 商店总入口 | <https://www.bagevm.com/index.php/store> |
| 传统购物车 | <https://www.bagevm.com/cart.php> |
| Looking Glass 聚合 | <http://lg.bagevm.net/> |
| 网络状态 | <https://www.bagevm.com/serverstatus.php>（需登录） |
| 公告 | <https://www.bagevm.com/index.php/announcements> |
| 推广计划 | <https://www.bagevm.com/affiliates.php> |

## 产品结构

产品 = **地区 × 系列**：

| 维度 | 取值 |
|------|------|
| 地区 | 中国香港（Standard / Lite）、日本（Standard / 非Standard）、新加坡（Standard / 非Standard）、美国洛杉矶、洛杉矶2、盐湖城、德国法兰克福、英国考文垂、中国台湾（Hinet VDS） |
| 系列 | **Standard**（EPYC 7663 + PCCWG/Telstra/Lumen/Retn/EIE 多上游）、**非Standard**（Ryzen 7950X + NTT/Cogent/Lumen/HE）、**Lite**（香港低价线）、**FiberState 段**（洛杉矶2 / 盐湖城）、**HiNet VDS**（台湾） |

> **选型主规律**：Standard 系列国内三网延迟明显低于非 Standard 系列（尤其移动、联通）；
> 非 Standard 系列胜在单核更强、国际互联更猛、口子更大（5000M / 10000M）。

## 推广链接格式

```
通用链接：https://www.bagevm.com/aff.php?aff={AFF}
```

- 面板为 WHMCS，推广走标准机制：`aff.php?aff=ID` 写入 `WHMCSAffiliateID` Cookie，之后下单计入推广。
- 官网产品页 URL 形如 `/index.php/store/<slug>`，`<slug>` 为**产品线**级（如 `los-angeles-servers`）；
  档位级 `/index.php/store/<slug>/<tier>` 会 302 回分类页，**没有 pid 级 aff 链接**。

## 价格调整记录

- 官网公告《Price Adjustment Notice》（2025-12-28）：因上游内存 / 硬盘 / 硬件成本上涨及长期亏损，
  **自 2026-01-01 起对部分套餐调价**，已存订单不受影响。
- 2026 中秋国庆活动：月付 8 折码 `2026OCTM`、年付 7 折码 `2026OCTY`（2026-09-14 ~ 10-01，仅新购）。
- 台湾 Hinet VDS 下单页当前挂促销码 `7DEHA13B0O`。

## 相关笔记

- 测试 IP 与 Looking Glass → [[BageVM-测试IP与LookingGlass]]
- 社交媒体账号 → [[BageVM-社交媒体账号]]
- 已收录产品线 → [[02 产品线库.base|产品线库]]
""")
stats["vendor"] += 1

# ---- 1b. 测试 IP / LG
lg_rows = "\n".join(
    f"| {l['name']} | {l['loc']} | <http://{l['lg']}> | <{l['order_url']}> |"
    for l in lines)
wr("厂商/BageVM-测试IP与LookingGlass.md", fm({
    "type": "vendor_info", "name": "BageVM 测试 IP 与 Looking Glass",
    "vendor": f"[[{VENDOR}]]", "kind": "test_ip",
    "lg_entry": "http://lg.bagevm.net/",
    "collected_at": TODAY,
    "tags": ["vps", "vps/vendor"],
}) + f"""
# BageVM 测试 IP 与 Looking Glass

BageVM **不单独公布测试 IP**，而是给每个节点提供一个 Looking Glass 网页（可 ping / traceroute / 测速）。
本笔记汇总 12 个节点的入口（{TODAY} 抓取）。

聚合入口：<http://lg.bagevm.net/>（顶部可切换全部节点）

| 节点 | 地区 | Looking Glass | 官网产品页 |
|------|------|---------------|-----------|
{lg_rows}

## 说明

- 上表 LG 地址来自各官网分类页的「Looking Glass / 服务器测试」按钮。
- 每个 LG 是独立的 Vue 单页应用；`lg.bagevm.net` 的 JS 包里内置了全部节点子域
  （含 `lg-twa.bagevm.net` 台湾节点）。
- 测速建议在**晚高峰（北京时间 20:00–23:30）**再做一次 —— BageVM 各节点晚高峰落差普遍较大。
- 各节点 IP 段（社区 HardwareQuality 报告观测，已脱敏）：
  香港/日本 常见 `209.33.*`（广播 IP，注册地 HK）；洛杉矶 `167.253.*`；
  洛杉矶2 / 盐湖城 `166.0.*`（FiberState）；新加坡 `77.93.*` / `85.149.*`；
  德国 `193.160.*`；英国 `51.241.*`；香港 Lite `103.219.*`。
""")
stats["vendor"] += 1

# ---- 1c. 社交媒体
wr("厂商/BageVM-社交媒体账号.md", fm({
    "type": "vendor_info", "name": "BageVM 社交媒体账号",
    "vendor": f"[[{VENDOR}]]", "kind": "social",
    "collected_at": TODAY,
    "tags": ["vps", "vps/vendor"],
}) + f"""
# BageVM 社交媒体账号

来源：官网首页 / 页脚 / 联系页 + 公开可访问性探测。（{TODAY}）

## 一、存在（归属待确认）

| 平台 | 名称 | 地址 | 规模 | 说明 |
|------|------|------|------|------|
| Telegram 频道 | BageVM补货监控 | <https://t.me/bagevm> | 97 subscribers | 补货监控频道，名称与 BageVM 直接相关；官网未挂链接，**无法确认是否为官方运营** |
| Telegram | @bagevmchat | <https://t.me/bagevmchat> | — | 账号页存在但无成员数据，归属待确认 |
| Telegram | @BageVMGroup | <https://t.me/BageVMGroup> | — | 账号页存在但无成员数据，归属待确认 |
| Telegram | @bagevmofficial | <https://t.me/bagevmofficial> | — | 账号页存在但无成员数据，归属待确认 |

## 二、确认不存在

- **X / Twitter**（`@bagevm` / `@BageVM`）：均返回 404。
- 官网首页与页脚**未挂任何社交账号链接**，只有 Store / About / Contact / Ticket / 公告等站内入口。

## 三、官方沟通渠道

| 渠道 | 地址 | 用途 |
|------|------|------|
| 工单系统 | <https://www.bagevm.com/submitticket.php> | 官方支持（General / Billing / Abuse 分队列） |
| 联系页 | <https://www.bagevm.com/contact.php> | 同上 |
| 公告 | <https://www.bagevm.com/index.php/announcements> | 调价 / 迁移通知 |

## 四、公司信息

- 主体：**BAGE CLOUD LLC**
- ASN：**AS63150**（洛杉矶2 / 盐湖城 上游为 AS26042 FiberState）
- 支付：社区资料称支持支付宝 / PayPal / USDT（官网未公开列出，以结账页为准）
- 面板：WHMCS + 自研 bage_cart 下单模板

> 结论：BageVM 的公开社交运营**很弱** —— 官网不挂社交链接，只有一个疑似官方的补货监控 TG 频道；
> 主要沟通渠道是**工单**（社区反馈「高质量回复工单」）。
""")
stats["vendor"] += 1

# ---- 2. 产品线 + 套餐
for l in lines:
    k = l["key"]
    meta = META[k]
    lf = line_file[k]
    tiers = [t for t in l["tiers"]]
    monthly_from = min(t[6] for t in tiers)
    n_buy = sum(1 for t in tiers if l["stock"].get(t[0]) != 0)
    line_stock = "在售" if n_buy else "缺货"

    best = [x for x, s in zip(("中国电信", "中国联通", "中国移动"), meta["star"]) if s == 3] if meta["star"] else []
    ok = [x for x, s in zip(("中国电信", "中国联通", "中国移动"), meta["star"]) if s == 2] if meta["star"] else []
    avoid = [x for x, s in zip(("中国电信", "中国联通", "中国移动"), meta["star"]) if s == 1] if meta["star"] else []
    tcp = l.get("tcp")
    tcp_txt = f"移动 {tcp[0]}　|　联通 {tcp[1]}　|　电信 {tcp[2]}" if tcp else "无数据"

    wr(f"产品线/{lf}.md", fm({
        "type": "product_line", "name": l["name"], "vendor": f"[[{VENDOR}]]",
        "region": l["loc"], "cpu": l["cpu"], "upstream": l["carriers"],
        "segment": meta["segment"], "series": meta["series"],
        "store": l["store"], "store_url": l["order_url"],
        "lg": l["lg"], "lg_url": f"http://{l['lg']}",
        "price_from": monthly_from, "price_from_cycle": "月付",
        "tier_count": len(tiers), "stock": line_stock,
        "tcp_test": tcp_txt,
        "isp_best": best, "isp_ok": ok, "isp_avoid": avoid,
        "isp_basis": ("实测" if tcp else "无数据"),
        "isp_note": meta["note"], "isp_source": meta["src"],
        "aff_link": l["aff_url"],
        "tags": ["vps", "vps/product"],
    }) + f"""
# {l['name']}

**{l['loc']} · {l['cpu']} · {l['carriers']}**（{meta['segment']}，流量计费）

{meta['note']}

| 项 | 值 |
|----|----|
| 地区 | {l['loc']} |
| CPU | {l['cpu']} |
| 上游线路 | {l['carriers']} |
| 定位 | {meta['segment']} |
| 系列 | {meta['series']} |
| 起价 | ${monthly_from}/月 |
| 档位数 | {len(tiers)} |
| 当前库存 | {line_stock} |
| 三网 TCPing | {tcp_txt} |
| Looking Glass | <http://{l['lg']}> |

## 适用运营商

| 档 | 运营商 |
|----|--------|
| ★★★ 推荐 | {('、'.join(best)) or '—'} |
| ★★☆ 可用 | {('、'.join(ok)) or '—'} |
| ★☆☆ 不建议 | {('、'.join(avoid)) or '—'} |
| 证据强度 | {('实测' if tcp else '无数据')} |

{meta['note']}

> **注意**：BageVM 全线无中国大陆优化，上表星级只反映「国内连过去的相对体验」，
> 不代表有回国优化保证。

证据帖：{('、'.join(meta['src'])) or '—'}

## 购买链接

<{l['aff_url']}>

## 档位

见 [[03 套餐价格表.base|套餐价格表]]（筛选 `product_name` 为该产品线）。

## 抓取入口

<{l['order_url']}>
""")
    stats["line"] += 1

    # 套餐
    for (name, c, r, d, bw, tf, mo, ap, ao) in tiers:
        tname = f"{l['name']} - {name}"
        pf = safe(f"{VENDOR}-{l['name']}-{name}")
        stock_n = l["stock"].get(name)
        if stock_n == 0:
            stock_cn, stock_raw = "缺货", "0 Available"
        elif isinstance(stock_n, int) and stock_n > 0:
            stock_cn, stock_raw = "在售", f"{stock_n} Available"
        else:
            stock_cn, stock_raw = "在售", "—"
        price_usd = mo
        traffic_gb = None
        mm = re.match(r"([\d.]+)\s*(TB|GB)", tf)
        if mm:
            traffic_gb = int(float(mm.group(1)) * 1024) if mm.group(2) == "TB" else int(float(mm.group(1)))
        row = dict(
            type="plan", name=tname, vendor=f"[[{VENDOR}]]", product=f"[[{lf}]]",
            product_name=l["name"], region=l["loc"], segment=meta["segment"], series=meta["series"],
            spec_cpu=f"{c}C / {r}G / {d}G", spec_traffic=f"{tf} @{bw}Mbps",
            spec_ip="1×IPv4 & 1×IPv6",
            cpu_cores=c, ram_gb=r, disk_gb=d, bandwidth_mbps=bw, traffic_gb=traffic_gb,
            price=mo, unit="月付", price_usd=price_usd,
            annual_price=ap if ap else (ao if ao else None),
            stock=stock_cn, stock_raw=stock_raw, buyable="是" if stock_cn == "在售" else "否",
            aff_link=l["aff_url"], store_url=l["order_url"],
        )
        annual_txt = (f"${ap}（75折后）" if ap else (f"${ao}（原价）" if ao else "—"))
        wr(f"套餐/{pf}.md", fm({**row, "tags": ["vps", "vps/plan"]}) + f"""
# {tname}

所属产品线：[[{lf}]]　|　地区：{l['loc']}　|　定位：{meta['segment']}

| 规格 | 值 |
|------|----|
| CPU / 内存 / 硬盘 | {c}C / {r}G / {d}G |
| 流量 / 带宽 | {tf} @{bw}Mbps |
| IP | 1×IPv4 & 1×IPv6 |
| 月付 | ${mo} |
| 年付 | {annual_txt} |
| 库存 | {stock_cn}（{stock_raw}） |
| 可下单 | {row['buyable']} |

## 推广链接

<{l['aff_url']}>

## 抓取入口

<{l['order_url']}>
""")
        stats["plan"] += 1
        plan_rows.append(row)
        PLAN_FILE_BY_NAME[row["name"]] = pf

# ---- 3. 库存快照
inv = collections.defaultdict(list)
for r in plan_rows:
    inv[r["product_name"]].append(r)
rows_md = []
for pn, rs in inv.items():
    c = collections.Counter(r["stock"] for r in rs)
    rows_md.append(f"| {pn} | {len(rs)} | {c.get('在售',0)} | {c.get('缺货',0)} |")
tot = len(plan_rows)
n_ok = sum(1 for r in plan_rows if r["stock"] == "在售")
n_out = sum(1 for r in plan_rows if r["stock"] == "缺货")
wr(f"库存/{TODAY} {VENDOR} 库存快照.md", fm({
    "type": "stock", "vendor": f"[[{VENDOR}]]", "vendor_name": VENDOR,
    "scraped_at": f"{TODAY} 09:00",
    "source": "https://www.bagevm.com/index.php/store",
    "total_plans": tot, "in_stock": n_ok, "sold_out": n_out,
    "buyable": n_ok, "no_order": n_out,
    "tags": ["vps", "vps/stock"],
}) + f"""
# {TODAY} {VENDOR} 库存快照

抓取时间：{TODAY} 09:00　|　来源：<https://www.bagevm.com/index.php/store>

**共 {tot} 个档位：在售 {n_ok} · 缺货 {n_out}**

> 说明：BageVM 官网**只在部分档位显示库存数量**（`N Available`），其余档位不显示数量，
> 按「能下单即视为在售」处理。

## 按产品线

| 产品线 | 档位 | 在售 | 缺货 |
|--------|------|------|------|
{chr(10).join(rows_md)}

## 缺货档位明细

{chr(10).join(f"- [[{PLAN_FILE_BY_NAME.get(r['name'], safe(VENDOR + '-' + r['name']))}|{r['name']}]]（{r['product_name']}，月付 ${r['price']}）" for r in plan_rows if r['stock'] == '缺货') or '（无）'}

## 说明

横向对比请按 `scraped_at` 排序查看 [[05 库存快照.base|库存快照]]。
""")
stats["stock"] += 1

# ---- 4. 来源帖
for fn in sorted(os.listdir(POSTS_DIR)):
    if "bage" not in fn.lower() or not fn.endswith(".md"):
        continue
    meta, orig, info_comments = parse_post(os.path.join(POSTS_DIR, fn))
    if meta.get("vendor") != VENDOR:
        continue
    ns_id = str(meta.get("ns_id", ""))
    title = meta.get("title", fn)
    url = meta.get("source", "")
    linked = POST_LINE.get(ns_id)
    fname = safe(f"NS{ns_id} {title[:40]}")
    cm = re.search(r"comments_fetched:\s*(\d+)", open(os.path.join(POSTS_DIR, fn), encoding="utf-8").read())
    wr(f"来源帖/{fname}.md", fm({
        "type": "source_post", "name": title, "title": title, "url": url,
        "ns_id": ns_id, "vendor": f"[[{VENDOR}]]",
        "product": f"[[{line_file[linked]}]]" if linked else None,
        "product_name": line_by_key[linked]["name"] if linked else None,
        "category": "测评" if "NQ" in title.upper() or "TQ" in title.upper() or "测评" in title else "讨论",
        "author": meta.get("author"),
        "post_time": meta.get("post_time"),
        "comment_count": int(cm.group(1)) if cm else None,
        "sentiment": meta.get("comment_sentiment"),
        "regions": re.findall(r'"([A-Z]{2})"', meta.get("regions", "")),
        "tags": ["vps", "vps/source"],
    }) + f"""
# {title}

来源：<{url}>　|　帖子 ID：`{ns_id}`
{'关联产品线：[[%s]]　' % line_file[linked] if linked else '关联产品线：—　'}｜　作者：{meta.get('author','—')}　|　发布：{meta.get('post_time','—')}

## 原帖正文

{orig[:4000] if orig else '（正文为图片 / 无文本）'}

## 有信息量的评论

{info_comments if info_comments else '（无）'}
""")
    stats["post"] += 1

print(json.dumps(stats, ensure_ascii=False))
print("产品线:", len(lines), "套餐:", len(plan_rows))
