import json
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from common import ROOT, OUT, CHARTS

S = json.loads((OUT / "key numbers.json").read_text(encoding="utf-8"))
REPO = (ROOT / "repo link.txt").read_text().strip()
BLACK, GREY = RGBColor(0, 0, 0), RGBColor(0x55, 0x55, 0x55)
prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


def text(slide, x, y, w, h, lines, size=20, bold_first=False):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        r = p.add_run()
        r.text = ln
        r.font.size = Pt(size)
        r.font.color.rgb = BLACK
        r.font.bold = bold_first and i == 0
        p.space_after = Pt(10)


def slide(title, notes):
    s = prs.slides.add_slide(BLANK)
    text(s, 0.6, 0.4, 12.2, 1.2, [title], 28, True)
    line = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.45), Inches(12.1), Inches(0.03))
    line.fill.solid(); line.fill.fore_color.rgb = BLACK; line.line.fill.background()
    s.notes_slide.notes_text_frame.text = notes
    return s


def img(s, name, x=1.6, y=1.65, h=5.6, w=None):
    if w:
        s.shapes.add_picture(str(CHARTS / name), Inches(x), Inches(y), width=Inches(w))
    else:
        s.shapes.add_picture(str(CHARTS / name), Inches(x), Inches(y), height=Inches(h))


s = prs.slides.add_slide(BLANK)
text(s, 0.8, 1.6, 11.5, 1, ["Release Day Radar"], 48, True)
text(s, 0.8, 2.9, 11.5, 2, ["Do not judge a film by its Friday buzz.", "Check if people are still looking for it on Monday."], 28)
text(s, 0.8, 5.6, 11.5, 1.2, ["Case Study A, Data and Storytelling, Module 1", "Gauri and Shivansh", "GitHub: " + REPO], 18)
s.notes_slide.notes_text_frame.text = ("Gauri: Good morning. We are the data team of a film company. "
    "Our answer is simple. Buzz before release does not tell us much. What matters is if people are still searching for the film on Monday.")

s = slide("Our answer",
          f"Gauri: Buzz before release explains only about {S['r2']:.0%} of box office. Films that kept their views on Monday "
          f"did better than expected {S['hold_beat']} out of {S['hold_n']} times. So we should check this every Monday.")
text(s, 0.8, 1.8, 11.8, 5, [
    f"1. Buzz before release explains only about {S['r2']:.0%} of the box office ({S['n_chart1']} films).",
    f"2. Better signal: Monday views / Friday views. When it was 1 or more, {S['hold_beat']} of {S['hold_n']} films "
    f"earned more than expected. When it was below 1, only {S['drop_beat']} of {S['drop_n']} did.",
    "3. Rule: 1 or more = keep or add screens. Below 0.8 = do not add screens, do not spend more.",
    "This is a warning sign, not a promise."], 22)

s = slide("The problem we are solving",
          "Shivansh: Every Friday the team has 72 hours to decide on screens and promotion. Today it is done by guess. "
          "We first wanted to see if trailer buzz predicts the opening. But that is known before Friday. "
          "So we asked: what signal is ready by Monday?")
text(s, 0.8, 1.8, 11.8, 5, [
    "Today the decision is made by guess, tweets and the Friday collection.",
    "Our question: Which online signal, ready by Monday, tells us if a film will do better or worse than its buzz?",
    "Films: top 5 films of 2025 in Hindi, Telugu, Tamil, Kannada and Malayalam. 25 films in total.",
    "For each film: every day from 30 days before release to 60 days after."], 22)

s = slide("Our data: 5 sources, 3 types",
          "Shivansh: We used box office tables, daily page views, film details and critic text from Wikipedia, "
          "and 50,000 IMDb reviews. Reddit blocked us and YouTube needs a key, so we used Wikipedia views as buzz. "
          "The hardest part was Variety: one film came in many formats and names.")
