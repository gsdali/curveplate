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


def _integrate_clothoid(A_squared: float, length: float, num_segments: int) -> tuple[list[Point], list[float]]:
    """Integrate a clothoid curve numerically.

    Args:
        A_squared: Clothoid parameter squared (A² = R * L)
        length: Total arc length
        num_segments: Number of segments

    Returns:
        Tuple of (points, tangent_angles) along the curve
    """
    points = []
    angles = []

    x, y = 0.0, 0.0
    theta = 0.0

    for i in range(num_segments + 1):
        s = (i / num_segments) * length
        points.append(Point(x, y))
        angles.append(theta)

        if i < num_segments:
            ds = length / num_segments
            # Curvature κ(s) = s / A² for a clothoid
            kappa = s / A_squared if s > 0 else 0

            # Update position and angle
            x += ds * math.cos(theta)
            y += ds * math.sin(theta)
            theta += kappa * ds

    return points, angles


def create_transition_template(
    gauge: float,
    end_radius: float,
    length: float,
    direction: Literal["left", "right"] = "right",
    num_segments: int = 64,
) -> Template:
    """Create a transition curve template (clothoid/Euler spiral).

    Transitions from straight (infinite radius) to the specified end radius
    over the given length. The inner rail is the reference clothoid, and the
    outer rail is offset perpendicular to maintain constant gauge. End caps
    are perpendicular to the inner rail tangent.

    Args:
        gauge: Track gauge in mm
        end_radius: Final curve radius to inner rail in mm
        length: Total length of transition in mm
        direction: Curve direction ('left' or 'right')
        num_segments: Number of segments for curve approximation

    Returns:
        Template with transition curve outline
    """
    # Clothoid parameter: A² = R * L
    A_squared = end_radius * length

    # Generate inner rail clothoid
    inner_points_raw, tangent_angles = _integrate_clothoid(A_squared, length, num_segments)

    # Apply direction and calculate outer rail as perpendicular offset
    inner_points = []
    outer_points = []

    for i, (p, theta) in enumerate(zip(inner_points_raw, tangent_angles)):
        if direction == "right":
            # Inner rail
            inner_points.append(Point(p.x, p.y))
            # Outer rail: offset perpendicular (normal points left of tangent)
            nx, ny = -math.sin(theta), math.cos(theta)
            outer_points.append(Point(p.x + gauge * nx, p.y + gauge * ny))
        else:
            # Mirror for left direction
            inner_points.append(Point(p.x, -p.y))
            # Outer rail: offset perpendicular (normal points right of tangent)
            nx, ny = math.sin(theta), math.cos(theta)
            outer_points.append(Point(p.x + gauge * nx, -p.y + gauge * ny))

    # Build closed polygon with perpendicular end caps
    points = []

    # Inner rail from start to end
    points.extend(inner_points)

    # End cap: from inner end to outer end (perpendicular to tangent)
    points.append(outer_points[-1])

    # Outer rail from end to start (reversed)
    points.extend(reversed(outer_points[:-1]))

    # Start cap: close back to inner start (perpendicular to start tangent)
    points.append(inner_points[0])

    return Template(gauge=gauge, points=points, template_type="transition")
