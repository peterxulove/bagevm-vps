# bagevm-vps

BageVM（bagevm.com · BAGE CLOUD LLC）VPS 全产品线推荐与选购指南

- 在线页面（GitHub Pages）：https://peterxulove.github.io/bagevm-vps/bagevm-vps-guide.html
- 在线页面（Google Sites，嵌入上面那页）：https://sites.google.com/view/bagevm-vps
- 一分钟选型结论（Markdown）：[bagevm-一分钟选型结论.md](bagevm-一分钟选型结论.md)
- 完整页 Markdown 版：[bagevm-vps-guide.md](bagevm-vps-guide.md)

## 内容

BageVM 12 条产品线、8 个国家/地区节点的线路与价格梳理：

- **核心结论：BageVM 全线无中国大陆优化**（官网标注 No China Mainland Optimization Guaranteed），定位是大带宽落地机 / 中转机 / 解锁机
- 「Standard 系列（EPYC 7663 + 多上游）」vs「普通系列（Ryzen 7950X + NTT/Cogent）」的国内三网延迟差异
- 按中国电信 / 联通 / 移动三大运营商分别给选型建议
- 12 个节点的 Looking Glass 测试入口清单
- 各产品线的规格、月付/年付价、库存表
- 香港 / 日本 / 新加坡 / 洛杉矶×2 / 盐湖城 / 德国 / 英国 / 台湾分节点详解

数据来自 BageVM 官网全量产品表（2026-10-14 扫描）+ NodeSeek 社区 37 篇实测帖子的正文与评论，均已标注来源。

> 价格与库存为抓取时点快照，随时可能变动，以官网实时信息为准。
> 页内购买链接含推广参数（aff=1195）**并带档位 pid**：`aff.php?aff=1195&pid=NNN`，点击直达对应档位。
> 完整 pid 对照见 [Obsidian 库 `厂商/BageVM-pid对照表.md`](file:///Users/peter/Documents/Obsidian%20Vault/bagevm/厂商/BageVM-pid对照表.md)。

## 档位 pid（推广链接参数）

BageVM 面板是 WHMCS，`aff.php?aff=1195&pid=<pid>` 会 302 到 `cart.php?a=add&pid=<pid>`，直达该档位。
pid 已通过遍历 1–110 逐个核对（用「加入购物车 → 配置页」读出真实产品名）：

- **在售 53 档**全部带 pid（见 `data/bagevm-产品线数据.json` 每个档位元组第 10 位）
- 另发现 **5 个其他在售产品**：IPv6 地址租赁(44)、IPv4 地址租赁(95)、GDCM-1000M(94)、盐湖城 MAX(96)、IP Transit(97)
- 以及 **29 个历史/缺货 pid**（隐藏 `min` 档、德国 Strong 线、`flash-sales/*` 节日闪购档）

脚本：`bagevm-pid-scan.py`（从商店页按钮 id 提取）、`bagevm-pid-full.py`（遍历 1–110 读产品名）、`build-pid-note.py`（生成对照表笔记）

## 已回写的 Obsidian 库

整理结果同步写入了 Obsidian 库 `~/Documents/Obsidian Vault/bagevm/`（结构对齐 `bytevirt/`）：

| 目录 | 数量 | 内容 |
|------|------|------|
| `首页.md` | 1 | 总览 dashboard（导航 + 查询配方 + 字段说明 + 嵌入视图） |
| `厂商/` | 3 | BageVM 厂商资料、测试 IP 与 Looking Glass、社交媒体账号 |
| `产品线/` | 12 | 每条产品线：地区 / 系列 / 上游 / 三网 TCPing / 运营商适配 / 推广链接 |
| `套餐/` | 53 | 每个档位：规格 / 流量带宽 / 月付 / 年付 / 库存 / 推广链接 |
| `库存/` | 1 | 2026-10-14 库存快照 |
| `来源帖/` | 37 | NodeSeek 来源帖（正文 + 有信息量的评论） |
| `数据库/` | 6 | 6 个 `.base`：厂商库 / 产品线库（11 视图）/ 套餐价格表（10 视图）/ 库存看板 / 库存快照 / 来源帖库 |

生成脚本：`build-vault.py` → `build-bases.py` → `build-home.py`
（**顺序重要**：`build-vault.py` 会清空并重建各目录，`.base` 必须在它之后生成）

## 目录结构

```
bagevm-vps/
├── bagevm-vps-guide.html      # 推广网页（主交付物）
├── bagevm-vps-guide.md        # 完整页 Markdown 版
├── bagevm-一分钟选型结论.md     # 论坛/社交发布用的精简版
├── index.html                 # 跳转到主页面
├── build-data.py              # 合并官网扫描 + 社区数据 -> data/bagevm-产品线数据.json
├── build-page.py              # 由数据生成 bagevm-vps-guide.html
├── build-vault.py             # 写入 Obsidian 库（厂商/产品线/套餐/库存/来源帖）
├── build-bases.py             # 生成 6 个 .base 数据库
├── build-home.py              # 生成库首页.md
├── bagevm-store-scan.py       # 官网商店页扫描器
└── data/
    ├── bagevm-产品线数据.json      # 结构化产品线数据（生成网页与库用）
    ├── bagevm-store扫描.json       # 官网 12 个商店页原始扫描
    ├── bagevm-官网产品明细.json     # Obsidian 库官网产品条目（2026-10-09 快照）
    └── bagevm-nodeseek帖子.json    # NodeSeek 社区帖子元数据（37 篇）
```

