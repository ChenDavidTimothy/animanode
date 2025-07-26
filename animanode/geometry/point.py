import numpy as np

from .base import WGPUGeometry


class WGPUPointGeometry(WGPUGeometry):
    """WebGPU Point Geometry - inspired by three.js PointGeometry"""

    def __init__(self, positions: list):
        """
        Create a point geometry from a list of positions

        Args:
            positions: List of [x, y, z] position vectors
        """
        super().__init__()
        # Evidence from three/geometry/PointGeometry.py: stores vertex positions
        self.positions = positions

    def generate_vertices(self) -> np.ndarray:
        """Generate point vertices in WebGPU format [x, y, z, w, u, v]"""
        vertices = []

        # Evidence from three/geometry/PointGeometry.py:
        # self.setAttribute("vec3", "vertexPosition", vertexPositionData)
        for pos in self.positions:
            # Convert [x, y, z] to [x, y, z, w, u, v] format
            # For points, UV coordinates can be (0, 0) since they're not textured
            vertices.append([pos[0], pos[1], pos[2], 1.0, 0.0, 0.0])

        return np.array(vertices, dtype=np.float32)

    def generate_indices(self) -> np.ndarray:
        """Generate sequential indices for points"""
        # Points are rendered as individual vertices, so indices are sequential
        return np.arange(len(self.positions), dtype=np.uint32)
