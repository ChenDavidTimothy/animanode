from math import cos, pi, sin

from .base import SurfaceGeometry


class WGPUSphereGeometry(SurfaceGeometry):
    """WebGPU Sphere Geometry - inspired by three.js SphereGeometry"""

    def __init__(self, radius: float = 1.0, width_segments: int = 32, height_segments: int = 16):
        """
        Create a sphere geometry

        Args:
            radius: Sphere radius
            width_segments: Number of horizontal segments (longitude)
            height_segments: Number of vertical segments (latitude)
        """
        # Evidence from three/geometry/SphereGeometry.py:
        # super().__init__(0, 2*pi, xResolution, -pi/2, pi/2, yResolution,
        #                 lambda u,v : [radius*sin(u)*cos(v), radius*sin(v), radius*cos(u)*cos(v)])

        def sphere_function(u, v):
            return [
                radius * sin(u) * cos(v),  # x
                radius * sin(v),  # y
                radius * cos(u) * cos(v),  # z
            ]

        super().__init__(
            u_start=0,
            u_end=2 * pi,
            u_resolution=width_segments,
            v_start=-pi / 2,
            v_end=pi / 2,
            v_resolution=height_segments,
            surface_function=sphere_function,
        )
