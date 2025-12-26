"""PDF file export for track templates."""

from datetime import datetime
from pathlib import Path

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from .geometry import Template


# ISO paper sizes in mm (width, height) - landscape orientation
PAPER_SIZES = {
    "a0": (1189, 841),
    "a1": (841, 594),
    "a2": (594, 420),
    "a3": (420, 297),
    "a4": (297, 210),
}


def select_paper_size(template: Template, margin: float = 20.0) -> str:
    """Select smallest paper size that fits the template."""
    width, height = template.dimensions()
    required_w = width + 2 * margin
    required_h = height + 2 * margin

    for size in ["a4", "a3", "a2", "a1", "a0"]:
        paper_w, paper_h = PAPER_SIZES[size]
        if (required_w <= paper_w and required_h <= paper_h) or (
            required_w <= paper_h and required_h <= paper_w
        ):
            return size

    return "a0"


def export_pdf(
    template: Template,
    output_path: str | Path,
    paper_size: str | None = None,
    add_border: bool = False,
    title: str | None = None,
) -> Path:
    """Export template to PDF file.

    Args:
        template: Template geometry to export
        output_path: Output file path (without extension)
        paper_size: ISO paper size (a0-a4) or None for auto-select
        add_border: Whether to add title block and border
        title: Title for title block

    Returns:
        Path to created PDF file
    """
    output_path = Path(output_path)
    if output_path.suffix.lower() != ".pdf":
        output_path = Path(str(output_path) + ".pdf")

    # Select paper size if not specified
    if paper_size is None:
        paper_size = select_paper_size(template)
    paper_size = paper_size.lower()
    paper_w, paper_h = PAPER_SIZES[paper_size]

    # Create PDF canvas
    c = canvas.Canvas(str(output_path), pagesize=(paper_w * mm, paper_h * mm))

    # Center template on paper
    min_pt, max_pt = template.bounding_box()
    template_w = max_pt.x - min_pt.x
    template_h = max_pt.y - min_pt.y

    offset_x = (paper_w - template_w) / 2 - min_pt.x
    offset_y = (paper_h - template_h) / 2 - min_pt.y

    # Draw template outline
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.5)

    path = c.beginPath()
    first_point = template.points[0]
    path.moveTo((first_point.x + offset_x) * mm, (first_point.y + offset_y) * mm)

    for point in template.points[1:]:
        path.lineTo((point.x + offset_x) * mm, (point.y + offset_y) * mm)

    path.close()
    c.drawPath(path, stroke=1, fill=0)

    # Add border and title block if requested
    if add_border:
        margin = 10.0
        _draw_border(c, paper_w, paper_h, margin)
        _draw_title_block(
            c,
            paper_w,
            paper_h,
            margin,
            title=title or "Track Template",
            gauge=template.gauge,
            template_type=template.template_type,
        )

    c.save()
    return output_path


def _draw_border(c: canvas.Canvas, paper_w: float, paper_h: float, margin: float) -> None:
    """Draw border rectangle."""
    c.setStrokeColorRGB(0, 0, 0.5)  # Dark blue
    c.setLineWidth(0.5)
    c.rect(
        margin * mm,
        margin * mm,
        (paper_w - 2 * margin) * mm,
        (paper_h - 2 * margin) * mm,
    )


def _draw_title_block(
    c: canvas.Canvas,
    paper_w: float,
    paper_h: float,
    margin: float,
    title: str,
    gauge: float,
    template_type: str,
) -> None:
    """Draw title block in bottom-right corner."""
    block_w = 100.0
    block_h = 30.0

    x1 = paper_w - margin - block_w
    y1 = margin
    x2 = paper_w - margin
    y2 = margin + block_h

    c.setStrokeColorRGB(0, 0, 0.5)
    c.setLineWidth(0.3)

    # Outer rectangle
    c.rect(x1 * mm, y1 * mm, block_w * mm, block_h * mm)

    # Horizontal divider
    c.line(x1 * mm, (y1 + 15) * mm, x2 * mm, (y1 + 15) * mm)

    # Vertical divider
    c.line((x1 + 50) * mm, y1 * mm, (x1 + 50) * mm, (y1 + 15) * mm)

    # Text
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 10)
    c.drawString((x1 + 5) * mm, (y2 - 10) * mm, title)

    c.setFont("Helvetica", 8)
    c.drawString((x1 + 5) * mm, (y1 + 5) * mm, f"Gauge: {gauge}mm")
    c.drawString((x1 + 55) * mm, (y1 + 5) * mm, f"Type: {template_type}")

    # Date
    c.setFont("Helvetica", 6)
    date_str = datetime.now().strftime("%Y-%m-%d")
    c.drawString((x1 + 5) * mm, (y1 + 17) * mm, f"Date: {date_str}")
