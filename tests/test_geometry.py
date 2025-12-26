"""Tests for geometry module."""

import math

import pytest

from curveplate.geometry import (
    Point,
    create_straight_template,
    create_curve_template,
    create_transition_template,
)


class TestPoint:
    def test_point_creation(self):
        p = Point(1.0, 2.0)
        assert p.x == 1.0
        assert p.y == 2.0

    def test_point_addition(self):
        p1 = Point(1.0, 2.0)
        p2 = Point(3.0, 4.0)
        result = p1 + p2
        assert result.x == 4.0
        assert result.y == 6.0

    def test_point_subtraction(self):
        p1 = Point(5.0, 7.0)
        p2 = Point(2.0, 3.0)
        result = p1 - p2
        assert result.x == 3.0
        assert result.y == 4.0

    def test_point_rotation(self):
        p = Point(1.0, 0.0)
        rotated = p.rotate(math.pi / 2)  # 90 degrees
        assert abs(rotated.x) < 1e-10
        assert abs(rotated.y - 1.0) < 1e-10


class TestStraightTemplate:
    def test_straight_template_dimensions(self):
        template = create_straight_template(gauge=9.0, length=100.0)
        width, height = template.dimensions()
        assert abs(width - 100.0) < 1e-10
        assert abs(height - 9.0) < 1e-10

    def test_straight_template_type(self):
        template = create_straight_template(gauge=16.5, length=50.0)
        assert template.template_type == "straight"

    def test_straight_template_closed_polygon(self):
        template = create_straight_template(gauge=9.0, length=100.0)
        # Polygon should be closed (first point == last point)
        assert template.points[0].x == template.points[-1].x
        assert template.points[0].y == template.points[-1].y

    def test_straight_template_has_5_points(self):
        """4 corners + 1 closing point."""
        template = create_straight_template(gauge=9.0, length=100.0)
        assert len(template.points) == 5


class TestCurveTemplate:
    def test_curve_template_with_arc_degrees(self):
        template = create_curve_template(gauge=9.0, radius=200.0, arc_degrees=45.0)
        assert template.template_type == "curve"

    def test_curve_template_with_length(self):
        template = create_curve_template(gauge=9.0, radius=200.0, length=100.0)
        assert template.template_type == "curve"

    def test_curve_template_requires_arc_or_length(self):
        with pytest.raises(ValueError):
            create_curve_template(gauge=9.0, radius=200.0)

    def test_curve_template_closed_polygon(self):
        template = create_curve_template(gauge=9.0, radius=200.0, arc_degrees=90.0)
        first = template.points[0]
        last = template.points[-1]
        assert abs(first.x - last.x) < 1e-6
        assert abs(first.y - last.y) < 1e-6

    def test_curve_left_vs_right(self):
        left = create_curve_template(gauge=9.0, radius=200.0, arc_degrees=45.0, direction="left")
        right = create_curve_template(gauge=9.0, radius=200.0, arc_degrees=45.0, direction="right")
        # The templates should be mirror images
        # Just check they're different
        assert left.points[1].y != right.points[1].y


class TestTransitionTemplate:
    def test_transition_template_basic(self):
        template = create_transition_template(
            gauge=9.0, end_radius=200.0, length=100.0, direction="right"
        )
        assert template.template_type == "transition"

    def test_transition_template_closed_polygon(self):
        template = create_transition_template(
            gauge=9.0, end_radius=200.0, length=150.0, direction="left"
        )
        first = template.points[0]
        last = template.points[-1]
        assert abs(first.x - last.x) < 1e-6
        assert abs(first.y - last.y) < 1e-6

    def test_transition_starts_straight(self):
        """The beginning of a transition should be essentially straight."""
        template = create_transition_template(
            gauge=9.0, end_radius=200.0, length=100.0, direction="right"
        )
        # First few points should have y close to 0 (straight)
        assert abs(template.points[0].y) < 1e-6
        assert abs(template.points[1].y) < 0.5  # Nearly straight at start
