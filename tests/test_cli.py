"""Tests for CLI module."""

import pytest

from curveplate.cli import create_parser, validate_args


class TestArgumentParser:
    def test_parser_requires_gauge(self):
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["-t", "s", "-l", "100"])

    def test_parser_requires_type(self):
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["-g", "9", "-l", "100"])

    def test_parser_straight_template(self):
        parser = create_parser()
        args = parser.parse_args(["-g", "9", "-t", "s", "-l", "100"])
        assert args.gauge == 9.0
        assert args.type == "s"
        assert args.length == 100.0

    def test_parser_curve_template(self):
        parser = create_parser()
        args = parser.parse_args(["-g", "16.5", "-t", "curve", "-r", "300", "-a", "45", "--right"])
        assert args.gauge == 16.5
        assert args.type == "curve"
        assert args.radius == 300.0
        assert args.arc == 45.0
        assert args.right is True

    def test_parser_transition_template(self):
        parser = create_parser()
        args = parser.parse_args(["-g", "9", "-t", "t", "-r", "200", "-l", "150", "--left"])
        assert args.gauge == 9.0
        assert args.type == "t"
        assert args.radius == 200.0
        assert args.length == 150.0
        assert args.left is True

    def test_parser_output_options(self):
        parser = create_parser()
        args = parser.parse_args(["-g", "9", "-t", "s", "-l", "100", "-p", "-d", "-s", "A3", "-b"])
        assert args.pdf is True
        assert args.dxf is True
        assert args.size == "A3"
        assert args.border is True

    def test_parser_3d_extrusion(self):
        parser = create_parser()
        args = parser.parse_args(["-g", "9", "-t", "s", "-l", "100", "-3D", "3"])
        assert args.extrude == 3.0


class TestArgumentValidation:
    def test_straight_requires_length(self):
        parser = create_parser()
        args = parser.parse_args(["-g", "9", "-t", "s"])
        errors = validate_args(args)
        assert "Straight template requires --length" in errors

    def test_straight_rejects_arc(self):
        parser = create_parser()
        args = parser.parse_args(["-g", "9", "-t", "s", "-l", "100", "-a", "45"])
        errors = validate_args(args)
        assert "Straight template does not use --arc" in errors

    def test_curve_requires_radius(self):
        parser = create_parser()
        args = parser.parse_args(["-g", "9", "-t", "c", "-l", "100"])
        errors = validate_args(args)
        assert "Curve template requires --radius" in errors

    def test_curve_requires_length_or_arc(self):
        parser = create_parser()
        args = parser.parse_args(["-g", "9", "-t", "c", "-r", "200"])
        errors = validate_args(args)
        assert "Curve template requires either --length or --arc" in errors

    def test_curve_rejects_both_length_and_arc(self):
        parser = create_parser()
        args = parser.parse_args(["-g", "9", "-t", "c", "-r", "200", "-l", "100", "-a", "45"])
        errors = validate_args(args)
        assert "Curve template: specify either --length or --arc, not both" in errors

    def test_transition_requires_direction(self):
        parser = create_parser()
        args = parser.parse_args(["-g", "9", "-t", "t", "-r", "200", "-l", "100"])
        errors = validate_args(args)
        assert "Transition template requires --left or --right" in errors

    def test_valid_straight_template(self):
        parser = create_parser()
        args = parser.parse_args(["-g", "9", "-t", "s", "-l", "100"])
        errors = validate_args(args)
        assert len(errors) == 0

    def test_valid_curve_template(self):
        parser = create_parser()
        args = parser.parse_args(["-g", "9", "-t", "c", "-r", "200", "-a", "45"])
        errors = validate_args(args)
        assert len(errors) == 0

    def test_valid_transition_template(self):
        parser = create_parser()
        args = parser.parse_args(["-g", "9", "-t", "t", "-r", "200", "-l", "100", "--left"])
        errors = validate_args(args)
        assert len(errors) == 0
