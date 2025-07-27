"""
WebGPU renderer for parametric geometries
Enhanced to support three directory's philosophy with uniform buffers
"""

import wgpu

from .geometry.parametric import ParametricGeometry


class Renderer:
    """
    WebGPU renderer for parametric geometric shapes

    Enhanced from original to support:
    - Uniform buffer management for parametric geometries
    - Pipeline creation with bind groups
    - Following three directory's Material class patterns
    """

    @staticmethod
    def setup_drawing_sync(
        canvas,
        geometry: ParametricGeometry,
        power_preference: str = "high-performance",
        limits=None,
    ):
        """
        Setup synchronous drawing for a parametric geometry

        Args:
            canvas: Canvas implementing WgpuCanvasInterface
            geometry: ParametricGeometry instance with parameters
            power_preference: GPU power preference
            limits: GPU limits

        Returns:
            Draw function ready for canvas.request_draw()
        """
        if not isinstance(geometry, ParametricGeometry):
            raise TypeError("geometry must be a ParametricGeometry instance")

        # Initialize WebGPU adapter and device
        adapter = wgpu.gpu.request_adapter_sync(power_preference=power_preference)
        device = adapter.request_device_sync(required_limits=limits)

        # Create and populate uniform buffer for geometry parameters
        uniform_data = geometry.get_uniform_data()
        uniform_buffer = device.create_buffer(
            size=geometry.get_uniform_size(),
            usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST,
        )
        device.queue.write_buffer(uniform_buffer, 0, uniform_data)

        # Create bind group layout for uniforms - following three's Material pattern
        bind_group_layout = device.create_bind_group_layout(
            entries=[
                {
                    "binding": 0,
                    "visibility": wgpu.ShaderStage.VERTEX | wgpu.ShaderStage.FRAGMENT,
                    "buffer": {
                        "type": wgpu.BufferBindingType.uniform,
                        "has_dynamic_offset": False,
                        "min_binding_size": geometry.get_uniform_size(),
                    },
                }
            ]
        )

        # Create bind group with uniform buffer
        bind_group = device.create_bind_group(
            layout=bind_group_layout,
            entries=[
                {
                    "binding": 0,
                    "resource": {
                        "buffer": uniform_buffer,
                        "offset": 0,
                        "size": geometry.get_uniform_size(),
                    },
                }
            ],
        )

        # Setup render pipeline - enhanced from original
        pipeline_kwargs = Renderer._get_render_pipeline_kwargs(
            canvas, device, geometry, bind_group_layout
        )
        render_pipeline = device.create_render_pipeline(**pipeline_kwargs)

        return Renderer._get_draw_function(
            canvas, device, render_pipeline, geometry, bind_group, asynchronous=False
        )

    @staticmethod
    async def setup_drawing_async(canvas, geometry: ParametricGeometry, limits=None):
        """
        Setup asynchronous drawing for a parametric geometry

        Args:
            canvas: Canvas implementing WgpuCanvasInterface
            geometry: ParametricGeometry instance with parameters
            limits: GPU limits

        Returns:
            Async draw function ready for canvas.request_draw()
        """
        if not isinstance(geometry, ParametricGeometry):
            raise TypeError("geometry must be a ParametricGeometry instance")

        # Initialize WebGPU adapter and device asynchronously
        adapter = await wgpu.gpu.request_adapter_async(power_preference="high-performance")
        device = await adapter.request_device_async(required_limits=limits)

        # Create and populate uniform buffer for geometry parameters
        uniform_data = geometry.get_uniform_data()
        uniform_buffer = device.create_buffer(
            size=geometry.get_uniform_size(),
            usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST,
        )
        device.queue.write_buffer(uniform_buffer, 0, uniform_data)

        # Create bind group layout for uniforms
        bind_group_layout = device.create_bind_group_layout(
            entries=[
                {
                    "binding": 0,
                    "visibility": wgpu.ShaderStage.VERTEX | wgpu.ShaderStage.FRAGMENT,
                    "buffer": {
                        "type": wgpu.BufferBindingType.uniform,
                        "has_dynamic_offset": False,
                        "min_binding_size": geometry.get_uniform_size(),
                    },
                }
            ]
        )

        # Create bind group with uniform buffer
        bind_group = device.create_bind_group(
            layout=bind_group_layout,
            entries=[
                {
                    "binding": 0,
                    "resource": {
                        "buffer": uniform_buffer,
                        "offset": 0,
                        "size": geometry.get_uniform_size(),
                    },
                }
            ],
        )

        # Setup render pipeline asynchronously
        pipeline_kwargs = Renderer._get_render_pipeline_kwargs(
            canvas, device, geometry, bind_group_layout
        )
        render_pipeline = await device.create_render_pipeline_async(**pipeline_kwargs)

        return Renderer._get_draw_function(
            canvas, device, render_pipeline, geometry, bind_group, asynchronous=True
        )

    @staticmethod
    def _get_render_pipeline_kwargs(canvas, device, geometry, bind_group_layout):
        """
        Create render pipeline configuration for a parametric geometry
        Enhanced from original to support bind group layouts
        """
        # Configure canvas context
        context = canvas.get_context("wgpu")
        render_texture_format = context.get_preferred_format(device.adapter)
        context.configure(device=device, format=render_texture_format)

        # Create shader module from geometry's parametric shader
        shader = device.create_shader_module(code=geometry.shader_source)

        # Create pipeline layout with bind group layout
        pipeline_layout = device.create_pipeline_layout(bind_group_layouts=[bind_group_layout])

        return {
            "layout": pipeline_layout,
            "vertex": {
                "module": shader,
                "entry_point": "vs_main",
            },
            "primitive": {
                "topology": wgpu.PrimitiveTopology.triangle_list,
                "front_face": wgpu.FrontFace.ccw,
                "cull_mode": wgpu.CullMode.none,
            },
            "depth_stencil": None,
            "multisample": None,
            "fragment": {
                "module": shader,
                "entry_point": "fs_main",
                "targets": [
                    {
                        "format": render_texture_format,
                        "blend": {
                            "color": {},
                            "alpha": {},
                        },
                    }
                ],
            },
        }

    @staticmethod
    def _get_draw_function(canvas, device, render_pipeline, geometry, bind_group, *, asynchronous):
        """
        Create draw function for a parametric geometry
        Enhanced from original to use bind groups for uniform parameters
        """

        def draw_frame_sync():
            current_texture_view = canvas.get_context("wgpu").get_current_texture().create_view()
            command_encoder = device.create_command_encoder()
            render_pass = command_encoder.begin_render_pass(
                color_attachments=[
                    {
                        "view": current_texture_view,
                        "resolve_target": None,
                        "clear_value": (0, 0, 0, 1),
                        "load_op": wgpu.LoadOp.clear,
                        "store_op": wgpu.StoreOp.store,
                    }
                ]
            )

            # Set pipeline and bind uniform parameters
            render_pass.set_pipeline(render_pipeline)
            render_pass.set_bind_group(0, bind_group)

            # Draw using procedural vertex generation
            render_pass.draw(geometry.vertex_count, 1, 0, 0)
            render_pass.end()
            device.queue.submit([command_encoder.finish()])

        async def draw_frame_async():
            draw_frame_sync()  # WebGPU draw calls are not inherently async

        if asynchronous:
            return draw_frame_async
        else:
            return draw_frame_sync

    @staticmethod
    def print_available_adapters():
        """
        Print all available GPU adapters for debugging
        Unchanged from original implementation
        """
        print("Available adapters on this system:")
        for adapter in wgpu.gpu.enumerate_adapters_sync():
            print(adapter.summary)

    @staticmethod
    def create_dynamic_renderer(canvas, initial_geometry: ParametricGeometry):
        """
        Create a renderer that can update geometry parameters dynamically

        Args:
            canvas: Canvas implementing WgpuCanvasInterface
            initial_geometry: Initial ParametricGeometry instance

        Returns:
            Dictionary with 'draw' function and 'update_geometry' function
        """
        # This would be for advanced use cases where parameters change frequently
        # For now, users should create new geometries and renderers for parameter changes
        raise NotImplementedError(
            "Dynamic parameter updates not yet implemented. "
            "Create new geometry instances for parameter changes."
        )
