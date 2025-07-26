from .cylinder import WGPUConeGeometry


class WGPUPyramidGeometry(WGPUConeGeometry):
    """WebGPU Pyramid Geometry - inspired by three.js PyramidGeometry"""

    def __init__(
        self,
        radius: float = 1.0,
        number_sides: int = 4,
        height: float = 2.0,
        height_segments: int = 8,
        closed: bool = True,
    ):
        """
        Create a pyramid geometry

        Args:
            radius: Radius at base of pyramid
            number_sides: Number of sides (4 for square pyramid, 3 for triangular, etc.)
            height: Height of pyramid
            height_segments: Number of segments along height
            closed: Whether to include bottom cap
        """
        # Evidence from three/geometry/PyramidGeometry.py:
        # super().__init__(radius=radius, radialSegments=numberSides, height=height,
        #                  heightSegments=heightSegments, closed=closed)

        super().__init__(
            radius=radius,
            height=height,
            radial_segments=number_sides,
            height_segments=height_segments,
            closed=closed,
        )
