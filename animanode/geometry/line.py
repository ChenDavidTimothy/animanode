import numpy as np

from .base import WGPUGeometry


class WGPULineGeometry(WGPUGeometry):
    """WebGPU Line Geometry - inspired by three.js LineGeometry"""

    def __init__(self, positions: list):
        """
        Create a line geometry from a list of positions

        Args:
            positions: List of [x, y, z] position vectors defining the line
        """
        super().__init__()
        # Evidence from three/geometry/LineGeometry.py: stores vertex positions
        self.positions = positions
        # Evidence: three.js version calculates arc lengths, but for WebGPU we focus on positions

    def generate_vertices(self) -> np.ndarray:
        """Generate line vertices in WebGPU format [x, y, z, w, u, v]"""
        vertices = []

        # Evidence from three/geometry/LineGeometry.py:
        # self.setAttribute("vec3", "vertexPosition", vertexPositionData)

        # Calculate arc length for UV mapping along the line
        total_length = 0.0
        segment_lengths = [0.0]

        for i in range(1, len(self.positions)):
            segment_length = np.linalg.norm(
                np.array(self.positions[i]) - np.array(self.positions[i - 1])
            )
            total_length += segment_length
            segment_lengths.append(total_length)

        # Convert positions to vertices with UV coordinates based on arc length
        for i, pos in enumerate(self.positions):
            # U coordinate represents progress along the line (0.0 to 1.0)
            u = segment_lengths[i] / total_length if total_length > 0 else 0.0
            # V coordinate is 0.0 for lines
            vertices.append([pos[0], pos[1], pos[2], 1.0, u, 0.0])

        return np.array(vertices, dtype=np.float32)

    def generate_indices(self) -> np.ndarray:
        """Generate sequential indices for line segments"""
        # Lines are rendered as connected line segments
        return np.arange(len(self.positions), dtype=np.uint32)
