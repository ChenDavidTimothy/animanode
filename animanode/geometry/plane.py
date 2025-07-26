from .base import SurfaceGeometry


class WGPUPlaneGeometry(SurfaceGeometry):
    """WebGPU Plane Geometry - inspired by three.js PlaneGeometry/QuadGeometry"""

    def __init__(
        self,
        width: float = 2.0,
        height: float = 2.0,
        width_segments: int = 1,
        height_segments: int = 1,
    ):
        """
        Create a plane geometry

        Args:
            width: Width of the plane (X dimension)
            height: Height of the plane (Y dimension)
            width_segments: Number of segments along width
            height_segments: Number of segments along height
        """
        # Evidence from three/geometry/QuadGeometry.py:
        # super().__init__(-width/2, width/2, widthResolution,
        #                  -height/2, height/2, heightResolution,
        #                  lambda u,v : [u, v, 0])

        def plane_function(u, v):
            return [u, v, 0.0]  # Simple XY plane at Z=0

        super().__init__(
            u_start=-width / 2,
            u_end=width / 2,
            u_resolution=width_segments,
            v_start=-height / 2,
            v_end=height / 2,
            v_resolution=height_segments,
            surface_function=plane_function,
        )
