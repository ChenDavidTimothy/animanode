import wgpu
from rendercanvas.auto import RenderCanvas, loop


def setup_drawing_sync(canvas, power_preference="high-performance", limits=None):
    """Setup to draw a rectangle on the given canvas.

    The given canvas must implement WgpuCanvasInterface, but nothing more.
    Returns the draw function.
    """

    adapter = wgpu.gpu.request_adapter_sync(power_preference=power_preference)
    device = adapter.request_device_sync(required_limits=limits)

    pipeline_kwargs = get_render_pipeline_kwargs(canvas, device)
    render_pipeline = device.create_render_pipeline(**pipeline_kwargs)

    return get_draw_function(canvas, device, render_pipeline, asynchronous=False)


async def setup_drawing_async(canvas, limits=None):
    """Setup to async-draw a rectangle on the given canvas.

    The given canvas must implement WgpuCanvasInterface, but nothing more.
    Returns the draw function.
    """

    adapter = await wgpu.gpu.request_adapter_async(power_preference="high-performance")
    device = await adapter.request_device_async(required_limits=limits)

    pipeline_kwargs = get_render_pipeline_kwargs(canvas, device)
    render_pipeline = await device.create_render_pipeline_async(**pipeline_kwargs)

    return get_draw_function(canvas, device, render_pipeline, asynchronous=True)


def get_render_pipeline_kwargs(canvas, device):
    context = canvas.get_context("wgpu")
    render_texture_format = context.get_preferred_format(device.adapter)
    context.configure(device=device, format=render_texture_format)

    shader = device.create_shader_module(code=shader_source)
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


def get_draw_function(canvas, device, render_pipeline, *, asynchronous):
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
        render_pass.draw(6, 1, 0, 0)  # Draw 6 vertices (2 triangles)
        render_pass.end()
        device.queue.submit([command_encoder.finish()])

    async def draw_frame_async():
        draw_frame_sync()  # nothing async here

    if asynchronous:
        return draw_frame_async
    else:
        return draw_frame_sync


# %% WGSL


shader_source = """
struct VertexInput {
    @builtin(vertex_index) vertex_index : u32,
};
struct VertexOutput {
    @location(0) color : vec4<f32>,
    @builtin(position) pos: vec4<f32>,
};

@vertex
fn vs_main(in: VertexInput) -> VertexOutput {
    // Rectangle as 2 triangles: 6 vertices total
    var positions = array<vec2<f32>, 6>(
        vec2<f32>(-0.5, -0.5),  // bottom-left
        vec2<f32>(0.5, -0.5),   // bottom-right
        vec2<f32>(0.5, 0.5),    // top-right
        vec2<f32>(-0.5, -0.5),  // bottom-left (triangle 2)
        vec2<f32>(0.5, 0.5),    // top-right (triangle 2)
        vec2<f32>(-0.5, 0.5),   // top-left
    );
    var colors = array<vec3<f32>, 6>(  // srgb colors
        vec3<f32>(1.0, 0.0, 0.0),  // red
        vec3<f32>(0.0, 1.0, 0.0),  // green
        vec3<f32>(0.0, 0.0, 1.0),  // blue
        vec3<f32>(1.0, 0.0, 0.0),  // red (triangle 2)
        vec3<f32>(0.0, 0.0, 1.0),  // blue (triangle 2)
        vec3<f32>(1.0, 1.0, 0.0),  // yellow
    );
    let index = i32(in.vertex_index);
    var out: VertexOutput;
    out.pos = vec4<f32>(positions[index], 0.0, 1.0);
    out.color = vec4<f32>(colors[index], 1.0);
    return out;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    let physical_color = pow(in.color.rgb, vec3<f32>(2.2));  // gamma correct
    return vec4<f32>(physical_color, in.color.a);
}
"""


print("Available adapters on this system:")
for a in wgpu.gpu.enumerate_adapters_sync():
    print(a.summary)


if __name__ == "__main__":
    canvas = RenderCanvas(
        size=(640, 480),
        title="wgpu rectangle example at $fps using $backend",
        update_mode="continuous",
        max_fps=60,
        vsync=True,
    )
    draw_frame = setup_drawing_sync(canvas)
    canvas.request_draw(draw_frame)
    loop.run()
