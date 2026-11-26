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
P(f"GitHub link: {REPO}")
P("Our question: A film comes on Friday. By Monday, can we find out if we should add screens, "
  "remove screens, or spend more money on promotion?", bold=True)

H("a. Executive summary (short answer)")
P(f"1. Buzz before release does not help much. It explains only about {S['r2']:.0%} of the box office "
  f"for {S['n_chart1']} big films of 2025.")
P(f"2. A better number is the Day 3 ratio. Day 3 ratio = Monday views / Friday views on Wikipedia. "
  f"When it was 1 or more, {S['hold_beat']} out of {S['hold_n']} films earned more than expected. "
  f"When it was less than 1, only {S['drop_beat']} out of {S['drop_n']} films earned more than expected.")
P("3. What we suggest: check this number every Monday morning. If it is 1 or more, keep or add screens and spend on promotion. "
  "If it is less than 0.8, do not add screens and do not spend more. This is only a warning sign. It is not 100% sure.")

H("b. Our question and why it is important")
P("Every Friday a new film comes. The company gets only 72 hours to decide three things: add screens, remove screens, "
  "or spend more on promotion. Today they decide by guess, by tweets and by the Friday collection.")
P("If we give a screen to a weak film, a good film loses that screen. So a wrong decision means loss of money.")
P("First we wanted to check if trailer buzz can tell us the opening collection. But this buzz is already known before Friday. "
  "The real decision comes after the film releases. So we changed our question: which number, ready by Monday, "
  "tells us if a film will do better or worse than its buzz?")
P("We took the top 5 films of 2025 from Hindi, Telugu, Tamil, Kannada and Malayalam. So we have 25 films. "
  "For each film we took data for every day, from 30 days before release to 60 days after release.")

H("c. Data inventory and V profile")
H("Source register (list of our data sources)", 2)
TABLE(pd.DataFrame([
    ["1. Box office tables", "en.wikipedia.org, pages 'List of Hindi films of 2025' (also Telugu, Tamil, Kannada, Malayalam)", "26 Nov 2026", "Wikipedia API, then read the table with pandas", "Structured (HTML table)", "Free to use (CC BY-SA). We sent requests slowly."],
    ["2. Daily page views", "wikimedia.org page views API", "26 Nov 2026", "API gives JSON, one number for each day", "Semi-structured (JSON)", "Free, no key needed"],
    ["3. Film details and edit history", "en.wikipedia.org API", "26 Nov 2026", "API gives JSON", "Semi-structured (JSON)", "Free to use (CC BY-SA)"],
    ["4. Critic review text", "'Critical reception' part of each film's Wikipedia page", "26 Nov 2026", "Taken from source 3 and cleaned", "Unstructured (text)", "Free to use (CC BY-SA)"],
    ["5. IMDb 50K reviews", "ai.stanford.edu/~amaas/data/sentiment/", "26 Nov 2026", "Downloaded zip file", "Unstructured (text files)", "Free for study"],
], columns=["Source", "Link", "Date", "How we got it", "Type", "Rules for use"]), size=8)
P("We also tried Reddit, YouTube and IMDb reviews. Reddit blocked us. YouTube and TMDb need a personal key. "
  "IMDb does not allow copying its reviews. So we used Wikipedia page views as our buzz number. "
  "It shows how many people searched for the film on each day.")

H("Data inventory (list of all columns we used)", 2)
TABLE(pd.DataFrame([
    ["film_id", "Made by us", "Nominal", "Structured"],
    ["language", "Source 1", "Nominal", "Structured"],
    ["worldwide_gross_cr (money earned)", "Source 1", "Continuous", "Structured"],
    ["gross_raw (text like '₹797.34 crore')", "Source 1", "Text, changed to continuous", "Structured"],
    ["release_date", "Source 3", "Date", "Semi-structured"],
    ["runtime_min", "Source 3", "Discrete", "Semi-structured"],
    ["budget_cr", "Source 3", "Continuous (many empty)", "Semi-structured"],
    ["opening_day_cr", "Source 3 text", "Continuous (many empty)", "Unstructured"],
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
], columns=["Column", "From", "Data type", "Shape"]), size=9)
P("Meaning of data types: Nominal means names or groups, like language. Ordinal means groups in an order, "
  "like negative, neutral, positive. Discrete means whole numbers we count, like views. "
  "Continuous means numbers with decimals, like money in crore.")

