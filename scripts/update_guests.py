"""
Rebuild guests.md to include upload date(s) and YouTube links per guest.

For each unique guest, list all their appearances as:
  YYYY-MM-DD (linked to YT) + episode title (truncated)
"""
import csv, re, sys, io
from pathlib import Path
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

REPO = Path(__file__).resolve().parent.parent
EPISODES_CSV = REPO / "data" / "episodes.csv"
OUT = REPO / "guests.md"

def md_escape(s):
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()

def fmt_date(d):
    return f"{d[:4]}-{d[4:6]}-{d[6:8]}" if len(d) == 8 else d

# aggregate
appearances = defaultdict(list)  # guest -> [(date, vid, title, host, org)]
guest_orgs = defaultdict(set)

with open(EPISODES_CSV, 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    next(reader)  # header
    for row in reader:
        idx, vid, date, title, host, host_org, guest, guest_org, flag = row
        if not guest:
            continue
        title_clean = title.replace("南方科技城-", "")
        for g in re.split(r'[、,，與]', guest):
            g = g.strip()
            if not g:
                continue
            appearances[g].append((date, vid, title_clean, host, guest_org))
            if guest_org:
                guest_orgs[g].add(guest_org)

# sort: by count desc, then by name
sorted_guests = sorted(appearances.items(), key=lambda x: (-len(x[1]), x[0]))

n_guests = len(sorted_guests)
total_appearances = sum(len(v) for v in appearances.values())

md = f"""# 來賓完整索引

> {n_guests} 位來賓，按出場次數排序。共 {total_appearances} 次出場（同人多集分開計）。
> 日期 = YouTube 上架日（點擊跳轉至該集）。

| # | 來賓 | 次數 | 單位（合併） | 出場集數（日期 + 標題）|
|---|---|---:|---|---|
"""

for i, (name, apps) in enumerate(sorted_guests, 1):
    # sort apps by date
    apps_sorted = sorted(apps, key=lambda x: x[0] or "")
    orgs = " ｜ ".join(sorted(guest_orgs.get(name, set())))
    episode_links = []
    for date, vid, title, host, _ in apps_sorted:
        dfmt = fmt_date(date) if date else "（無日期）"
        ttitle = title[:30] + ("…" if len(title) > 30 else "")
        if vid:
            episode_links.append(f"[{dfmt}](https://www.youtube.com/watch?v={vid}) {md_escape(ttitle)}")
        else:
            episode_links.append(f"{dfmt} {md_escape(ttitle)}")
    eps_cell = "<br>".join(episode_links)
    md += f"| {i} | **{md_escape(name)}** | {len(apps)} | {md_escape(orgs)} | {eps_cell} |\n"

md += f"""
---

*[← 回 README](README.md)* | *[主持人索引 →](hosts.md)* | *[逐集明細 →](episodes.md)*
"""

OUT.write_text(md, encoding='utf-8')
print(f"Written: {OUT}", flush=True)
print(f"Guests: {n_guests}, Appearances: {total_appearances}", flush=True)
