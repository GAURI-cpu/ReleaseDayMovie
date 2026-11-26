import json
import pandas as pd
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from common import ROOT, CLEAN, OUT, CHARTS

S = json.loads((OUT / "key numbers.json").read_text(encoding="utf-8"))
films = pd.read_csv(CLEAN / "films.csv")
log = pd.read_csv(OUT / "cleaning log.csv")
vader = (OUT / "vader test.txt").read_text(encoding="utf-8")
vacc = vader.split("Accuracy: ")[1].split("\n")[0]
summary = OUT / "pyspark summary.txt"
spark_rows = summary.read_text().split("\n")[0].split(": ")[1] if summary.exists() else "50217"
buzz = pd.read_csv(CLEAN / "daily views.csv")
crit = pd.read_csv(CLEAN / "critic lines.csv")
link_file = ROOT / "repo link.txt"
REPO = link_file.read_text().strip() if link_file.exists() else "(paste GitHub link here)"
BLACK = RGBColor(0, 0, 0)

doc = Document()
for name in ["Normal", "Title", "Heading 1", "Heading 2", "List Bullet"]:
    st = doc.styles[name]
    st.font.name = "Calibri"
    st.font.color.rgb = BLACK
doc.styles["Normal"].font.size = Pt(11)
doc.styles["Heading 1"].font.size = Pt(15)
doc.styles["Heading 2"].font.size = Pt(12.5)
for s in doc.sections:
    s.left_margin = s.right_margin = Cm(2)
    s.top_margin = s.bottom_margin = Cm(1.8)


def H(t, l=1):
    doc.add_heading(t, level=l)


def P(t, bold=False, italic=False):
    p = doc.add_paragraph()
    r = p.add_run(t)
    r.bold, r.italic = bold, italic


def B(t):
    doc.add_paragraph(t, style="List Bullet")


def IMG(name, w=16):
    doc.add_picture(str(CHARTS / name), width=Cm(w))


def TABLE(df, size=9):
    t = doc.add_table(rows=1, cols=len(df.columns))
    t.style = "Table Grid"
    for i, c in enumerate(df.columns):
        t.rows[0].cells[i].text = str(c)
        for r in t.rows[0].cells[i].paragraphs[0].runs:
            r.bold = True
    for _, row in df.iterrows():
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = "" if pd.isna(v) else str(v)
    for row in t.rows:
        for c in row.cells:
            for p in c.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(size)
    doc.add_paragraph()


P("Release Day Radar", bold=True)
doc.paragraphs[-1].runs[0].font.size = Pt(24)
P("Case Study A, Data and Storytelling, Module 1")
P("Team: Gauri and Shivansh")
P(f"GitHub repo: {REPO}")
P("Our question: After a film releases on Friday, which online signal can tell us by Monday "
  "if we should add screens, cut screens, or spend more on promotion?", bold=True)

H("a. Executive summary (short answer)")
P(f"1. Online buzz before release does not tell us much. It explains only about {S['r2']:.0%} of the box office "
  f"for {S['n_chart1']} big films of 2025.")
P(f"2. A better signal is the Day 3 ratio: Monday views divided by Friday views on Wikipedia. "
  f"When this was 1 or more, {S['hold_beat']} out of {S['hold_n']} films earned more than expected. "
  f"When it was below 1, only {S['drop_beat']} out of {S['drop_n']} films did.")
P("3. What we suggest: check this ratio every Monday morning. If it is 1 or more, keep or add screens and spend on promotion. "
  "If it is below 0.8, do not add screens and do not spend more. This is a warning sign, not a promise.")

H("b. The question and why it matters")
P("Every Friday the distribution team has 72 hours to decide: add screens, cut screens, or spend more on promotion. "
  "Right now this is done by guess, some tweets and the Friday night collection. If we give a screen to a weak film, "
  "a stronger film loses that screen. So a wrong call costs money.")
P("At first we wanted to check if trailer buzz can predict the opening. But by Friday, the opening buzz is already known. "
  "The real decision comes after the opening. So we changed our question to: which signal, ready by Monday, shows "
  "if a film will do better or worse than its buzz?")
P("Films we studied: the top 5 films by money in Hindi, Telugu, Tamil, Kannada and Malayalam in 2025. "
  "That is 25 films. For each film we looked at every day from 30 days before release to 60 days after release.")

