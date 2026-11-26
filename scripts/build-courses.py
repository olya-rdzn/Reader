#!/usr/bin/env python3
"""Rebuilds data/courses.json from the folders inside data/.

Folder layout:
  data/<course>/course.json        title + languages of the course (optional once courses.json knows it)
  data/<course>/NN-lecture-name.json   one file per lecture; NN = order (01, 02, 03 ...)
  data/<course>/img/               images (ignored here)

The top-level settings of courses.json (title, footer) are kept; only "courses" is rebuilt.
Run locally with:  python3 scripts/build-courses.py
"""
import json, os, re, sys, string

D = os.environ.get("DATA_DIR", "data")
CJ = os.path.join(D, "courses.json")
LESSON = re.compile(r"^(\d+)[-_](.+)\.json$")
SKIP = {"course.json", "courses.json"}

def fail(msg):
    print("ERROR: " + msg)
    sys.exit(1)

def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        fail(f"{path} is not valid JSON ({e})")

def natkey(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]

old = load(CJ) if os.path.exists(CJ) else {}
old_courses = {c.get("id"): c for c in old.get("courses", [])}
old_titles = {l.get("file"): l.get("title") for c in old_courses.values() for l in c.get("lessons", [])}

def text_of(v):
    if isinstance(v, list):
        v = v[0] if v else ""
    if isinstance(v, dict):
        v = v.get("x", "")
    return str(v).replace("\n", " ").strip()

def fallback_title(blocks, langs, stem):
    for b in blocks:
        if b.get("t") == "h2":
            for code in langs:
                t = text_of(b.get(code, ""))
                if t:
                    return string.capwords(t) if t.isupper() else t
    return stem.replace("-", " ").replace("_", " ").title()

def infer_languages(files):
    codes = []
    for p in files:
        for b in load(p).get("blocks", []):
            for k in b:
                if k not in ("t", "src", "alt") and k not in codes:
                    codes.append(k)
    return [{"code": c, "label": c.upper(), "name": c} for c in codes]

courses, warnings = [], []
for name in sorted(os.listdir(D), key=natkey):
    folder = os.path.join(D, name)
    if not os.path.isdir(folder):
        continue
    meta_path = os.path.join(folder, "course.json")
    meta = load(meta_path) if os.path.exists(meta_path) else {}
    jsons = sorted([f for f in os.listdir(folder) if f.endswith(".json") and f not in SKIP], key=natkey)
    if not jsons and not meta:
        continue
    cid = meta.get("id", name)
    base = old_courses.get(cid, {})
    paths = [os.path.join(folder, f) for f in jsons]
    langs = meta.get("languages") or base.get("languages") or infer_languages(paths)
    codes = [l["code"] for l in langs]

    if "lessons" in meta:                      # manual control: use the list exactly as written
        lessons = meta["lessons"]
    else:
        lessons, seen = [], set()
        for f in jsons:
            m = LESSON.match(f)
            if not m:
                warnings.append(f"{name}/{f}: ignored, the name must start with a number, e.g. 03-{f}")
                continue
            lesson = load(os.path.join(folder, f))
            if not isinstance(lesson.get("blocks"), list):
                fail(f'{name}/{f} has no "blocks" list')
            lid, rel = m.group(2), f"{name}/{f}"
            if lid in seen:
                fail(f"{name}: two lectures share the id '{lid}' ({f})")
            seen.add(lid)
            title = lesson.get("title") or old_titles.get(rel) or fallback_title(lesson["blocks"], codes, lid)
            lessons.append({"id": lid, "title": title, "file": rel})

    default_order = list(old_courses).index(cid) + 1 if cid in old_courses else 100
    courses.append((meta.get("order", default_order), natkey(name), {
        "id": cid,
        "title": meta.get("title") or base.get("title") or name.replace("-", " ").replace("_", " ").title(),
        "languages": langs,
        "lessons": lessons}))

courses.sort(key=lambda c: (c[0], c[1]))
out = {k: v for k, v in old.items() if k != "courses"}
out["courses"] = [c[2] for c in courses]
new = json.dumps(out, ensure_ascii=False, indent=1) + "\n"
old_text = open(CJ, encoding="utf-8").read() if os.path.exists(CJ) else ""
if new != old_text:
    with open(CJ, "w", encoding="utf-8") as f:
        f.write(new)
for w in warnings:
    print("WARNING: " + w)
print(f"{CJ}: {'updated' if new != old_text else 'unchanged'} - {len(out['courses'])} course(s), {sum(len(c['lessons']) for c in out['courses'])} lecture(s)")
