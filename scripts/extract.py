"""
南方科技城 270 集主持人/來賓抽取
Channel: 高雄廣播電臺
Playlist: PLuNXocnS3NOJspjOUiWqgQn5terWDMGMR

修正：Windows subprocess 預設用 cp950 解碼 yt-dlp 輸出 → 亂碼
改用 --print-to-file 讓 yt-dlp 直接寫 UTF-8 檔案，繞過 stdout 編碼問題
"""
import json, re, subprocess, sys, csv, io, os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PLAYLIST = "https://www.youtube.com/playlist?list=PLuNXocnS3NOJspjOUiWqgQn5terWDMGMR"
OUT_DIR = Path(r"C:\Users\PYC\Desktop\southtech-analysis")
DESC_DIR = OUT_DIR / "descriptions"
DESC_DIR.mkdir(parents=True, exist_ok=True)

# Step 1: flat playlist (UTF-8 via env)
print("[1/3] Fetching playlist index...", flush=True)
env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'
r = subprocess.run(
    ["yt-dlp", "--flat-playlist", "-J", PLAYLIST],
    capture_output=True, timeout=120, env=env
)
# yt-dlp on Windows may output cp950; JSON itself contains \uXXXX escapes so latin-1 works
data = json.loads(r.stdout.decode('utf-8', errors='replace'))
entries = data.get('entries', [])
print(f"     Got {len(entries)} videos", flush=True)

# Step 2: fetch description per video, write to UTF-8 files
def fetch(entry):
    eid = entry['id']
    out_file = DESC_DIR / f"{eid}.txt"
    if out_file.exists() and out_file.stat().st_size > 0:
        return eid, "cached"
    try:
        # --print-to-file writes UTF-8 directly, bypassing stdout encoding
        # We dump id|date|title on line 1, then description from line 2
        meta_file = DESC_DIR / f"{eid}.meta.txt"
        r = subprocess.run(
            ["yt-dlp", "--skip-download", "--no-warnings",
             "--print-to-file", "%(upload_date)s\t%(title)s", str(meta_file),
             "--print-to-file", "%(description)s", str(out_file),
             f"https://www.youtube.com/watch?v={eid}"],
            capture_output=True, timeout=60, env=env
        )
        return eid, "ok" if r.returncode == 0 else f"rc={r.returncode}"
    except Exception as e:
        return eid, f"ERROR:{e}"

print(f"[2/3] Fetching {len(entries)} descriptions (parallel x10)...", flush=True)
done = 0
errors = []
with ThreadPoolExecutor(max_workers=10) as ex:
    futs = {ex.submit(fetch, e): e for e in entries}
    for f in as_completed(futs):
        eid, status = f.result()
        done += 1
        if status not in ("ok", "cached"):
            errors.append((eid, status))
        if done % 20 == 0:
            print(f"     {done}/{len(entries)} (errors: {len(errors)})", flush=True)
print(f"     Done. errors: {len(errors)}", flush=True)
if errors[:5]:
    print(f"     Sample errors: {errors[:5]}", flush=True)

# Step 3: parse
print("[3/3] Parsing host/guest...", flush=True)

# Patterns observed:
#   主持人：羅光閔（國立高雄科技大學教授兼副學務長）
#   來賓：王振昌（金屬中心海洋職能科技發展組副組長）
# Also possible: 多個來賓 by 、, or 來 賓: (extra space), or no parens
HOST_RE = re.compile(r'主\s*持\s*人\s*[:：]\s*([^\n（(]+?)(?:\s*[（(]\s*([^\n）)]+?)\s*[)）])?\s*(?:\n|$)')
GUEST_RE = re.compile(r'來\s*賓\s*[:：]\s*([^\n（(]+?)(?:\s*[（(]\s*([^\n）)]+?)\s*[)）])?\s*(?:\n|$)')

rows = []
parse_fail = 0
no_desc = 0
for idx, e in enumerate(entries, 1):
    eid = e['id']
    desc_file = DESC_DIR / f"{eid}.txt"
    meta_file = DESC_DIR / f"{eid}.meta.txt"

    if not desc_file.exists():
        rows.append([idx, eid, "", "", "", "", "", "", "[NO_DESC_FILE]"])
        no_desc += 1
        continue

    desc = desc_file.read_text(encoding='utf-8', errors='replace')
    meta = meta_file.read_text(encoding='utf-8', errors='replace').strip() if meta_file.exists() else ""
    meta_parts = meta.split('\t', 1)
    date = meta_parts[0] if meta_parts else ""
    title = meta_parts[1] if len(meta_parts) > 1 else ""

    host_m = HOST_RE.search(desc)
    guest_m = GUEST_RE.search(desc)
    host_name = host_m.group(1).strip() if host_m else ""
    host_org = (host_m.group(2) or "").strip() if host_m else ""
    guest_name = guest_m.group(1).strip() if guest_m else ""
    guest_org = (guest_m.group(2) or "").strip() if guest_m else ""
    flag = "" if (host_name and guest_name) else "REVIEW"
    if not host_name and not guest_name:
        parse_fail += 1
    rows.append([idx, eid, date, title, host_name, host_org, guest_name, guest_org, flag])

# write CSV
csv_path = OUT_DIR / "southtech_hosts_guests.csv"
with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(["集數", "影片ID", "上架日", "標題", "主持人", "主持人單位", "來賓", "來賓單位", "備註"])
    w.writerows(rows)
print(f"     CSV: {csv_path}", flush=True)

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

# write unique tables
hosts_path = OUT_DIR / "unique_hosts.csv"
with open(hosts_path, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(["主持人", "出場次數", "單位（可能多）"])
    for n, c in sorted(hosts.items(), key=lambda x: -x[1]):
        orgs = " | ".join(sorted(host_orgs.get(n, set())))
        w.writerow([n, c, orgs])

guests_path = OUT_DIR / "unique_guests.csv"
with open(guests_path, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(["來賓", "出場次數", "單位（可能多）"])
    for n, c in sorted(guests.items(), key=lambda x: -x[1]):
        orgs = " | ".join(sorted(guest_orgs.get(n, set())))
        w.writerow([n, c, orgs])

print(f"\n=== SUMMARY ===", flush=True)
print(f"Total episodes: {len(rows)}", flush=True)
print(f"No description file: {no_desc}", flush=True)
print(f"Parse failed (both host+guest empty): {parse_fail}", flush=True)
print(f"Unique hosts: {len(hosts)}", flush=True)
print(f"Unique guests: {len(guests)}", flush=True)
print(f"\nTop 10 hosts:", flush=True)
for n, c in sorted(hosts.items(), key=lambda x: -x[1])[:10]:
    print(f"  {c:3d}  {n}", flush=True)
print(f"\nTop 15 guests:", flush=True)
for n, c in sorted(guests.items(), key=lambda x: -x[1])[:15]:
    print(f"  {c:3d}  {n}", flush=True)
