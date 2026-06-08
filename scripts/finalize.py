"""
Normalize host/guest names — fix 3 format variants observed:
  變形 A: 「主持人：國立高雄科技大學羅光閔副教授」(機構+名+職稱連寫)
  變形 B: 「主持人：郭俊賢國立高雄科技大學教授兼副校長」(名+機構+職稱連寫)
  變形 C: 全描述在一行（集86 標題早期格式）

策略：已知主持人姓名清單 → substring match → 拆出 name + org
"""
import json, re, csv, io, sys, subprocess, os
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

OUT_DIR = Path(r"C:\Users\PYC\Desktop\southtech-analysis")
DESC_DIR = OUT_DIR / "descriptions"
env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'

# 已知主持人姓名（從上輪統計 ≥3 次且乾淨者）
KNOWN_HOSTS = ["羅光閔", "魏裕珍", "蔡匡忠", "潘俊仁", "郭俊賢", "林皇耀",
               "廖婉茹", "李憶甄", "蔡孟修", "丁國桓", "邱國勛", "侯清賢"]

# Regex — 加寬結束條件處理單行格式（集86）
HOST_RE = re.compile(
    r'[●◎]?\s*主\s*持\s*人\s*[:：]\s*'
    r'([^\n（(]+?)'
    r'(?:\s*[（(]\s*([^\n）)]+?)\s*[)）])?'
    r'(?=\s*(?:[\n●◎]|來\s*賓|$))'
)
GUEST_RE = re.compile(
    r'[●◎]?\s*來\s*賓\s*[:：]\s*'
    r'([^\n（(]+?)'
    r'(?:\s*[（(]\s*([^\n）)]+?)\s*[)）])?'
    r'(?=\s*(?:[\n●◎]|主\s*持\s*人|探索|本期|本集|隨著|--|$))'
)

def normalize(raw_name, raw_org):
    """If raw_name contains known host name + extra junk, split it."""
    if not raw_name:
        return raw_name, raw_org
    for known in KNOWN_HOSTS:
        if known in raw_name and raw_name != known:
            # split: part before known = prefix_org, part after = suffix_role
            idx = raw_name.find(known)
            prefix = raw_name[:idx].strip()
            suffix = raw_name[idx+len(known):].strip()
            merged_org = (prefix + suffix).strip()
            if merged_org and not raw_org:
                return known, merged_org
            return known, raw_org or merged_org
    return raw_name, raw_org

# reload entries
print("Loading playlist...", flush=True)
r = subprocess.run(["yt-dlp","--flat-playlist","-J",
                    "https://www.youtube.com/playlist?list=PLuNXocnS3NOJspjOUiWqgQn5terWDMGMR"],
                   capture_output=True, timeout=120, env=env)
entries = json.loads(r.stdout.decode('utf-8', errors='replace')).get('entries', [])

rows = []
parse_fail_ids = []
no_desc_ids = []
for idx, e in enumerate(entries, 1):
    eid = e['id']
    desc_file = DESC_DIR / f"{eid}.txt"
    meta_file = DESC_DIR / f"{eid}.meta.txt"

    if not desc_file.exists() or desc_file.stat().st_size == 0:
        rows.append([idx, eid, "", e.get('title',''), "", "", "", "", "[NO_DESC]"])
        no_desc_ids.append(eid)
        continue

    desc = desc_file.read_text(encoding='utf-8', errors='replace')
    if meta_file.exists():
        meta = meta_file.read_text(encoding='utf-8', errors='replace').strip()
        if '\\t' in meta and '\t' not in meta:
            meta = meta.replace('\\t', '\t')
        mp = meta.split('\t', 1)
        date = mp[0] if mp else ""
        title = mp[1] if len(mp) > 1 else e.get('title','')
    else:
        date = ""
        title = e.get('title','')

    host_m = HOST_RE.search(desc)
    guest_m = GUEST_RE.search(desc)
    host_name = host_m.group(1).strip() if host_m else ""
    host_org = (host_m.group(2) or "").strip() if host_m else ""
    guest_name = guest_m.group(1).strip() if guest_m else ""
    guest_org = (guest_m.group(2) or "").strip() if guest_m else ""

    # normalize merged names
    host_name, host_org = normalize(host_name, host_org)

    flag = "" if (host_name and guest_name) else "REVIEW"
    if not host_name and not guest_name:
        parse_fail_ids.append(eid)
    rows.append([idx, eid, date, title, host_name, host_org, guest_name, guest_org, flag])

# write CSV
csv_path = OUT_DIR / "southtech_hosts_guests.csv"
with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(["集數","影片ID","上架日","標題","主持人","主持人單位","來賓","來賓單位","備註"])
    w.writerows(rows)

# stats
hosts, host_orgs, guests, guest_orgs = {}, {}, {}, {}
for r in rows:
    if r[4]:
        hosts[r[4]] = hosts.get(r[4], 0) + 1
        if r[5]:
            host_orgs.setdefault(r[4], set()).add(r[5])
    if r[6]:
        for g in re.split(r'[、,，與]', r[6]):
            g = g.strip()
            if g:
                guests[g] = guests.get(g, 0) + 1
                if r[7]:
                    guest_orgs.setdefault(g, set()).add(r[7])

# write unique tables
with open(OUT_DIR / "unique_hosts.csv", 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(["主持人","出場次數","單位（合併）"])
    for n, c in sorted(hosts.items(), key=lambda x: -x[1]):
        w.writerow([n, c, " | ".join(sorted(host_orgs.get(n, set())))])
with open(OUT_DIR / "unique_guests.csv", 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(["來賓","出場次數","單位（合併）"])
    for n, c in sorted(guests.items(), key=lambda x: -x[1]):
        w.writerow([n, c, " | ".join(sorted(guest_orgs.get(n, set())))])

print(f"\n=== FINAL ===", flush=True)
print(f"Total: {len(rows)}", flush=True)
print(f"No desc: {len(no_desc_ids)} {no_desc_ids}", flush=True)
print(f"Parse fail: {len(parse_fail_ids)} {parse_fail_ids}", flush=True)
print(f"Unique hosts: {len(hosts)}", flush=True)
print(f"Unique guests: {len(guests)}", flush=True)
print(f"\nAll hosts:", flush=True)
for n, c in sorted(hosts.items(), key=lambda x: -x[1]):
    print(f"  {c:3d}  {n}", flush=True)
print(f"\nTop 25 guests:", flush=True)
for n, c in sorted(guests.items(), key=lambda x: -x[1])[:25]:
    orgs = " | ".join(sorted(guest_orgs.get(n, set())))[:80]
    print(f"  {c:3d}  {n}  [{orgs}]", flush=True)