text(s, 0.8, 1.8, 6.2, 5, [
    "Structured: box office tables (HTML)",
    "Semi-structured: daily page views and film details (JSON from APIs)",
    "Unstructured: critic text (217 lines) and IMDb reviews (50,000)",
    "Could not use: Reddit (blocked), YouTube (needs key), IMDb (not allowed)"], 18)
text(s, 7.3, 1.8, 5.5, 5, [
    "The 3 Vs",
    "Volume: 2,201 daily rows, 50,217 text rows",
    "Velocity: up to 5,47,830 views on one release day",
    "Variety: HTML, JSON, wiki code and text. One film had 3 names."], 18, True)

s = slide("Cleaning: Saiyaara first showed zero buzz",
          "Shivansh: Our most important cleaning step. Saiyaara's Wikipedia page was renamed, so its old views were under the old name. "
          "We added them back. We also made one name for each film, changed money text into numbers, and did not fill missing results.")
text(s, 0.8, 1.8, 11.8, 5.5, [
    "Same film, different names: 'Saiyaara', 'Saiyaara (film)'. We made one key: saiyaara_2025",
    "Renamed pages: we added views of the old page names",
    "Money as text: '₹1,350.83 crore' changed to 1350.83",
    "Missing data: if the page did not exist, we left it empty, not 0",
    "Same scale for all films: log, z-score, and views divided by each film's highest day",
    "Excel vs pandas: Excel formula failed on ranges. pandas did it in one line.",
    "SQL: 4 tables and 7 queries. PySpark: 50,217 text rows."], 19)

s = slide("Finding 1: Buzz before release is a weak guide",
          "Gauri: Each mark is a film. Left to right is views before release. Up is money earned. "
          "War 2 and Game Changer had big buzz but earned less. Mahavatar Narsimha had almost no buzz and earned Rs 300 crore.")
img(s, "chart1.png")

s = slide("Finding 2: Buzz falls fast, but word of mouth keeps going",
          "Gauri: Each film's highest day is set to 1. The thick line is the middle film. Most films lose half their views in about a week. "
          "But Saiyaara and Su From So went up after release. That is word of mouth.")
img(s, "chart2.png")

s = slide("Finding 3: The Day 3 signal (main result)",
          f"Shivansh: Left to right is Monday views divided by Friday views. Up is money earned compared to what we expected. "
          f"On the right side, {S['hold_beat']} of {S['hold_n']} films did better than expected. On the left side, only {S['drop_beat']} of {S['drop_n']}.")
img(s, "chart6.png")

s = slide("Be careful: compare films of the same language",
          f"Shivansh: English Wikipedia has fewer users for Telugu, Tamil and Kannada films. So their views are lower for the same money. "
          f"Our Buzz Score guessed hit or not right {S['loo_hit_rate']:.0%} of the time. Good as a warning, not for exact numbers.")
img(s, "chart3.png", x=0.4, y=1.8, w=6.3)
img(s, "chart5.png", x=6.9, y=1.8, w=6.1)

s = slide("What to do next Friday",
          "Gauri: Here is the rule. Our limits: only 22 films, only top films, English Wikipedia users only, and producer numbers can be high. "
          "Also, a link is not the same as a cause. Next we want YouTube data and 2026 films. Thank you.")
text(s, 0.8, 1.8, 6.3, 5.5, [
    "Monday morning: Monday views / Friday views",
    "1 or more: keep all screens, add shows, spend on promotion",
    "0.8 to 1: keep screens, no extra spend, check on Wednesday",
    "Below 0.8: do not add screens, do not spend more",
    "Compare only with films of the same language"], 19, True)
text(s, 7.4, 1.8, 5.5, 5.5, [
    "Limits",
    "Only 22 films",
    "Only top films, no flops",
    "English Wikipedia users only",
    "Stars and holidays also matter",
    "Box office numbers can be too high",
    "A link is not a cause"], 18, True)

out = ROOT / "report" / "Release Day Radar Slides.pptx"
text(s, 0.8, 6.7, 12, 0.5, ["Code and data: " + REPO], 14)
prs.save(out)
print("saved", out, len(prs.slides), "slides")
