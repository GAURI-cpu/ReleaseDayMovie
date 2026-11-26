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
        if "http" in ln:
            r.text = ln[:ln.index("http")]
            r2 = p.add_run()
            r2.text = ln[ln.index("http"):]
            r2.font.size = Pt(size)
            r2.font.color.rgb = BLACK
            r2.font.underline = True
            r2.hyperlink.address = r2.text


def slide(title, notes):
    s = prs.slides.add_slide(BLANK)
    text(s, 0.6, 0.4, 12.2, 1.2, [title], 28, True)
    s.notes_slide.notes_text_frame.text = notes
    return s


def img(s, name, x=None, y=1.5, h=5.85, w=None):
    shot = OUT / "screenshots" / name
    path = str(shot if shot.exists() else CHARTS / name)
    if w:
        s.shapes.add_picture(path, Inches(x), Inches(y), width=Inches(w))
    else:
        pic = s.shapes.add_picture(path, 0, Inches(y), height=Inches(h))
        pic.left = int((prs.slide_width - pic.width) / 2)


s = prs.slides.add_slide(BLANK)
text(s, 0.8, 1.6, 11.5, 1, ["Release Day Radar"], 48, True)
text(s, 0.8, 2.9, 11.5, 2, ["Do not judge a film only by its Friday buzz.", "Check if people are still searching for it on Monday."], 28)
text(s, 0.8, 5.4, 11.5, 1.6, ["Case Study A, Data and Storytelling, Module 1", "Gauri (1RV23EC048) and Shivansh Shekhar (1RV23EC138)", "GitHub: " + REPO], 18)
s.notes_slide.notes_text_frame.text = ("Gauri: Good morning. We are the data team of a film company. "
    "Our answer is simple. Buzz before release does not help much. What matters is if people are still searching for the film on Monday.")

s = slide("Our Answer in Short",
          f"Gauri: Buzz before release explains only about {S['r2']:.0%} of the box office. Films that kept their views on Monday "
          f"did better than expected {S['hold_beat']} out of {S['hold_n']} times. So we should check this every Monday.")
text(s, 0.8, 1.8, 11.8, 5, [
    f"1. Buzz before release explains only about {S['r2']:.0%} of the box office ({S['n_chart1']} films).",
    f"2. Better number: Monday views / Friday views. When it was 1 or more, {S['hold_beat']} of {S['hold_n']} films "
    f"earned more than expected. When it was less than 1, only {S['drop_beat']} of {S['drop_n']} did.",
    "3. Rule: 1 or more = keep or add screens. Less than 0.8 = do not add screens, do not spend more.",
    "This is only a warning sign. It is not 100% sure."], 22)

s = slide("Our Question",
          "Shivansh: Every Friday the company gets only 72 hours to decide about screens and promotion. Today they decide by guess. "
          "First we wanted to check trailer buzz. But that is known before Friday. "
          "So we asked: which number is ready by Monday?")
text(s, 0.8, 1.8, 11.8, 5, [
    "Today the company decides by guess, tweets and the Friday collection.",
    "Our question: Which number, ready by Monday, tells us if a film will do better or worse than its buzz?",
    "Films: top 5 films of 2025 in Hindi, Telugu, Tamil, Kannada and Malayalam. 25 films in total.",
    "For each film: data for every day, from 30 days before release to 60 days after."], 22)

s = slide("The Data We Used",
          "Shivansh: We took box office tables, daily page views, film details and critic text from Wikipedia, "
          "and 50,000 IMDb reviews. Reddit blocked us and YouTube needs a key, so we used Wikipedia views as buzz. "
          "The hardest part was Variety. One film came in many types and with many names.")
text(s, 0.8, 1.8, 6.2, 5, [
    "Structured: box office tables (HTML)",
    "Semi-structured: daily page views and film details (JSON)",
    "Unstructured: critic text (217 lines) and IMDb reviews (50,000)",
    "Could not use: Reddit (blocked), YouTube (needs key), IMDb (not allowed)"], 18)
