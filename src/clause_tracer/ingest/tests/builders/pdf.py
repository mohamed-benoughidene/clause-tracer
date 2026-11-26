"""Build PDFs with known glyph positions for the tests (S5-M1-T8).

ReportLab draws the pages with `invariant=1`; pikepdf adds what
ReportLab cannot do: rotation, a crop box, optional-content layers and
encryption. The builder returns what it placed, so a test can compare
the reader with the builder instead of a typed number.
"""

import io
from collections.abc import Sequence
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import pikepdf
import reportlab
from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfgen.textobject import PDFTextObject


@dataclass(frozen=True, slots=True, kw_only=True)
class Text:
    """One run of text, in PDF user space (origin bottom-left)."""

    x: float
    baseline: float
    text: str
    size: float = 10.0
    color: tuple[float, float, float] = (0.0, 0.0, 0.0)
    alpha: float = 1.0
    render_mode: int = 0
    font: str = "Vera"


@dataclass(frozen=True, slots=True, kw_only=True)
class Pic:
    """One flat grey image."""

    x: float
    y: float
    width: float
    height: float
    grey: int = 128


@dataclass(frozen=True, slots=True, kw_only=True)
class Layer:
    """An optional-content group around one page's items."""

    name: str
    items: tuple[Text, ...]
    visible: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class PageSpec:
    """One page: items, layers, rotation and crop box."""

    width: float = 612.0
    height: float = 792.0
    items: tuple[Text | Pic, ...] = ()
    layers: tuple[Layer, ...] = ()
    rotate: int = 0
    crop: tuple[float, float, float, float] | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class Placed:
    """One character the builder drew, and where it drew it."""

    page: int
    char: str
    x: float
    baseline: float
    size: float


@dataclass(frozen=True, slots=True, kw_only=True)
class BuiltPdf:
    """The bytes, and the characters placed in them."""

    data: bytes
    placed: tuple[Placed, ...]


@cache
def _register_vera() -> None:
    """Register the Vera font that ships with ReportLab, once."""
    path = Path(reportlab.__file__).parent / "fonts" / "Vera.ttf"
    pdfmetrics.registerFont(TTFont("Vera", str(path)))


def _draw_text(canvas: Canvas, item: Text, page: int, placed: list[Placed]) -> None:
    # The saved state keeps this item's colour, alpha and render mode from
    # reaching the next item.
    canvas.saveState()
    canvas.setFont(item.font, item.size)
    canvas.setFillColorRGB(*item.color)
    canvas.setFillAlpha(item.alpha)
    text = canvas.beginText(item.x, item.baseline)
    assert isinstance(text, PDFTextObject)
    text.setFont(item.font, item.size)
    text.setTextRenderMode(item.render_mode)
    text.textOut(item.text)
    canvas.drawText(text)
    canvas.restoreState()
    for index, char in enumerate(item.text):
        placed.append(
            Placed(
                page=page,
                char=char,
                x=item.x + pdfmetrics.stringWidth(item.text[:index], item.font, item.size),
                baseline=item.baseline,
                size=item.size,
            )
        )


def _draw_pic(canvas: Canvas, item: Pic) -> None:
    canvas.setFillAlpha(1.0)
    image = Image.new("L", (4, 4), item.grey)
    canvas.drawImage(ImageReader(image), item.x, item.y, item.width, item.height)


def _finish(
    data: bytes,
    pages: Sequence[PageSpec],
    *,
    copy_off: bool,
    user_password: str | None,
) -> bytes:
    pdf = pikepdf.open(io.BytesIO(data))
    try:
        on_groups: list[pikepdf.Object] = []
        off_groups: list[pikepdf.Object] = []
        for number, spec in enumerate(pages):
            if spec.rotate:
                pdf.pages[number].obj.Rotate = spec.rotate
            if spec.crop is not None:
                pdf.pages[number].cropbox = pikepdf.Array(spec.crop)
            if not spec.layers:
                continue
            page = pdf.pages[number]
            resources = page.get("/Resources", pikepdf.Dictionary())
            properties = resources.get("/Properties", pikepdf.Dictionary())
            for layer in spec.layers:
                group = pdf.make_indirect(
                    pikepdf.Dictionary(Type=pikepdf.Name("/OCG"), Name=pikepdf.String(layer.name))
                )
                properties[pikepdf.Name("/" + layer.name)] = group
                if layer.visible:
                    on_groups.append(group)
                else:
                    off_groups.append(group)
            resources.Properties = properties
            page.Resources = resources
        if on_groups or off_groups:
            pdf.Root.OptionalContentProperties = pikepdf.Dictionary(
                OCGs=pikepdf.Array(on_groups + off_groups),
                D=pikepdf.Dictionary(ON=pikepdf.Array(on_groups), OFF=pikepdf.Array(off_groups)),
            )
        output = io.BytesIO()
        if copy_off or user_password is not None:
            pdf.save(
                output,
                encryption=pikepdf.Encryption(
                    owner="clause-tracer",
                    user=user_password or "",
                    allow=pikepdf.Permissions(extract=not copy_off),
                ),
            )
        else:
            pdf.save(output)
        return output.getvalue()
    finally:
        pdf.close()


