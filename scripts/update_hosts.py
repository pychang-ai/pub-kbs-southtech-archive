"""
Rebuild hosts.md to include upload date(s) and YouTube links per host.
"""
import csv, re, sys, io
from pathlib import Path
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

REPO = Path(__file__).resolve().parent.parent
EPISODES_CSV = REPO / "data" / "episodes.csv"
OUT = REPO / "hosts.md"

def md_escape(s):
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()

def fmt_date(d):
    return f"{d[:4]}-{d[4:6]}-{d[6:8]}" if len(d) == 8 else d

appearances = defaultdict(list)  # host -> [(date, vid, title, guest)]
host_orgs = defaultdict(set)

with open(EPISODES_CSV, 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        idx, vid, date, title, host, host_org, guest, guest_org, flag = row
        if not host:
            continue
        title_clean = title.replace("南方科技城-", "")
        appearances[host].append((date, vid, title_clean, guest))
        if host_org:
            host_orgs[host].add(host_org)

sorted_hosts = sorted(appearances.items(), key=lambda x: (-len(x[1]), x[0]))

n_hosts = len(sorted_hosts)
total = sum(len(v) for v in appearances.values())

md = f"""# 主持人完整索引

> {n_hosts} 位主持人，全為國立高雄科技大學（NKUST）教師。
> 共 {total} 次主持紀錄。日期 = YouTube 上架日（點擊跳轉至該集）。

| # | 主持人 | 次數 | 單位（含職稱變化） | 主持集數（日期 + 標題 + 來賓）|
|---|---|---:|---|---|
"""

for i, (name, apps) in enumerate(sorted_hosts, 1):
    apps_sorted = sorted(apps, key=lambda x: x[0] or "")
    orgs = " ｜ ".join(sorted(host_orgs.get(name, set())))
    lines = []
    for date, vid, title, guest in apps_sorted:
        dfmt = fmt_date(date) if date else "（無日期）"
        ttitle = title[:28] + ("…" if len(title) > 28 else "")
        guest_tag = f"（來賓：{md_escape(guest[:20])}{'…' if len(guest)>20 else ''}）" if guest else ""
        if vid:
            lines.append(f"[{dfmt}](https://www.youtube.com/watch?v={vid}) {md_escape(ttitle)} {guest_tag}")
        else:
            lines.append(f"{dfmt} {md_escape(ttitle)} {guest_tag}")
    eps_cell = "<br>".join(lines)
    md += f"| {i} | **{md_escape(name)}** | {len(apps)} | {md_escape(orgs)} | {eps_cell} |\n"

md += f"""
---

*[← 回 README](README.md)* | *[來賓索引 →](guests.md)* | *[逐集明細 →](episodes.md)*
"""

OUT.write_text(md, encoding='utf-8')
print(f"Written: {OUT}", flush=True)
print(f"Hosts: {n_hosts}, Total appearances: {total}", flush=True)
