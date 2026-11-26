"""Does one cleaning step in Excel and in pandas, to compare."""
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from common import CLEAN, OUT, to_crore

g = pd.read_csv(CLEAN / "boxoffice_list_tables.csv")
wb = Workbook(); ws = wb.active; ws.title = "gross_cleaning"
ws.append(["gross_raw (from Wikipedia HTML)", "title", "Excel formula result (crore)", "pandas result (crore)", "match?"])
for c in ws[1]:
    c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="30638E")
for i, r in enumerate(g.itertuples(), start=2):
    ws.append([r.gross_raw, r.title_list,
               f'=IFERROR(VALUE(TRIM(SUBSTITUTE(SUBSTITUTE(SUBSTITUTE(A{i},"₹",""),",","")," crore",""))),"#NEEDS MANUAL FIX")',
               to_crore(r.gross_raw),
               f'=IF(ISNUMBER(C{i}),IF(ABS(C{i}-D{i})<0.01,"same","DIFFERENT"),"Excel failed")'])
for col, w in zip("ABCDE", (34, 30, 28, 22, 14)):
    ws.column_dimensions[col].width = w
note = wb.create_sheet("comparison_note")
for line in [
    "Same step, two tools: '₹1,350.83 crore' -> 1350.83",
    "Spreadsheet: nested SUBSTITUTE + VALUE formula, filled down. Visible and easy to audit cell by cell,",
    "  but it FAILS on ranges ('₹90–130 crore'), footnote marks ('[a]') and 'lakh' values -> these show '#NEEDS MANUAL FIX'.",
    "  Every new film means copying the formula again; nothing records that the step happened.",
    "pandas: gross['worldwide_gross_cr'] = gross['gross_raw'].map(to_crore) - one line, handles ranges (midpoint),",
    "  footnotes and lakh/rupee formats, and re-runs identically on new data (reproducible, version-controlled in Git).",
    "Verdict: spreadsheet for a quick look at <100 rows; pandas for anything repeated every Friday.",
]:
    note.append([line])
wb.save(OUT / "spreadsheet_cleaning_step.xlsx")
print("rows", len(g), "| pandas parsed", g["gross_raw"].map(to_crore).notna().sum())
