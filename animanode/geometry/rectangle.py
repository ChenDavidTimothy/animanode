import numpy as np

from ..core.node import GeometryNode


class RectangleNode(GeometryNode):
    """Rectangle geometry node for 2D rendering"""

    def __init__(self, width: float = 1.0, height: float = 1.0, name: str = "Rectangle"):
        super().__init__(name)
        self.width = width
        self.height = height
        self._vertices = None
        self._indices = None
        self._generate_geometry()

    def set_size(self, width: float, height: float) -> "RectangleNode":
        """Set rectangle size and return self for chaining"""
        self.width = width
        self.height = height
        self._generate_geometry()
        self.mark_dirty()
        return self

    def _generate_geometry(self):
        """Generate rectangle vertex data centered at origin"""
        half_width = self.width * 0.5
        half_height = self.height * 0.5

        # Vertex format: [x, y, u, v] (position + UV coordinates)
        self._vertices = np.array(
            [
                [-half_width, half_height, 0.0, 0.0],  # top left
                [half_width, half_height, 1.0, 0.0],  # top right
                [half_width, -half_height, 1.0, 1.0],  # bottom right
                [-half_width, -half_height, 0.0, 1.0],  # bottom left
            ],
            dtype=np.float32,
        )

        # Index data for two triangles (counter-clockwise winding)
        self._indices = np.array(
            [
                0,
                1,
                2,  # first triangle
                0,
                2,
                3,  # second triangle
            ],
            dtype=np.uint32,
        )

    def get_vertices(self) -> np.ndarray:
        """Return vertex data as numpy array"""
        return self._vertices

    def get_indices(self) -> np.ndarray:
        """Return index data as numpy array"""
        return self._indices

    def compute(self) -> "RectangleNode":
        """Return self as the computed result"""
        return self
