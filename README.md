# bagevm-vps

BageVM（bagevm.com · BAGE CLOUD LLC）VPS 全产品线推荐与选购指南

- 在线页面：https://peterxulove.github.io/bagevm-vps/bagevm-vps-guide.html
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
> 页内购买链接含推广参数（aff=1195），通过链接下单不影响你的价格。

## 目录结构

```
bagevm-vps/
├── bagevm-vps-guide.html      # 推广网页（主交付物）
├── bagevm-vps-guide.md        # 完整页 Markdown 版
├── bagevm-一分钟选型结论.md     # 论坛/社交发布用的精简版
├── index.html                 # 跳转到主页面
├── build-data.py              # 合并官网扫描 + 社区数据 -> data/bagevm-产品线数据.json
├── build-page.py              # 由数据生成 bagevm-vps-guide.html
├── bagevm-store-scan.py       # 官网商店页扫描器
└── data/
    ├── bagevm-产品线数据.json      # 结构化产品线数据（生成网页用）
    ├── bagevm-store扫描.json       # 官网 12 个商店页原始扫描
    ├── bagevm-官网产品明细.json     # Obsidian 库官网产品条目（2026-10-09 快照）
    └── bagevm-nodeseek帖子.json    # NodeSeek 社区帖子元数据（37 篇）
```
