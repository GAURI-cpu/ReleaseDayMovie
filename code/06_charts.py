"""Makes all the charts, the Buzz Score test and the ER diagram."""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import CLEAN, CHARTS, OUT

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.titlesize": 11,
                     "axes.grid": True, "grid.color": "#dddddd", "grid.linewidth": 0.6,
                     "axes.edgecolor": "black", "figure.dpi": 150, "savefig.facecolor": "white"})
MARK = {"Hindi": "o", "Telugu": "s", "Tamil": "^", "Kannada": "D", "Malayalam": "v"}

films = pd.read_csv(CLEAN / "films.csv", parse_dates=["release_date"])
buzz = pd.read_csv(CLEAN / "daily_buzz.csv")
crit = pd.read_csv(CLEAN / "critic_sentences.csv")
short = lambda fid: fid.replace("_2025", "").replace("_", " ").title()
stats = {}


def dots(ax, df, x, y):
    for lang, g in df.groupby("language"):
        ax.scatter(g[x], g[y], marker=MARK[lang], s=45, facecolor="white", edgecolor="black", label=lang, zorder=3)
    for _, row in df.iterrows():
        ax.annotate(short(row.film_id), (row[x], row[y]), fontsize=7, xytext=(4, 3), textcoords="offset points")
    ax.legend(fontsize=8, title="Language", title_fontsize=8)


def save(fig, name):
    from matplotlib.ticker import ScalarFormatter, NullFormatter
    for ax in fig.axes:
        for axis, scale in ((ax.xaxis, ax.get_xscale()), (ax.yaxis, ax.get_yscale())):
            if scale == "log":
                f = ScalarFormatter(); f.set_scientific(False)
                axis.set_major_formatter(f); axis.set_minor_formatter(NullFormatter())
    fig.tight_layout()
    fig.savefig(CHARTS / name)
    plt.close(fig)


d = films.dropna(subset=["prerelease_views_7d", "worldwide_gross_cr"])
x, y = np.log10(d["prerelease_views_7d"]), np.log10(d["worldwide_gross_cr"])
r = np.corrcoef(x, y)[0, 1]
rs = d["prerelease_views_7d"].rank().corr(d["worldwide_gross_cr"].rank())
slope, icpt = np.polyfit(x, y, 1)
stats.update(n_chart1=len(d), pearson_log=round(r, 2), spearman=round(rs, 2), r2=round(r * r, 2))
fig, ax = plt.subplots(figsize=(9, 5.4))
dots(ax, d, "prerelease_views_7d", "worldwide_gross_cr")
xs = np.linspace(x.min(), x.max(), 50)
ax.plot(10 ** xs, 10 ** (icpt + slope * xs), color="black", ls="--", lw=1, label="Trend line")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("Wikipedia views in the 7 days before release")
ax.set_ylabel("Total money earned worldwide (Rs crore)")
ax.set_title(f"Chart 1: More views before release does not always mean more money\n"
             f"{len(d)} films. The link is weak (r = {r:.2f}).")
save(fig, "chart1_prerelease_buzz_vs_gross.png")

b = buzz.merge(films[["film_id", "peak_views"]], on="film_id")
b["norm"] = b["views"] / b["peak_views"]
fig, ax = plt.subplots(figsize=(9, 5))
for fid, g in b.groupby("film_id"):
    ax.plot(g["day_from_release"], g["norm"], color="#bbbbbb", lw=0.7)
styles = {"saiyaara_2025": "-", "war_2_2025": ":", "su_from_so_2025": "-."}
for fid, ls in styles.items():
    g = b[b.film_id == fid]
    ax.plot(g["day_from_release"], g["norm"], color="black", ls=ls, lw=1.8, label=short(fid))
med = b.groupby("day_from_release")["norm"].median()
ax.plot(med.index, med.values, color="black", lw=3, label="Middle (median) of all 25 films")
ax.axvline(0, color="black", lw=0.8)
ax.set_xlim(-30, 60); ax.set_ylim(0, 1.1)
ax.set_xlabel("Days from release (0 = release day)")
ax.set_ylabel("Views that day / highest views of that film")
half = films["buzz_half_life_days"].median()
stats["median_half_life"] = half
ax.set_title(f"Chart 2: Most films lose half their views within about {half:.0f} days\n"
             "But word-of-mouth hits like Saiyaara and Su From So keep going up after release")
ax.legend(fontsize=8)
save(fig, "chart2_buzz_decay_normalised.png")

c3 = films.dropna(subset=["gross_per_1k_prerelease_views"]).copy()
order = c3.groupby("language")["gross_per_1k_prerelease_views"].median().sort_values()
fig, ax = plt.subplots(figsize=(9, 4.6))
for i, lang in enumerate(order.index):
    v = c3[c3.language == lang]["gross_per_1k_prerelease_views"]
    ax.scatter(v, [i] * len(v), marker="o", facecolor="white", edgecolor="black", s=45, zorder=3)
    ax.plot([v.median()] * 2, [i - 0.3, i + 0.3], color="black", lw=2.5)
