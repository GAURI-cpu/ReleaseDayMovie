# Release Day Radar

Case Study A, Data and Storytelling, Module 1

Team: Gauri (1RV23EC048) and Shivansh Shekhar (1RV23EC138)

GitHub link: https://github.com/GAURI-cpu/ReleaseDayMovie

## What is this project?

A film company has 72 hours after every Friday release to decide: add screens, cut screens, or spend more on promotion.
We looked at 25 Indian films from 2025 to find a simple signal that helps with this decision.

**Our answer:** Buzz before release does not tell us much. A better signal is **Monday views divided by Friday views**
on the film's Wikipedia page. When this number was 1 or more, 8 out of 11 films earned more than expected.
When it was below 1, only 3 out of 11 films did.

## Folders

| Folder or file | What is inside |
|---|---|
| `report/` | The report (Word) and the slides (PowerPoint) |
| `code/` | Python code. Run the files in number order. |
| `sql/` | SQL tables, data and queries |
| `data/raw/wiki/` | Raw data from Wikipedia (JSON files), not changed |
| `data/clean/` | Clean data (CSV files) |
| `outputs/charts/` | All charts and the ER diagram |
| `outputs/cleaning log.csv` | Cleaning log, one row for each decision |
| `outputs/sql results.md` | Results of the SQL queries |
| `outputs/pyspark *.csv` | Results of the PySpark job |
| `outputs/excel cleaning step.xlsx` | Same cleaning step done in Excel |

## How to set up

1. Install Python 3.10.
2. Open PowerShell in this folder and run:

```powershell
python -m venv .venv
```

```powershell
.\.venv\Scripts\python -m pip install pandas numpy matplotlib requests vaderSentiment openpyxl lxml tabulate python-docx python-pptx pyspark==3.5.3 nbformat nbconvert nbclient ipykernel
```

   On Mac or Linux, use these commands instead:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install pandas numpy matplotlib requests vaderSentiment openpyxl lxml tabulate python-docx python-pptx pyspark==3.5.3 nbformat nbconvert nbclient ipykernel
```

3. PySpark needs Java 17. Download the Java 17 JRE zip for Windows from https://adoptium.net/temurin/releases/?version=17
   and unzip it into the folder `C:\Users\<your name>\.jdks\`.
4. Download the IMDb reviews file `aclImdb_v1.tar.gz` (84 MB) from https://ai.stanford.edu/~amaas/data/sentiment/
   and unzip it into `data/raw/imdb50k/`. You should get `data/raw/imdb50k/aclImdb/train/pos/...`.

## How to run

Run everything with one command:

```powershell
& ".\run all.ps1"
```

This runs these steps in order:

1. `1 collect data.py`: gets data from Wikipedia.
2. `2 old page names.py`: gets views for old page names.
3. `3 clean data.py`: cleans and joins the data, writes the cleaning log.
4. `4 sentiment.py`: gives a sentiment score to critic lines.
5. `5 sql.py`: makes the SQL tables and runs the queries.
6. `6 pyspark.py`: PySpark job on 50,217 text rows.
7. `7 charts.py`: makes the charts.
8. `8 excel vs pandas.py`: Excel and pandas comparison.
9. `11 make notebook.py` and `12 take screenshots.py`: run the chart code in a notebook and take screenshots.
10. `9 make report.py` and `10 make slides.py`: make the report and slides.

## MySQL

The SQL files work in MySQL:

```powershell
mysql -u root -p < sql/schema.sql
```

```powershell
mysql -u root -p release_day_radar < sql/data.sql
```

```powershell
mysql -u root -p release_day_radar < sql/queries.sql
```

The code also runs the same queries in SQLite, so you can see the results without MySQL.

## Data sources

- Wikipedia and Wikimedia APIs (free to use, CC BY-SA). We sent slow requests.
- IMDb 50K reviews (Maas and others, 2011), free for study use.
- We did not save any user names.