H("V profile (Volume, Velocity, Variety)", 2)
peak = buzz.loc[buzz[buzz.day_from_release == 0].views.idxmax()]
TABLE(pd.DataFrame([
    ["Volume (how much data)", f"25 films. {len(buzz):,} rows of daily data. {len(crit)} critic lines. 50,000 IMDb reviews. "
                               f"About 8 MB of JSON files and 84 MB of IMDb files. PySpark used {int(spark_rows):,} rows of text."],
    ["Velocity (how fast data comes)", f"On release day, {peak.film_id.replace('_2025', '').title()} got {int(peak.views):,} views. That is about "
                                       f"{int(peak.views / 24):,} views every hour. One page got 155 edits in one day. "
                                       f"Most films lose half their views in about {S['median_half_life']:.0f} days. So buzz comes fast and goes fast."],
    ["Variety (how many types of data)", "This was our biggest problem. Data for one film came in 5 types: HTML tables, 2 types of JSON, wiki code, normal text and text files. "
                                         "One film had 3 names. Money came as '₹1,350.83 crore', '₹90–130 crore' or in US dollars."],
    ["How it changed our tools", "Because of Variety, first we made one common name (key) for each film and a cleaning log. "
                                 "We used json_normalize for JSON, read_html for tables, and SQL to join everything. "
                                 "Because of Velocity, we kept data for each day, not just one number for each film. "
                                 "Because of Volume, we used PySpark for the 50,000+ text rows."],
], columns=["V", "Our data"]), size=9)

H("d. Pipeline: how data goes from source to chart")
for s in ["Step 1 (1 collect data.py): get data from Wikipedia and save it as it is.",
          "Step 2 (2 old page names.py): get views for the old names of each page.",
          "Step 3 (3 clean data.py): clean the data, join it, and write the cleaning log.",
          f"Step 4 (4 sentiment.py): test the VADER tool on IMDb reviews ({vacc} correct). Then use it on critic lines.",
          "Step 5 (5 sql.py): put the data in 4 SQL tables and run 7 queries.",
          f"Step 6 (6 pyspark.py): PySpark job on {int(spark_rows):,} text rows.",
          "Step 7 (7 charts.py): make the charts and test the Buzz Score.",
          "Step 8 (8, 9, 10): Excel comparison, this report and the slides.",
          "The file 'run all.ps1' runs all the steps one by one."]:
    B(s)

H("e. Cleaning log")
P("Each row is one cleaning step we did.")
TABLE(log[["step", "area", "problem", "rows_affected", "action", "why"]], size=8)
H("Excel vs pandas (same cleaning step)", 2)
P("Step: change '₹1,350.83 crore' into the number 1350.83.")
P("In Excel we used a formula with SUBSTITUTE and VALUE (file: outputs/excel cleaning step.xlsx). "
  "It is easy to see and check. But it does not work for a range like '₹90–130 crore'. "
  "Also, for every new film we must copy the formula again.")
P("In pandas it is only one line of code. It works for ranges also. We can run it again every Friday and get the same answer.")
P("Our view: Excel is good for a quick look. pandas is better for work we do every week.")

H("f. Findings")
H("Finding 1: Buzz before release does not help much", 2)
IMG("chart1.png", 15.5)
P(f"This chart uses two sources: page views (JSON) and box office (HTML table). The link is weak (r = {S['pearson_log']}, "
  f"{S['n_chart1']} films). War 2 and Game Changer had very high buzz, but they earned less than expected. "
  "Mahavatar Narsimha had almost no buzz, but it still earned about Rs 300 crore.")
H("Finding 2: Buzz goes down fast, but word of mouth films keep going", 2)
IMG("chart2.png", 15.5)
P("Here the highest day of each film is set to 1. This way big and small films can be compared. "
  "War 2 was highest on day 1 and then fell fast. Saiyaara and Su From So kept going up for many days after release. "
  "This is word of mouth, which means people telling their friends to watch the film.")
H("Finding 3: The Day 3 number (main result)", 2)
IMG("chart6.png", 15.5)
P("This chart also uses two sources. Left to right: Monday views / Friday views. Bottom to top: money earned / money expected. "
  "Films on the right side mostly did better than expected. Films on the left side mostly did worse.")
P(f"The match score (Spearman) is {S['spearman_day3_vs_overperf']} for {S['n_chart6']} films. 1 means full match and 0 means no match. "
  "This number is ready on Monday morning, inside the 72 hours.")
