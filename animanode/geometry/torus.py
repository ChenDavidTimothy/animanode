from math import cos, pi, sin

import numpy as np

from .base import WGPUGeometry


class WGPUTorusGeometry(WGPUGeometry):
    """WebGPU Torus Geometry - inspired by three.js TorusGeometry with FIXED depth testing"""

    def __init__(
        self,
        central_radius: float = 0.6,
        tube_radius: float = 0.4,
        tubular_segments: int = 32,
        radial_segments: int = 10,
        scale: float = 1.0,
    ):
        """
        Create a torus geometry with correct winding order for depth testing

        Args:
            central_radius: Distance from center to center of tube
            tube_radius: Radius of the tube
            tubular_segments: Number of segments around the torus
            radial_segments: Number of segments around the tube
            scale: Overall scale factor
        """
        super().__init__()
        self.central_radius = central_radius
        self.tube_radius = tube_radius
        self.tubular_segments = tubular_segments
        self.radial_segments = radial_segments
        self.scale = scale

    def generate_vertices(self) -> np.ndarray:
        """Generate torus vertices with CORRECT winding order for depth testing"""
        vertices = []

        # Generate grid of positions using torus parametric equations
        # Evidence from three/geometry/TorusGeometry.py mathematical formulation
        positions = []
        uvs = []

        for u_index in range(self.tubular_segments + 1):
            row_positions = []
            row_uvs = []

            for v_index in range(self.radial_segments + 1):
                # Parametric coordinates
                u = (u_index / self.tubular_segments) * 2 * pi  # Around the torus
                v = (v_index / self.radial_segments) * 2 * pi  # Around the tube

                # Torus parametric equations - Evidence from three/geometry/TorusGeometry.py:
                # lambda u,v: [((centralRadius + tubeRadius*cos(v))*cos(u)*scale),
                #              ((centralRadius + tubeRadius*cos(v))*sin(u)*scale),
                #              (tubeRadius*sin(v)*scale)]
                x = (self.central_radius + self.tube_radius * cos(v)) * cos(u) * self.scale
                y = (self.central_radius + self.tube_radius * cos(v)) * sin(u) * self.scale
                z = self.tube_radius * sin(v) * self.scale

                row_positions.append([x, y, z])

                # UV coordinates - map parametric space to texture space
                uv_u = u_index / self.tubular_segments
                uv_v = v_index / self.radial_segments
                row_uvs.append([uv_u, uv_v])

            positions.append(row_positions)
            uvs.append(row_uvs)

        # Generate triangles with CORRECT counter-clockwise winding order
        # This is critical for proper depth testing and back-face culling
        for u_index in range(self.tubular_segments):
            for v_index in range(self.radial_segments):
                # Get quad corners in grid
                p00 = positions[u_index][v_index]  # Current u, current v
                p10 = positions[u_index + 1][v_index]  # Next u, current v
                p01 = positions[u_index][v_index + 1]  # Current u, next v
                p11 = positions[u_index + 1][v_index + 1]  # Next u, next v

                # Corresponding UV coordinates
                uv00 = uvs[u_index][v_index]
                uv10 = uvs[u_index + 1][v_index]
                uv01 = uvs[u_index][v_index + 1]
                uv11 = uvs[u_index + 1][v_index + 1]

                # CRITICAL FIX: Correct winding order for torus topology
                # When viewed from outside the torus, triangles must be counter-clockwise
                # This ensures proper depth testing and prevents "inside-out" faces

                # First triangle: p00 -> p01 -> p11 (counter-clockwise from outside)
                vertices.extend(
                    [
                        [p00[0], p00[1], p00[2], 1.0, uv00[0], uv00[1]],
                        [p01[0], p01[1], p01[2], 1.0, uv01[0], uv01[1]],
                        [p11[0], p11[1], p11[2], 1.0, uv11[0], uv11[1]],
                    ]
                )

                # Second triangle: p00 -> p11 -> p10 (counter-clockwise from outside)
                vertices.extend(
                    [
                        [p00[0], p00[1], p00[2], 1.0, uv00[0], uv00[1]],
                        [p11[0], p11[1], p11[2], 1.0, uv11[0], uv11[1]],
                        [p10[0], p10[1], p10[2], 1.0, uv10[0], uv10[1]],
                    ]
                )

        return np.array(vertices, dtype=np.float32)

    def generate_indices(self) -> np.ndarray:
        """Generate sequential indices since vertices are already in triangle order"""
        # Each quad generates 2 triangles = 6 vertices
        vertex_count = self.tubular_segments * self.radial_segments * 6
        return np.arange(vertex_count, dtype=np.uint32)
