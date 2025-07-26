from math import cos, pi, radians, sin

import numpy as np

from .base import WGPUGeometry


class WGPUCylinderGeometry(WGPUGeometry):
    """WebGPU Cylinder Geometry - inspired by three.js CylinderGeometry with caps"""

    def __init__(
        self,
        radius_top: float = 1.0,
        radius_bottom: float = 1.0,
        height: float = 2.0,
        radial_segments: int = 32,
        height_segments: int = 2,
        circle_top: bool = True,
        circle_bottom: bool = True,
    ):
        """
        Create a cylinder geometry with caps

        Args:
            radius_top: Radius at top of cylinder
            radius_bottom: Radius at bottom of cylinder
            height: Height of cylinder
            radial_segments: Number of segments around circumference
            height_segments: Number of segments along height
            circle_top: Whether to include top cap
            circle_bottom: Whether to include bottom cap
        """
        super().__init__()
        self.radius_top = radius_top
        self.radius_bottom = radius_bottom
        self.height = height
        self.radial_segments = radial_segments
        self.height_segments = height_segments
        self.circle_top = circle_top
        self.circle_bottom = circle_bottom

    def generate_vertices(self) -> np.ndarray:
        """Generate cylinder vertices with caps - Evidence from three/geometry/CylinderGeometry.py"""
        vertices = []

        # Generate cylindrical surface (mantle)
        delta_u = (2 * pi) / self.radial_segments
        delta_v = 1.0 / self.height_segments

        # Generate grid of positions for mantle
        positions = []
        uvs = []
        for u_index in range(self.radial_segments + 1):
            row_positions = []
            row_uvs = []
            for v_index in range(self.height_segments + 1):
                u = u_index * delta_u
                v = v_index * delta_v

                # Cylinder function from three.js
                radius = v * self.radius_top + (1 - v) * self.radius_bottom
                pos = [
                    radius * cos(-u),  # x
                    (v - 0.5) * self.height,  # y (centered at 0)
                    radius * sin(-u),  # z
                ]
                row_positions.append(pos)

                # UV coordinates for mantle
                uv = [u_index / self.radial_segments, v_index / self.height_segments]
                row_uvs.append(uv)

            positions.append(row_positions)
            uvs.append(row_uvs)

        # Convert mantle to triangles (vertex format: [x, y, z, w, u, v])
        for u_index in range(self.radial_segments):
            for v_index in range(self.height_segments):
                # Get quad corners
                p00 = positions[u_index][v_index]
                p10 = positions[u_index + 1][v_index]
                p01 = positions[u_index][v_index + 1]
                p11 = positions[u_index + 1][v_index + 1]

                uv00 = uvs[u_index][v_index]
                uv10 = uvs[u_index + 1][v_index]
                uv01 = uvs[u_index][v_index + 1]
                uv11 = uvs[u_index + 1][v_index + 1]

                # First triangle: p00, p10, p11
                vertices.extend(
                    [
                        [p00[0], p00[1], p00[2], 1.0, uv00[0], uv00[1]],
                        [p10[0], p10[1], p10[2], 1.0, uv10[0], uv10[1]],
                        [p11[0], p11[1], p11[2], 1.0, uv11[0], uv11[1]],
                    ]
                )

                # Second triangle: p00, p11, p01
                vertices.extend(
                    [
                        [p00[0], p00[1], p00[2], 1.0, uv00[0], uv00[1]],
                        [p11[0], p11[1], p11[2], 1.0, uv11[0], uv11[1]],
                        [p01[0], p01[1], p01[2], 1.0, uv01[0], uv01[1]],
                    ]
                )

        # Add top cap - TESTING: Try reversed winding to fix visibility
        if self.circle_top:
            angle = radians(360) / self.radial_segments
            pos_center = [0, self.height / 2, 0]
            uv_center = [0.5, 0.5]

            for i in range(self.radial_segments):
                pos_a = [
                    self.radius_top * cos(i * angle),
                    self.height / 2,
                    self.radius_top * sin(i * angle),
                ]
                pos_b = [
                    self.radius_top * cos((i + 1) * angle),
                    self.height / 2,
                    self.radius_top * sin((i + 1) * angle),
                ]

                # UV coordinates: radial from center
                uv_a = [cos(i * angle) * 0.5 + 0.5, sin(i * angle) * 0.5 + 0.5]
                uv_b = [cos((i + 1) * angle) * 0.5 + 0.5, sin((i + 1) * angle) * 0.5 + 0.5]

                # TESTING: Try [center, B, A] instead of [center, A, B] for upward normal
                vertices.extend(
                    [
                        [
                            pos_center[0],
                            pos_center[1],
                            pos_center[2],
                            1.0,
                            uv_center[0],
                            uv_center[1],
                        ],
                        [pos_b[0], pos_b[1], pos_b[2], 1.0, uv_b[0], uv_b[1]],
                        [pos_a[0], pos_a[1], pos_a[2], 1.0, uv_a[0], uv_a[1]],
                    ]
                )

        # Add bottom cap - FIXED: Reverse winding order for outward normal
        if self.circle_bottom:
            angle = radians(360) / self.radial_segments
            pos_center = [0, -self.height / 2, 0]
            uv_center = [0.5, 0.5]

            for i in range(self.radial_segments):
                pos_a = [
                    self.radius_bottom * cos(i * angle),
                    -self.height / 2,
                    self.radius_bottom * sin(i * angle),
                ]
                pos_b = [
                    self.radius_bottom * cos((i + 1) * angle),
                    -self.height / 2,
                    self.radius_bottom * sin((i + 1) * angle),
                ]

                # UV coordinates: radial from center
                uv_a = [cos(i * angle) * 0.5 + 0.5, sin(i * angle) * 0.5 + 0.5]
                uv_b = [cos((i + 1) * angle) * 0.5 + 0.5, sin((i + 1) * angle) * 0.5 + 0.5]

                # FIXED: Reverse winding [center, B, A] for downward normal
                vertices.extend(
                    [
                        [
                            pos_center[0],
                            pos_center[1],
                            pos_center[2],
                            1.0,
                            uv_center[0],
                            uv_center[1],
                        ],
                        [pos_b[0], pos_b[1], pos_b[2], 1.0, uv_b[0], uv_b[1]],
                        [pos_a[0], pos_a[1], pos_a[2], 1.0, uv_a[0], uv_a[1]],
                    ]
                )

        return np.array(vertices, dtype=np.float32)

    def generate_indices(self) -> np.ndarray:
        """Generate sequential indices since vertices are already in triangle order"""
        # FIXED: Use base class method instead of non-existent internal method
        vertex_count = len(self.get_vertex_data())
        return np.arange(vertex_count, dtype=np.uint32)


class WGPUConeGeometry(WGPUCylinderGeometry):
    """WebGPU Cone Geometry - inspired by three.js ConeGeometry"""

    def __init__(
        self,
        radius: float = 1.0,
        height: float = 2.0,
        radial_segments: int = 32,
        height_segments: int = 2,
        closed: bool = True,
    ):
        """
        Create a cone geometry

        Args:
            radius: Radius at base of cone
            height: Height of cone
            radial_segments: Number of segments around circumference
            height_segments: Number of segments along height
            closed: Whether to include bottom cap
        """
        # Evidence from three/geometry/ConeGeometry.py:
        # super().__init__(radiusTop=0.0001, radiusBottom=radius, ...)
        super().__init__(
            radius_top=0.0001,  # Nearly zero to avoid degenerate triangles
            radius_bottom=radius,
            height=height,
            radial_segments=radial_segments,
            height_segments=height_segments,
            circle_top=False,  # Cone has no top cap (comes to a point)
            circle_bottom=closed,  # Only bottom cap if closed
        )
