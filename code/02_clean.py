import json, re
from io import StringIO
import numpy as np
import pandas as pd
from common import (RAW, CLEAN, OUT, film_key, infobox_field, strip_wikitext,
                    section_text, parse_film_date, to_crore)

LOG = []


def log(area, problem, rows, action, why):
    LOG.append(dict(step=len(LOG) + 1, area=area, problem=problem,
                    rows_affected=rows, action=action, why=why))


film_pages = json.loads((RAW / "film_pages.json").read_text(encoding="utf-8"))
LANGS = sorted({l for l, _ in film_pages})

frames = []
for lang in LANGS:
    d = json.loads((RAW / f"list_{lang}_2025.json").read_text(encoding="utf-8"))
    html = d["parse"]["text"]["*"]
    tables = pd.read_html(StringIO(html))
    t = next(t for t in tables if any("gross" in str(c).lower() for c in t.columns))
    t.columns = [re.sub(r"\[.*?\]", "", str(c)).strip() for c in t.columns]
    gcol = next(c for c in t.columns if "gross" in c.lower())
    t = t.rename(columns={gcol: "gross_raw", "Title": "title_list"})[["title_list", "gross_raw"]]
    t["language"] = lang
    frames.append(t)
gross = pd.concat(frames, ignore_index=True)
n_raw = len(gross)
gross["title_list"] = gross["title_list"].astype(str).str.replace(r"\s*#\s*$|\[.*?\]", "", regex=True).str.strip()
log("Box office table", "Film names had extra marks like '#' and '[a]'",
    n_raw, "Removed these marks", "Names must be the same in every source, or the join fails")

gross["worldwide_gross_cr"] = gross["gross_raw"].map(to_crore)
bad = gross["worldwide_gross_cr"].isna().sum()
log("Type casting", "Money was text, like '₹1,350.83 crore' or a range like '₹90–130 crore'",
    n_raw, f"Changed to a number in crore. For a range we took the middle value. Rows not converted: {bad}",
    "We need numbers to do maths and make charts")
gross["film_id"] = gross["title_list"].map(film_key)
gross = gross.drop_duplicates("film_id")

rows, sentences, buzz = [], [], []
REDIRECT_ROWS = []
for lang, title in film_pages:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", title).strip("_")
    art = json.loads((RAW / f"article_{slug}.json").read_text(encoding="utf-8"))["parse"]
    wt = art["wikitext"]["*"]
    rel = parse_film_date(infobox_field(wt, "released"))
    runtime_raw = infobox_field(wt, "runtime")
    runtime = re.search(r"(\d{2,3})\s*min", runtime_raw or "")
    budget_raw = infobox_field(wt, "budget")
    budget_cr = to_crore(strip_wikitext(budget_raw)) if budget_raw else None

    bo = strip_wikitext(section_text(wt, r"box[ -]office"))
    op_day = None
    for sent in re.split(r"(?<=[.!?])\s+", bo):
        if re.search(r"opening day|first day|day one|day 1\b|opened with|opening of", sent, re.I):
            m = re.search(r"₹\s?([\d,.]+)\s*crore", sent)
            if m:
                op_day = float(m.group(1).replace(",", ""))
                break
    op_wkd = None
    for sent in re.split(r"(?<=[.!?])\s+", bo):
        if re.search(r"opening weekend|first weekend", sent, re.I):
            m = re.findall(r"₹\s?([\d,.]+)\s*crore", sent)
            if m:
                op_wkd = float(m[0].replace(",", ""))
                break

    fid = film_key(art["title"])
    rows.append(dict(film_id=fid, wiki_title=art["title"], language=lang, release_date=rel,
                     runtime_min=int(runtime.group(1)) if runtime else None,
                     budget_raw=strip_wikitext(budget_raw)[:60] if budget_raw else None,
                     budget_cr=budget_cr, opening_day_cr=op_day, opening_weekend_cr=op_wkd))

    crit = section_text(wt, r"critical (?:reception|response)|reviews?|critical reviews")
    text = strip_wikitext(crit)
    for i, s in enumerate(re.split(r"(?<=[.!?])\s+(?=[A-Z\"'])", text)):
        s = s.strip()
        if len(s) > 25:
            sentences.append(dict(film_id=fid, sentence_no=i, source="wikipedia_critic_reception", text=s))

    pv = json.loads((RAW / f"pageviews_{slug}.json").read_text(encoding="utf-8"))
    if "items" in pv:
        p = pd.json_normalize(pv["items"])[["timestamp", "views"]]
        p["date"] = pd.to_datetime(p["timestamp"].str[:8], format="%Y%m%d")
        p["film_id"] = fid
        buzz.append(p[["film_id", "date", "views"]])
    rp = RAW / f"redirect_pageviews_{slug}.json"
    if rp.exists():
        for rtitle, items in json.loads(rp.read_text(encoding="utf-8")).items():
            if items:
                p = pd.json_normalize(items)[["timestamp", "views"]]
                p["date"] = pd.to_datetime(p["timestamp"].str[:8], format="%Y%m%d")
                p["film_id"] = fid
                REDIRECT_ROWS.append(len(p))
                buzz.append(p[["film_id", "date", "views"]])

    revs = json.loads((RAW / f"revisions_{slug}.json").read_text(encoding="utf-8"))
    page = next(iter(revs["query"]["pages"].values()))
    r = pd.json_normalize(page.get("revisions", []))
    if len(r):
        r["date"] = pd.to_datetime(r["timestamp"]).dt.tz_localize(None).dt.normalize()
        e = r.groupby("date").size().rename("edits").reset_index()
        e["film_id"] = fid
        buzz.append(e)

