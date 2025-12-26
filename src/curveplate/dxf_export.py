"""DXF file export for track templates."""

from pathlib import Path

import ezdxf
from ezdxf.enums import TextEntityAlignment

from .geometry import Template, Point


# ISO paper sizes in mm (width, height) - landscape orientation
PAPER_SIZES = {
    "a0": (1189, 841),
    "a1": (841, 594),
    "a2": (594, 420),
    "a3": (420, 297),
    "a4": (297, 210),
}


def select_paper_size(template: Template, margin: float = 20.0) -> str:
    """Select smallest paper size that fits the template.

    Args:
        template: Template to fit
        margin: Margin around template in mm

    Returns:
        Paper size string (a0-a4)
    """
    width, height = template.dimensions()
    required_w = width + 2 * margin
    required_h = height + 2 * margin

    # Try sizes from smallest to largest
    for size in ["a4", "a3", "a2", "a1", "a0"]:
        paper_w, paper_h = PAPER_SIZES[size]
        # Check both orientations
        if (required_w <= paper_w and required_h <= paper_h) or (
            required_w <= paper_h and required_h <= paper_w
        ):
            return size

    return "a0"  # Fallback to largest


def export_dxf(
    template: Template,
    output_path: str | Path,
    paper_size: str | None = None,
    add_border: bool = False,
    title: str | None = None,
) -> Path:
    """Export template to DXF file.

    Args:
        template: Template geometry to export
        output_path: Output file path (without extension)
        paper_size: ISO paper size (a0-a4) or None for auto-select
        add_border: Whether to add title block and border
        title: Title for title block

    Returns:
        Path to created DXF file
    """
    output_path = Path(output_path)
    if output_path.suffix.lower() != ".dxf":
        output_path = Path(str(output_path) + ".dxf")

    # Select paper size if not specified
    if paper_size is None:
        paper_size = select_paper_size(template)
    paper_size = paper_size.lower()
    paper_w, paper_h = PAPER_SIZES[paper_size]

    # Create DXF document
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    # Add template layer
    doc.layers.add("TEMPLATE", color=7)  # White
    if add_border:
        doc.layers.add("BORDER", color=5)  # Blue
        doc.layers.add("TITLEBLOCK", color=5)

    # Center template on paper
    min_pt, max_pt = template.bounding_box()
    template_w = max_pt.x - min_pt.x
    template_h = max_pt.y - min_pt.y

    offset_x = (paper_w - template_w) / 2 - min_pt.x
    offset_y = (paper_h - template_h) / 2 - min_pt.y

    # Draw template outline as polyline
    translated_points = [(p.x + offset_x, p.y + offset_y) for p in template.points]
    msp.add_lwpolyline(translated_points, close=True, dxfattribs={"layer": "TEMPLATE"})

    # Add border and title block if requested
    if add_border:
        margin = 10.0
        _add_border(msp, paper_w, paper_h, margin)
        _add_title_block(
            msp,
            paper_w,
            paper_h,
            margin,
            title=title or "Track Template",
            gauge=template.gauge,
            template_type=template.template_type,
            scale="1:1",
        )

    doc.saveas(output_path)
    return output_path


def _add_border(msp, paper_w: float, paper_h: float, margin: float) -> None:
    """Add drawing border."""
    points = [
        (margin, margin),
        (paper_w - margin, margin),
        (paper_w - margin, paper_h - margin),
        (margin, paper_h - margin),
        (margin, margin),
    ]
    msp.add_lwpolyline(points, dxfattribs={"layer": "BORDER"})


def _add_title_block(
    msp,
    paper_w: float,
    paper_h: float,
    margin: float,
    title: str,
    gauge: float,
    template_type: str,
    scale: str,
) -> None:
    """Add title block in bottom-right corner."""
    block_w = 100.0
    block_h = 30.0

    x1 = paper_w - margin - block_w
    y1 = margin
    x2 = paper_w - margin
    y2 = margin + block_h

    # Title block outline
    msp.add_lwpolyline(
        [(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)],
        dxfattribs={"layer": "TITLEBLOCK"},
    )

    # Horizontal divider
    msp.add_line((x1, y1 + 15), (x2, y1 + 15), dxfattribs={"layer": "TITLEBLOCK"})

    # Vertical divider
    msp.add_line((x1 + 50, y1), (x1 + 50, y1 + 15), dxfattribs={"layer": "TITLEBLOCK"})

    # Text
    text_height = 3.0
    msp.add_text(
        title,
        height=text_height,
        dxfattribs={"layer": "TITLEBLOCK"},
    ).set_placement((x1 + 5, y2 - 8), align=TextEntityAlignment.LEFT)

    msp.add_text(
        f"Gauge: {gauge}mm",
        height=2.5,
        dxfattribs={"layer": "TITLEBLOCK"},
    ).set_placement((x1 + 5, y1 + 5), align=TextEntityAlignment.LEFT)

    msp.add_text(
        f"Type: {template_type}",
        height=2.5,
        dxfattribs={"layer": "TITLEBLOCK"},
    ).set_placement((x1 + 55, y1 + 5), align=TextEntityAlignment.LEFT)
