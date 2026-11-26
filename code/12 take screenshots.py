import subprocess, copy
import nbformat as nbf
from nbconvert import HTMLExporter
from PIL import Image, ImageChops
from common import ROOT

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUTDIR = ROOT / "outputs" / "screenshots"
OUTDIR.mkdir(parents=True, exist_ok=True)
TMP = ROOT / "outputs" / "screenshots" / "html"
TMP.mkdir(exist_ok=True)

nb = nbf.read(str(ROOT / "code" / "charts.ipynb"), as_version=4)
exp = HTMLExporter(template_name="lab")

for i, cell in enumerate(nb.cells):
    tag = cell.metadata.get("tags", [""])[0]
    if not tag.startswith("chart"):
        continue
    for o in cell.outputs:
        if o.get("output_type") == "error":
            raise SystemExit(f"{tag} has an error")
    one = copy.deepcopy(nb)
    one.cells = [cell]
    html, _ = exp.from_notebook_node(one)
    html = html.replace("</head>", "<style>body{background:white;padding:10px 20px;}</style></head>")
    page = TMP / f"{tag}.html"
    page.write_text(html, encoding="utf-8")
    png = OUTDIR / f"{tag}.png"
    subprocess.run([EDGE, "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1.5",
                    "--window-size=1000,1100", f"--screenshot={png}", page.as_uri()],
                   check=True, capture_output=True, timeout=120)
    im = Image.open(png).convert("RGB")
    bg = Image.new("RGB", im.size, (255, 255, 255))
    box = ImageChops.difference(im, bg).getbbox()
    if box:
        im = im.crop((0, 0, im.width, min(im.height, box[3] + 30)))
    im.save(png)
    print("saved", png, im.size)