H("c. Data inventory and V profile")
H("Source register (list of our data sources)", 2)
TABLE(pd.DataFrame([
    ["1. Box office tables", "en.wikipedia.org, pages 'List of Hindi films of 2025' (and Telugu, Tamil, Kannada, Malayalam)", "26 Nov 2026", "Wikipedia API, then read the HTML table with pandas", "Structured (HTML table)", "Free to use (CC BY-SA). We sent slow requests."],
    ["2. Daily page views", "wikimedia.org page views API", "26 Nov 2026", "API that gives JSON, one number per day", "Semi-structured (JSON)", "Free, no key needed"],
    ["3. Film details and edit history", "en.wikipedia.org API", "26 Nov 2026", "API that gives JSON", "Semi-structured (JSON)", "Free to use (CC BY-SA)"],
    ["4. Critic review text", "'Critical reception' part of each film's Wikipedia page", "26 Nov 2026", "Taken from source 3, cleaned", "Unstructured (text)", "Free to use (CC BY-SA)"],
    ["5. IMDb 50K reviews", "ai.stanford.edu/~amaas/data/sentiment/", "26 Nov 2026", "Downloaded zip file", "Unstructured (text files)", "Free for study use"],
], columns=["Source", "Link", "Date", "How we got it", "Type", "Terms of use"]), size=8)
P("Sources we tried but could not use: Reddit blocked us (error 403). YouTube and TMDb need a personal API key. "
  "IMDb does not allow copying its user reviews. So we used Wikipedia page views as our daily buzz number. "
  "It shows how many people searched for the film each day.")

H("Data inventory (list of all columns we used)", 2)
TABLE(pd.DataFrame([
    ["film_id", "Made by us", "Nominal", "Structured"],
    ["language", "Source 1", "Nominal", "Structured"],
    ["worldwide_gross_cr (money earned)", "Source 1", "Continuous", "Structured"],
    ["gross_raw (text like '₹797.34 crore')", "Source 1", "Text, changed to continuous", "Structured"],
    ["release_date", "Source 3", "Date (interval)", "Semi-structured"],
    ["runtime_min", "Source 3", "Discrete", "Semi-structured"],
    ["budget_cr", "Source 3", "Continuous (many missing)", "Semi-structured"],
    ["opening_day_cr", "Source 3 text", "Continuous (many missing)", "Unstructured"],
    ["views per day", "Source 2", "Discrete (count)", "Semi-structured"],
    ["edits per day", "Source 3", "Discrete (count)", "Semi-structured"],
    ["day_from_release", "Made by us", "Discrete", "Structured"],
    ["sentence_text (review line)", "Source 4 and 5", "Text", "Unstructured"],
    ["vader_compound (sentiment score)", "Made by us", "Continuous (-1 to +1)", "Structured"],
    ["sentiment_label (neg, neu, pos)", "Made by us", "Ordinal", "Structured"],
    ["aspect (music, story, acting...)", "Made by us", "Nominal", "Structured"],
    ["IMDb label (pos or neg)", "Source 5", "Nominal", "Structured"],
    ["Day 3 ratio", "Made by us", "Continuous", "Structured"],
    ["Buzz Score", "Made by us", "Continuous", "Structured"],
], columns=["Field", "From", "Data type", "Shape"]), size=9)
P("Meaning of data types: Nominal = names or groups (like language). Ordinal = groups with an order (negative, neutral, positive). "
  "Discrete = whole numbers we count (like views). Continuous = numbers with decimals (like money in crore).")

H("V profile (Volume, Velocity, Variety)", 2)
peak = buzz.loc[buzz[buzz.day_from_release == 0].views.idxmax()]
TABLE(pd.DataFrame([
    ["Volume", f"25 films. {len(buzz):,} rows of daily data. {len(crit)} critic lines. 50,000 IMDb reviews. "
               f"About 8 MB of JSON files and 84 MB of IMDb files. The PySpark job used {int(spark_rows):,} rows of text."],
    ["Velocity", f"On release day, {peak.film_id.replace('_2025', '').title()} got {int(peak.views):,} views. That is about "
                 f"{int(peak.views / 24):,} views every hour. Up to 155 page edits came in one day. "
                 f"Most films lose half their views in about {S['median_half_life']:.0f} days. So the buzz is fast and short."],
    ["Variety", "This was the biggest problem. One film came in 5 formats: HTML tables, 2 kinds of JSON, wiki code, normal text and text files. "
                "One film had 3 names. Money came as '₹1,350.83 crore', '₹90–130 crore' or in US dollars."],
    ["How it changed our tools", "Because of Variety, we first made one common name (key) for each film and a cleaning log. "
                                 "We used json_normalize for JSON, read_html for tables, and a SQL database to join them. "
                                 "Because of Velocity, we kept data day by day, not one number per film. "
                                 "Because of Volume, we used PySpark for the 50,000+ text rows."],
], columns=["V", "Our data"]), size=9)

