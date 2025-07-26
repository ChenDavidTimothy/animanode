from math import cos, radians, sin

import numpy as np

from .base import WGPUGeometry


class WGPUCircleGeometry(WGPUGeometry):
    """WebGPU Circle Geometry - inspired by three.js CircleGeometry"""

    def __init__(self, radius: float = 1.0, segments: int = 32):
        """
        Create a circle geometry

        Args:
            radius: Radius of the circle
            segments: Number of triangular segments around the circle
        """
        super().__init__()
        self.radius = radius
        self.segments = segments

    def generate_vertices(self) -> np.ndarray:
        """Generate circle vertices - Evidence from three/geometry/CircleGeometry.py"""
        vertices = []

        # Evidence from three/geometry/CircleGeometry.py shows fan-based circle construction
        angle = radians(360) / self.segments
        pos_center = [0.0, 0.0, 0.0]
        uv_center = [0.5, 0.5]

        for i in range(self.segments):
            # Calculate positions for current and next point on circumference
            pos_a = [self.radius * cos(i * angle), self.radius * sin(i * angle), 0.0]
            pos_b = [self.radius * cos((i + 1) * angle), self.radius * sin((i + 1) * angle), 0.0]

            # Calculate UV coordinates
            # Evidence: three.js maps UV radially from center
            uv_a = [cos(i * angle) * 0.5 + 0.5, sin(i * angle) * 0.5 + 0.5]
            uv_b = [cos((i + 1) * angle) * 0.5 + 0.5, sin((i + 1) * angle) * 0.5 + 0.5]

            # Create triangle from center to edge
            # Evidence from three/geometry/CircleGeometry.py:
            # vertexPositionData.extend( [posCenter, posA, posB] )
            vertices.extend(
                [
                    [pos_center[0], pos_center[1], pos_center[2], 1.0, uv_center[0], uv_center[1]],
                    [pos_a[0], pos_a[1], pos_a[2], 1.0, uv_a[0], uv_a[1]],
                    [pos_b[0], pos_b[1], pos_b[2], 1.0, uv_b[0], uv_b[1]],
                ]
            )

        return np.array(vertices, dtype=np.float32)

    def generate_indices(self) -> np.ndarray:
        """Generate sequential indices since vertices are already in triangle order"""
        vertex_count = self.segments * 3  # 3 vertices per triangle
        return np.arange(vertex_count, dtype=np.uint32)
