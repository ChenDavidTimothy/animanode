from typing import Any

import numpy as np
import wgpu

from ..core.node import GeometryNode
from ..material.basic import Basic2DMaterial
from ..math.matrix2d import Matrix2D
from ..transform.transform import Transform2DNode


class Renderer2D:
    """WebGPU-based 2D renderer for offscreen video generation"""

    def __init__(
        self, width: int = 1920, height: int = 1080, clear_color: tuple = (0.0, 0.0, 0.0, 1.0)
    ):
        self.width = width
        self.height = height
        self.clear_color = clear_color

        # Initialize WebGPU for offscreen rendering
        self.adapter = wgpu.gpu.request_adapter_sync(power_preference="high-performance")
        self.device = self.adapter.request_device_sync()

        # Create offscreen render target
        self.render_format = wgpu.TextureFormat.rgba8unorm
        self._create_render_target()

        # Create default material
        self.default_material = Basic2DMaterial(self.device)

        # Create render pipeline
        self.render_pipeline = self.device.create_render_pipeline(
            **self.default_material.get_render_pipeline_descriptor(self.render_format)
        )

        # Storage for geometry buffers
        self.geometry_buffers: dict[GeometryNode, tuple] = {}  # (vertex_buffer, index_buffer)

    def _create_render_target(self):
        """Create offscreen render target texture"""
        self.render_texture = self.device.create_texture(
            size=(self.width, self.height, 1),
            usage=wgpu.TextureUsage.RENDER_ATTACHMENT | wgpu.TextureUsage.COPY_SRC,
            dimension=wgpu.TextureDimension.d2,
            format=self.render_format,
            mip_level_count=1,
            sample_count=1,
        )
        self.render_view = self.render_texture.create_view()

    def _create_geometry_buffers(self, geometry_node: GeometryNode) -> tuple:
        """Create vertex and index buffers for a geometry node"""
        vertices = geometry_node.get_vertices()
        indices = geometry_node.get_indices()

        vertex_buffer = self.device.create_buffer_with_data(
            data=vertices, usage=wgpu.BufferUsage.VERTEX
        )

        index_buffer = self.device.create_buffer_with_data(
            data=indices, usage=wgpu.BufferUsage.INDEX
        )

        return vertex_buffer, index_buffer

    def _get_geometry_buffers(self, geometry_node: GeometryNode) -> tuple:
        """Get or create buffers for geometry node"""
        if geometry_node not in self.geometry_buffers:
            self.geometry_buffers[geometry_node] = self._create_geometry_buffers(geometry_node)
        return self.geometry_buffers[geometry_node]

    def render_frame(self, root_nodes: list[Any]) -> np.ndarray:
        """Render nodes and return frame as numpy array"""
        # Begin render pass
        command_encoder = self.device.create_command_encoder()

        render_pass = command_encoder.begin_render_pass(
            color_attachments=[
                {
                    "view": self.render_view,
                    "resolve_target": None,
                    "clear_value": self.clear_color,
                    "load_op": wgpu.LoadOp.clear,
                    "store_op": wgpu.StoreOp.store,
                }
            ]
        )

        render_pass.set_pipeline(self.render_pipeline)

        # Process each root node
        for root_node in root_nodes:
            self._render_node_recursive(root_node, render_pass, Matrix2D.identity())

        render_pass.end()
        self.device.queue.submit([command_encoder.finish()])

        # Read back the rendered frame
        return self._read_frame()

    def _render_node_recursive(self, node: Any, render_pass, parent_transform: Matrix2D) -> None:
        """Recursively render a node and find its input geometry"""
        # Evaluate the node
        result = node.evaluate()

        # Calculate accumulated transform
        current_transform = parent_transform
        if isinstance(node, Transform2DNode):
            current_transform = parent_transform.multiply(node.transform)

            # Recursively render input node if it exists
            if node.input_node:
                self._render_node_recursive(node.input_node, render_pass, current_transform)

        # If this is a geometry node, render it
        elif isinstance(node, GeometryNode):
            self._render_geometry(node, render_pass, current_transform)

    def _render_geometry(
        self, geometry_node: GeometryNode, render_pass, transform: Matrix2D
    ) -> None:
        """Render a single geometry node with transform"""
        # Get buffers for this geometry
        vertex_buffer, index_buffer = self._get_geometry_buffers(geometry_node)

        # Update material with transform
        self.default_material.update_transform(transform)
        self.default_material.upload_uniforms()

        # Set buffers and bind group
        render_pass.set_vertex_buffer(0, vertex_buffer)
        render_pass.set_index_buffer(index_buffer, wgpu.IndexFormat.uint32)
        render_pass.set_bind_group(0, self.default_material.bind_group)

        # Draw
        indices = geometry_node.get_indices()
        render_pass.draw_indexed(indices.size, 1, 0, 0, 0)

    def _read_frame(self) -> np.ndarray:
        """Read rendered frame from GPU to numpy array"""
        # Create staging buffer to copy texture data
        staging_buffer = self.device.create_buffer(
            size=self.width * self.height * 4,  # RGBA = 4 bytes per pixel
            usage=wgpu.BufferUsage.MAP_READ | wgpu.BufferUsage.COPY_DST,
        )

        # Copy texture to staging buffer
        command_encoder = self.device.create_command_encoder()
        command_encoder.copy_texture_to_buffer(
            {
                "texture": self.render_texture,
                "mip_level": 0,
                "origin": (0, 0, 0),
            },
            {
                "buffer": staging_buffer,
                "offset": 0,
                "bytes_per_row": self.width * 4,
            },
            (self.width, self.height, 1),
        )
        self.device.queue.submit([command_encoder.finish()])

        # Map buffer and read data directly
        staging_buffer.map_sync(wgpu.MapMode.READ)
        data = staging_buffer.read_mapped()
        staging_buffer.unmap()

        # Convert to numpy array and reshape
        frame = np.frombuffer(data, dtype=np.uint8).reshape((self.height, self.width, 4))

        # Convert RGBA to RGB and flip Y (WebGPU is top-left origin)
        frame = np.flip(frame[:, :, :3], axis=0)

        return frame

    def set_material_color(self, r: float, g: float, b: float, a: float = 1.0) -> None:
        """Set default material color"""
        self.default_material.set_color(r, g, b, a)

    def clear_geometry_cache(self) -> None:
        """Clear cached geometry buffers"""
        self.geometry_buffers.clear()
