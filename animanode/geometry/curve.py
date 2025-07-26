from collections.abc import Callable

from .line import WGPULineGeometry


class WGPUCurveGeometry(WGPULineGeometry):
    """WebGPU Curve Geometry - inspired by three.js CurveGeometry"""

    def __init__(
        self,
        curve_function: Callable[[float], list] | list | None = None,
        t_min: float = 0.0,
        t_max: float = 1.0,
        divisions: int = 50,
        positions: list | None = None,
    ):
        """
        Create a curve geometry

        Args:
            curve_function: Function that takes parameter t and returns [x, y, z] or list of positions
            t_min: Minimum parameter value
            t_max: Maximum parameter value
            divisions: Number of divisions along the curve
            positions: Alternative to curve_function - direct list of positions
        """
        # Evidence from three/geometry/CurveGeometry.py:
        # super().__init__( curve.getPoints() )

        if positions is not None:
            # Direct positions provided
            curve_positions = positions
        elif callable(curve_function):
            # Generate positions from parametric function
            curve_positions = []
            for i in range(divisions + 1):
                t = t_min + (t_max - t_min) * i / divisions
                point = curve_function(t)
                curve_positions.append(point)
        elif isinstance(curve_function, list):
            # curve_function is actually a list of positions
            curve_positions = curve_function
        else:
            raise ValueError(
                "Either curve_function (callable or list) or positions must be provided"
            )

        # Initialize as LineGeometry with the curve points
        super().__init__(curve_positions)

    @classmethod
    def create_circle_curve(
        cls,
        radius: float = 1.0,
        divisions: int = 64,
    ) -> "WGPUCurveGeometry":
        """Create a circular curve"""
        import math

        def circle_function(t):
            angle = t * 2 * math.pi
            return [radius * math.cos(angle), radius * math.sin(angle), 0.0]

        return cls(circle_function, 0.0, 1.0, divisions)

    @classmethod
    def create_helix_curve(
        cls,
        radius: float = 1.0,
        height: float = 2.0,
        revolutions: int = 3,
        divisions: int = 128,
    ) -> "WGPUCurveGeometry":
        """Create a helical curve"""
        import math

        def helix_function(t):
            angle = t * 2 * math.pi * revolutions
            return [
                radius * math.cos(angle),
                height * t - height / 2,  # Center around y=0
                radius * math.sin(angle),
            ]

        return cls(helix_function, 0.0, 1.0, divisions)

    @classmethod
    def create_bezier_curve(
        cls,
        control_points: list,
        divisions: int = 100,
    ) -> "WGPUCurveGeometry":
        """Create a cubic Bezier curve from 4 control points"""
        if len(control_points) != 4:
            raise ValueError("Bezier curve requires exactly 4 control points")

        def bezier_function(t):
            # Cubic Bezier formula
            p0, p1, p2, p3 = control_points
            inv_t = 1 - t
            return [
                inv_t**3 * p0[0]
                + 3 * inv_t**2 * t * p1[0]
                + 3 * inv_t * t**2 * p2[0]
                + t**3 * p3[0],
                inv_t**3 * p0[1]
                + 3 * inv_t**2 * t * p1[1]
                + 3 * inv_t * t**2 * p2[1]
                + t**3 * p3[1],
                inv_t**3 * p0[2]
                + 3 * inv_t**2 * t * p1[2]
                + 3 * inv_t * t**2 * p2[2]
                + t**3 * p3[2],
            ]

        return cls(bezier_function, 0.0, 1.0, divisions)
