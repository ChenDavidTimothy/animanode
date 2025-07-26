import time

import numpy as np
import wgpu

from .geometry.base import WGPUGeometry


def setup_geometry_drawing_sync(
    canvas, geometry: WGPUGeometry, power_preference="high-performance", limits=None
):
    """
    Setup to draw any geometry on the given canvas - inspired by cube.py

    Args:
        canvas: Canvas to render to
        geometry: WGPUGeometry instance to render
        power_preference: GPU power preference
        limits: GPU limits

    Returns:
        Callable draw function compatible with offscreen_video.py
    """
    adapter = wgpu.gpu.request_adapter_sync(power_preference=power_preference)
    device = adapter.request_device_sync(required_limits=limits)

    pipeline_layout, uniform_buffer, bind_groups = create_pipeline_layout(device)
    pipeline_kwargs = get_render_pipeline_kwargs(canvas, device, pipeline_layout)

    render_pipeline = device.create_render_pipeline(**pipeline_kwargs)

    return get_draw_function(
        canvas, device, render_pipeline, uniform_buffer, bind_groups, geometry, asynchronous=False
    )


async def setup_geometry_drawing_async(canvas, geometry: WGPUGeometry, limits=None):
    """
    Setup to async-draw any geometry on the given canvas

    Args:
        canvas: Canvas to render to
        geometry: WGPUGeometry instance to render
        limits: GPU limits

    Returns:
        Callable async draw function
    """
    adapter = await wgpu.gpu.request_adapter_async(power_preference="high-performance")
    device = await adapter.request_device_async(required_limits=limits)

    pipeline_layout, uniform_buffer, bind_groups = create_pipeline_layout(device)
    pipeline_kwargs = get_render_pipeline_kwargs(canvas, device, pipeline_layout)

    render_pipeline = await device.create_render_pipeline_async(**pipeline_kwargs)

    return get_draw_function(
        canvas, device, render_pipeline, uniform_buffer, bind_groups, geometry, asynchronous=True
    )


def get_render_pipeline_kwargs(canvas, device, pipeline_layout):
    """Create render pipeline kwargs with DEPTH TESTING - Fixed from cube.py"""
    context = canvas.get_context("wgpu")
    render_texture_format = context.get_preferred_format(device.adapter)
    context.configure(device=device, format=render_texture_format)

    shader = device.create_shader_module(code=shader_source)

    return {
        "layout": pipeline_layout,
        "vertex": {
            "module": shader,
            "entry_point": "vs_main",
            "buffers": [
                {
                    "array_stride": 4 * 6,  # 6 floats per vertex: [x,y,z,w,u,v]
                    "step_mode": wgpu.VertexStepMode.vertex,
                    "attributes": [
                        {
                            "format": wgpu.VertexFormat.float32x4,
                            "offset": 0,
                            "shader_location": 0,
                        },
                        {
                            "format": wgpu.VertexFormat.float32x2,
                            "offset": 4 * 4,
                            "shader_location": 1,
                        },
                    ],
                },
            ],
        },
        "primitive": {
            "topology": wgpu.PrimitiveTopology.triangle_list,
            "front_face": wgpu.FrontFace.ccw,
            "cull_mode": wgpu.CullMode.back,
        },
        # FIXED: Enable depth testing for proper 3D rendering
        "depth_stencil": {
            "format": wgpu.TextureFormat.depth24plus,
            "depth_write_enabled": True,
            "depth_compare": wgpu.CompareFunction.less,
        },
        "multisample": None,
        "fragment": {
            "module": shader,
            "entry_point": "fs_main",
            "targets": [
                {
                    "format": render_texture_format,
                    "blend": {
                        "alpha": {},
                        "color": {},
                    },
                }
            ],
        },
    }


