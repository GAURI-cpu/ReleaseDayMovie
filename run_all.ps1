$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\code"
$py = "$PSScriptRoot\.venv\Scripts\python.exe"
$env:PYTHONIOENCODING = "utf-8"
$jdk = Get-ChildItem "$HOME\.jdks" -Directory -ErrorAction SilentlyContinue | Select-Object -First 1
if ($jdk) { $env:JAVA_HOME = $jdk.FullName; $env:PATH = "$($jdk.FullName)\bin;$env:PATH" }
$env:PYSPARK_PYTHON = $py
$env:PYSPARK_DRIVER_PYTHON = $py
foreach ($s in "01_collect.py","01b_collect_redirects.py","02_clean.py","03_sentiment.py","04_sql.py","05_pyspark_text.py","06_charts.py","07_spreadsheet_vs_pandas.py","08_build_report.py","09_build_slides.py") {
    Write-Host "==> $s"
    & $py $s
    if ($LASTEXITCODE -ne 0) { throw "$s failed" }
}
