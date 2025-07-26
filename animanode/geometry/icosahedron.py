from math import atan2, pi, sqrt

import numpy as np

from .base import WGPUGeometry


class WGPUIcosahedronGeometry(WGPUGeometry):
    """WebGPU Icosahedron Geometry - inspired by three.js IcosahedronGeometry"""

    def __init__(self, radius: float = 1.0):
        """
        Create an icosahedron geometry

        Args:
            radius: Radius of the icosahedron
        """
        super().__init__()
        self.radius = radius

    def generate_vertices(self) -> np.ndarray:
        """Generate icosahedron vertices - Evidence from three/geometry/IcosahedronGeometry.py"""
        vertices = []

        # Evidence from three/geometry/IcosahedronGeometry.py:
        # Golden ratio calculation and vertex positions
        t = (1 + sqrt(5)) / 2

        # Predefined icosahedron vertices
        vertex_positions = [
            [-1, t, 0],
            [1, t, 0],
            [-1, -t, 0],
            [1, -t, 0],
            [0, -1, t],
            [0, 1, t],
            [0, -1, -t],
            [0, 1, -t],
            [t, 0, -1],
            [t, 0, 1],
            [-t, 0, -1],
            [-t, 0, 1],
        ]

        # Evidence: Triangle data defines the faces of the icosahedron
        triangle_indices = [
            [0, 11, 5],
            [0, 5, 1],
            [0, 1, 7],
            [0, 7, 10],
            [0, 10, 11],
            [1, 5, 9],
            [5, 11, 4],
            [11, 10, 2],
            [10, 7, 6],
            [7, 1, 8],
            [3, 9, 4],
            [3, 4, 2],
            [3, 2, 6],
            [3, 6, 8],
            [3, 8, 9],
            [4, 9, 5],
            [2, 4, 11],
            [6, 2, 10],
            [8, 6, 7],
            [9, 8, 1],
        ]

        # Generate vertices for each triangle
        for triangle in triangle_indices:
            for vertex_index in triangle:
                position = vertex_positions[vertex_index]

                # Normalize the position vector
                normal = np.array(position)
                normal = normal / np.linalg.norm(normal)
                x, y, z = normal

                # Calculate UV coordinates using spherical mapping
                # Evidence from three/geometry/IcosahedronGeometry.py:
                # u = atan2(x, z) / (2*pi) + 0.5
                # v = y * 0.5 + 0.5
                u = atan2(x, z) / (2 * pi) + 0.5
                v = y * 0.5 + 0.5

                # Scale to desired radius
                final_position = normal * self.radius

                # Add vertex in [x, y, z, w, u, v] format
                vertices.append(
                    [final_position[0], final_position[1], final_position[2], 1.0, u, v]
                )

        return np.array(vertices, dtype=np.float32)

    def generate_indices(self) -> np.ndarray:
        """Generate sequential indices since vertices are already in triangle order"""
        # 20 triangles * 3 vertices per triangle = 60 vertices
        vertex_count = 20 * 3
        return np.arange(vertex_count, dtype=np.uint32)