def create_pipeline_layout(device):
    """Create pipeline layout - Evidence from cube.py"""
    # Create uniform buffer - data is uploaded each frame
    uniform_buffer = device.create_buffer(
        size=uniform_data.nbytes,
        usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST,
    )

    # Create another buffer to copy data to it
    uniform_buffer.copy_buffer = device.create_buffer(
        size=uniform_data.nbytes,
        usage=wgpu.BufferUsage.MAP_WRITE | wgpu.BufferUsage.COPY_SRC,
    )

    # Create texture and upload data - Evidence from cube.py texture creation
    texture = device.create_texture(
        size=texture_size,
        usage=wgpu.TextureUsage.COPY_DST | wgpu.TextureUsage.TEXTURE_BINDING,
        dimension=wgpu.TextureDimension.d2,
        format=wgpu.TextureFormat.r8unorm,
        mip_level_count=1,
        sample_count=1,
    )
    texture_view = texture.create_view()

    device.queue.write_texture(
        {
            "texture": texture,
            "mip_level": 0,
            "origin": (0, 0, 0),
        },
        texture_data,
        {
            "offset": 0,
            "bytes_per_row": texture_data.strides[0],
        },
        texture_size,
    )

    # Create sampler
    sampler = device.create_sampler()

    # Create bind groups - Evidence from cube.py bind group structure
    bind_groups_entries = [[]]
    bind_groups_layout_entries = [[]]

    bind_groups_entries[0].append(
        {
            "binding": 0,
            "resource": {
                "buffer": uniform_buffer,
                "offset": 0,
                "size": uniform_buffer.size,
            },
        }
    )
    bind_groups_layout_entries[0].append(
        {
            "binding": 0,
            "visibility": wgpu.ShaderStage.VERTEX | wgpu.ShaderStage.FRAGMENT,
            "buffer": {},
        }
    )

    bind_groups_entries[0].append({"binding": 1, "resource": texture_view})
    bind_groups_layout_entries[0].append(
        {
            "binding": 1,
            "visibility": wgpu.ShaderStage.FRAGMENT,
            "texture": {},
        }
    )

    bind_groups_entries[0].append({"binding": 2, "resource": sampler})
    bind_groups_layout_entries[0].append(
        {
            "binding": 2,
            "visibility": wgpu.ShaderStage.FRAGMENT,
            "sampler": {},
        }
    )

    # Create wgpu binding objects
    bind_group_layouts = []
    bind_groups = []

    for entries, layout_entries in zip(
        bind_groups_entries, bind_groups_layout_entries, strict=False
    ):
        bind_group_layout = device.create_bind_group_layout(entries=layout_entries)
        bind_group_layouts.append(bind_group_layout)
        bind_groups.append(device.create_bind_group(layout=bind_group_layout, entries=entries))

    pipeline_layout = device.create_pipeline_layout(bind_group_layouts=bind_group_layouts)

    return pipeline_layout, uniform_buffer, bind_groups


