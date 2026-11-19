#!/usr/bin/env python3
"""
generate_index.py — Auto-generates homepage + recursive index pages
for a study-material folder tree (Board/Class/Subject/Book/Chapter).
Style matches the AIM SMART reference design.
"""

import os
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
IGNORE = {".git", ".github", "node_modules", "scripts"}

# ---------- Shared CSS (matches reference design) ----------
SHARED_CSS = """
* { margin:0; padding:0; box-sizing:border-box; }
body {
  font-family: 'Nunito', 'Inter', sans-serif;
  background: linear-gradient(145deg, #e0f2fe 0%, #bae6fd 40%, #d5f5e3 100%);
  color:#0f172a; line-height:1.5; padding:24px 16px; min-height:100vh;
}
.container { max-width:1200px; margin:0 auto; }
.hero {
  background: linear-gradient(135deg,#0a2e1a 0%,#1a4a2a 25%,#1e8449 60%,#0F766E 100%);
  border-radius:24px; padding:40px 32px; margin-bottom:28px; text-align:center;
  color:white; box-shadow:0 12px 40px rgba(0,0,0,.25);
  border:1px solid rgba(255,255,255,.12);
}
.hero-badge {
  background:rgba(30,132,73,.6); display:inline-block; padding:6px 22px;
  border-radius:40px; font-size:.8rem; font-weight:700; letter-spacing:1.5px;
  margin-bottom:14px; border:1px solid rgba(255,255,255,.15);
}
.hero h1 {
  font-family:'Playfair Display',serif; font-size:2.4rem; font-weight:900;
  margin-bottom:6px; text-shadow:0 4px 20px rgba(0,0,0,.3);
}
.hero h1 .highlight { color:#fcd34d; }
.hero .sub { font-size:1.05rem; opacity:.92; font-weight:600; }
.search {
  display:block; margin:20px auto 0; max-width:480px; width:100%;
  padding:12px 18px; border:none; border-radius:40px; font-size:15px;
  background:rgba(255,255,255,.95); box-shadow:0 4px 20px rgba(0,0,0,.15);
}
.section-header { display:flex; justify-content:space-between; align-items:center;
  margin-bottom:16px; flex-wrap:wrap; gap:8px; }
.section-header h2 { font-family:'Playfair Display',serif; font-size:1.6rem; color:#0a1628; }
.grid { display:grid; gap:18px; margin-bottom:28px;
  grid-template-columns:repeat(auto-fill, minmax(240px,1fr)); }
.card {
  display:block; background:linear-gradient(135deg,#d6eaf8,#aed6f1);
  border-radius:20px; padding:20px; text-decoration:none; color:inherit;
  box-shadow:0 4px 16px rgba(0,0,0,.06); border:1px solid rgba(255,255,255,.4);
  transition:transform .25s, box-shadow .25s; position:relative; overflow:hidden;
}
.card:nth-child(3n+2) { background:linear-gradient(135deg,#d5f5e3,#a9dfbf); }
.card:nth-child(3n+3) { background:linear-gradient(135deg,#e8daef,#d2b4de); }
.card::before { content:''; position:absolute; top:0; left:0; width:6px; height:100%;
  background:linear-gradient(180deg,#1e8449,#0F766E); }
.card:hover { transform:translateY(-6px); box-shadow:0 12px 32px rgba(0,0,0,.12); }
.card-icon { font-size:2rem; margin-bottom:6px; }
.card-title { font-weight:800; font-size:1.1rem; color:#0a1628; }
.card-meta { font-size:.8rem; color:#444; margin-top:4px; }
.card-foot { font-size:.72rem; color:#666; margin-top:10px;
  border-top:1px dashed rgba(0,0,0,.1); padding-top:6px; }
.breadcrumb {
  background:rgba(255,255,255,.75); border-radius:40px; padding:10px 22px;
  margin-bottom:20px; font-size:.85rem; font-weight:600;
  display:flex; flex-wrap:wrap; gap:6px; align-items:center;
}
.breadcrumb a { color:#0F766E; text-decoration:none; }
.breadcrumb a:hover { text-decoration:underline; }
.breadcrumb .sep { color:#999; }
.file-card {
  display:block; background:white; border-radius:16px; padding:18px 20px;
  text-decoration:none; color:inherit; box-shadow:0 2px 12px rgba(0,0,0,.06);
  border-left:5px solid #0F766E; transition:transform .2s;
}
.file-card:hover { transform:translateX(6px); box-shadow:0 4px 20px rgba(0,0,0,.1); }
.file-card .file-icon { font-size:1.4rem; margin-right:8px; }
.file-card .file-title { font-weight:700; color:#0a1628; }
.file-card .file-meta { font-size:.75rem; color:#666; margin-top:4px; }
.footer {
  background:linear-gradient(135deg,#0a2e1a 0%,#1a4a2a 40%,#1E8449 80%,#0F766E 100%);
  color:white; text-align:center; padding:28px 32px; border-radius:24px;
  margin-top:36px; border:1px solid rgba(255,255,255,.08);
  box-shadow:0 8px 40px rgba(0,0,0,.2);
}
.footer strong { color:#fcd34d; }
.footer .brand { font-size:1.1rem; font-weight:700; letter-spacing:1px; }
.footer .brand span { color:#fcd34d; }
.footer .sub-text { font-size:.85rem; opacity:.85; margin-top:4px; }
@media (max-width:768px) {
  .hero h1 { font-size:1.6rem; } .hero { padding:28px 18px; }
  .grid { grid-template-columns:repeat(auto-fill, minmax(160px,1fr)); }
}
"""

