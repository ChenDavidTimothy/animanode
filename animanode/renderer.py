"""
WebGPU renderer for geometries
"""

import wgpu


class Renderer:
    """WebGPU renderer for geometric shapes"""

    @staticmethod
    def setup_drawing_sync(canvas, geometry, power_preference="high-performance", limits=None):
        """Setup synchronous drawing for a geometry on the given canvas.

        Args:
            canvas: Canvas implementing WgpuCanvasInterface
            geometry: Geometry class with shader_source and vertex_count
            power_preference: GPU power preference
            limits: GPU limits

        Returns:
            Draw function
        """
        adapter = wgpu.gpu.request_adapter_sync(power_preference=power_preference)
        device = adapter.request_device_sync(required_limits=limits)

        pipeline_kwargs = Renderer._get_render_pipeline_kwargs(canvas, device, geometry)
        render_pipeline = device.create_render_pipeline(**pipeline_kwargs)

        return Renderer._get_draw_function(
            canvas, device, render_pipeline, geometry, asynchronous=False
        )

    @staticmethod
    async def setup_drawing_async(canvas, geometry, limits=None):
        """Setup asynchronous drawing for a geometry on the given canvas.

        Args:
            canvas: Canvas implementing WgpuCanvasInterface
            geometry: Geometry class with shader_source and vertex_count
            limits: GPU limits

        Returns:
            Async draw function
        """
        adapter = await wgpu.gpu.request_adapter_async(power_preference="high-performance")
        device = await adapter.request_device_async(required_limits=limits)

        pipeline_kwargs = Renderer._get_render_pipeline_kwargs(canvas, device, geometry)
        render_pipeline = await device.create_render_pipeline_async(**pipeline_kwargs)

        return Renderer._get_draw_function(
            canvas, device, render_pipeline, geometry, asynchronous=True
        )

    @staticmethod
    def _get_render_pipeline_kwargs(canvas, device, geometry):
        """Create render pipeline configuration for a geometry"""
        context = canvas.get_context("wgpu")
        render_texture_format = context.get_preferred_format(device.adapter)
        context.configure(device=device, format=render_texture_format)

        shader = device.create_shader_module(code=geometry.shader_source)
        pipeline_layout = device.create_pipeline_layout(bind_group_layouts=[])

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
    def _get_draw_function(canvas, device, render_pipeline, geometry, *, asynchronous):
        """Create draw function for a geometry"""

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
                ],
            )

            render_pass.set_pipeline(render_pipeline)
            render_pass.draw(geometry.vertex_count, 1, 0, 0)
            render_pass.end()
            device.queue.submit([command_encoder.finish()])

        async def draw_frame_async():
            draw_frame_sync()  # nothing async here

        if asynchronous:
            return draw_frame_async
        else:
            return draw_frame_sync

    @staticmethod
    def print_available_adapters():
        """Print all available GPU adapters"""
        print("Available adapters on this system:")
        for adapter in wgpu.gpu.enumerate_adapters_sync():
            print(adapter.summary)
