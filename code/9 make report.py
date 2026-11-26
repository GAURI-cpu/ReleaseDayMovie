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
P("Team: Gauri (1RV23EC048) and Shivansh (1RV23EC138)")
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
p = doc.add_paragraph()
p.add_run("GitHub link: ")
link = OxmlElement("w:hyperlink")
link.set(qn("r:id"), p.part.relate_to(REPO, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True))
run = OxmlElement("w:r")
rpr = OxmlElement("w:rPr")
u = OxmlElement("w:u"); u.set(qn("w:val"), "single"); rpr.append(u)
run.append(rpr)
t = OxmlElement("w:t"); t.text = REPO; run.append(t)
link.append(run)
p._p.append(link)
P("Our question: A film comes on Friday. By Monday, can we find out if we should add screens, "
  "remove screens, or spend more money on promotion?", bold=True)

H("a. Our Short Answer (Executive Summary)")
P(f"1. Buzz before release does not help much. It explains only about {S['r2']:.0%} of the box office "
  f"for {S['n_chart1']} big films of 2025.")
P(f"2. A better number is the Day 3 ratio. Day 3 ratio = Monday views / Friday views on Wikipedia. "
  f"When it was 1 or more, {S['hold_beat']} out of {S['hold_n']} films earned more than expected. "
  f"When it was less than 1, only {S['drop_beat']} out of {S['drop_n']} films earned more than expected.")
P("3. What we suggest: check this number every Monday morning. If it is 1 or more, keep or add screens and spend on promotion. "
  "If it is less than 0.8, do not add screens and do not spend more. This is only a warning sign. It is not 100% sure.")

H("b. Our Question and Why We Chose It")
P("Every Friday a new film comes. The company gets only 72 hours to decide three things: add screens, remove screens, "
  "or spend more on promotion. Today they decide by guess, by tweets and by the Friday collection.")
P("If we give a screen to a weak film, a good film loses that screen. So a wrong decision means loss of money.")
P("First we wanted to check if trailer buzz can tell us the opening collection. But this buzz is already known before Friday. "
  "The real decision comes after the film releases. So we changed our question: which number, ready by Monday, "
  "tells us if a film will do better or worse than its buzz?")
P("We took the top 5 films of 2025 from Hindi, Telugu, Tamil, Kannada and Malayalam. So we have 25 films. "
  "For each film we took data for every day, from 30 days before release to 60 days after release.")

H("c. The Data We Used")
H("Where We Got the Data (Source Register)", 2)
TABLE(pd.DataFrame([
    ["1", "Box office tables", "Wikipedia ('List of Hindi films of 2025' and the same page for Telugu, Tamil, Kannada, Malayalam)", "HTML table", "Yes, free (CC BY-SA)"],
    ["2", "Daily page views", "Wikimedia page views API", "JSON", "Yes, free, no key"],
    ["3", "Film details", "Wikipedia API", "JSON", "Yes, free (CC BY-SA)"],
    ["4", "Critic reviews", "Wikipedia film pages", "Text", "Yes, free (CC BY-SA)"],
    ["5", "IMDb 50K reviews", "ai.stanford.edu", "Text files", "Yes, for study"],
], columns=["No.", "Data", "Where from", "Format", "Allowed to use?"]), size=9)
P("We took all the data on 26 Nov 2026. For sources 1 to 4 we used the Wikipedia API. For source 5 we downloaded a zip file.")
P("We also tried Reddit, YouTube and IMDb reviews. Reddit blocked us. YouTube and TMDb need a personal key. "
  "IMDb does not allow copying its reviews. So we used Wikipedia page views as our buzz number. "
  "It shows how many people searched for the film on each day.")

H("All the Columns We Used (Data Inventory)", 2)
TABLE(pd.DataFrame([
    ["Film name", "Name of the film", "Nominal", "Structured"],
    ["Language", "Hindi, Tamil, etc.", "Nominal", "Structured"],
    ["Money earned", "Total money in crore", "Continuous", "Structured"],
    ["Release date", "Date the film came", "Date", "Semi-structured"],
    ["Runtime", "Length in minutes", "Discrete", "Semi-structured"],
    ["Budget", "Cost of the film (many empty)", "Continuous", "Semi-structured"],
    ["Opening day money", "Money on day 1 (many empty)", "Continuous", "Unstructured"],
    ["Views per day", "People who opened the page", "Discrete", "Semi-structured"],
    ["Edits per day", "Changes made to the page", "Discrete", "Semi-structured"],
    ["Day number", "Days before or after release", "Discrete", "Structured"],
    ["Review line", "One line from a review", "Text", "Unstructured"],
    ["Review score", "From -1 to +1", "Continuous", "Structured"],
    ["Review type", "Negative, neutral, positive", "Ordinal", "Structured"],
    ["Topic", "Music, story, acting, etc.", "Nominal", "Structured"],
    ["IMDb label", "Positive or negative", "Nominal", "Structured"],
    ["Day 3 ratio", "Monday views / Friday views", "Continuous", "Structured"],
    ["Buzz Score", "Our own score", "Continuous", "Structured"],
], columns=["Column", "Meaning", "Data type", "Shape"]), size=9)
P("Nominal means names or groups. Ordinal means groups in an order. "
  "Discrete means whole numbers we count. Continuous means numbers with decimals.")