text(s, 7.3, 1.8, 5.5, 5, [
    "The 3 Vs",
    "Volume: 2,201 daily rows, 50,217 text rows",
    "Velocity: up to 5,47,830 views on one release day",
    "Variety: HTML, JSON, wiki code and text. One film had 3 names."], 18, True)

s = slide("How We Cleaned the Data",
          "Shivansh: This was our most important cleaning step. Saiyaara's Wikipedia page name was changed, so its old views were under the old name. "
          "We added them back. We also made one name for each film, changed money text into numbers, and did not fill empty results.")
text(s, 0.8, 1.8, 11.8, 5.5, [
    "Same film, many names: 'Saiyaara' and 'Saiyaara (film)'. We made one name: saiyaara_2025",
    "Page name changed: we added the views of the old page names",
    "Money as text: '₹1,350.83 crore' changed to 1350.83",
    "Empty data: if the page did not exist, we left it empty, not 0",
    "Same scale for all films: log, z-score, and views / highest day of the film",
    "Excel vs pandas: Excel formula did not work for ranges. pandas did it in one line.",
    "SQL: 4 tables and 7 queries. PySpark: 50,217 text rows."], 19)

s = slide("Finding 1: Early Buzz Does Not Help Much",
          "Gauri: Each mark is one film. Left to right is views before release. Bottom to top is money earned. "
          "War 2 and Game Changer had big buzz but earned less. Mahavatar Narsimha had almost no buzz and still earned Rs 300 crore.")
img(s, "chart1.png")

s = slide("Finding 2: Buzz Goes Down Fast",
          "Gauri: The highest day of each film is set to 1. The thick line is the middle film. Most films lose half their views in about a week. "
          "But Saiyaara and Su From So kept going up after release. That is word of mouth.")
img(s, "chart2.png")

s = slide("Finding 3: The Monday Number (Main Result)",
          f"Shivansh: Left to right is Monday views / Friday views. Bottom to top is money earned compared to money expected. "
          f"On the right side, {S['hold_beat']} of {S['hold_n']} films did better than expected. On the left side, only {S['drop_beat']} of {S['drop_n']}.")
img(s, "chart6.png")

s = slide("Finding 4: Each Language Is Different",
          f"Shivansh: Fewer people use English Wikipedia for Telugu, Tamil and Kannada films. So these films get fewer views for the same money. "
          f"Our Buzz Score guessed hit or not correctly {S['loo_hit_rate']:.0%} of the time. It is good as a warning, not for exact numbers.")
img(s, "chart3.png", x=0.4, y=1.8, w=6.3)
img(s, "chart5.png", x=6.9, y=1.8, w=6.1)

s = slide("What We Suggest and Our Limits",
          "Gauri: This is our rule. Our limits: only 22 films, only top films, only English Wikipedia users, and producer numbers can be high. "
          "Also, if two things go together, one may not cause the other. Next we want YouTube data and 2026 films. Thank you.")
text(s, 0.8, 1.8, 6.3, 5.5, [
    "Monday morning: Monday views / Friday views",
    "1 or more: keep all screens, add shows, spend on promotion",
    "0.8 to 1: keep screens, no extra money, check on Wednesday",
    "Less than 0.8: do not add screens, do not spend more",
    "Compare only with films of the same language"], 19, True)
text(s, 7.4, 1.8, 5.5, 5.5, [
    "Limits",
    "Only 22 films",
    "Only top films, no flops",
    "Only English Wikipedia users",
    "Stars and holidays also matter",
    "Box office numbers can be high",
    "Going together is not the same as cause"], 18, True)

out = ROOT / "report" / "Release Day Radar Slides.pptx"
text(s, 0.8, 6.7, 12, 0.5, ["Code and data: " + REPO], 14)
prs.save(out)
print("saved", out, len(prs.slides), "slides")