H("Finding 4: Same buzz means different things for different languages", 2)
IMG("chart3.png", 15)
P("Fewer people use English Wikipedia for Telugu, Tamil and Kannada films. So these films get fewer views for the same money. "
  "So we should compare a film only with films of the same language. We have only 4 to 5 films in each language, so this is a rough idea only.")
H("Finding 5: What critics like and do not like", 2)
IMG("chart4.png", 15)
P(f"We gave a score to {len(crit)} critic lines using VADER. VADER is a free tool. It tells if a sentence is positive or negative. "
  "Critics said the nicest things about direction and acting. They said less nice things about length and action. "
  "For example, one critic said the ending of Dhurandhar was not worth its long runtime. "
  "One problem: VADER gave a score of 0 to some clearly negative lines. So it misses some negative comments.")
P("Our PySpark job on 50,000 IMDb reviews shows the same thing. Words like long, slow and boring come 12,621 times "
  "in negative reviews and only 7,235 times in positive reviews. So people do not like films that feel too long.")
H("Extra: our own Buzz Score", 2)
IMG("chart5.png", 15)
P("We made a Buzz Score using 4 things: views before release, views in week 1, critic score, and views on day 7.")
P(f"We tested it in a fair way. For each film, we made the score using only the other 24 films. "
  f"It guessed 'above or below average money' correctly for {S['loo_hit_rate']:.0%} of films. "
  "This is better than tossing a coin (50%), but it cannot guess the exact money.")
H("SQL", 2)
P("We made 4 tables: films, boxoffice, daily_buzz and critic_sentences. They are joined using film_id. "
  "The table code is in sql/schema.sql. The 7 queries (with JOIN and GROUP BY) are in sql/queries.sql. "
  "The answers are in outputs/sql results.md.")
IMG("er diagram.png", 14)

H("g. What to do next Friday")
for s in ["Friday: write down the Wikipedia views of our film on release day.",
          "Monday morning: find Day 3 ratio = Monday views / Friday views.",
          "If it is 1 or more: keep all screens, add more shows in week 2, and spend on promotion.",
          "If it is between 0.8 and 1: keep the screens, do not spend more, check again on Wednesday.",
          "If it is less than 0.8: do not add screens, give extra shows to a better film, do not spend more.",
          "Always compare a film only with films of the same language."]:
    B(s)

H("h. Limits and bias")
for s in ["We have only 22 to 25 films. With more films, the result can change.",
          "We took only top films, no flop films. So the result may look better than it really is.",
          "English Wikipedia is used mostly by city people who read English. Many single screen and regional viewers are not counted.",
          "Other things also matter: big stars, holidays, other films on the same week, budget and number of screens.",
          "Some views can be paid or fake. Wikipedia removes known bots, but not paid views.",
          "Producers give the box office numbers, and sometimes they give higher numbers.",
          "VADER is made for English social media. It does not understand jokes or Hinglish. It was only 70% correct on IMDb reviews.",
          "If two things go together, it does not mean one causes the other. Maybe people liked the film, and that caused both."]:
    B(s)

H("i. Reflection (what we learned)")
P("Our question changed two times. First, we could not get Reddit or YouTube data, so we used Wikipedia views. "
  "Second, our first chart showed that buzz before release does not help much, and it is already known before Friday. "
  "Then we looked at the views day by day. We saw that what happens after release is more important. So that became our main question.")
P("The biggest surprise came during cleaning. Saiyaara was the biggest word of mouth hit, but first it showed almost zero buzz. "
  "This happened because its Wikipedia page name was changed. After we fixed it, the result made sense.")
P("If we had better data, we would add YouTube trailer views and comments, Google Trends in Indian languages, daily India collections "
  "and number of screens. We would also test our rule on new 2026 films.")

doc.add_page_break()
H("Appendix A: Use of AI tools")
P("We used Claude, an AI tool, to help us write and fix the Python, SQL and PySpark code, and to help with the report and slides. "
  "We chose the question and the films. We checked every chart with the data. We decided the rule for screens. "
  "Both of us have gone through all the code and can explain every step.")
H("Appendix B: Team work")
TABLE(pd.DataFrame([
    ["Gauri", "Got data from APIs, sentiment, PySpark, charts and Buzz Score, slides", "50%"],
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
