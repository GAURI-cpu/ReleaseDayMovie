import re, sqlite3
import pandas as pd
from common import ROOT, CLEAN, OUT

SQL = ROOT / "sql"
films = pd.read_csv(CLEAN / "films.csv")
bo = films[["film_id", "gross_raw", "worldwide_gross_cr"]].copy()
bo["source_page"] = "List of " + films["language"] + " films of 2025"
buzz = pd.read_csv(CLEAN / "daily_buzz.csv").rename(columns={"date": "buzz_date"})
crit = pd.read_csv(CLEAN / "critic_sentences.csv").rename(columns={"text": "sentence_text"})

tables = {
    "films": films[["film_id", "wiki_title", "language", "release_date", "runtime_min", "budget_cr",
                    "opening_day_cr", "prerelease_views_7d", "release_week_views", "peak_day",
                    "buzz_half_life_days"]],
    "boxoffice": bo,
    "daily_buzz": buzz[["film_id", "buzz_date", "day_from_release", "views", "edits"]],
    "critic_sentences": crit[["film_id", "sentence_text", "vader_compound", "sentiment_label", "aspect"]],
}

def lit(v):
    if pd.isna(v):
        return "NULL"
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return repr(float(v)) if isinstance(v, float) and not float(v).is_integer() else str(int(v))
    return "'" + str(v).replace("\\", "\\\\").replace("'", "''") + "'"

with open(SQL / "load_data_mysql.sql", "w", encoding="utf-8") as fh:
    fh.write("USE release_day_radar;\n")
    for name, df in tables.items():
        cols = ", ".join(df.columns)
        for rec in df.itertuples(index=False):
            fh.write(f"INSERT INTO {name} ({cols}) VALUES ({', '.join(lit(v) for v in rec)});\n")


ddl = (SQL / "schema_mysql.sql").read_text(encoding="utf-8")
ddl = re.sub(r"^(CREATE DATABASE|USE).*$", "", ddl, flags=re.M)
ddl = ddl.replace("AUTO_INCREMENT PRIMARY KEY", "PRIMARY KEY AUTOINCREMENT").replace("INT PRIMARY KEY AUTOINCREMENT", "INTEGER PRIMARY KEY AUTOINCREMENT")
db = ROOT / "data" / "clean" / "release_day_radar.sqlite"
db.unlink(missing_ok=True)
con = sqlite3.connect(db)
con.executescript(ddl)
for name, df in tables.items():
    df.to_sql(name, con, if_exists="append", index=False)

counts = {n: con.execute(f"SELECT COUNT(*) FROM {n}").fetchone()[0] for n in tables}
qtext = (SQL / "queries.sql").read_text(encoding="utf-8")
blocks = re.split(r"\n(?=-- Q\d+:)", qtext)
md = ["# SQL results\n", "Row counts: " + ", ".join(f"`{k}` = {v}" for k, v in counts.items()) + "\n"]
for b in blocks:
    m = re.match(r"-- (Q\d+:.*)", b)
    if not m:
        continue
    q = "\n".join(l for l in b.splitlines() if not l.startswith("--")).strip()
    res = pd.read_sql_query(q, con)
    md += [f"\n## {m.group(1)}\n", "```sql\n" + q + "\n```\n", res.head(25).to_markdown(index=False) + "\n"]
    print(m.group(1), "->", len(res), "rows")
(OUT / "sql_results.md").write_text("\n".join(md), encoding="utf-8")
print("row counts", counts)
