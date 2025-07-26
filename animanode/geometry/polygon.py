from .circle import WGPUCircleGeometry


class WGPUPolygonGeometry(WGPUCircleGeometry):
    """WebGPU Polygon Geometry - inspired by three.js PolygonGeometry"""

    def __init__(self, radius: float = 1.0, number_sides: int = 6):
        """
        Create a polygon geometry

        Args:
            radius: Distance from center to vertices
            number_sides: Number of sides (3=triangle, 4=square, 5=pentagon, etc.)
        """
        # Evidence from three/geometry/PolygonGeometry.py:
        # super().__init__(radius=radius, segments=numberSides)

        # A polygon is essentially a circle with a specific number of segments
        super().__init__(radius=radius, segments=number_sides)
