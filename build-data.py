#!/usr/bin/env python3
"""合并 BageVM 官网新鲜扫描(2026-10-14) + NodeSeek 社区价格，产出结构化产品线数据。"""
import json, re, os

HERE = os.path.dirname(os.path.abspath(__file__))
AFF = "https://www.bagevm.com/aff.php?aff=1195"

# ---- 官网 2026-10-14 新鲜扫描 + 社区年付价（来源：NS938368 总集篇，75折促销价；原价年付由 75 折反推）----
# tiers: (名, 核, 内存G, 盘G, 带宽Mbps, 流量描述, 月付$, 年付促销$(75折), 年付原付$)
LINES = [
 dict(key="hk-lite", name="香港 Lite", loc="中国香港", cpu="AMD EPYC 7663 / DDR4",
      carriers="PCCWG+TELSTRA+NTT+Cogent+HE+HKIX+EIE",
      lg="lg-hkb.bagevm.net", store="hong-kong-lite-servers", tier_slug=None,
      verdict="大带宽落地", tiers=[
   ("TINY",1,1,20,1000,"4TB",2.99,24.74,32.99),
   ("STARTER",2,2,30,2000,"8TB",4.99,41.24,54.99),
   ("MEDIUM",4,4,40,3000,"12TB",8.99,74.24,98.99),
   ("LARGE",4,8,50,5000,"20TB",17.55,154.16,None),
   ("CUSTOM",4,8,50,5000,"20TB",17.55,None,None)]),
 dict(key="hk-std", name="香港 Standard", loc="中国香港", cpu="AMD EPYC 7663 / DDR4",
      carriers="PCCWG+TELSTRA+NTT+Lumen+Retn+Cogent+HE+HKIX+EIE",
      lg="lg-hka.bagevm.net", store="hong-kong-servers", tier_slug=None,
      verdict="移动低延迟", tiers=[
   ("TINY",1,1,20,1000,"2TB",3.99,32.99,None),
   ("STARTER",1,2,30,2000,"4TB",6.99,56.99,None),
   ("MEDIUM",2,4,40,3000,"6TB",10.99,83.24,None),
   ("LARGE",4,4,50,5000,"10TB",20.99,173.24,None),
   ("CUSTOM",4,4,50,5000,"10TB",20.99,None,None)]),
 dict(key="jp", name="日本 Japan", loc="日本东京", cpu="AMD Ryzen 9 7950X / DDR5",
      carriers="NTT+Cogent+Lumen+HE",
      lg="lg-jpa.bagevm.net", store="japan-servers", tier_slug=None,
      verdict="国际强/回国一般", tiers=[
   ("SMALL",1,1,10,5000,"2TB",3.99,32.99,None),
   ("TINY",1,1,10,5000,"5TB",5.99,53.24,None),
   ("STARTER",1,2,20,5000,"8TB",8.99,74.24,None),
   ("MEDIUM",2,4,30,10000,"12TB",15.99,141.74,None),
   ("LARGE",4,4,40,10000,"20TB",25.99,214.49,None)]),
 dict(key="jp-std", name="日本 Standard", loc="日本东京", cpu="AMD EPYC 7663 / DDR4",
      carriers="PCCWG+TELSTRA+NTT+Lumen+Cogent+EIE",
      lg="lg-jpb.bagevm.net", store="japan-standard-servers", tier_slug=None,
      verdict="三网延迟最低", tiers=[
   ("SMALL",1,1,10,1000,"2TB",3.99,32.99,None),
   ("TINY",1,1,20,1000,"5TB",5.99,53.24,None),
   ("STARTER",1,2,30,2000,"8TB",10.99,83.24,None),
   ("MEDIUM",2,4,40,3000,"12TB",20.99,183.74,None),
   ("LARGE",4,4,50,5000,"15TB",25.99,214.49,None),
   ("CUSTOM",4,4,50,5000,"15TB",25.99,None,None)]),
 dict(key="sg", name="新加坡 Singapore", loc="新加坡", cpu="AMD Ryzen 9 7950X / DDR5",
      carriers="NTT+Cogent+Lumen+HE",
      lg="lg-sga.bagevm.net", store="singapore-servers", tier_slug=None,
      verdict="IP偏脏/基本缺货", tiers=[
   ("SMALL",1,1,10,5000,"2TB",3.99,32.99,None),
   ("TINY",1,1,10,5000,"5TB",5.99,53.24,None),
   ("STARTER",1,2,20,5000,"8TB",8.99,74.24,None),
   ("MEDIUM",2,4,30,10000,"12TB",15.99,141.74,None),
   ("LARGE",4,4,40,10000,"20TB",25.99,214.49,None)]),
 dict(key="sg-std", name="新加坡 Standard", loc="新加坡", cpu="AMD EPYC 7663 / DDR4",
      carriers="PCCWG+TELSTRA+NTT+Lumen+Cogent+EIE",
      lg="lg-sgb.bagevm.net", store="singapore-standard-servers", tier_slug=None,
      verdict="落地可用", tiers=[
   ("SMALL",1,1,10,1000,"2TB",3.99,32.99,None),
   ("TINY",1,1,20,1000,"5TB",5.99,53.24,None),
   ("STARTER",1,2,30,2000,"8TB",10.99,83.24,None),
   ("MEDIUM",2,4,40,3000,"12TB",20.99,183.74,None),
   ("LARGE",4,4,50,5000,"15TB",25.99,214.49,None),
   ("CUSTOM",4,4,50,5000,"15TB",25.99,None,None)]),
 dict(key="la", name="洛杉矶 Los Angeles", loc="美国洛杉矶", cpu="AMD Ryzen 9 7900(标称)/9950X3D(实测) / DDR5",
      carriers="TATA+GTT+Comcast",
      lg="lg-usa.bagevm.net", store="los-angeles-servers", tier_slug=None,
      verdict="原生IP美西落地", tiers=[
   ("TINY",1,1,20,1000,"4TB",2.99,None,32.99),
   ("STARTER",1,2,30,2000,"8TB",4.99,None,54.99),
   ("MEDIUM",2,2,40,2000,"12TB",8.99,None,98.99),
   ("LARGE",3,4,50,3000,"20TB",14.99,None,164.99)]),
 dict(key="la2", name="洛杉矶2 Los Angeles2", loc="美国洛杉矶", cpu="AMD Ryzen 9 9950X / DDR5",
      carriers="TATA+GTT+PCCW",
      lg="lg-usc.bagevm.net", store="los-angeles2-servers", tier_slug=None,
      verdict="解锁/美西落地首选", tiers=[
   ("TINY",1,1,20,1000,"4TB",2.99,None,32.99),
   ("STARTER",1,2,30,2000,"8TB",4.99,None,54.99),
   ("MEDIUM",2,2,40,2000,"12TB",8.99,None,98.99),
   ("LARGE",3,4,50,3000,"20TB",14.99,None,164.99)]),
 dict(key="slc", name="盐湖城 Salt Lake City", loc="美国盐湖城", cpu="AMD Ryzen 9 9950X / DDR5",
      carriers="Cogent+GTT+He+Lumen+PCCW",
      lg="lg-usb.bagevm.net", store="salt-lake-city-servers", tier_slug=None,
      verdict="美中落地/位置偏", tiers=[
   ("TINY",1,1,20,1000,"4TB",2.99,24.74,32.99),
   ("STARTER",1,2,30,2000,"8TB",4.99,41.24,54.99),
   ("MEDIUM",2,2,40,2000,"12TB",8.99,74.24,98.99),
   ("LARGE",3,4,50,3000,"20TB",14.99,123.74,164.99)]),
 dict(key="de", name="德国法兰克福 Germany", loc="德国法兰克福", cpu="AMD Ryzen 9 7950X(标称)/9950X(实测) / DDR5",
      carriers="Cogent+NTT+GTT+Lumen",
      lg="lg-dea.bagevm.net", store="germany-servers", tier_slug=None,
      verdict="欧洲落地最强", tiers=[
   ("TINY",1,1,20,1000,"4TB",2.99,24.74,32.99),
   ("STARTER",1,2,30,2000,"8TB",4.99,41.24,54.99),
   ("MEDIUM",2,2,40,2000,"12TB",8.99,74.24,98.99),
   ("LARGE",3,4,50,3000,"20TB",14.99,123.74,164.99)]),
 dict(key="uk", name="英国考文垂 United Kingdom", loc="英国考文垂(商店页)/伦敦(社区)", cpu="AMD Ryzen 9 7900(标称)/9950X(实测) / DDR5",
      carriers="NTT+GTT+PCCW",
      lg="lg-gba.bagevm.net", store="united-kingdom-servers", tier_slug=None,
      verdict="英国原生IP", tiers=[
   ("TINY",1,1,10,1000,"4TB",2.99,None,32.99),
   ("STARTER",1,2,15,1000,"8TB",4.99,None,54.99),
   ("MEDIUM",2,2,20,1000,"12TB",8.99,None,98.99),
   ("LARGE",3,4,25,1000,"20TB",14.99,None,164.99)]),
 dict(key="tw", name="台湾 Hinet VDS", loc="中国台湾", cpu="—",
      carriers="中华电信 HiNet（动态 IP）",
      lg="lg-twa.bagevm.net", store="tw-hinet-vds", tier_slug=None,
      verdict="HiNet动态IP/缺货", tiers=[
   ("Hinet Dynamic 600M",6,6,60,600,"200TB",45.55,None,None)]),
]

