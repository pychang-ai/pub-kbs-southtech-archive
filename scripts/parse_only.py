"""
Re-parse step only — descriptions/ already populated, regenerate CSVs.
Also handle the 4 retry meta files (which got literal \t from bash loop).
"""
import json, re, subprocess, sys, csv, io, os
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PLAYLIST = "https://www.youtube.com/playlist?list=PLuNXocnS3NOJspjOUiWqgQn5terWDMGMR"
OUT_DIR = Path(r"C:\Users\PYC\Desktop\southtech-analysis")
DESC_DIR = OUT_DIR / "descriptions"

env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'

# fix 4 meta files (rewritten via Python so %s gets substituted)
print("Fixing meta files for 4 retry videos...", flush=True)
for vid in ["Ll9gqWvwyoA", "GSrnyXMFGN0", "B1Om4pl58dY", "t1rOT-cwMH8"]:
    meta_file = DESC_DIR / f"{vid}.meta.txt"
    if meta_file.exists():
        content = meta_file.read_text(encoding='utf-8', errors='replace')
        if '\\t' in content:  # literal backslash-t
            # re-run yt-dlp via Python (properly substitutes)
            subprocess.run(
                ["yt-dlp", "--skip-download", "--no-warnings",
                 "--print-to-file", "%(upload_date)s\t%(title)s", str(meta_file),
                 f"https://www.youtube.com/watch?v={vid}"],
                capture_output=True, timeout=60, env=env
            )
            print(f"  fixed {vid}", flush=True)

# reload entries (for ordering)
print("Loading playlist index...", flush=True)
r = subprocess.run(["yt-dlp","--flat-playlist","-J", PLAYLIST],
                   capture_output=True, timeout=120, env=env)
data = json.loads(r.stdout.decode('utf-8', errors='replace'))
entries = data.get('entries', [])

# patterns
HOST_RE = re.compile(r'主\s*持\s*人\s*[:：]\s*([^\n（(]+?)(?:\s*[（(]\s*([^\n）)]+?)\s*[)）])?\s*(?:\n|$)')
GUEST_RE = re.compile(r'來\s*賓\s*[:：]\s*([^\n（(]+?)(?:\s*[（(]\s*([^\n）)]+?)\s*[)）])?\s*(?:\n|$)')

rows = []
parse_fail = 0
no_desc = 0
no_desc_ids = []
parse_fail_ids = []

for idx, e in enumerate(entries, 1):
    eid = e['id']
    desc_file = DESC_DIR / f"{eid}.txt"
    meta_file = DESC_DIR / f"{eid}.meta.txt"

    if not desc_file.exists() or desc_file.stat().st_size == 0:
        rows.append([idx, eid, "", e.get('title',''), "", "", "", "", "[NO_DESC]"])
        no_desc += 1
        no_desc_ids.append(eid)
        continue

    desc = desc_file.read_text(encoding='utf-8', errors='replace')
    if meta_file.exists():
        meta = meta_file.read_text(encoding='utf-8', errors='replace').strip()
        # handle either literal \t or real tab
        if '\\t' in meta and '\t' not in meta:
            meta = meta.replace('\\t', '\t')
        meta_parts = meta.split('\t', 1)
        date = meta_parts[0] if meta_parts else ""
        title = meta_parts[1] if len(meta_parts) > 1 else e.get('title','')
    else:
        date = ""
        title = e.get('title','')

    host_m = HOST_RE.search(desc)
    guest_m = GUEST_RE.search(desc)
    host_name = host_m.group(1).strip() if host_m else ""
    host_org = (host_m.group(2) or "").strip() if host_m else ""
    guest_name = guest_m.group(1).strip() if guest_m else ""
    guest_org = (guest_m.group(2) or "").strip() if guest_m else ""
    flag = "" if (host_name and guest_name) else "REVIEW"
    if not host_name and not guest_name:
        parse_fail += 1
        parse_fail_ids.append(eid)
    rows.append([idx, eid, date, title, host_name, host_org, guest_name, guest_org, flag])

# write per-episode CSV
csv_path = OUT_DIR / "southtech_hosts_guests.csv"
with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(["集數", "影片ID", "上架日", "標題", "主持人", "主持人單位", "來賓", "來賓單位", "備註"])
    w.writerows(rows)

# stats
hosts = {}
host_orgs = {}
guests = {}
guest_orgs = {}
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

# unique hosts
hosts_path = OUT_DIR / "unique_hosts.csv"
with open(hosts_path, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(["主持人", "出場次數", "單位（可能多）"])
    for n, c in sorted(hosts.items(), key=lambda x: -x[1]):
        orgs = " | ".join(sorted(host_orgs.get(n, set())))
        w.writerow([n, c, orgs])

# unique guests
guests_path = OUT_DIR / "unique_guests.csv"
with open(guests_path, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(["來賓", "出場次數", "單位（可能多）"])
    for n, c in sorted(guests.items(), key=lambda x: -x[1]):
        orgs = " | ".join(sorted(guest_orgs.get(n, set())))
        w.writerow([n, c, orgs])

print(f"\n=== FINAL SUMMARY ===", flush=True)
print(f"Total episodes: {len(rows)}", flush=True)
print(f"No description: {no_desc} {no_desc_ids}", flush=True)
print(f"Parse failed: {parse_fail} {parse_fail_ids}", flush=True)
print(f"Unique hosts: {len(hosts)}", flush=True)
print(f"Unique guests: {len(guests)}", flush=True)
print(f"\nAll hosts:", flush=True)
for n, c in sorted(hosts.items(), key=lambda x: -x[1]):
    orgs = " | ".join(sorted(host_orgs.get(n, set())))
    print(f"  {c:3d}  {n}    [{orgs}]", flush=True)
print(f"\nTop 20 guests:", flush=True)
for n, c in sorted(guests.items(), key=lambda x: -x[1])[:20]:
    print(f"  {c:3d}  {n}", flush=True)
print(f"\nOutput files in {OUT_DIR}:", flush=True)
print(f"  southtech_hosts_guests.csv  (per-episode)", flush=True)
print(f"  unique_hosts.csv            ({len(hosts)} unique)", flush=True)
print(f"  unique_guests.csv           ({len(guests)} unique)", flush=True)
