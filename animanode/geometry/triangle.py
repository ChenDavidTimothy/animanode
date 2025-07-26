import numpy as np

from ..core.node import GeometryNode


class TriangleNode(GeometryNode):
    """Triangle geometry node for 2D rendering"""

    def __init__(self, width: float = 1.0, height: float = 1.0, name: str = "Triangle"):
        super().__init__(name)
        self.width = width
        self.height = height
        self._vertices = None
        self._indices = None
        self._generate_geometry()

    def set_size(self, width: float, height: float) -> "TriangleNode":
        """Set triangle size and return self for chaining"""
        self.width = width
        self.height = height
        self._generate_geometry()
        self.mark_dirty()
        return self

    def _generate_geometry(self):
        """Generate triangle vertex data centered at origin"""
        # Triangle vertices: top, bottom-left, bottom-right
        # Centered at origin with specified width/height
        half_width = self.width * 0.5
        half_height = self.height * 0.5

        # Vertex format: [x, y, u, v] (position + UV coordinates)
        self._vertices = np.array(
            [
                [0.0, half_height, 0.5, 0.0],  # top center
                [-half_width, -half_height, 0.0, 1.0],  # bottom left
                [half_width, -half_height, 1.0, 1.0],  # bottom right
            ],
            dtype=np.float32,
        )

        # Index data for triangle (counter-clockwise winding)
        self._indices = np.array([0, 1, 2], dtype=np.uint32)

    def get_vertices(self) -> np.ndarray:
        """Return vertex data as numpy array"""
        return self._vertices

    def get_indices(self) -> np.ndarray:
        """Return index data as numpy array"""
        return self._indices

    def compute(self) -> "TriangleNode":
        """Return self as the computed result"""
        return self
