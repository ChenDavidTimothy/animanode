from .sphere import WGPUSphereGeometry


class WGPUOctahedronGeometry(WGPUSphereGeometry):
    """WebGPU Octahedron Geometry - inspired by three.js OctahedronGeometry"""

    def __init__(self, radius: float = 1.0):
        """
        Create an octahedron geometry

        Args:
            radius: Radius of the octahedron
        """
        # Evidence from three/geometry/OctahedronGeometry.py:
        # super().__init__(radius=radius, xResolution=4, yResolution=2)

        # An octahedron is essentially a low-resolution sphere
        super().__init__(
            radius=radius,
            width_segments=4,  # 4 horizontal segments
            height_segments=2,  # 2 vertical segments
        )
