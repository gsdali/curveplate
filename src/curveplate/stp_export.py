"""STEP (STP) file export for 3D track templates.

Uses cadquery for proper B-rep geometry generation and STEP export.
"""

from pathlib import Path

from .geometry import Template


def export_stp(
    template: Template,
    output_path: str | Path,
    thickness: float,
) -> Path:
    """Export template as extruded 3D STEP file.

    Args:
        template: Template geometry to export
        output_path: Output file path (without extension)
        thickness: Extrusion thickness in mm

    Returns:
        Path to created STP file
    """
    output_path = Path(output_path)
    if output_path.suffix.lower() not in (".stp", ".step"):
        output_path = Path(str(output_path) + ".stp")

    try:
        import cadquery as cq
    except ImportError:
        raise ImportError(
            "cadquery is required for STEP export. "
            "Install with: pip install curveplate[stp]"
        )

    # Extract polygon vertices (excluding closing point if present)
    vertices = template.points
    if len(vertices) > 1 and vertices[0].x == vertices[-1].x and vertices[0].y == vertices[-1].y:
        vertices = vertices[:-1]

    # Convert to list of tuples for cadquery
    points = [(p.x, p.y) for p in vertices]

    # Create 2D profile using polyline
    # cadquery needs the points to form a closed wire
    wire = cq.Workplane("XY").polyline(points).close()

    # Extrude to create 3D solid
    solid = wire.extrude(thickness)

    # Export to STEP
    cq.exporters.export(solid, str(output_path), exportType="STEP")

    return output_path