def get_draw_function(
    canvas,
    device,
    render_pipeline,
    uniform_buffer,
    bind_groups,
    geometry: WGPUGeometry,
    *,
    asynchronous,
):
    """Create draw function - Modified from cube.py with DEPTH BUFFER"""

    # Create buffers from geometry - KEY DIFFERENCE from cube.py
    vertex_buffer, index_buffer = geometry.create_buffers(device)

    # Create depth texture for 3D rendering
    depth_texture = None

    def update_transform():
        """Update uniform transform - Evidence from cube.py"""
        a1 = -0.3
        a2 = time.time()
        s = 0.6
        ortho = np.array(
            [
                [s, 0, 0, 0],
                [0, s, 0, 0],
                [0, 0, s, 0],
                [0, 0, 0, 1],
            ],
        )
        rot1 = np.array(
            [
                [1, 0, 0, 0],
                [0, np.cos(a1), -np.sin(a1), 0],
                [0, np.sin(a1), +np.cos(a1), 0],
                [0, 0, 0, 1],
            ],
        )
        rot2 = np.array(
            [
                [np.cos(a2), 0, np.sin(a2), 0],
                [0, 1, 0, 0],
                [-np.sin(a2), 0, np.cos(a2), 0],
                [0, 0, 0, 1],
            ],
        )
        uniform_data["transform"] = rot2 @ rot1 @ ortho

    def upload_uniform_buffer_sync():
        """Upload uniform buffer sync - Evidence from cube.py"""
        tmp_buffer = uniform_buffer.copy_buffer
        tmp_buffer.map_sync(wgpu.MapMode.WRITE)
        tmp_buffer.write_mapped(uniform_data)
        tmp_buffer.unmap()
        command_encoder = device.create_command_encoder()
        command_encoder.copy_buffer_to_buffer(tmp_buffer, 0, uniform_buffer, 0, uniform_data.nbytes)
        device.queue.submit([command_encoder.finish()])

    async def upload_uniform_buffer_async():
        """Upload uniform buffer async - Evidence from cube.py"""
        tmp_buffer = uniform_buffer.copy_buffer
        await tmp_buffer.map_async(wgpu.MapMode.WRITE)
        tmp_buffer.write_mapped(uniform_data)
        tmp_buffer.unmap()
        command_encoder = device.create_command_encoder()
        command_encoder.copy_buffer_to_buffer(tmp_buffer, 0, uniform_buffer, 0, uniform_data.nbytes)
        device.queue.submit([command_encoder.finish()])

    def draw_frame():
        """Draw frame with DEPTH BUFFER - Fixed for proper 3D rendering"""
        nonlocal depth_texture

        current_texture = canvas.get_context("wgpu").get_current_texture()
        current_texture_view = current_texture.create_view()

        # Create or recreate depth texture if size changed
        canvas_size = current_texture.size
        if depth_texture is None or depth_texture.size != canvas_size:
            if depth_texture:
                depth_texture.destroy()
            depth_texture = device.create_texture(
                size=canvas_size,
                usage=wgpu.TextureUsage.RENDER_ATTACHMENT,
                dimension=wgpu.TextureDimension.d2,
                format=wgpu.TextureFormat.depth24plus,
                mip_level_count=1,
                sample_count=1,
            )

        depth_view = depth_texture.create_view()

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
            # FIXED: Add depth attachment for proper 3D rendering
            depth_stencil_attachment={
                "view": depth_view,
                "depth_clear_value": 1.0,
                "depth_load_op": wgpu.LoadOp.clear,
                "depth_store_op": wgpu.StoreOp.store,
            },
        )

        render_pass.set_pipeline(render_pipeline)
        render_pass.set_index_buffer(index_buffer, wgpu.IndexFormat.uint32)
        render_pass.set_vertex_buffer(0, vertex_buffer)
        for bind_group_id, bind_group in enumerate(bind_groups):
            render_pass.set_bind_group(bind_group_id, bind_group)

        # Use geometry index count instead of hardcoded cube data
        render_pass.draw_indexed(geometry.get_index_count(), 1, 0, 0, 0)
        render_pass.end()

        device.queue.submit([command_encoder.finish()])

    def draw_frame_sync():
        """Sync draw frame"""
        update_transform()
        upload_uniform_buffer_sync()
        draw_frame()

    async def draw_frame_async():
        """Async draw frame"""
        update_transform()
        await upload_uniform_buffer_async()
        draw_frame()

    if asynchronous:
        return draw_frame_async
    else:
        return draw_frame_sync


# Shader source - Evidence from cube.py (identical)
shader_source = """
struct Locals {
    transform: mat4x4<f32>,
};
@group(0) @binding(0)
var<uniform> r_locals: Locals;

struct VertexInput {
    @location(0) pos : vec4<f32>,
    @location(1) texcoord: vec2<f32>,
};
struct VertexOutput {
    @location(0) texcoord: vec2<f32>,
    @builtin(position) pos: vec4<f32>,
};
struct FragmentOutput {
    @location(0) color : vec4<f32>,
};

@vertex
fn vs_main(in: VertexInput) -> VertexOutput {
    let ndc: vec4<f32> = r_locals.transform * in.pos;
    let xy_ratio = 0.75;  // hardcoded for 640x480 canvas size
    var out: VertexOutput;
    out.pos = vec4<f32>(ndc.x * xy_ratio, ndc.y, 0.0, 1.0);
    out.texcoord = in.texcoord;
    return out;
}

@group(0) @binding(1)
var r_tex: texture_2d<f32>;

@group(0) @binding(2)
var r_sampler: sampler;

@fragment
fn fs_main(in: VertexOutput) -> FragmentOutput {
    let value = textureSample(r_tex, r_sampler, in.texcoord).r;
    let physical_color = vec3<f32>(pow(value, 2.2));  // gamma correct
    var out: FragmentOutput;
    out.color = vec4<f32>(physical_color.rgb, 1.0);
    return out;
}
"""

# Texture data - Evidence from cube.py (identical)
texture_data = np.array(
    [
        [50, 100, 150, 200],
        [100, 150, 200, 50],
        [150, 200, 50, 100],
        [200, 50, 100, 150],
    ],
    dtype=np.uint8,
)
texture_data = np.repeat(texture_data, 64, 0)
texture_data = np.repeat(texture_data, 64, 1)
texture_size = texture_data.shape[1], texture_data.shape[0], 1

# Uniform data - Evidence from cube.py (identical)
uniform_dtype = [("transform", "float32", (4, 4))]
uniform_data = np.zeros((), dtype=uniform_dtype)
