#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 BageVM 的 6 个 Obsidian Bases（.base）文件（结构对齐 bytevirt）。"""
import os, io

ROOT = "/Users/peter/Documents/Obsidian Vault/bagevm"
D = os.path.join(ROOT, "数据库")
os.makedirs(D, exist_ok=True)


def wr(name, text):
    with io.open(os.path.join(D, name), "w", encoding="utf-8") as f:
        f.write(text)


def order_block(items, indent="    "):
    return f"{indent}order:\n" + "".join(f"{indent}  - {i}\n" for i in items)


PLAN_ORDER = ["file.name", "product_name", "region", "series", "spec_cpu", "spec_traffic",
              "bandwidth_mbps", "traffic_gb", "price", "annual_price", "price_usd",
              "stock", "buyable", "pid", "aff_link"]

PLAN_PROPS = """properties:
  name:
    displayName: 套餐
  product_name:
    displayName: 产品线
  region:
    displayName: 地区
  segment:
    displayName: 定位
  series:
    displayName: 系列
  spec_cpu:
    displayName: 规格
  spec_traffic:
    displayName: 流量/带宽
  spec_ip:
    displayName: IP
  cpu_cores:
    displayName: 核数
  ram_gb:
    displayName: 内存(GB)
  disk_gb:
    displayName: 硬盘(GB)
  bandwidth_mbps:
    displayName: 带宽(Mbps)
  traffic_gb:
    displayName: 流量(GB)
  price:
    displayName: 月付(USD)
  unit:
    displayName: 计费周期
  price_usd:
    displayName: 折合月付(USD)
  annual_price:
    displayName: 年付(USD)
  stock:
    displayName: 库存
  buyable:
    displayName: 可下单
  pid:
    displayName: pid
  aff_link:
    displayName: 推广链接
  formula.per_gb:
    displayName: 每GB流量成本
"""

LINE_ORDER = ["file.name", "region", "series", "segment", "cpu", "upstream", "pid_from", "isp_best", "isp_ok",
              "isp_avoid", "isp_basis", "price_from", "tier_count", "lg", "aff_link"]

LINE_PROPS = """properties:
  name:
    displayName: 产品线
  vendor:
    displayName: 厂商
  region:
    displayName: 地区
  cpu:
    displayName: CPU
  upstream:
    displayName: 上游线路
  segment:
    displayName: 定位
  series:
    displayName: 系列
  price_from:
    displayName: 月付起
  price_from_cycle:
    displayName: 起价周期
  tier_count:
    displayName: 档位数
  stock:
    displayName: 库存
  tcp_test:
    displayName: 三网TCPing
  lg:
    displayName: LookingGlass
  lg_url:
    displayName: LG地址
  isp_best:
    displayName: 推荐运营商
  isp_ok:
    displayName: 可用运营商
  isp_avoid:
    displayName: 不建议
  isp_basis:
    displayName: 证据强度
  isp_note:
    displayName: 运营商说明
  isp_source:
    displayName: 证据帖
  pid_from:
    displayName: 起档pid
  aff_link:
    displayName: 推广链接
  formula.isp_fit:
    displayName: 推荐
  formula.isp_risk:
    displayName: 避开
"""

# ---------------- 01 厂商库
wr("01 厂商库.base", """filters:
  and:
    - file.inFolder("bagevm/厂商")
properties:
  name:
    displayName: 名称
  type:
    displayName: 类型
  kind:
    displayName: 子类
  homepage:
    displayName: 官网
  store_page:
    displayName: 商店
  lg_entry:
    displayName: LookingGlass
  aff_param:
    displayName: 推广参数
  aff_link:
    displayName: 推广链接
  company:
    displayName: 公司
  asn:
    displayName: ASN
  optimization:
    displayName: 回国优化
  payment:
    displayName: 支付
  scrape_tool:
    displayName: 抓取脚本
views:
  - type: table
    name: 厂商与资料
    order:
      - file.name
      - type
      - kind
      - homepage
      - aff_param
      - company
      - optimization
""")