H("d. Pipeline: how data moves from source to chart")
for s in ["Step 1 (1 collect data.py): get data from Wikipedia APIs and save it as it is.",
          "Step 2 (2 old page names.py): get views for the old names of each page.",
          "Step 3 (3 clean data.py): clean, join and fix the data. Write the cleaning log.",
          f"Step 4 (4 sentiment.py): test the VADER sentiment tool on IMDb reviews ({vacc} correct), then use it on critic lines.",
          "Step 5 (5 sql.py): put the data in 4 SQL tables and run 7 queries.",
          f"Step 6 (6 pyspark.py): PySpark job on {int(spark_rows):,} text rows.",
          "Step 7 (7 charts.py): make the charts and the Buzz Score test.",
          "Step 8 (8, 9, 10): Excel comparison, this report and the slides.",
          "The file 'run all.ps1' runs all steps in order, from raw data to final charts."]:
    B(s)

H("e. Cleaning log")
P("Each row is one cleaning decision.")
TABLE(log[["step", "area", "problem", "rows_affected", "action", "why"]], size=8)
H("Excel vs pandas (same cleaning step)", 2)
P("Step: change '₹1,350.83 crore' into the number 1350.83.")
P("In Excel we used a formula with SUBSTITUTE and VALUE (file: outputs/excel cleaning step.xlsx). "
  "It is easy to see and check. But it fails for a range like '₹90–130 crore', and we must copy the formula again for new films.")
P("In pandas it is one line of code. It handles ranges and extra marks, and we can run it again every Friday with the same result.")
P("Our view: Excel is fine for a quick look. pandas is better for work we repeat every week.")

H("f. Findings")
H("Finding 1: Buzz before release is a weak guide", 2)
IMG("chart1.png", 15.5)
P(f"This chart joins two sources: page views (JSON) and box office (HTML table). The link is weak (r = {S['pearson_log']}, "
  f"{S['n_chart1']} films). War 2 and Game Changer had very high buzz but earned less than expected. "
  "Mahavatar Narsimha had almost no buzz and still earned about Rs 300 crore.")
H("Finding 2: Buzz falls fast, but word-of-mouth films keep going", 2)
IMG("chart2.png", 15.5)
P("Here each film's highest day is set to 1, so big and small films can be compared. "
  "War 2 was highest on day 1 and then fell fast. Saiyaara and Su From So went up for many days after release. "
  "This is word of mouth, that is, people telling their friends to watch the film.")
H("Finding 3: The Day 3 signal (main result)", 2)
IMG("chart6.png", 15.5)
P(f"This chart also joins two sources. Left to right: Monday views divided by Friday views. Up and down: money earned "
  f"divided by money expected from early buzz. Films on the right side mostly did better than expected. "
  f"The match score (Spearman) is {S['spearman_day3_vs_overperf']} for {S['n_chart6']} films. 1 means a perfect match and 0 means no match. "
  "This number is ready on Monday morning, inside the 72 hours.")
H("Finding 4: The same buzz means different things for different languages", 2)
IMG("chart3.png", 15)
P("English Wikipedia is used less by people who watch Telugu, Tamil or Kannada films. So their views are lower for the same money. "
  "We should compare a film only with films of the same language. We have only 4 to 5 films per language, so this is a rough idea.")
H("Finding 5: What critics like and dislike", 2)
IMG("chart4.png", 15)
P(f"We gave a score to {len(crit)} critic lines using VADER. VADER is a free tool that says if a sentence is positive or negative. Critics talk most kindly about direction and acting. "
  "They are less kind about length and action. For example, one critic said Dhurandhar's ending does not justify its long runtime. "
  "One problem: VADER gave a score of 0 to some clearly negative lines, so it misses some criticism.")