# ---- 2026-10-14 库存（官网实时）。None=页面未显示；数字=Available；0=缺货 ----
STOCK = {
 "hk-lite":  {"TINY":None,"STARTER":None,"MEDIUM":None,"LARGE":None,"CUSTOM":None},
 "hk-std":   {"TINY":None,"STARTER":None,"MEDIUM":None,"LARGE":None,"CUSTOM":None},
 "jp":       {"SMALL":0,"TINY":0,"STARTER":0,"MEDIUM":0,"LARGE":2},
 "jp-std":   {"SMALL":None,"TINY":None,"STARTER":None,"MEDIUM":None,"LARGE":None,"CUSTOM":None},
 "sg":       {"SMALL":0,"TINY":0,"STARTER":0,"MEDIUM":1,"LARGE":0},
 "sg-std":   {"SMALL":None,"TINY":None,"STARTER":None,"MEDIUM":None,"LARGE":None,"CUSTOM":None},
 "la":       {"TINY":None,"STARTER":None,"MEDIUM":None,"LARGE":None},
 "la2":      {"TINY":None,"STARTER":None,"MEDIUM":None,"LARGE":None},
 "slc":      {"TINY":None,"STARTER":None,"MEDIUM":None,"LARGE":None},
 "de":       {"TINY":None,"STARTER":None,"MEDIUM":None,"LARGE":None},
 "uk":       {"TINY":0,"STARTER":4,"MEDIUM":1,"LARGE":3},
 "tw":       {"Hinet Dynamic 600M":0},
}

