import numpy as np

from .base import WGPUGeometry


class WGPUBoxGeometry(WGPUGeometry):
    """WebGPU Box Geometry - inspired by three.js BoxGeometry"""

    def __init__(self, width: float = 2.0, height: float = 2.0, depth: float = 2.0):
        """
        Create a box geometry

        Args:
            width: Width of the box (X dimension)
            height: Height of the box (Y dimension)
            depth: Depth of the box (Z dimension)
        """
        super().__init__()
        self.width = width
        self.height = height
        self.depth = depth

    def generate_vertices(self) -> np.ndarray:
        """Generate box vertices - Evidence from cube.py vertex format [x, y, z, w, u, v]"""
        w, h, d = self.width / 2, self.height / 2, self.depth / 2

        # Evidence from examples/cube.py vertex data structure
        vertices = [
            # Front face (z = +d)
            [-w, -h, d, 1.0, 0.0, 0.0],  # bottom-left
            [w, -h, d, 1.0, 1.0, 0.0],  # bottom-right
            [w, h, d, 1.0, 1.0, 1.0],  # top-right
            [-w, h, d, 1.0, 0.0, 1.0],  # top-left
            # Back face (z = -d)
            [-w, h, -d, 1.0, 1.0, 0.0],  # top-left
            [w, h, -d, 1.0, 0.0, 0.0],  # top-right
            [w, -h, -d, 1.0, 0.0, 1.0],  # bottom-right
            [-w, -h, -d, 1.0, 1.0, 1.0],  # bottom-left
            # Right face (x = +w)
            [w, -h, -d, 1.0, 0.0, 0.0],  # bottom-left
            [w, h, -d, 1.0, 1.0, 0.0],  # top-left
            [w, h, d, 1.0, 1.0, 1.0],  # top-right
            [w, -h, d, 1.0, 0.0, 1.0],  # bottom-right
            # Left face (x = -w)
            [-w, -h, d, 1.0, 1.0, 0.0],  # bottom-left
            [-w, h, d, 1.0, 0.0, 0.0],  # top-left
            [-w, h, -d, 1.0, 0.0, 1.0],  # top-right
            [-w, -h, -d, 1.0, 1.0, 1.0],  # bottom-right
            # Top face (y = +h)
            [w, h, -d, 1.0, 1.0, 0.0],  # top-right
            [-w, h, -d, 1.0, 0.0, 0.0],  # top-left
            [-w, h, d, 1.0, 0.0, 1.0],  # bottom-left
            [w, h, d, 1.0, 1.0, 1.0],  # bottom-right
            # Bottom face (y = -h)
            [w, -h, d, 1.0, 0.0, 0.0],  # bottom-right
            [-w, -h, d, 1.0, 1.0, 0.0],  # bottom-left
            [-w, -h, -d, 1.0, 1.0, 1.0],  # top-left
            [w, -h, -d, 1.0, 0.0, 1.0],  # top-right
        ]

        return np.array(vertices, dtype=np.float32)

    def generate_indices(self) -> np.ndarray:
        """Generate box indices - Evidence from cube.py index pattern"""
        # Evidence from examples/cube.py index data structure
        indices = [
            [0, 1, 2, 2, 3, 0],  # front
            [4, 5, 6, 6, 7, 4],  # back
            [8, 9, 10, 10, 11, 8],  # right
            [12, 13, 14, 14, 15, 12],  # left
            [16, 17, 18, 18, 19, 16],  # top
            [20, 21, 22, 22, 23, 20],  # bottom
        ]

        return np.array(indices, dtype=np.uint32).flatten()
