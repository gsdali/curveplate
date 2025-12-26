"""Geometry calculations for track templates."""

from dataclasses import dataclass
from typing import Literal
import math


@dataclass
class Point:
    """2D point."""
    x: float
    y: float

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        return Point(self.x - other.x, self.y - other.y)

    def rotate(self, angle_rad: float, origin: "Point | None" = None) -> "Point":
        """Rotate point around origin by angle in radians."""
        if origin is None:
            origin = Point(0, 0)
        dx = self.x - origin.x
        dy = self.y - origin.y
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        return Point(
            origin.x + dx * cos_a - dy * sin_a,
            origin.y + dx * sin_a + dy * cos_a,
        )


@dataclass
class Template:
    """Base template with geometry data."""
    gauge: float
    points: list[Point]  # Closed polygon outline
    template_type: Literal["straight", "curve", "transition"]

    def bounding_box(self) -> tuple[Point, Point]:
        """Return min and max corners of bounding box."""
        xs = [p.x for p in self.points]
        ys = [p.y for p in self.points]
        return Point(min(xs), min(ys)), Point(max(xs), max(ys))

    def dimensions(self) -> tuple[float, float]:
        """Return width and height of template."""
        min_pt, max_pt = self.bounding_box()
        return max_pt.x - min_pt.x, max_pt.y - min_pt.y


def create_straight_template(gauge: float, length: float) -> Template:
    """Create a straight track template (rectangle).

    Args:
        gauge: Track gauge in mm (width between rails)
        length: Length of template in mm

    Returns:
        Template with rectangular outline
    """
    # Rectangle with inner rail at y=0, outer rail at y=gauge
    points = [
        Point(0, 0),
        Point(length, 0),
        Point(length, gauge),
        Point(0, gauge),
        Point(0, 0),  # Close the polygon
    ]
    return Template(gauge=gauge, points=points, template_type="straight")


def create_curve_template(
    gauge: float,
    radius: float,
    arc_degrees: float | None = None,
    length: float | None = None,
    direction: Literal["left", "right"] = "right",
    num_segments: int = 64,
) -> Template:
    """Create a curved track template.

    Args:
        gauge: Track gauge in mm
        radius: Radius to inner rail in mm
        arc_degrees: Arc angle in degrees (alternative to length)
        length: Arc length along inner rail in mm (alternative to arc_degrees)
        direction: Curve direction ('left' or 'right')
        num_segments: Number of segments for arc approximation

    Returns:
        Template with curved outline
    """
    # Calculate arc angle from length if not given
    if arc_degrees is not None:
        angle_rad = math.radians(arc_degrees)
    elif length is not None:
        # Arc length = radius * angle
        angle_rad = length / radius
    else:
        raise ValueError("Must specify either arc_degrees or length")

    # Inner arc points
    inner_points = []
    outer_points = []

    for i in range(num_segments + 1):
        t = i / num_segments
        theta = t * angle_rad

        # Inner rail arc
        if direction == "right":
            # Center is at (0, radius), curving clockwise
            inner_x = radius * math.sin(theta)
            inner_y = radius - radius * math.cos(theta)
            outer_x = (radius + gauge) * math.sin(theta)
            outer_y = radius - (radius + gauge) * math.cos(theta)
        else:
            # Center is at (0, -radius), curving counter-clockwise
            inner_x = radius * math.sin(theta)
            inner_y = -radius + radius * math.cos(theta)
            outer_x = (radius + gauge) * math.sin(theta)
            outer_y = -radius + (radius + gauge) * math.cos(theta)

        inner_points.append(Point(inner_x, inner_y))
        outer_points.append(Point(outer_x, outer_y))

    # Build closed polygon: inner arc -> end cap -> outer arc reversed -> start cap
    points = inner_points.copy()
    points.append(outer_points[-1])  # End cap (implicit line)
    points.extend(reversed(outer_points[:-1]))
    points.append(inner_points[0])  # Close polygon

    return Template(gauge=gauge, points=points, template_type="curve")


def create_transition_template(
    gauge: float,
    end_radius: float,
    length: float,
    direction: Literal["left", "right"] = "right",
    num_segments: int = 64,
) -> Template:
    """Create a transition curve template (clothoid/Euler spiral).

    Transitions from straight (infinite radius) to the specified end radius
    over the given length.

    Args:
        gauge: Track gauge in mm
        end_radius: Final curve radius to inner rail in mm
        length: Total length of transition in mm
        direction: Curve direction ('left' or 'right')
        num_segments: Number of segments for curve approximation

    Returns:
        Template with transition curve outline
    """
    # Clothoid parameter: A² = R * L where R is end radius, L is length
    # At distance s along the curve: radius(s) = A² / s
    # Curvature κ(s) = s / A²

    A_squared = end_radius * length

    inner_points = []
    outer_points = []

    # Integrate clothoid numerically
    x, y = 0.0, 0.0
    theta = 0.0

    for i in range(num_segments + 1):
        s = (i / num_segments) * length

        inner_points.append(Point(x, y if direction == "right" else -y))

        # Calculate offset point for outer rail
        # Normal vector at current point
        if direction == "right":
            nx, ny = -math.sin(theta), math.cos(theta)
        else:
            nx, ny = math.sin(theta), -math.cos(theta)

        outer_points.append(Point(x + gauge * nx, (y if direction == "right" else -y) + gauge * ny))

        if i < num_segments:
            # Step forward
            ds = length / num_segments
            # Curvature at this point
            if s > 0:
                kappa = s / A_squared
            else:
                kappa = 0

            # Update position and angle
            x += ds * math.cos(theta)
            y += ds * math.sin(theta)
            theta += kappa * ds

    # Build closed polygon
    points = inner_points.copy()
    points.append(outer_points[-1])
    points.extend(reversed(outer_points[:-1]))
    points.append(inner_points[0])

    return Template(gauge=gauge, points=points, template_type="transition")