H("Our 3 Vs (V Profile)", 2)
peak = buzz.loc[buzz[buzz.day_from_release == 0].views.idxmax()]
TABLE(pd.DataFrame([
    ["Volume", "How much data", f"25 films, {len(buzz):,} daily rows, {len(crit)} critic lines, 50,000 IMDb reviews (about 92 MB)"],
    ["Velocity", "How fast data comes", f"{peak.film_id.replace('_2025', '').title()} got {int(peak.views):,} views on release day (about {int(peak.views / 24):,} per hour)"],
    ["Variety", "How many types of data", "HTML, JSON, wiki code, text. One film had 3 names."],
], columns=["V", "Meaning", "Our data"]), size=10)
P("Variety was our biggest problem. Money came in many forms, like '₹1,350.83 crore', '₹90–130 crore' or US dollars. "
  "So first we made one common name for each film and wrote a cleaning log. "
  "Because of Velocity, we kept data for every day. Because of Volume, we used PySpark for the 50,000+ text rows.")

H("d. How We Did It, Step by Step (Pipeline)")
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

H("e. How We Cleaned the Data (Cleaning Log)")
P("Each row is one cleaning step we did.")
cl = log[["step", "problem", "rows_affected", "action", "why"]].copy()
cl.columns = ["No.", "Problem we found", "Rows", "What we did", "Why"]
TABLE(cl, size=8)
H("Same Step in Excel and in pandas", 2)
P("Step: change '₹1,350.83 crore' into the number 1350.83.")
P("In Excel we used a formula with SUBSTITUTE and VALUE (file: outputs/excel cleaning step.xlsx). "
  "It is easy to see and check. But it does not work for a range like '₹90–130 crore'. "
  "Also, for every new film we must copy the formula again.")
P("In pandas it is only one line of code. It works for ranges also. We can run it again every Friday and get the same answer.")
P("Our view: Excel is good for a quick look. pandas is better for work we do every week.")

H("f. What We Found")
H("Finding 1: Early Buzz Does Not Help Much", 2)
IMG("chart1.png", 15.5)
P(f"This chart uses two sources: page views (JSON) and box office (HTML table). The link is weak (r = {S['pearson_log']}, "
  f"{S['n_chart1']} films). War 2 and Game Changer had very high buzz, but they earned less than expected. "
  "Mahavatar Narsimha had almost no buzz, but it still earned about Rs 300 crore.")
H("Finding 2: Buzz Goes Down Fast, but Word of Mouth Films Keep Going", 2)
IMG("chart2.png", 15.5)
P("Here the highest day of each film is set to 1. This way big and small films can be compared. "
  "War 2 was highest on day 1 and then fell fast. Saiyaara and Su From So kept going up for many days after release. "
  "This is word of mouth, which means people telling their friends to watch the film.")
H("Finding 3: The Monday Number (Our Main Result)", 2)
IMG("chart6.png", 15.5)
P("This chart also uses two sources. Left to right: Monday views / Friday views. Bottom to top: money earned / money expected. "
  "Films on the right side mostly did better than expected. Films on the left side mostly did worse.")
P(f"The match score (Spearman) is {S['spearman_day3_vs_overperf']} for {S['n_chart6']} films. 1 means full match and 0 means no match. "
  "This number is ready on Monday morning, inside the 72 hours.")
H("Finding 4: Each Language Is Different", 2)
IMG("chart3.png", 15)
P("Fewer people use English Wikipedia for Telugu, Tamil and Kannada films. So these films get fewer views for the same money. "
  "So we should compare a film only with films of the same language. We have only 4 to 5 films in each language, so this is a rough idea only.")
H("Finding 5: What Critics Liked and Did Not Like", 2)
IMG("chart4.png", 15)
P(f"We gave a score to {len(crit)} critic lines using VADER. VADER is a free tool. It tells if a sentence is positive or negative. "
  "Critics said the nicest things about direction and acting. They said less nice things about length and action. "
  "For example, one critic said the ending of Dhurandhar was not worth its long runtime. "
  "One problem: VADER gave a score of 0 to some clearly negative lines. So it misses some negative comments.")
