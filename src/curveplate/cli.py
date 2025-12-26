"""Command-line interface for curveplate."""

import argparse
import sys
from datetime import datetime

from . import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for curveplate."""
    parser = argparse.ArgumentParser(
        prog="curveplate",
        description="Generate model railway flexible track laying templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  curveplate -g 9 -t s -l 100
      Generate a straight template, 9mm gauge, 100mm length

  curveplate -g 16.5 -t c -r 300 -a 45 --right -p
      Generate a 45° curve template, 16.5mm gauge, 300mm radius, curving right, PDF only

  curveplate -g 9 -t t -r 200 -l 150 --left -3D 3
      Generate a transition template with 3mm thick STP file
""",
    )

    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

    # Output options
    output_group = parser.add_argument_group("output options")
    output_group.add_argument(
        "-o", "--output", type=str, help="Output filename (default: timestamp-based)"
    )
    output_group.add_argument("-p", "--pdf", action="store_true", help="Output PDF file")
    output_group.add_argument("-d", "--dxf", action="store_true", help="Output DXF file")
    output_group.add_argument(
        "-s",
        "--size",
        type=str,
        choices=["a0", "a1", "a2", "a3", "a4", "A0", "A1", "A2", "A3", "A4"],
        help="Paper size (ISO A0-A4)",
    )
    output_group.add_argument(
        "-b", "--border", action="store_true", help="Add title block and drawing boundary"
    )
    output_group.add_argument(
        "-3D",
        "--extrude",
        type=float,
        dest="extrude",
        metavar="THICKNESS",
        help="Extrusion thickness in mm, outputs STP file",
    )

    # Required template parameters
    required_group = parser.add_argument_group("required template parameters")
    required_group.add_argument(
        "-g", "--gauge", type=float, required=True, help="Track gauge in mm (distance between rails)"
    )
    required_group.add_argument(
        "-t",
        "--type",
        type=str,
        required=True,
        choices=["s", "c", "t", "straight", "curve", "transition"],
        help="Template type: s(traight), c(urve), or t(ransition)",
    )

    # Geometry parameters
    geom_group = parser.add_argument_group("geometry parameters")
    geom_group.add_argument(
        "-l", "--length", type=float, help="Length in mm along inner rail"
    )
    geom_group.add_argument(
        "-a", "--arc", type=float, help="Arc angle in degrees (alternative to length for curves)"
    )
    geom_group.add_argument(
        "-r", "--radius", type=float, help="Curve radius to inner rail in mm"
    )

    # Direction (mutually exclusive)
    direction_group = parser.add_mutually_exclusive_group()
    direction_group.add_argument(
        "--left", action="store_true", help="Curve to the left"
    )
    direction_group.add_argument(
        "--right", action="store_true", help="Curve to the right"
    )

    return parser


def validate_args(args: argparse.Namespace) -> list[str]:
    """Validate argument combinations and return list of errors."""
    errors = []
    template_type = args.type.lower()[0]  # Normalize to s/c/t

    if template_type == "s":  # Straight
        if not args.length:
            errors.append("Straight template requires --length")
        if args.arc:
            errors.append("Straight template does not use --arc")
        if args.radius:
            errors.append("Straight template does not use --radius")
        if args.left or args.right:
            errors.append("Straight template does not use --left/--right")

    elif template_type == "c":  # Curve
        if not args.radius:
            errors.append("Curve template requires --radius")
        if not args.length and not args.arc:
            errors.append("Curve template requires either --length or --arc")
        if args.length and args.arc:
            errors.append("Curve template: specify either --length or --arc, not both")

    elif template_type == "t":  # Transition
        if not args.radius:
            errors.append("Transition template requires --radius")
        if not args.length:
            errors.append("Transition template requires --length")
        if not args.left and not args.right:
            errors.append("Transition template requires --left or --right")
        if args.arc:
            errors.append("Transition template does not use --arc")

    return errors


def get_output_filename(args: argparse.Namespace) -> str:
    """Generate output filename based on args or use timestamp."""
    if args.output:
        return args.output

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    template_type = args.type.lower()[0]
    return f"template_{template_type}_{args.gauge}mm_{timestamp}"


def main() -> int:
    """Main entry point for curveplate CLI."""
    parser = create_parser()
    args = parser.parse_args()

    # Validate argument combinations
    errors = validate_args(args)
    if errors:
        for error in errors:
            print(f"Error: {error}", file=sys.stderr)
        return 1

    # Determine output formats
    output_pdf = args.pdf
    output_dxf = args.dxf
    output_stp = args.extrude is not None

    # Default: output both PDF and DXF if nothing specified
    if not output_pdf and not output_dxf and not output_stp:
        output_pdf = True
        output_dxf = True

    # Get output filename
    base_filename = get_output_filename(args)

    # Normalize template type
    template_type = args.type.lower()[0]

    print(f"Generating {template_type} template...")
    print(f"  Gauge: {args.gauge}mm")

    # Generate geometry
    from .geometry import (
        create_straight_template,
        create_curve_template,
        create_transition_template,
    )

    if template_type == "s":
        print(f"  Length: {args.length}mm")
        template = create_straight_template(gauge=args.gauge, length=args.length)
    elif template_type == "c":
        print(f"  Radius: {args.radius}mm")
        direction = "left" if args.left else "right"
        if args.arc:
            print(f"  Arc: {args.arc}°")
            template = create_curve_template(
                gauge=args.gauge,
                radius=args.radius,
                arc_degrees=args.arc,
                direction=direction,
            )
        else:
            print(f"  Length: {args.length}mm")
            template = create_curve_template(
                gauge=args.gauge,
                radius=args.radius,
                length=args.length,
                direction=direction,
            )
    elif template_type == "t":
        print(f"  Radius: {args.radius}mm")
        print(f"  Length: {args.length}mm")
        direction = "left" if args.left else "right"
        print(f"  Direction: {direction}")
        template = create_transition_template(
            gauge=args.gauge,
            end_radius=args.radius,
            length=args.length,
            direction=direction,
        )

    # Export files
    paper_size = args.size.lower() if args.size else None

    if output_dxf:
        from .dxf_export import export_dxf

        dxf_path = export_dxf(
            template,
            base_filename,
            paper_size=paper_size,
            add_border=args.border,
            title=f"{template_type.upper()} Template - {args.gauge}mm gauge",
        )
        print(f"  -> {dxf_path}")

    if output_pdf:
        from .pdf_export import export_pdf

        pdf_path = export_pdf(
            template,
            base_filename,
            paper_size=paper_size,
            add_border=args.border,
            title=f"{template_type.upper()} Template - {args.gauge}mm gauge",
        )
        print(f"  -> {pdf_path}")

    if output_stp:
        from .stp_export import export_stp

        stp_path = export_stp(template, base_filename, thickness=args.extrude)
        print(f"  -> {stp_path}")

    print("Done!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
