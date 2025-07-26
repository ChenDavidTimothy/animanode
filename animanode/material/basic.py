import numpy as np
import wgpu


class Basic2DMaterial:
    """Basic 2D material with solid color and transform support"""

    # Combined shader with shared structs
    SHADER_SOURCE = """
    struct VertexInput {
        @location(0) position: vec2<f32>,
        @location(1) uv: vec2<f32>,
    }

    struct VertexOutput {
        @builtin(position) position: vec4<f32>,
        @location(0) uv: vec2<f32>,
    }

    struct Uniforms {
        transform: mat3x3<f32>,
        color: vec4<f32>,
    }

    @group(0) @binding(0)
    var<uniform> uniforms: Uniforms;

    @vertex
    fn vs_main(in: VertexInput) -> VertexOutput {
        var out: VertexOutput;

        // Apply 2D transform (homogeneous coordinates)
        let pos_2d = uniforms.transform * vec3<f32>(in.position, 1.0);
        out.position = vec4<f32>(pos_2d.xy, 0.0, 1.0);
        out.uv = in.uv;

        return out;
    }

    @fragment
    fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
        return uniforms.color;
    }
    """

    def __init__(
        self,
        device: wgpu.GPUDevice,
        color: tuple[float, float, float, float] = (1.0, 0.0, 0.0, 1.0),
    ):
        self.device = device
        self.color = np.array(color, dtype=np.float32)

        # Create shader module
        self.shader_module = device.create_shader_module(code=self.SHADER_SOURCE)

        # Create uniform buffer
        self.uniform_data = np.zeros(
            (),
            dtype=[
                (
                    "transform",
                    "float32",
                    (3, 4),
                ),  # mat3x3 in WGSL is stored as 3 columns of vec4 (16-byte aligned)
                ("color", "float32", (4,)),
            ],
        )

        self.uniform_buffer = device.create_buffer(
            size=self.uniform_data.nbytes,
            usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST,
        )

        # Create bind group layout
        self.bind_group_layout = device.create_bind_group_layout(
            entries=[
                {
                    "binding": 0,
                    "visibility": wgpu.ShaderStage.VERTEX | wgpu.ShaderStage.FRAGMENT,
                    "buffer": {"type": wgpu.BufferBindingType.uniform},
                }
            ]
        )

        # Create bind group
        self.bind_group = device.create_bind_group(
            layout=self.bind_group_layout,
            entries=[
                {
                    "binding": 0,
                    "resource": {
                        "buffer": self.uniform_buffer,
                        "offset": 0,
                        "size": self.uniform_data.nbytes,
                    },
                }
            ],
        )

        # Initialize uniform data
        self.uniform_data["color"] = self.color
        # Initialize transform as identity (3x4 with padding for WGSL alignment)
        identity_3x4 = np.zeros((3, 4), dtype=np.float32)
        identity_3x4[:3, :3] = np.eye(3, dtype=np.float32)
        self.uniform_data["transform"] = identity_3x4

    def set_color(self, r: float, g: float, b: float, a: float = 1.0) -> None:
        """Set material color"""
        self.color = np.array([r, g, b, a], dtype=np.float32)
        self.uniform_data["color"] = self.color

    def update_transform(self, transform_matrix: "Matrix2D") -> None:
        """Update transform matrix"""
        self.uniform_data["transform"] = transform_matrix.matrix

    def upload_uniforms(self) -> None:
        """Upload uniform data to GPU"""
        self.device.queue.write_buffer(self.uniform_buffer, 0, self.uniform_data.tobytes())

    def get_render_pipeline_descriptor(self, render_format: wgpu.TextureFormat) -> dict:
        """Get render pipeline descriptor for this material"""
        return {
            "layout": self.device.create_pipeline_layout(
                bind_group_layouts=[self.bind_group_layout]
            ),
            "vertex": {
                "module": self.shader_module,
                "entry_point": "vs_main",
                "buffers": [
                    {
                        "array_stride": 4 * 4,  # 4 floats per vertex (x, y, u, v)
                        "step_mode": wgpu.VertexStepMode.vertex,
                        "attributes": [
                            {
                                "format": wgpu.VertexFormat.float32x2,
                                "offset": 0,
                                "shader_location": 0,  # position
                            },
                            {
                                "format": wgpu.VertexFormat.float32x2,
                                "offset": 8,
                                "shader_location": 1,  # uv
                            },
                        ],
                    }
                ],
            },
            "primitive": {
                "topology": wgpu.PrimitiveTopology.triangle_list,
                "front_face": wgpu.FrontFace.ccw,
                "cull_mode": wgpu.CullMode.none,
            },
            "depth_stencil": None,
            "multisample": None,
            "fragment": {
                "module": self.shader_module,
                "entry_point": "fs_main",
                "targets": [
                    {
                        "format": render_format,
                        "blend": {
                            "color": {
                                "src_factor": wgpu.BlendFactor.src_alpha,
                                "dst_factor": wgpu.BlendFactor.one_minus_src_alpha,
                            },
                            "alpha": {
                                "src_factor": wgpu.BlendFactor.one,
                                "dst_factor": wgpu.BlendFactor.zero,
                            },
                        },
                    }
                ],
            },
        }