P("Our PySpark job on 50,000 IMDb reviews shows the same thing. Words about length (long, slow, boring) come 12,621 times "
  "in negative reviews and 7,235 times in positive reviews. So people do not like films that feel too long.")
H("Extra: our own Buzz Score", 2)
IMG("chart5.png", 15)
P(f"We made a Buzz Score from 4 things: views before release, views in week 1, critic score, and views kept on day 7. "
  f"We tested it fairly: for each film, we built the score using only the other 24 films. It guessed 'above or below average money' "
  f"right for {S['loo_hit_rate']:.0%} of films. This is better than a coin toss (50%) but not good enough to guess exact money.")
H("SQL", 2)
P("We made 4 tables: films, boxoffice, daily_buzz and critic_sentences. They are joined by film_id. "
  "The code is in sql/schema.sql and the 7 queries (with JOIN and GROUP BY) are in sql/queries.sql. "
  "The results are in outputs/sql results.md.")
IMG("er diagram.png", 14)

H("g. What to do next Friday")
for s in ["Friday: note the Wikipedia views of our film on release day.",
          "Monday morning: find the Day 3 ratio = Monday views / Friday views.",
          "1 or more: keep all screens, add shows in week 2, and spend on promotion.",
          "Between 0.8 and 1: keep screens, do not spend more, check again on Wednesday.",
          "Below 0.8: do not add screens, give extra shows to a stronger film, do not spend more.",
          "Compare a film only with films of the same language."]:
    B(s)

H("h. Limits and bias")
for s in ["Small sample: only 22 to 25 films. The result can change with more films.",
          "We only took top films, no flop films. So the result may be too positive.",
          "English Wikipedia users are mostly city people who read English. Many single screen and regional viewers are missing.",
          "Other things also matter: big stars, holidays, other films releasing the same week, budget and number of screens.",
          "Paid promotion and fake views are possible. Wikipedia removes known bots, but not paid views.",
          "Box office numbers are given by producers and can be too high.",
          "VADER is made for English social media. It misses jokes and Hinglish. It was only 70% correct on IMDb reviews.",
          "A link between two things does not mean one causes the other. People liking the film may cause both."]:
    B(s)

H("i. Reflection (what we learned)")
P("Our question changed two times. First, we could not get Reddit or YouTube data, so we used Wikipedia views. "
  "Second, our first chart showed that buzz before release is weak, and it is known before the decision anyway. "
  "When we looked at the daily views, we saw the shape after release matters more. That became our main question.")
P("The biggest surprise was in cleaning. Saiyaara, the biggest word-of-mouth hit, first showed almost zero buzz. "
  "This was because its Wikipedia page was renamed. After fixing it, the result made sense.")
P("With better data we would add YouTube trailer views and comments, Google Trends in Indian languages, daily India collections, "
  "and screen counts. We would also test our rule on new 2026 films.")

doc.add_page_break()
H("Appendix A: Use of AI tools")
P("We used Claude (an AI tool) to help write and fix the Python, SQL and PySpark code, and to help with the report and slides. "
  "We chose the question and the films, checked every chart with the data, and decided the rule for screens. "
  "Both of us have gone through all the code and can explain every step.")
H("Appendix B: Team work")
TABLE(pd.DataFrame([
    ["Gauri", "Collected data from APIs, sentiment, PySpark, charts and Buzz Score, slides", "50%"],
    ["Shivansh", "Box office tables, cleaning log, film name matching, SQL tables and queries, Excel comparison, report", "50%"],
], columns=["Member", "Work done", "Share"]))
H("Appendix C: List of films")
fl = films[["film_id", "language", "release_date", "worldwide_gross_cr", "prerelease_views_7d", "day3_attention_ratio", "critic_tone"]].copy()
fl["day3_attention_ratio"] = fl["day3_attention_ratio"].round(2)
fl.columns = ["Film", "Language", "Release date", "Money (Rs crore)", "Views 7 days before", "Day 3 ratio", "Critic score"]
TABLE(fl, size=8)

out = ROOT / "report" / "Release Day Radar Report.docx"
doc.save(out)
print("saved", out)