films = pd.DataFrame(rows)
log("Film name matching", "Same film had different names, like 'Saiyaara' and 'Saiyaara (film)', or 'Coolie (2025 film)'",
    len(films), "Made one key for each film: small letters, removed '(film)' and '(2025 film)', spaces to '_', added '_2025'",
    "With one key, all sources can be joined")

films = films.merge(gross[["film_id", "worldwide_gross_cr", "gross_raw"]], on="film_id", how="left")
unmatched = films["worldwide_gross_cr"].isna().sum()
log("Join", "Films that did not match the box office table",
    int(unmatched), "Kept the film, left money empty", "We should not make up a number")

films["release_date"] = pd.to_datetime(films["release_date"])
log("Type casting", "Release date was text, like '14 February 2025' or a wiki code", len(films),
    "Changed to a date", "We need the date to count days before and after release")
log("Type casting", "Runtime was text, like '161 minutes'", len(films),
    "Changed to a whole number of minutes", "So we can compare runtimes")
nb = films["budget_cr"].isna().sum()
log("Missing values", "Budget was missing or only given in US dollars", int(nb),
    "Left it empty. For a range we took the middle value",
    "Budget numbers are guesses on Wikipedia. Filling them would make up data. We do not use budget in the main result")
no = films["opening_day_cr"].isna().sum()
log("Missing values", "Opening day money was not written in the article", int(no),
    "Left it empty", "This is a result number. Filling it would change the result")

mv = json.loads((RAW / "moved_pageviews_Saiyaara.json").read_text(encoding="utf-8"))
p = pd.json_normalize(mv["items"])[["timestamp", "views"]]
p["date"] = pd.to_datetime(p["timestamp"].str[:8], format="%Y%m%d")
p = p[p["date"] < "2025-09-04"]
p["film_id"] = "saiyaara_2025"
buzz.append(p[["film_id", "date", "views"]])
log("Film name matching", "Saiyaara's Wikipedia page was renamed on 4 Sep 2025. Before that its views were under the old name 'Saiyaara'",
    len(p), "Added the views of the old name, only for dates before 4 Sep 2025",
    "Without this, the biggest word-of-mouth hit of 2025 showed almost no views in release week")
b = pd.concat(buzz, ignore_index=True)
log("Film name matching", "Wikipedia counts views for each page name. Old names of a page (redirects) have their own views",
    int(sum(REDIRECT_ROWS)), "Took views of every old name and added them to the film",
    "Otherwise some films look less popular than they were")
b = b.groupby(["film_id", "date"], as_index=False).agg(views=("views", "sum"), edits=("edits", "sum"))
full = []
for fid, g in b.groupby("film_id"):
    rng = pd.date_range(g["date"].min(), g["date"].max(), freq="D")
    g = g.set_index("date").reindex(rng).rename_axis("date").reset_index()
    g["film_id"] = fid
    full.append(g)
