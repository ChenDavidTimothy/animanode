from abc import ABC, abstractmethod

import numpy as np
import wgpu


class WGPUGeometry(ABC):
    """Base class for WebGPU geometries inspired by three.js geometry system"""

    def __init__(self):
        self._vertex_data = None
        self._index_data = None
        self._vertex_buffer = None
        self._index_buffer = None

    @abstractmethod
    def generate_vertices(self) -> np.ndarray:
        """Generate vertex data as numpy array with format [x, y, z, w, u, v]"""
        pass

    @abstractmethod
    def generate_indices(self) -> np.ndarray:
        """Generate index data as numpy array"""
        pass

    def get_vertex_data(self) -> np.ndarray:
        """Get cached vertex data, generating if necessary"""
        if self._vertex_data is None:
            self._vertex_data = self.generate_vertices()
        return self._vertex_data

    def get_index_data(self) -> np.ndarray:
        """Get cached index data, generating if necessary"""
        if self._index_data is None:
            self._index_data = self.generate_indices()
        return self._index_data

    def create_buffers(self, device: wgpu.GPUDevice) -> tuple:
        """Create WebGPU vertex and index buffers"""
        if self._vertex_buffer is None:
            self._vertex_buffer = device.create_buffer_with_data(
                data=self.get_vertex_data(), usage=wgpu.BufferUsage.VERTEX
            )
        if self._index_buffer is None:
            self._index_buffer = device.create_buffer_with_data(
                data=self.get_index_data(), usage=wgpu.BufferUsage.INDEX
            )
        return self._vertex_buffer, self._index_buffer

    def get_vertex_count(self) -> int:
        """Get number of vertices"""
        return len(self.get_vertex_data())

    def get_index_count(self) -> int:
        """Get number of indices"""
        return self.get_index_data().size


class SurfaceGeometry(WGPUGeometry):
    """Base class for parametric surface geometries"""

    def __init__(
        self,
        u_start: float,
        u_end: float,
        u_resolution: int,
        v_start: float,
        v_end: float,
        v_resolution: int,
        surface_function,
    ):
        super().__init__()
        self.u_start = u_start
        self.u_end = u_end
        self.u_resolution = u_resolution
        self.v_start = v_start
        self.v_end = v_end
        self.v_resolution = v_resolution
        self.surface_function = surface_function

    def generate_vertices(self) -> np.ndarray:
        """Generate vertices from parametric surface"""
        delta_u = (self.u_end - self.u_start) / self.u_resolution
        delta_v = (self.v_end - self.v_start) / self.v_resolution

        vertices = []

        # Generate grid of positions
        positions = []
        uvs = []
        for u_index in range(self.u_resolution + 1):
            row_positions = []
            row_uvs = []
            for v_index in range(self.v_resolution + 1):
                u = self.u_start + u_index * delta_u
                v = self.v_start + v_index * delta_v

                pos = self.surface_function(u, v)
                row_positions.append(pos)

                # UV coordinates
                uv = [u_index / self.u_resolution, v_index / self.v_resolution]
                row_uvs.append(uv)

            positions.append(row_positions)
            uvs.append(row_uvs)

        # Convert to triangles (vertex format: [x, y, z, w, u, v])
        for u_index in range(self.u_resolution):
            for v_index in range(self.v_resolution):
                # Get quad corners
                p00 = positions[u_index][v_index]
                p10 = positions[u_index + 1][v_index]
                p01 = positions[u_index][v_index + 1]
                p11 = positions[u_index + 1][v_index + 1]

                uv00 = uvs[u_index][v_index]
                uv10 = uvs[u_index + 1][v_index]
                uv01 = uvs[u_index][v_index + 1]
                uv11 = uvs[u_index + 1][v_index + 1]

                # REVERTED: Original three.js winding is correct for parametric surfaces
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

        return np.array(vertices, dtype=np.float32)

    def generate_indices(self) -> np.ndarray:
        """Generate sequential indices since vertices are already in triangle order"""
        vertex_count = self.u_resolution * self.v_resolution * 6  # 6 vertices per quad
        return np.arange(vertex_count, dtype=np.uint32)
