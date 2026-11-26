import os, glob, pathlib
from pyspark.sql import SparkSession, functions as F
from pyspark.ml.feature import StopWordsRemover

ROOT = pathlib.Path(__file__).resolve().parents[1]
IMDB = ROOT / "data" / "raw" / "imdb50k" / "aclImdb"
OUT = ROOT / "outputs"

spark = (SparkSession.builder.appName("ReleaseDayRadar-text")
         .master("local[*]").config("spark.driver.memory", "3g")
         .config("spark.sql.shuffle.partitions", "8").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")


import pandas as pd
rows = []
for split in ("train", "test"):
    for lab in ("pos", "neg"):
        for f in (IMDB / split / lab).glob("*.txt"):
            rows.append((f.name, f.read_text(encoding="utf-8"), "imdb50k_" + lab, "imdb50k"))
imdb = spark.createDataFrame(rows, ["path", "text", "film_id", "source"]).repartition(8)
c = pd.read_csv(ROOT / "data" / "clean" / "critic lines.csv")
crit = spark.createDataFrame([("", t, f, "wiki_critic") for t, f in zip(c["text"], c["film_id"])],
                             ["path", "text", "film_id", "source"])
df = imdb.unionByName(crit)
total = df.count()
print("rows in Spark job:", total)


df = (df.withColumn("clean", F.lower(F.regexp_replace("text", r"<br\s*/?>", " ")))
        .withColumn("clean", F.regexp_replace("clean", r"https?://\S+|@\w+", " "))
        .withColumn("clean", F.regexp_replace("clean", r"[^a-z\s]", " "))
        .withColumn("clean", F.trim(F.regexp_replace("clean", r"\s+", " "))))


df = (df.withColumn("n_chars", F.length("text"))
        .withColumn("tokens", F.split("clean", " "))
        .withColumn("n_words", F.size("tokens")))


by_film = (df.groupBy("source", "film_id")
             .agg(F.count("*").alias("rows"), F.round(F.avg("n_words"), 1).alias("avg_words"),
                  F.max("n_words").alias("max_words"))
             .orderBy("source", F.desc("rows")))
by_film.toPandas().to_csv(OUT / "pyspark length by film.csv", index=False)
by_film.show(40, truncate=False)


sw = StopWordsRemover(inputCol="tokens", outputCol="terms",
                      stopWords=StopWordsRemover.loadDefaultStopWords("english") + ["", "br", "film", "movie", "one", "s", "t"])
terms = sw.transform(df).select("source", "film_id", F.explode("terms").alias("term")).filter(F.length("term") > 2)
top_imdb = (terms.filter(F.col("source") == "imdb50k").groupBy("film_id", "term").count()
            .withColumn("rk", F.row_number().over(
                __import__("pyspark.sql.window", fromlist=["Window"]).Window.partitionBy("film_id").orderBy(F.desc("count"))))
            .filter("rk <= 20").drop("rk"))
top_imdb.toPandas().to_csv(OUT / "pyspark top words imdb.csv", index=False)
top_crit = terms.filter(F.col("source") == "wiki_critic").groupBy("term").count().orderBy(F.desc("count")).limit(40)
top_crit.toPandas().to_csv(OUT / "pyspark top words critics.csv", index=False)
top_crit.show(20)


aspects = {"music": ["music", "song", "songs", "score", "soundtrack"],
           "story": ["story", "plot", "script", "screenplay", "writing"],
           "acting": ["acting", "performance", "performances", "actor", "actress", "cast"],
           "vfx_action": ["effects", "action", "cgi", "visuals", "vfx"],
           "length": ["long", "slow", "boring", "length", "pacing", "minutes"]}
amap = spark.createDataFrame([(w, a) for a, ws in aspects.items() for w in ws], ["term", "aspect"])
asp = (terms.join(amap, "term").groupBy("source", "film_id", "aspect").count().orderBy("source", "film_id", F.desc("count")))
asp.toPandas().to_csv(OUT / "pyspark topic counts.csv", index=False)
with open(OUT / "pyspark summary.txt", "w") as fh:
    fh.write(f"Rows processed: {total}\nSpark version: {spark.version}\n")
spark.stop()