# ---- 社区三网 TCPing（NS938368 总集篇, 2026-09-16）：移动/联通/电信 延迟ms与丢包 ----
TCP = {
 "hk-lite": ("310 / 0.06%","384 / 1.78%","375 / 0.0%"),
 "hk-std":  ("61 / 0.01%","363 / 1.82%","377 / 0.01%"),
 "jp":      ("119 / 0.41%","577 / 3.3%","387 / 0.41%"),
 "jp-std":  ("81 / 0.01%","92 / 1.67%","168 / 0.09%"),
 "sg":      ("99 / 0.01%","531 / 2.83%","404 / 3.23%"),
 "sg-std":  ("106 / 0.02%","284 / 1.76%","321 / 0%"),
 "la":      ("242 / 0.7%","239 / 1.78%","233 / 1.12%"),
 "la2":     ("228 / 0.1%","224 / 1.86%","260 / 0.06%"),
 "slc":     ("259 / 0.01%","223 / 1.73%","247 / 0.01%"),
 "de":      ("255 / 0.01%","183 / 1.75%","243 / 0.07%"),
 "uk":      ("396 / 0.6%","261 / 2.36%","311 / 0.67%"),
}

out = {"aff": AFF, "scraped_at": "2026-10-14", "lines": []}
for ln in LINES:
    d = dict(ln)
    d["stock"] = STOCK.get(ln["key"], {})
    d["tcp"] = TCP.get(ln["key"])
    d["order_url"] = f'https://www.bagevm.com/index.php/store/{ln["store"]}'
    d["aff_url"] = f'{AFF}'
    out["lines"].append(d)

with open(os.path.join(HERE, "data", "bagevm-产品线数据.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

n_tiers = sum(len(l["tiers"]) for l in LINES)
print(f"{len(LINES)} lines, {n_tiers} tiers -> data/bagevm-产品线数据.json")
for l in LINES:
    m = l["tiers"][0][6]
    print(f'  {l["name"]:24s} {len(l["tiers"])}档  月付起 ${m}  {l["carriers"][:40]}')
