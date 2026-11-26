import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font
from common import CLEAN, OUT, to_crore

g = pd.read_csv(CLEAN / "boxoffice_list_tables.csv")
wb = Workbook(); ws = wb.active; ws.title = "gross_cleaning"
ws.append(["gross_raw (from Wikipedia HTML)", "title", "Excel formula result (crore)", "pandas result (crore)", "match?"])
for c in ws[1]:
    c.font = Font(bold=True, color="000000")
for i, r in enumerate(g.itertuples(), start=2):
    ws.append([r.gross_raw, r.title_list,
               f'=IFERROR(VALUE(TRIM(SUBSTITUTE(SUBSTITUTE(SUBSTITUTE(A{i},"₹",""),",","")," crore",""))),"#NEEDS MANUAL FIX")',
               to_crore(r.gross_raw),
               f'=IF(ISNUMBER(C{i}),IF(ABS(C{i}-D{i})<0.01,"same","DIFFERENT"),"Excel failed")'])
for col, w in zip("ABCDE", (34, 30, 28, 22, 14)):
    ws.column_dimensions[col].width = w
note = wb.create_sheet("comparison_note")
for line in [
    "Same step done in two ways: change '₹1,350.83 crore' into the number 1350.83",
    "Excel: we used SUBSTITUTE and VALUE in a formula and copied it down. It is easy to see and check.",
    "But it does not work for a range like '₹90–130 crore' or for extra marks like '[a]'. Those rows show '#NEEDS MANUAL FIX'.",
    "For every new film we must copy the formula again.",
    "pandas: it is one line of code. It works for ranges and extra marks too.",
    "We can run it again every Friday and get the same result.",
    "Our view: Excel is fine for a quick look. pandas is better for work we do every week.",
]:
    note.append([line])
wb.save(OUT / "spreadsheet_cleaning_step.xlsx")
print("rows", len(g), "| pandas parsed", g["gross_raw"].map(to_crore).notna().sum())
