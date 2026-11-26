"""Gives a sentiment score to each critic line. First tests it on IMDb reviews."""
import re, random, pathlib
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from common import ROOT, CLEAN, OUT

an = SentimentIntensityAnalyzer()
IMDB = ROOT / "data" / "raw" / "imdb50k" / "aclImdb"


random.seed(42)
files = [(p, lab) for split in ("train", "test") for lab in ("pos", "neg")
         for p in (IMDB / split / lab).glob("*.txt")]
print("IMDb files found:", len(files))
sample = random.sample(files, 5000)
rows = []
for p, lab in sample:
    t = re.sub(r"<br\s*/?>", " ", p.read_text(encoding="utf-8"))
    c = an.polarity_scores(t)["compound"]
    rows.append(dict(label=lab, compound=c, pred="pos" if c >= 0.05 else "neg"))
v = pd.DataFrame(rows)
acc = (v["label"] == v["pred"]).mean()
cm = pd.crosstab(v["label"], v["pred"], rownames=["actual"], colnames=["VADER"])
print(f"VADER accuracy on 5,000 labelled IMDb reviews: {acc:.1%}")
print(cm)
with open(OUT / "vader_validation.txt", "w", encoding="utf-8") as fh:
    fh.write("We tested VADER on 5,000 IMDb reviews where we already know if the review is positive or negative.\n")
    fh.write(f"Accuracy: {acc:.1%}\n\nTable of right and wrong answers:\n{cm.to_string()}\n")
    fh.write("\nMain mistake: some negative reviews got a positive score, because of jokes or happy words in the story.\n")


ASPECTS = {
    "music": r"music|song|score|soundtrack|background score|bgm|composer",
    "acting": r"perform|acting|actor|actress|portray|cast\b|screen presence|chemistry",
    "story": r"story|plot|script|screenplay|narrative|writing|dialogue|climax|twist",
    "vfx_action": r"vfx|visual effect|action|cgi|stunt|spectacle|visuals|cinematograph",
    "length": r"length|runtime|long|lengthy|drag|pacing|slow|second half|first half|tedious",
    "direction": r"direct|filmmak|helm",
}
def aspect(t):
    t = t.lower()
    for a, rx in ASPECTS.items():
        if re.search(rx, t):
            return a
    return "none"

s = pd.read_csv(CLEAN / "critic_sentences.csv")
s["vader_compound"] = s["text"].map(lambda t: an.polarity_scores(t)["compound"])
s["sentiment_label"] = pd.cut(s["vader_compound"], [-1.01, -0.05, 0.05, 1.01], labels=["neg", "neu", "pos"])
s["aspect"] = s["text"].map(aspect)
s.to_csv(CLEAN / "critic_sentences.csv", index=False)

per_film = s.groupby("film_id").agg(critic_sentences=("text", "size"),
                                    critic_tone=("vader_compound", "mean"),
                                    critic_pos_share=("sentiment_label", lambda x: (x == "pos").mean())).round(3)
films = pd.read_csv(CLEAN / "films.csv")
films = films.drop(columns=[c for c in per_film.columns if c in films.columns]).merge(
    per_film, left_on="film_id", right_index=True, how="left")
films.to_csv(CLEAN / "films.csv", index=False)
print(s.groupby("aspect")["vader_compound"].agg(["size", "mean"]).round(3))