# ---------------- 02 产品线库
wr("02 产品线库.base", """filters:
  and:
    - file.inFolder("bagevm/产品线")
formulas:
  isp_fit: if(isp_best.isEmpty(), "—", isp_best.join(" / "))
  isp_risk: if(isp_avoid.isEmpty(), "—", isp_avoid.join(" / "))
""" + LINE_PROPS + """views:
  - type: table
    name: 全部产品线
""" + order_block(LINE_ORDER) + """    sort:
      - property: price_from
        direction: ASC
  - type: table
    name: 按运营商 · 中国移动
    filters:
      and:
        - isp_best.contains("中国移动")
""" + order_block(LINE_ORDER) + """    sort:
      - property: price_from
        direction: ASC
  - type: table
    name: 按运营商 · 中国联通
    filters:
      and:
        - isp_best.contains("中国联通")
""" + order_block(LINE_ORDER) + """    sort:
      - property: price_from
        direction: ASC
  - type: table
    name: 按运营商 · 中国电信
    filters:
      and:
        - isp_best.contains("中国电信")
""" + order_block(LINE_ORDER) + """    sort:
      - property: price_from
        direction: ASC
  - type: table
    name: Standard 系列
    filters:
      and:
        - series == "Standard"
""" + order_block(LINE_ORDER) + """    sort:
      - property: price_from
        direction: ASC
  - type: table
    name: 非 Standard 系列
    filters:
      and:
        - series == "非Standard"
""" + order_block(LINE_ORDER) + """    sort:
      - property: price_from
        direction: ASC
  - type: table
    name: 北美
    filters:
      and:
        - segment == "北美"
""" + order_block(LINE_ORDER) + """    sort:
      - property: price_from
        direction: ASC
  - type: table
    name: 欧洲
    filters:
      and:
        - segment == "欧洲"
""" + order_block(LINE_ORDER) + """    sort:
      - property: price_from
        direction: ASC
  - type: table
    name: 有实测依据
    filters:
      and:
        - isp_basis == "实测"
""" + order_block(LINE_ORDER) + """    sort:
      - property: price_from
        direction: ASC
  - type: table
    name: 不建议清单
    filters:
      and:
        - "!isp_avoid.isEmpty()"
""" + order_block(["file.name", "region", "series", "formula.isp_risk", "isp_note"]) + """  - type: table
    name: 有 Looking Glass
    filters:
      and:
        - "!lg.isEmpty()"
""" + order_block(["file.name", "region", "series", "lg", "lg_url", "aff_link"]) + "")

# ---------------- 03 套餐价格表
wr("03 套餐价格表.base", """filters:
  and:
    - file.inFolder("bagevm/套餐")
formulas:
  per_gb: if(traffic_gb, (price_usd / traffic_gb * 1024).toFixed(2))
""" + PLAN_PROPS + """views:
  - type: table
    name: 全部套餐
""" + order_block(PLAN_ORDER) + """    sort:
      - property: price_usd
        direction: ASC
  - type: table
    name: Standard 系列
    filters:
      and:
        - series == "Standard"
""" + order_block(PLAN_ORDER) + """    sort:
      - property: price_usd
        direction: ASC
  - type: table
    name: 非 Standard 系列
    filters:
      and:
        - series == "非Standard"
""" + order_block(PLAN_ORDER) + """    sort:
      - property: price_usd
        direction: ASC
  - type: table
    name: 北美
    filters:
      and:
        - segment == "北美"
""" + order_block(PLAN_ORDER) + """    sort:
      - property: price_usd
        direction: ASC
  - type: table
    name: 欧洲
    filters:
      and:
        - segment == "欧洲"
""" + order_block(PLAN_ORDER) + """    sort:
      - property: price_usd
        direction: ASC
  - type: table
    name: 超低价 ≤$3/月
    filters:
      and:
        - price_usd <= 3
""" + order_block(PLAN_ORDER) + """    sort:
      - property: price_usd
        direction: ASC
  - type: table
    name: 大带宽 ≥1Gbps
    filters:
      and:
        - bandwidth_mbps >= 1000
""" + order_block(PLAN_ORDER) + """    sort:
      - property: bandwidth_mbps
        direction: DESC
  - type: table
    name: 大流量 ≥4TB
    filters:
      and:
        - traffic_gb >= 4096
""" + order_block(PLAN_ORDER) + """    sort:
      - property: traffic_gb
        direction: DESC
  - type: table
    name: 每GB流量成本
""" + order_block(["file.name", "product_name", "traffic_gb", "price_usd",
                   "formula.per_gb", "buyable"]) + """    sort:
      - property: formula.per_gb
        direction: ASC
  - type: table
    name: pid 对照
    order:
      - pid
      - file.name
      - product_name
      - spec_cpu
      - price
      - stock
      - aff_link
    sort:
      - property: pid
        direction: ASC
  - type: table
    name: 当前可下单
    filters:
      and:
        - buyable == "是"
""" + order_block(PLAN_ORDER) + """    sort:
      - property: price_usd
        direction: ASC
""")