ax.set_yticks(range(len(order))); ax.set_yticklabels(order.index)
ax.set_xscale("log")
ax.set_xlabel("Rs crore earned for every 1,000 views before release (thick line = middle value)")
ratio = order.max() / order.min()
stats["conversion_by_lang"] = order.round(3).to_dict()
top, bottom = order.index[-1], order.index[0]
ax.set_title(f"Chart 3: The same views bring about {ratio:.0f} times more money for {top} films than {bottom} films\n"
             "So compare a film only with films of the same language")
save(fig, "chart3_conversion_by_language.png")

a = crit[crit.aspect != "none"].groupby("aspect").agg(n=("text", "size"), tone=("vader_compound", "mean"),
                                                       neg=("sentiment_label", lambda s: (s == "neg").mean()))
a = a.sort_values("tone")
names = {"vfx_action": "action / VFX", "length": "length", "story": "story", "music": "music",
         "acting": "acting", "direction": "direction"}
fig, ax = plt.subplots(figsize=(9, 4.4))
ax.barh([names[i] for i in a.index], a["tone"], color="#888888", edgecolor="black")
for i, (asp, row) in enumerate(a.iterrows()):
    ax.text(row.tone + 0.01, i, f"{int(row.n)} lines, {row.neg:.0%} negative", va="center", fontsize=8)
ax.set_xlabel("Average score of critic lines (-1 = very negative, +1 = very positive)")
stats["aspects"] = a.round(3).to_dict(orient="index")
ax.set_title(f"Chart 4: Critics are most positive about {names[a.index[-1]]} and least positive about {names[a.index[0]]}\n"
             f"{len(crit)} critic lines from {crit.film_id.nunique()} films")
ax.set_xlim(min(0, a.tone.min() - 0.05), a.tone.max() + 0.35)
save(fig, "chart4_critic_aspects.png")

d7 = buzz[buzz.day_from_release.isin([0, 7])].pivot(index="film_id", columns="day_from_release", values="views")
films["day7_retention"] = films["film_id"].map((d7[7] / d7[0].replace(0, np.nan)))
comp = pd.DataFrame({
    "pre": np.log10(films["prerelease_views_7d"]).values,
    "wk1": np.log10(films["release_week_views"].clip(lower=1)).values,
    "tone": films["critic_tone"].values,
    "ret": np.log10(films["day7_retention"]).values,
}, index=films["film_id"])
comp = comp.replace([np.inf, -np.inf], np.nan)
z = (comp - comp.mean()) / comp.std()
films["buzz_index"] = z.mean(axis=1, skipna=True).values
films["z_log_gross"] = ((np.log10(films.worldwide_gross_cr) - np.log10(films.worldwide_gross_cr).mean())
                        / np.log10(films.worldwide_gross_cr).std())

preds = []
ok = films.dropna(subset=["buzz_index", "worldwide_gross_cr"])
for fid in ok.film_id:
    tr = ok[ok.film_id != fid]
    s_, i_ = np.polyfit(tr.buzz_index, np.log10(tr.worldwide_gross_cr), 1)
    te = ok[ok.film_id == fid].iloc[0]
    preds.append(dict(film_id=fid, actual_cr=te.worldwide_gross_cr, predicted_cr=round(10 ** (i_ + s_ * te.buzz_index), 1)))
loo = pd.DataFrame(preds)
loo["error_pct"] = ((loo.predicted_cr - loo.actual_cr) / loo.actual_cr * 100).round(0)
med_g = ok.worldwide_gross_cr.median()
loo["called_right"] = (loo.predicted_cr > med_g) == (loo.actual_cr > med_g)
loo.to_csv(OUT / "buzz_index_leave_one_out.csv", index=False)
r_bi = np.corrcoef(ok.buzz_index, np.log10(ok.worldwide_gross_cr))[0, 1]
stats.update(buzz_index_r=round(r_bi, 2), loo_hit_rate=round(loo.called_right.mean(), 2),
             loo_median_abs_err=float(loo.error_pct.abs().median()))
films.to_csv(CLEAN / "films.csv", index=False)

fig, ax = plt.subplots(figsize=(9, 5.2))
dots(ax, ok, "buzz_index", "worldwide_gross_cr")
ax.set_yscale("log"); ax.axhline(med_g, color="black", lw=0.8, ls=":")
ax.set_xlabel("Buzz Score (views before release + views in week 1 + critic score + views kept on day 7)")
ax.set_ylabel("Total money earned worldwide (Rs crore)")
ax.set_title(f"Chart 5: Our Buzz Score guessed 'hit or not' right for {loo.called_right.mean():.0%} of films\n"
             "Each film was guessed using only the other 24 films. Good as a warning sign, not for exact numbers.")
save(fig, "chart5_buzz_index_holdout.png")

