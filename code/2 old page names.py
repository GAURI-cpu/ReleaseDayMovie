import json, time, re, urllib.parse
from common import RAW

API = "https://en.wikipedia.org/w/api.php"
PV = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{}/daily/20241101/20260228"
import urllib.request
HEADERS = {"User-Agent": "ReleaseDayRadar-student-project/0.1 (educational case study)"}

def get_json(url, params=None):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    for attempt in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=40) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {"items": []}
            time.sleep(10 * (attempt + 1))
    return {"error": "failed"}

film_pages = json.loads((RAW / "film pages.json").read_text(encoding="utf-8"))
for lang, title in film_pages:
    slug = re.sub(r"[^A-Za-z0-9]+", " ", title).strip()
    out = RAW / f"redirect pageviews {slug}.json"
    if out.exists():
        continue
    d = get_json(API, {"action": "query", "prop": "redirects", "titles": title, "rdlimit": 50,
                       "format": "json", "redirects": 1})
    page = next(iter(d["query"]["pages"].values()))
    reds = [r["title"] for r in page.get("redirects", [])]
    res = {}
    for rt in reds:
        pv = get_json(PV.format(urllib.parse.quote(rt.replace(" ", "_"), safe="")))
        items = pv.get("items", [])
        if sum(i["views"] for i in items) > 0:
            res[rt] = items
        time.sleep(0.2)
    out.write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
    print(title, "redirects:", len(reds), "with views:", len(res))
    time.sleep(1)
