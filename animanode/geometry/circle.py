import math

import numpy as np

from ..core.node import GeometryNode


class CircleNode(GeometryNode):
    """Circle geometry node for 2D rendering"""

    def __init__(self, radius: float = 0.5, segments: int = 32, name: str = "Circle"):
        super().__init__(name)
        self.radius = radius
        self.segments = max(3, segments)  # Minimum 3 segments for a triangle
        self._vertices = None
        self._indices = None
        self._generate_geometry()

    def set_radius(self, radius: float) -> "CircleNode":
        """Set circle radius and return self for chaining"""
        self.radius = radius
        self._generate_geometry()
        self.mark_dirty()
        return self

    def set_segments(self, segments: int) -> "CircleNode":
        """Set number of segments and return self for chaining"""
        self.segments = max(3, segments)
        self._generate_geometry()
        self.mark_dirty()
        return self

    def _generate_geometry(self):
        """Generate circle vertex data centered at origin"""
        # Create center vertex + perimeter vertices
        vertices = []
        indices = []

        # Center vertex
        vertices.append([0.0, 0.0, 0.5, 0.5])  # [x, y, u, v]

        # Perimeter vertices
        for i in range(self.segments):
            angle = 2.0 * math.pi * i / self.segments
            x = self.radius * math.cos(angle)
            y = self.radius * math.sin(angle)

            # UV coordinates mapped to [0,1] range
            u = (x / self.radius + 1.0) * 0.5
            v = (y / self.radius + 1.0) * 0.5

            vertices.append([x, y, u, v])

        # Generate triangle indices (center + two adjacent perimeter vertices)
        for i in range(self.segments):
            next_i = (i + 1) % self.segments
            # Triangle: center, current perimeter vertex, next perimeter vertex
            indices.extend([0, i + 1, next_i + 1])

        self._vertices = np.array(vertices, dtype=np.float32)
        self._indices = np.array(indices, dtype=np.uint32)

    def get_vertices(self) -> np.ndarray:
        """Return vertex data as numpy array"""
        return self._vertices

    def get_indices(self) -> np.ndarray:
        """Return index data as numpy array"""
        return self._indices

    def compute(self) -> "CircleNode":
        """Return self as the computed result"""
        return self