fig, ax = plt.subplots(figsize=(9, 4.6)); ax.axis("off")
boxes = {
    "films": (0.36, 0.55, ["film_id  PK", "wiki_title", "language", "release_date", "runtime_min", "budget_cr",
                            "opening_day_cr", "prerelease_views_7d", "release_week_views", "peak_day", "buzz_half_life_days"]),
    "boxoffice": (0.02, 0.62, ["film_id  PK, FK", "gross_raw", "worldwide_gross_cr", "source_page"]),
    "daily_buzz": (0.70, 0.62, ["film_id  PK, FK", "buzz_date  PK", "day_from_release", "views", "edits"]),
    "critic_sentences": (0.70, 0.02, ["sentence_id  PK", "film_id  FK", "sentence_text", "vader_compound",
                                      "sentiment_label", "aspect"]),
}
for name, (x0, y0, fields) in boxes.items():
    h = 0.055 * (len(fields) + 1)
    y0 = min(y0, 0.98 - h)
    ax.add_patch(plt.Rectangle((x0, y0), 0.27, h, fill=False, lw=1.3))
    ax.add_patch(plt.Rectangle((x0, y0 + h - 0.055), 0.27, 0.055, facecolor="#dddddd", edgecolor="black"))
    ax.text(x0 + 0.01, y0 + h - 0.04, name, color="black", fontweight="bold", fontsize=9)
    for i, f_ in enumerate(fields):
        ax.text(x0 + 0.01, y0 + h - 0.095 - i * 0.055, f_, fontsize=8)
    boxes[name] = (x0, y0, h)


def link(a, b_, label):
    xa, ya, ha = boxes[a]; xb, yb, hb = boxes[b_]
    ax.annotate("", xy=(xb + (0.27 if xb < xa else 0), yb + hb / 2), xytext=(xa + (0 if xb < xa else 0.27), ya + ha / 2),
                arrowprops=dict(arrowstyle="-", lw=1, color="black"))
    ax.text((xa + xb) / 2 + 0.13, (ya + yb + ha / 2 + hb / 2) / 2 + 0.02, label, fontsize=7, ha="center")


link("films", "boxoffice", "1 : 1")
link("films", "daily_buzz", "1 : many")
link("films", "critic_sentences", "1 : many")
ax.set_title("ER diagram: 4 tables joined using film_id", loc="left", fontweight="bold")
fig.savefig(CHARTS / "er_diagram.png", bbox_inches="tight"); plt.close(fig)

p = buzz.pivot(index="film_id", columns="day_from_release", values="views")
films["day3_attention_ratio"] = films["film_id"].map(p[3] / p[0].replace(0, np.nan))
d = films.dropna(subset=["prerelease_views_7d", "day3_attention_ratio", "worldwide_gross_cr"]).copy()
xx, yy = np.log10(d.prerelease_views_7d), np.log10(d.worldwide_gross_cr)
s_, i_ = np.polyfit(xx, yy, 1)
d["overperformance_x"] = 10 ** (yy - (i_ + s_ * xx))
films = films.drop(columns=["overperformance_x"], errors="ignore").merge(d[["film_id", "overperformance_x"]], on="film_id", how="left")
films.to_csv(CLEAN / "films.csv", index=False)
rs6 = d.day3_attention_ratio.rank().corr(d.overperformance_x.rank())
hold = d[d.day3_attention_ratio >= 1]; drop = d[d.day3_attention_ratio < 1]
stats.update(n_chart6=len(d), spearman_day3_vs_overperf=round(rs6, 2),
             hold_n=len(hold), hold_beat=int((hold.overperformance_x > 1).sum()), hold_median_x=round(hold.overperformance_x.median(), 2),
             drop_n=len(drop), drop_beat=int((drop.overperformance_x > 1).sum()), drop_median_x=round(drop.overperformance_x.median(), 2))
fig, ax = plt.subplots(figsize=(9, 5.4))
ax.axvspan(0.4, 1, color="#eeeeee", zorder=0)
dots(ax, d, "day3_attention_ratio", "overperformance_x")
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(0.4, 10)
ax.axhline(1, color="black", lw=0.8, ls="--"); ax.axvline(1, color="black", lw=1)
ax.text(1.05, ax.get_ylim()[1] * 0.85, f"KEEP / ADD SCREENS\n{stats['hold_beat']} of {len(hold)} films earned\nmore than expected",
        fontsize=8, va="top")
ax.text(0.42, ax.get_ylim()[1] * 0.85, f"DO NOT ADD SCREENS\nonly {stats['drop_beat']} of {len(drop)} films earned\nmore than expected",
        fontsize=8, va="top")
ax.set_xlabel("Day 3 views / Day 0 views (above 1 = more people looking on Monday than on Friday)")
ax.set_ylabel("Money earned / money expected from early views\n(above 1 = did better than expected)")
ax.set_title("Chart 6: Films that kept their views on Day 3 earned more than expected\n"
             f"{len(d)} films")
save(fig, "chart6_72h_signal.png")

(OUT / "key_stats.json").write_text(json.dumps(stats, indent=1, default=str), encoding="utf-8")
print(json.dumps(stats, indent=1, default=str))