def build_pdf(
    pages: Sequence[PageSpec],
    *,
    copy_off: bool = False,
    user_password: str | None = None,
) -> BuiltPdf:
    """Return the bytes and the characters placed in them."""
    _register_vera()
    first = pages[0] if pages else PageSpec()
    buffer = io.BytesIO()
    canvas = Canvas(buffer, pagesize=(first.width, first.height), invariant=1)
    placed: list[Placed] = []
    for number, spec in enumerate(pages, start=1):
        canvas.setPageSize((spec.width, spec.height))
        for item in spec.items:
            if isinstance(item, Text):
                _draw_text(canvas, item, number, placed)
            else:
                _draw_pic(canvas, item)
        for layer in spec.layers:
            # ReportLab has no public marked-content method; the operators
            # are the two tokens of an optional-content block.
            canvas._code.append(f"/OC /{layer.name} BDC")
            for item in layer.items:
                _draw_text(canvas, item, number, placed)
            canvas._code.append("EMC")
        canvas.showPage()
    canvas.save()
    data = _finish(buffer.getvalue(), pages, copy_off=copy_off, user_password=user_password)
    return BuiltPdf(data=data, placed=tuple(placed))


def plain_page(lines: Sequence[str]) -> BuiltPdf:
    """Ten-point Vera lines, 14 points apart, from the top left."""
    return build_pdf(
        [
            PageSpec(
                items=tuple(
                    Text(x=72.0, baseline=720.0 - 14.0 * index, text=line)
                    for index, line in enumerate(lines)
                )
            )
        ]
    )


def ligature_page() -> BuiltPdf:
    """One glyph that PDFium reads as two letters."""
    return build_pdf([PageSpec(items=(Text(x=72.0, baseline=720.0, text="\ufb01"),))])


def two_column_page() -> BuiltPdf:
    """Two blocks side by side, each drawn column first."""
    left = tuple(
        Text(x=72.0, baseline=720.0 - 14.0 * index, text=text)
        for index, text in enumerate(("Left one", "Left two"))
    )
    right = tuple(
        Text(x=320.0, baseline=720.0 - 14.0 * index, text=text)
        for index, text in enumerate(("Right one", "Right two"))
    )
    return build_pdf([PageSpec(items=left + right)])


def header_footer_pages(count: int) -> BuiltPdf:
    """One body line on each page, with a header at the top and a footer below."""
    return build_pdf(
        [
            PageSpec(
                items=(
                    Text(x=72.0, baseline=720.0, text="Services Agreement"),
                    Text(x=72.0, baseline=686.0, text=f"Body {number}."),
                    Text(x=72.0, baseline=72.0, text=f"Page {number} of {count}"),
                )
            )
            for number in range(1, count + 1)
        ]
    )


def scanned_page() -> BuiltPdf:
    """One picture over the whole page, with no text."""
    return build_pdf([PageSpec(items=(Pic(x=0.0, y=0.0, width=612.0, height=792.0),))])


def scanned_with_ocr_layer() -> BuiltPdf:
    """A page picture with ten invisible lines of text over it."""
    return build_pdf(
        [
            PageSpec(
                items=(
                    Pic(x=0.0, y=0.0, width=612.0, height=792.0),
                    *(
                        Text(
                            x=72.0,
                            baseline=720.0 - 14.0 * index,
                            text=f"OCR line {index + 1}",
                            render_mode=3,
                        )
                        for index in range(10)
                    ),
                )
            )
        ]
    )