FONTS_AND_HEAD = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400;14..32,600;14..32,800&family=Playfair+Display:wght@700;900&family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
"""

# ---------- Helpers ----------
def list_subdirs(path):
    return sorted([d for d in os.listdir(path)
                   if os.path.isdir(os.path.join(path, d)) and d not in IGNORE])

def list_htmls(path):
    return sorted([f for f in os.listdir(path)
                   if f.lower().endswith((".html", ".htm")) and f != "index.html"])

def count_materials(path):
    n = 0
    for r, _, fs in os.walk(path):
        n += sum(1 for f in fs if f.lower().endswith((".html", ".htm")) and f != "index.html")
    return n

def latest_mtime(path):
    latest = 0
    for r, _, fs in os.walk(path):
        for f in fs:
            if f.lower().endswith((".html", ".htm")) and f != "index.html":
                latest = max(latest, os.path.getmtime(os.path.join(r, f)))
    return latest

def fmt_date(ts):
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d") if ts else "—"

# ---------- Page builders ----------
def build_page(title, breadcrumb_html, body_html):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
{FONTS_AND_HEAD}
<style>{SHARED_CSS}</style>
</head>
<body>
<div class="container">
{breadcrumb_html}
{body_html}
<div class="footer">
  <div class="brand">🏫 <span>AIM SMART</span> EDUCATION</div>
  <div class="sub-text">Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
</div>
</div>
</body>
</html>"""

def build_breadcrumb(rel_parts):
    """rel_parts = path components relative to ROOT."""
    if not rel_parts:
        return ""
    crumbs = ['<a href="/">🏠 Home</a>']
    href = "/"
    for part in rel_parts:
        href = href.rstrip("/") + "/" + part
        crumbs.append('<span class="sep">›</span>')
        crumbs.append(f'<a href="{href}/index.html">{part}</a>')
    return '<div class="breadcrumb">' + ''.join(crumbs) + '</div>'

def write_index_for_dir(dirpath, rel_parts):
    """Write index.html inside dirpath listing subdirs + html files."""
    subdirs = list_subdirs(dirpath)
    htmls = list_htmls(dirpath)
    if not subdirs and not htmls:
        return  # nothing to index

    title = rel_parts[-1] if rel_parts else "Study Hub"
    crumb = build_breadcrumb(rel_parts)

    cards = ""
    for d in subdirs:
        full = os.path.join(dirpath, d)
        n_mat = count_materials(full)
        latest = fmt_date(latest_mtime(full))
        cards += f'''
        <a class="card" href="{d}/index.html">
          <div class="card-icon">📁</div>
          <div class="card-title">{d}</div>
          <div class="card-meta">{n_mat} material{'s' if n_mat!=1 else ''}</div>
          <div class="card-foot">Updated {latest}</div>
        </a>'''

    files = ""
    for f in htmls:
        size_kb = os.path.getsize(os.path.join(dirpath, f)) // 1024
        files += f'''
        <a class="file-card" href="{f}">
          <span class="file-icon">📄</span>
          <span class="file-title">{f}</span>
          <div class="file-meta">{size_kb} KB</div>
        </a>'''

    body = f'''
    <div class="hero">
      <div class="hero-badge">📘 STUDY MATERIALS</div>
      <h1>{title}</h1>
      <div class="sub">{len(subdirs)} folders · {len(htmls)} files</div>
    </div>
    {crumb}
    <div class="section-header"><h2>📂 Contents</h2></div>
    <div class="grid">{cards}</div>
    {('<div class="section-header"><h2>📄 Files</h2></div><div class="grid">' + files + '</div>') if files else ''}
    '''

    html = build_page(f"{title} — Study Hub", "", body)
    with open(os.path.join(dirpath, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"  wrote {os.path.join(dirpath, 'index.html')}")

def walk_and_generate(dirpath, rel_parts):
    for d in list_subdirs(dirpath):
        walk_and_generate(os.path.join(dirpath, d), rel_parts + [d])
    write_index_for_dir(dirpath, rel_parts)

# ---------- Homepage ----------
def generate_homepage():
    boards = list_subdirs(ROOT)
    cards = ""
    for b in boards:
        full = os.path.join(ROOT, b)
        n_cls = len(list_subdirs(full))
        n_mat = count_materials(full)
        latest = fmt_date(latest_mtime(full))
        cards += f'''
        <a class="card" href="{b}/index.html">
          <div class="card-icon">🏛️</div>
          <div class="card-title">{b}</div>
          <div class="card-meta">{n_cls} Classes · {n_mat} materials</div>
          <div class="card-foot">Updated {latest}</div>
        </a>'''

    body = f'''
    <div class="hero">
      <div class="hero-badge">📘 CBSE • ICSE • STATE BOARDS</div>
      <h1>🏫 <span class="highlight">AIM SMART</span> Study Hub</h1>
      <div class="sub">Select your board to begin</div>
      <input class="search" id="search" placeholder="🔍 Search board...">
    </div>
    <div class="section-header"><h2>📚 Available Boards</h2></div>
    <div class="grid" id="grid">{cards}</div>
    <script>
      document.getElementById('search').addEventListener('input', e => {{
        const q = e.target.value.toLowerCase();
        document.querySelectorAll('.card').forEach(c => {{
          c.style.display = c.textContent.toLowerCase().includes(q) ? '' : 'none';
        }});
      }});
    </script>
    '''

    html = build_page("AIM SMART Study Hub", "", body)
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"  wrote {os.path.join(ROOT, 'index.html')}")

# ---------- Main ----------
if __name__ == "__main__":
    print("Generating index pages...")
    generate_homepage()
    walk_and_generate(ROOT, [])
    print("Done.")
