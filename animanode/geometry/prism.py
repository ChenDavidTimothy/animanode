from .cylinder import WGPUCylinderGeometry


class WGPUPrismGeometry(WGPUCylinderGeometry):
    """WebGPU Prism Geometry - inspired by three.js PrismGeometry"""

    def __init__(
        self,
        radius: float = 1.0,
        number_sides: int = 4,
        height: float = 2.0,
        height_segments: int = 1,
        closed: bool = True,
    ):
        """
        Create a prism geometry

        Args:
            radius: Radius of the prism (distance from center to vertex)
            number_sides: Number of sides (4 for square prism, 6 for hexagonal, etc.)
            height: Height of prism
            height_segments: Number of segments along height
            closed: Whether to include top and bottom caps
        """
        # Evidence from three/geometry/PrismGeometry.py:
        # super().__init__(radiusTop=radius, radiusBottom=radius, radialSegments=numberSides,
        #                  height=height, heightSegments=heightSegments,
        #                  circleTop=True, circleBottom=True)

        super().__init__(
            radius_top=radius,
            radius_bottom=radius,
            height=height,
            radial_segments=number_sides,
            height_segments=height_segments,
            circle_top=closed,
            circle_bottom=closed,
        )