P("Our PySpark job on 50,000 IMDb reviews shows the same thing. Words like long, slow and boring come 12,621 times "
  "in negative reviews and only 7,235 times in positive reviews. So people do not like films that feel too long.")
H("Something Extra: Our Own Buzz Score", 2)
IMG("chart5.png", 15)
P("We made a Buzz Score using 4 things: views before release, views in week 1, critic score, and views on day 7.")
P(f"We tested it in a fair way. For each film, we made the score using only the other 24 films. "
  f"It guessed 'above or below average money' correctly for {S['loo_hit_rate']:.0%} of films. "
  "This is better than tossing a coin (50%), but it cannot guess the exact money.")
H("Our SQL Tables", 2)
P("We made 4 tables: films, boxoffice, daily_buzz and critic_sentences. They are joined using film_id. "
  "The table code is in sql/schema.sql. The 7 queries (with JOIN and GROUP BY) are in sql/queries.sql. "
  "The answers are in outputs/sql results.md.")
IMG("er diagram.png", 14)

H("g. What We Suggest for Next Friday")
for s in ["Friday: write down the Wikipedia views of our film on release day.",
          "Monday morning: find Day 3 ratio = Monday views / Friday views.",
          "If it is 1 or more: keep all screens, add more shows in week 2, and spend on promotion.",
          "If it is between 0.8 and 1: keep the screens, do not spend more, check again on Wednesday.",
          "If it is less than 0.8: do not add screens, give extra shows to a better film, do not spend more.",
          "Always compare a film only with films of the same language."]:
    B(s)

H("h. Problems and Limits in Our Work")
for s in ["We have only 22 to 25 films. With more films, the result can change.",
          "We took only top films, no flop films. So the result may look better than it really is.",
          "English Wikipedia is used mostly by city people who read English. Many single screen and regional viewers are not counted.",
          "Other things also matter: big stars, holidays, other films on the same week, budget and number of screens.",
          "Some views can be paid or fake. Wikipedia removes known bots, but not paid views.",
          "Producers give the box office numbers, and sometimes they give higher numbers.",
          "VADER is made for English social media. It does not understand jokes or Hinglish. It was only 70% correct on IMDb reviews.",
          "If two things go together, it does not mean one causes the other. Maybe people liked the film, and that caused both."]:
    B(s)

H("i. What We Learned (Reflection)")
P("Our question changed two times. First, we could not get Reddit or YouTube data, so we used Wikipedia views. "
  "Second, our first chart showed that buzz before release does not help much, and it is already known before Friday. "
  "Then we looked at the views day by day. We saw that what happens after release is more important. So that became our main question.")
P("The biggest surprise came during cleaning. Saiyaara was the biggest word of mouth hit, but first it showed almost zero buzz. "
  "This happened because its Wikipedia page name was changed. After we fixed it, the result made sense.")
P("If we had better data, we would add YouTube trailer views and comments, Google Trends in Indian languages, daily India collections "
  "and number of screens. We would also test our rule on new 2026 films.")

doc.add_page_break()
H("Appendix A: AI Tools We Used")
P("We used Claude, an AI tool, to help us write and fix the Python, SQL and PySpark code, and to help with the report and slides. "
  "We chose the question and the films. We checked every chart with the data. We decided the rule for screens. "
  "Both of us have gone through all the code and can explain every step.")
H("Appendix B: Who Did What")
TABLE(pd.DataFrame([
    ["Gauri (1RV23EC048)", "Got data from APIs, sentiment, PySpark, charts and Buzz Score, slides", "50%"],
    ["Shivansh (1RV23EC138)", "Box office tables, cleaning log, film name matching, SQL tables and queries, Excel comparison, report", "50%"],
], columns=["Name (USN)", "Work done", "Share"]))
H("Appendix C: All 25 Films")
fl = films[["wiki_title", "language", "release_date", "worldwide_gross_cr", "day3_attention_ratio"]].copy()
fl["wiki_title"] = fl["wiki_title"].str.replace(r" \(.*\)", "", regex=True)
fl["release_date"] = pd.to_datetime(fl["release_date"]).dt.strftime("%d-%m-%Y")
fl["worldwide_gross_cr"] = fl["worldwide_gross_cr"].round(0).astype(int)
fl["day3_attention_ratio"] = fl["day3_attention_ratio"].round(2)
fl.insert(0, "No.", range(1, len(fl) + 1))
fl.columns = ["No.", "Film", "Language", "Release date", "Money (Rs crore)", "Monday / Friday views"]
TABLE(fl, size=8)

out = ROOT / "report" / "Release Day Radar Report.docx"
doc.save(out)
print("saved", out)
