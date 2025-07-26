from collections.abc import Callable
from math import cos, radians, sin

import numpy as np

from .base import WGPUGeometry


class WGPUTubeGeometry(WGPUGeometry):
    """WebGPU Tube Geometry - inspired by three.js TubeGeometry"""

    def __init__(
        self,
        curve_function: Callable[[float], list] | list,
        tube_radius: float = 0.1,
        radius_segments: int = 6,
        length_segments: int = 50,
        t_min: float = 0.0,
        t_max: float = 1.0,
    ):
        """
        Create a tube geometry along a curve

        Args:
            curve_function: Function that takes parameter t and returns [x, y, z] or list of positions
            tube_radius: Radius of the tube
            radius_segments: Number of segments around the tube circumference
            length_segments: Number of segments along the tube length
            t_min: Minimum parameter value (for parametric functions)
            t_max: Maximum parameter value (for parametric functions)
        """
        super().__init__()
        self.tube_radius = tube_radius
        self.radius_segments = radius_segments
        self.length_segments = length_segments

        # Generate curve points
        if callable(curve_function):
            self.curve_points = []
            for i in range(length_segments + 1):
                t = t_min + (t_max - t_min) * i / length_segments
                point = curve_function(t)
                self.curve_points.append(np.array(point))
        elif isinstance(curve_function, list):
            self.curve_points = [np.array(p) for p in curve_function]
            self.length_segments = len(self.curve_points) - 1
        else:
            raise ValueError("curve_function must be callable or list of positions")

    def _calculate_tube_frames(self):
        """Calculate tangent, normal, and binormal vectors along the curve"""
        # Evidence from three/geometry/TubeGeometry.py shows frame calculation
        frames = {"tangents": [], "normals": [], "binormals": []}

        # Calculate tangents
        for i in range(len(self.curve_points)):
            if i == 0:
                # Forward difference for first point
                tangent = self.curve_points[1] - self.curve_points[0]
            elif i == len(self.curve_points) - 1:
                # Backward difference for last point
                tangent = self.curve_points[i] - self.curve_points[i - 1]
            else:
                # Central difference for middle points
                tangent = self.curve_points[i + 1] - self.curve_points[i - 1]

            # Normalize tangent
            tangent = tangent / np.linalg.norm(tangent)
            frames["tangents"].append(tangent)

        # Calculate initial normal vector (arbitrary but consistent)
        arbitrary_vector = np.array([1, 1, 1])
        initial_normal = np.cross(frames["tangents"][0], arbitrary_vector)
        if np.linalg.norm(initial_normal) < 0.001:
            arbitrary_vector = np.array([1, 1, -1])
            initial_normal = np.cross(frames["tangents"][0], arbitrary_vector)
        initial_normal = initial_normal / np.linalg.norm(initial_normal)
        frames["normals"].append(initial_normal)

        # Calculate remaining normals using parallel transport
        for i in range(1, len(frames["tangents"])):
            prev_normal = frames["normals"][i - 1]
            prev_tangent = frames["tangents"][i - 1]
            curr_tangent = frames["tangents"][i]

            # Check if tangent has changed direction
            cross_product = np.cross(prev_tangent, curr_tangent)
            magnitude = np.linalg.norm(cross_product)

            if magnitude > 0.0001:
                # Tangent has changed, rotate normal accordingly
                cross_product = cross_product / magnitude
                theta = np.arccos(np.clip(np.dot(prev_tangent, curr_tangent), -1, 1))

                # Rodrigues rotation formula
                cos_theta = np.cos(theta)
                sin_theta = np.sin(theta)
                normal = (
                    prev_normal * cos_theta
                    + np.cross(cross_product, prev_normal) * sin_theta
                    + cross_product * np.dot(cross_product, prev_normal) * (1 - cos_theta)
                )
            else:
                # Tangent hasn't changed, keep previous normal
                normal = prev_normal

            frames["normals"].append(normal)

        # Calculate binormals
        for i in range(len(frames["tangents"])):
            binormal = np.cross(frames["tangents"][i], frames["normals"][i])
            frames["binormals"].append(binormal)

        return frames

    def generate_vertices(self) -> np.ndarray:
        """Generate tube vertices - Evidence from three/geometry/TubeGeometry.py"""
        vertices = []
        frames = self._calculate_tube_frames()

        # Generate tube points in a 2D grid
        tube_points = []
        tube_normals = []
        angle = radians(360) / self.radius_segments

        for length_index in range(len(self.curve_points)):
            radial_points = []
            radial_normals = []

            center = self.curve_points[length_index]
            normal = frames["normals"][length_index]
            binormal = frames["binormals"][length_index]

            for radius_index in range(self.radius_segments + 1):
                # Calculate position around the tube circumference
                cos_angle = cos(angle * radius_index)
                sin_angle = sin(angle * radius_index)

                # Local normal in the tube cross-section
                local_normal = cos_angle * normal + sin_angle * binormal
                point = center + self.tube_radius * local_normal

                radial_points.append(point)
                radial_normals.append(local_normal)

            tube_points.append(radial_points)
            tube_normals.append(radial_normals)

        # Generate triangles
        # Evidence from three/geometry/TubeGeometry.py shows quad decomposition
        for length_index in range(self.length_segments):
            for radius_index in range(self.radius_segments):
                # Get quad corners
                p_a = tube_points[length_index][radius_index]
                p_b = tube_points[length_index + 1][radius_index]
                p_c = tube_points[length_index + 1][radius_index + 1]
                p_d = tube_points[length_index][radius_index + 1]

                # Calculate UV coordinates
                u_a = length_index / self.length_segments
                u_b = (length_index + 1) / self.length_segments
                v_a = radius_index / self.radius_segments
                v_b = (radius_index + 1) / self.radius_segments

                # First triangle: A, B, C
                vertices.extend(
                    [
                        [p_a[0], p_a[1], p_a[2], 1.0, u_a, v_a],
                        [p_b[0], p_b[1], p_b[2], 1.0, u_b, v_a],
                        [p_c[0], p_c[1], p_c[2], 1.0, u_b, v_b],
                    ]
                )

                # Second triangle: A, C, D
                vertices.extend(
                    [
                        [p_a[0], p_a[1], p_a[2], 1.0, u_a, v_a],
                        [p_c[0], p_c[1], p_c[2], 1.0, u_b, v_b],
                        [p_d[0], p_d[1], p_d[2], 1.0, u_a, v_b],
                    ]
                )

        return np.array(vertices, dtype=np.float32)

    def generate_indices(self) -> np.ndarray:
        """Generate sequential indices since vertices are already in triangle order"""
        vertex_count = self.length_segments * self.radius_segments * 6  # 6 vertices per quad
        return np.arange(vertex_count, dtype=np.uint32)