# ---------------- 04 库存看板
wr("04 库存看板.base", """filters:
  and:
    - file.inFolder("bagevm/套餐")
properties:
  name:
    displayName: 套餐
  product_name:
    displayName: 产品线
  region:
    displayName: 地区
  series:
    displayName: 系列
  price:
    displayName: 月付
  unit:
    displayName: 周期
  stock:
    displayName: 库存
  stock_raw:
    displayName: 官网原文
  buyable:
    displayName: 可下单
views:
  - type: kanban
    name: 库存分布
    groupBy:
      property: stock
      direction: ASC
    groupOrder:
      - 在售
      - 缺货
  - type: table
    name: 缺货清单
    filters:
      and:
        - stock == "缺货"
""" + order_block(["file.name", "product_name", "region", "series", "price", "unit", "stock_raw"]) + """  - type: table
    name: 全部档位库存
""" + order_block(["file.name", "product_name", "region", "series", "price", "unit",
                   "stock", "buyable"]) + """    sort:
      - property: product_name
        direction: ASC
""")

# ---------------- 05 库存快照
wr("05 库存快照.base", """filters:
  and:
    - file.inFolder("bagevm/库存")
properties:
  scraped_at:
    displayName: 抓取时间
  vendor:
    displayName: 厂商
  total_plans:
    displayName: 档位总数
  in_stock:
    displayName: 在售
  sold_out:
    displayName: 缺货
  buyable:
    displayName: 可下单
  source:
    displayName: 来源
views:
  - type: table
    name: 库存快照（按时间）
    order:
      - file.name
      - scraped_at
      - total_plans
      - in_stock
      - sold_out
      - buyable
      - source
    sort:
      - property: scraped_at
        direction: DESC
""")

# ---------------- 06 来源帖库
wr("06 来源帖库.base", """filters:
  and:
    - file.inFolder("bagevm/来源帖")
properties:
  name:
    displayName: 标题
  product_name:
    displayName: 关联产品线
  category:
    displayName: 分类
  author:
    displayName: 作者
  post_time:
    displayName: 发布
  comment_count:
    displayName: 已抓评论
  sentiment:
    displayName: 评论倾向
  url:
    displayName: 链接
views:
  - type: table
    name: 全部来源帖
    order:
      - file.name
      - product_name
      - category
      - author
      - post_time
      - comment_count
      - sentiment
    sort:
      - property: comment_count
        direction: DESC
  - type: table
    name: 测评帖
    filters:
      and:
        - category == "测评"
    order:
      - file.name
      - product_name
      - author
      - post_time
      - comment_count
    sort:
      - property: comment_count
        direction: DESC
  - type: table
    name: 按产品线
    order:
      - file.name
      - product_name
      - category
      - comment_count
    sort:
      - property: product_name
        direction: ASC
  - type: table
    name: 评论最多的
    order:
      - file.name
      - product_name
      - comment_count
      - sentiment
    sort:
      - property: comment_count
        direction: DESC
""")

print("已生成 6 个 .base 到", D)
