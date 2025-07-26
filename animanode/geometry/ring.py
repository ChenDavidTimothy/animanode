from math import cos, radians, sin

import numpy as np

from .base import WGPUGeometry


class WGPURingGeometry(WGPUGeometry):
    """WebGPU Ring Geometry - inspired by three.js RingGeometry"""

    def __init__(
        self,
        inner_radius: float = 0.25,
        outer_radius: float = 1.0,
        segments: int = 32,
    ):
        """
        Create a ring geometry

        Args:
            inner_radius: Inner radius of the ring
            outer_radius: Outer radius of the ring
            segments: Number of segments around the ring
        """
        super().__init__()
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.segments = segments

    def generate_vertices(self) -> np.ndarray:
        """Generate ring vertices - Evidence from three/geometry/RingGeometry.py"""
        vertices = []

        # Evidence from three/geometry/RingGeometry.py shows quad-based ring construction
        angle = radians(360) / self.segments

        for i in range(self.segments):
            # Calculate angles for current and next segment
            angle_a = i * angle
            angle_b = (i + 1) * angle

            # Calculate positions for the four corners of each quad
            pos_a_inner = [self.inner_radius * cos(angle_a), self.inner_radius * sin(angle_a), 0.0]
            pos_b_inner = [self.inner_radius * cos(angle_b), self.inner_radius * sin(angle_b), 0.0]
            pos_a_outer = [self.outer_radius * cos(angle_a), self.outer_radius * sin(angle_a), 0.0]
            pos_b_outer = [self.outer_radius * cos(angle_b), self.outer_radius * sin(angle_b), 0.0]

            # Calculate UV coordinates
            # Evidence: three.js maps UV radially from center
            uv_a_inner = [cos(angle_a) * 0.5 + 0.5, sin(angle_a) * 0.5 + 0.5]
            uv_b_inner = [cos(angle_b) * 0.5 + 0.5, sin(angle_b) * 0.5 + 0.5]
            uv_a_outer = [cos(angle_a) * 0.5 + 0.5, sin(angle_a) * 0.5 + 0.5]
            uv_b_outer = [cos(angle_b) * 0.5 + 0.5, sin(angle_b) * 0.5 + 0.5]

            # Create two triangles per segment
            # Evidence from three/geometry/RingGeometry.py:
            # vertexPositionData.extend( [posA,posB,posC, posA,posC,posD] )

            # First triangle: inner_a, outer_a, outer_b
            vertices.extend(
                [
                    [
                        pos_a_inner[0],
                        pos_a_inner[1],
                        pos_a_inner[2],
                        1.0,
                        uv_a_inner[0],
                        uv_a_inner[1],
                    ],
                    [
                        pos_a_outer[0],
                        pos_a_outer[1],
                        pos_a_outer[2],
                        1.0,
                        uv_a_outer[0],
                        uv_a_outer[1],
                    ],
                    [
                        pos_b_outer[0],
                        pos_b_outer[1],
                        pos_b_outer[2],
                        1.0,
                        uv_b_outer[0],
                        uv_b_outer[1],
                    ],
                ]
            )

            # Second triangle: inner_a, outer_b, inner_b
            vertices.extend(
                [
                    [
                        pos_a_inner[0],
                        pos_a_inner[1],
                        pos_a_inner[2],
                        1.0,
                        uv_a_inner[0],
                        uv_a_inner[1],
                    ],
                    [
                        pos_b_outer[0],
                        pos_b_outer[1],
                        pos_b_outer[2],
                        1.0,
                        uv_b_outer[0],
                        uv_b_outer[1],
                    ],
                    [
                        pos_b_inner[0],
                        pos_b_inner[1],
                        pos_b_inner[2],
                        1.0,
                        uv_b_inner[0],
                        uv_b_inner[1],
                    ],
                ]
            )

        return np.array(vertices, dtype=np.float32)

    def generate_indices(self) -> np.ndarray:
        """Generate sequential indices since vertices are already in triangle order"""
        vertex_count = self.segments * 6  # 6 vertices per segment (2 triangles)
        return np.arange(vertex_count, dtype=np.uint32)
