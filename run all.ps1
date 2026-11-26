$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\code"
$py = "$PSScriptRoot\.venv\Scripts\python.exe"
$env:PYTHONIOENCODING = "utf-8"
$jdk = Get-ChildItem "$HOME\.jdks" -Directory -ErrorAction SilentlyContinue | Select-Object -First 1
if ($jdk) { $env:JAVA_HOME = $jdk.FullName; $env:PATH = "$($jdk.FullName)\bin;$env:PATH" }
$env:PYSPARK_PYTHON = $py
$env:PYSPARK_DRIVER_PYTHON = $py
foreach ($s in "1 collect data.py","2 old page names.py","3 clean data.py","4 sentiment.py","5 sql.py","6 pyspark.py","7 charts.py","8 excel vs pandas.py","11 make notebook.py","12 take screenshots.py","9 make report.py","10 make slides.py") {
    Write-Host "==> $s"
    & $py $s
    if ($LASTEXITCODE -ne 0) { throw "$s failed" }
}
