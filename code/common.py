import re, pathlib, unicodedata, datetime as dt

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "wiki"
CLEAN = ROOT / "data" / "clean"
OUT = ROOT / "outputs"
CHARTS = OUT / "charts"
for p in (CLEAN, OUT, CHARTS):
    p.mkdir(parents=True, exist_ok=True)


def film_key(raw_title: str, year: int = 2025) -> str:
    """'Saiyaara (film)' / 'SAIYAARA - Official Trailer' / 'Saiyaara (2025)' -> 'saiyaara_2025'"""
    t = unicodedata.normalize("NFKD", raw_title).encode("ascii", "ignore").decode()
    t = t.lower()
    t = re.sub(r"\((?:\d{4}\s*)?(?:[a-z]+\s)?film\)|\(\d{4}\)", "", t)
    t = re.sub(r"[-|:]\s*official.*$|trailer.*$|teaser.*$", "", t)
    t = re.sub(r"[^a-z0-9]+", "_", t).strip("_")
    return f"{t}_{year}"


def infobox_field(wt: str, name: str) -> str | None:
    m = re.search(r"\n\s*\|\s*" + name + r"\s*=(.*?)(?=\n\s*\|\s*[a-z_]+\s*=|\n}})", wt, re.S)
    return m.group(1).strip() if m else None


def strip_wikitext(s: str) -> str:
    s = re.sub(r"<ref[^>]*/>", "", s)
    s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"\{\{INRConvert\|([\d.]+)\|c[^}]*\}\}", r"₹\1 crore", s)
    s = re.sub(r"\{\{INR\}\}", "₹", s)
    s = re.sub(r"\{\{efn[^{}]*\}\}", "", s)
    for _ in range(4):
        s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    s = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\[https?://\S+\s([^\]]*)\]", r"\1", s)
    s = re.sub(r"'''?", "", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()


def section_text(wt: str, heading_regex: str) -> str:
    """Return raw wikitext of the first section whose heading matches, until next heading of same/higher level."""
    m = re.search(r"^(={2,4})\s*(" + heading_regex + r")\s*\1\s*$", wt, re.M | re.I)
    if not m:
        return ""
    level = len(m.group(1))
    rest = wt[m.end():]
    nxt = re.search(r"^={2," + str(level) + r"}[^=].*?={2," + str(level) + r"}\s*$", rest, re.M)
    return rest[: nxt.start()] if nxt else rest


def parse_film_date(released: str | None):
    if not released:
        return None

    ms = re.findall(r"\|\s*(\d{4})\s*\|\s*(\d{1,2})\s*\|\s*(\d{1,2})", released)
    if ms:
        ms = [dt.date(int(y), int(mo), int(d)) for y, mo, d in ms]
        in_year = [d for d in ms if d.year == 2025]
        return (in_year or ms)[0]
    m = re.search(r"(\d{1,2})\s+([A-Z][a-z]+)\s+(\d{4})", strip_wikitext(released))
    if m:
        return dt.datetime.strptime(" ".join(m.groups()), "%d %B %Y").date()
    return None


def to_crore(text) -> float | None:
    """'₹1,350.83 crore' -> 1350.83 ; '₹90–130 crore' -> 110 (midpoint) ;
       '1,25,00,000' (rupees, Indian grouping) -> 1.25 ; '$5 million' -> None"""
    if text is None:
        return None
    s = str(text)
    s = re.sub(r"\[.*?\]", "", s)
    s = s.replace("–", "-").replace("—", "-")
    if re.search(r"US\$|\$|million", s) and "crore" not in s.lower():
        return None
    nums = [float(n.replace(",", "")) for n in re.findall(r"\d[\d,]*\.?\d*", s)]
    if not nums:
        return None
    if "crore" in s.lower() or "cr" in s.lower():
        vals = nums[:2] if re.search(r"\d\s*-\s*[₹]?\s*\d", s) else nums[:1]
        return round(sum(vals) / len(vals), 2)
    if "lakh" in s.lower():
        return round(nums[0] / 100, 2)
    if nums[0] > 1e5:
        return round(nums[0] / 1e7, 2)
    return None