def white_text_page() -> BuiltPdf:
    """A body line in black and one in white."""
    return build_pdf(
        [
            PageSpec(
                items=(
                    Text(x=72.0, baseline=720.0, text="Black body line."),
                    Text(x=72.0, baseline=700.0, text="White hidden line.", color=(1.0, 1.0, 1.0)),
                )
            )
        ]
    )


def tiny_text_page() -> BuiltPdf:
    """A line at 1 point."""
    return build_pdf([PageSpec(items=(Text(x=72.0, baseline=720.0, text="Tiny line.", size=1.0),))])


def invisible_mode_page() -> BuiltPdf:
    """A line drawn in render mode 3, with no picture."""
    return build_pdf(
        [PageSpec(items=(Text(x=72.0, baseline=720.0, text="Invisible line.", render_mode=3),))]
    )


def low_alpha_page() -> BuiltPdf:
    """A black line at alpha 0.05."""
    return build_pdf(
        [PageSpec(items=(Text(x=72.0, baseline=720.0, text="Faint line.", alpha=0.05),))]
    )


def hidden_layer_page() -> BuiltPdf:
    """One visible layer and one switched off."""
    return build_pdf(
        [
            PageSpec(
                items=(Text(x=72.0, baseline=720.0, text="Body line."),),
                layers=(
                    Layer(
                        name="Visible",
                        items=(Text(x=72.0, baseline=700.0, text="Visible layer."),),
                        visible=True,
                    ),
                    Layer(
                        name="Hidden",
                        items=(Text(x=72.0, baseline=680.0, text="Hidden layer."),),
                        visible=False,
                    ),
                ),
            )
        ]
    )


def off_page_text() -> BuiltPdf:
    """A line that starts off the left edge."""
    return build_pdf([PageSpec(items=(Text(x=-300.0, baseline=720.0, text="Off the page."),))])


def duplicate_glyph_page() -> BuiltPdf:
    """The same text twice at the same place, white first and black second."""
    return build_pdf(
        [
            PageSpec(
                items=(
                    Text(x=72.0, baseline=720.0, text="Duplicate.", color=(1.0, 1.0, 1.0)),
                    Text(x=72.0, baseline=720.0, text="Duplicate."),
                )
            )
        ]
    )


def rotated_page(degrees: int) -> BuiltPdf:
    """One page with a rotation, set with pikepdf."""
    return build_pdf(
        [PageSpec(items=(Text(x=72.0, baseline=720.0, text="Rotated page."),), rotate=degrees)]
    )


def cropped_page() -> BuiltPdf:
    """One page with a crop box, set with pikepdf."""
    return build_pdf(
        [
            PageSpec(
                items=(Text(x=72.0, baseline=720.0, text="Cropped page."),),
                crop=(0.0, 0.0, 400.0, 600.0),
            )
        ]
    )


def blank_page() -> BuiltPdf:
    """One page with nothing on it."""
    return build_pdf([PageSpec()])


def left_blank_page() -> BuiltPdf:
    """One page with only the words that say it is blank."""
    return build_pdf(
        [
            PageSpec(
                items=(Text(x=72.0, baseline=720.0, text="This page is intentionally left blank."),)
            )
        ]
    )


def signature_page() -> BuiltPdf:
    """Two lines and a small picture."""
    return build_pdf(
        [
            PageSpec(
                items=(
                    Text(x=72.0, baseline=720.0, text="Signed by:"),
                    Text(x=72.0, baseline=700.0, text="A. Person"),
                    Pic(x=72.0, y=600.0, width=120.0, height=40.0),
                )
            )
        ]
    )


def many_pages(count: int) -> BuiltPdf:
    """`count` pages that share one page object, cheap for 1,000."""
    one = build_pdf([PageSpec(items=(Text(x=72.0, baseline=720.0, text="Page"),))])
    pdf = pikepdf.open(io.BytesIO(one.data))
    try:
        for _ in range(count - 1):
            pdf.pages.append(pdf.pages[0])
        output = io.BytesIO()
        pdf.save(output, object_stream_mode=pikepdf.ObjectStreamMode.generate)
        return BuiltPdf(data=output.getvalue(), placed=one.placed)
    finally:
        pdf.close()
