"""Trial check: does the PDFium build inside pypdfium2 expose what the hidden-text checks need?"""
import ctypes, platform, sys
from reportlab.pdfgen import canvas
import pypdfium2 as pdfium, pypdfium2.raw as r

print(platform.platform(), "| pypdfium2", pdfium.PYPDFIUM_INFO, "| pdfium", pdfium.PDFIUM_INFO)
NEEDED = ["FPDFText_GetFillColor", "FPDFText_GetFontSize", "FPDFText_GetCharBox", "FPDFText_GetUnicode",
          "FPDFText_HasUnicodeMapError", "FPDFText_GetTextObject", "FPDFTextObj_GetTextRenderMode",
          "FPDFText_IsGenerated", "FPDFPageObj_GetIsActive"]
missing = [n for n in NEEDED if not hasattr(r, n)]
print("missing functions:", missing)

c = canvas.Canvas("t.pdf", pagesize=(400, 200))
c.setFont("Helvetica", 12); c.setFillColorRGB(0, 0, 0); c.drawString(20, 160, "Visible")
c.setFillColorRGB(1, 1, 1); c.drawString(20, 130, "White")
c.setFillColorRGB(0, 0, 0); c.setFont("Helvetica", 1); c.drawString(20, 100, "Tiny")
c.setFont("Helvetica", 12)
t = c.beginText(20, 70); t.setTextRenderMode(3); t.textLine("Invis"); c.drawText(t)
c.save()

tp = pdfium.PdfDocument("t.pdf")[0].get_textpage()
seen = {}
for i in range(r.FPDFText_CountChars(tp.raw)):
    ch = chr(r.FPDFText_GetUnicode(tp.raw, i))
    if not ch.strip():
        continue
    R, G, B, A = (ctypes.c_uint() for _ in range(4))
    r.FPDFText_GetFillColor(tp.raw, i, R, G, B, A)
    size = round(r.FPDFText_GetFontSize(tp.raw, i), 1)
    obj = r.FPDFText_GetTextObject(tp.raw, i)
    mode = r.FPDFTextObj_GetTextRenderMode(obj) if obj else None
    box = [ctypes.c_double() for _ in range(4)]
    assert r.FPDFText_GetCharBox(tp.raw, i, *box)
    seen.setdefault((R.value, G.value, B.value, size, mode), []).append(ch)
got = {"".join(v): k for k, v in seen.items()}
for word, k in got.items():
    print(f"{word:8s} R,G,B,size,render_mode = {k}")
expected = {"Visible": (0, 0, 0, 12.0, 0), "White": (255, 255, 255, 12.0, 0),
            "Tiny": (0, 0, 0, 1.0, 0), "Invis": (0, 0, 0, 12.0, 3)}
ok = not missing and got == expected
print("RESULT pdfium:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
