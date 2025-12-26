"""STEP (STP) file export for 3D track templates.

Uses a lightweight approach to generate STEP files for simple extruded geometry
without heavy CAD dependencies.
"""

from pathlib import Path
from datetime import datetime

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

    # For now, generate a placeholder STEP file
    # TODO: Implement proper STEP geometry using steputils or similar
    step_content = _generate_step_file(template, thickness)

    output_path.write_text(step_content)
    return output_path


def _generate_step_file(template: Template, thickness: float) -> str:
    """Generate STEP file content for extruded template.

    This is a minimal STEP AP214 file structure.
    For production use, consider using steputils for proper entity generation.
    """
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # Extract polygon vertices (excluding closing point)
    vertices = template.points[:-1] if template.points[-1] == template.points[0] else template.points

    # STEP file header
    header = f"""ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('Curveplate Track Template'),'2;1');
FILE_NAME('{template.template_type}_template.stp','{timestamp}',(''),(''),'','curveplate','');
FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));
ENDSEC;
DATA;
"""

    # Basic STEP entities for a simple extruded polygon
    # This is a simplified structure - full implementation would need proper B-rep
    entities = []
    entity_id = 1

    # Application context
    entities.append(f"#{entity_id}=APPLICATION_CONTEXT('automotive design');")
    app_context_id = entity_id
    entity_id += 1

    entities.append(
        f"#{entity_id}=APPLICATION_PROTOCOL_DEFINITION('international standard',"
        f"'automotive_design',2010,#{app_context_id});"
    )
    entity_id += 1

    # Product definition
    entities.append(f"#{entity_id}=PRODUCT('Template','Track Template','',(#{entity_id + 1}));")
    product_id = entity_id
    entity_id += 1

    entities.append(
        f"#{entity_id}=PRODUCT_CONTEXT('',#{app_context_id},'mechanical');"
    )
    entity_id += 1

    entities.append(
        f"#{entity_id}=PRODUCT_DEFINITION_FORMATION('','',#{product_id});"
    )
    pdf_id = entity_id
    entity_id += 1

    entities.append(
        f"#{entity_id}=PRODUCT_DEFINITION_CONTEXT('part definition',#{app_context_id},'design');"
    )
    pdc_id = entity_id
    entity_id += 1

    entities.append(
        f"#{entity_id}=PRODUCT_DEFINITION('design','',#{pdf_id},#{pdc_id});"
    )
    entity_id += 1

    # Cartesian points for vertices
    point_ids = []
    for v in vertices:
        entities.append(f"#{entity_id}=CARTESIAN_POINT('',('{v.x}','{v.y}','0.0'));")
        point_ids.append(entity_id)
        entity_id += 1

    # Add comment about geometry
    entities.append(f"/* Template: {template.template_type}, Gauge: {template.gauge}mm, Thickness: {thickness}mm */")
    entities.append(f"/* Vertices: {len(vertices)} points defining the cross-section */")

    # Note: Full STEP implementation would include:
    # - EDGE_CURVE, EDGE_LOOP, FACE_BOUND for the profile
    # - EXTRUDED_AREA_SOLID for the 3D shape
    # - MANIFOLD_SOLID_BREP for the complete solid
    # This requires proper B-rep construction with steputils

    footer = """ENDSEC;
END-ISO-10303-21;
"""

    return header + "\n".join(entities) + "\n" + footer
