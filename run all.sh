#!/usr/bin/env bash
# Mac / Linux version of "run all.ps1": runs every step in order.
set -e
cd "$(dirname "$0")/code"
py="../.venv/bin/python"
export PYTHONIOENCODING=utf-8
export PYSPARK_PYTHON="$py"
export PYSPARK_DRIVER_PYTHON="$py"
for s in "1 collect data.py" "2 old page names.py" "3 clean data.py" "4 sentiment.py" "5 sql.py" "6 pyspark.py" "7 charts.py" "8 excel vs pandas.py" "11 make notebook.py" "12 take screenshots.py" "9 make report.py" "10 make slides.py"; do
    echo "==> $s"
    "$py" "$s"
done