b = pd.concat(full, ignore_index=True)
gaps = int(b["views"].isna().sum())
b["views"] = b["views"].fillna(0).astype(int)
b["edits"] = b["edits"].fillna(0).astype(int)
log("Missing values", "Some days were missing in the views and edits data", gaps,
    "Filled with 0", "The website skips a day only when nothing happened that day, so 0 is correct")
b = b.merge(films[["film_id", "release_date"]], on="film_id")
b["day_from_release"] = (b["date"] - b["release_date"]).dt.days
b = b[(b["day_from_release"] >= -30) & (b["day_from_release"] <= 60)].drop(columns="release_date")
log("Filtering", "We had views from Nov 2024 to Feb 2026", len(b),
    "Kept only 30 days before to 60 days after release", "Same time window for every film, so the comparison is fair")


def feats(g):
    g = g.set_index("day_from_release")["views"]
    pre = g.loc[-7:-1].sum()
    wk1 = g.loc[0:6].sum()
    peak_day = int(g.idxmax())
    peak = g.max()
    after = g.loc[peak_day:]
    below = after[after < peak / 2]
    half_life = int(below.index[0] - peak_day) if len(below) else None
    return pd.Series(dict(prerelease_views_7d=int(pre), release_week_views=int(wk1),
                          peak_views=int(peak), peak_day=peak_day, buzz_half_life_days=half_life,
                          day60_vs_peak=round(g.loc[50:60].mean() / peak, 3) if peak else None))


f = b.groupby("film_id")[["day_from_release", "views"]].apply(feats).reset_index()
films = films.merge(f, on="film_id", how="left")
first_day = b[b["views"] > 0].groupby("film_id")["day_from_release"].min()
late = first_day[first_day > -7].index
films.loc[films["film_id"].isin(late), "prerelease_views_7d"] = np.nan
log("Missing values", "The Wikipedia page was made less than 7 days before release. So views before release show 0, "
    "but only because the page did not exist", len(late),
    "Left 'views before release' empty for: " + ", ".join(late),
    "0 views and 'page did not exist' are not the same thing")

s = pd.DataFrame(sentences)
before = len(s)
s["text"] = s["text"].str.replace(r"https?://\S+|@\w+", "", regex=True).str.strip()
s = s[s["text"].str.len() > 25].drop_duplicates(["film_id", "text"])
log("Text cleaning", "Critic text had wiki codes, links and repeated lines",
    before, f"Removed codes, links and @names. Removed very short and repeated lines. {len(s)} lines left",
    "The sentiment tool needs clean sentences. Also we must not keep people's user names")
nt = (~films["film_id"].isin(s["film_id"])).sum()
log("Missing values", "Some film pages had no critic review section", int(nt),
    "Kept the film, left critic score empty", "We should not make up a score")

films["log_prerelease_views"] = np.log10(films["prerelease_views_7d"].clip(lower=1))
films["log_gross"] = np.log10(films["worldwide_gross_cr"])
for c in ["log_prerelease_views", "log_gross"]:
    films["z_" + c] = (films[c] - films[c].mean()) / films[c].std()
films["gross_per_1k_prerelease_views"] = (films["worldwide_gross_cr"] / (films["prerelease_views_7d"] / 1000)).round(3)
log("Normalisation", "Films are very different in size (Rs 16 crore to Rs 1,350 crore)", len(films),
    "Used log and z-score. Also made 'money per 1,000 views'",
    "So a small Kannada film and a big Hindi film can be compared fairly")

films.to_csv(CLEAN / "films.csv", index=False)
b.to_csv(CLEAN / "daily_buzz.csv", index=False)
s.to_csv(CLEAN / "critic_sentences.csv", index=False)
gross.to_csv(CLEAN / "boxoffice_list_tables.csv", index=False)
pd.DataFrame(LOG).to_csv(OUT / "cleaning_log.csv", index=False)
print("films", len(films), "| daily rows", len(b), "| critic lines", len(s), "| log rows", len(LOG))
