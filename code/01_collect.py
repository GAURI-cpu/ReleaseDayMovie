"""Gets the raw data from Wikipedia and saves it."""
import json, time, re, pathlib, datetime as dt
import urllib.request, urllib.parse
from common import infobox_field, parse_film_date

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "wiki"
RAW.mkdir(parents=True, exist_ok=True)

API = "https://en.wikipedia.org/w/api.php"
PV = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{}/daily/{}/{}"
HEADERS = {"User-Agent": "ReleaseDayRadar-student-project/0.1 (educational case study)"}
LANGS = ["Hindi", "Telugu", "Tamil", "Kannada", "Malayalam"]
TOP_N = 5
PAUSE = 1.5


def get_json(url, params=None):
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    last = None
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            last = e
            time.sleep(10 * (attempt + 1))
    raise last


def save(name, obj):
    (RAW / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


film_pages = []
for lang in LANGS:
    page = f"List_of_{lang}_films_of_2025"
    d = get_json(API, {"action": "parse", "page": page, "prop": "text|wikitext",
                       "section": 1, "format": "json", "redirects": 1})
    save(f"list_{lang}_2025.json", d)
    wt = d["parse"]["wikitext"]["*"]

    titles = re.findall(r"\|\s*''\[\[([^\]|]+)(?:\|[^\]]*)?\]\]''", wt)
    seen = []
    for t in titles:
        if t not in seen:
            seen.append(t)


    taken = {t for _, t in film_pages}
    keep = [t for t in seen if t not in taken
            and not re.search(r"Express|Times|Hindustan|Hungama|Sacnilk|\(India\)", t)][:TOP_N]
    film_pages.extend((lang, t) for t in keep)
    print(f"{lang}: {keep}")
    time.sleep(PAUSE)

save("film_pages.json", film_pages)


for lang, title in film_pages:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", title).strip("_")
    if (RAW / f"pageviews_{slug}.json").exists():
        print("cached", title); continue
    art = get_json(API, {"action": "parse", "page": title, "prop": "wikitext|sections",
                         "format": "json", "redirects": 1})
    save(f"article_{slug}.json", art)
    time.sleep(PAUSE)


    rel = parse_film_date(infobox_field(art["parse"]["wikitext"]["*"], "released"))
    start = (rel - dt.timedelta(days=30)).isoformat() + "T00:00:00Z" if rel else "2024-11-01T00:00:00Z"
    revs = get_json(API, {"action": "query", "prop": "revisions", "titles": title,
                          "rvprop": "timestamp|size", "rvlimit": 500, "rvdir": "newer",
                          "rvstart": start, "format": "json", "redirects": 1})
    save(f"revisions_{slug}.json", revs)
    time.sleep(PAUSE)


    canonical = art["parse"]["title"].replace(" ", "_")
    try:
        pv = get_json(PV.format(urllib.parse.quote(canonical, safe=""), "20241101", "20260228"))
    except Exception as e:
        pv = {"error": str(e)}
    save(f"pageviews_{slug}.json", pv)
    print("collected", lang, title)
    time.sleep(PAUSE)

(RAW / "_collected_at.txt").write_text(dt.datetime.now().isoformat(), encoding="utf-8")
print("done:", len(film_pages), "films")
