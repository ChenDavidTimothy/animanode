"""
Parametric triangle geometry for AnimaNode
Enhanced version of the original hardcoded triangle with mathematical parameterization
"""

import struct

from .parametric import GeometryParameters, ParametricGeometry


class Triangle(ParametricGeometry):
    """
    Parametric triangle with configurable size and orientation

    Enhanced from the original hardcoded version with:
    - Configurable size scaling
    - Mathematical vertex positioning
    - Consistent with three directory's parametric approach
    """

    def __init__(self, size: float = 1.0, rotation: float = 0.0):
        """
        Create parametric triangle

        Args:
            size: Triangle scale factor (must be positive)
            rotation: Rotation angle in radians
        """
        # Validate parameters following three directory's validation pattern
        size = GeometryParameters.validate_positive_float(size, "size")
        if not isinstance(rotation, (int, float)):
            raise ValueError(f"rotation must be a number, got {rotation}")

        super().__init__({"size": size, "rotation": float(rotation)})

    def _calculate_vertex_count(self) -> int:
        """
        Triangle always has 3 vertices
        """
        return 3

    def _generate_shader(self) -> str:
        """
        Generate WGSL shader with parametric triangle mathematics

        Mathematical approach:
        - Base triangle vertices with mathematical scaling
        - Rotation transformation using rotation matrix
        - Size scaling parameter
        """
        return """
struct GeometryParams {
    size: f32,
    rotation: f32,
    padding1: f32,  // 16-byte alignment
    padding2: f32,
};

@group(0) @binding(0)
var<uniform> params: GeometryParams;

struct VertexInput {
    @builtin(vertex_index) vertex_index : u32,
};

struct VertexOutput {
    @location(0) color : vec4<f32>,
    @builtin(position) pos: vec4<f32>,
};

@vertex
fn vs_main(in: VertexInput) -> VertexOutput {
    // Base triangle vertices - mathematical positioning
    var base_positions = array<vec2<f32>, 3>(
        vec2<f32>(0.0, -0.5),   // Bottom vertex
        vec2<f32>(0.5, 0.5),    // Top-right vertex
        vec2<f32>(-0.5, 0.75),  // Top-left vertex (slightly higher for visual interest)
    );

    // Color mapping - sRGB colors for each vertex
    var colors = array<vec3<f32>, 3>(
        vec3<f32>(1.0, 1.0, 0.0),  // Yellow - bottom
        vec3<f32>(1.0, 0.0, 1.0),  // Magenta - top-right
        vec3<f32>(0.0, 1.0, 1.0),  // Cyan - top-left
    );

    let index = i32(in.vertex_index);
    var base_pos = base_positions[index];

    // Apply size scaling - mathematical transformation
    base_pos = base_pos * params.size;

    // Apply rotation transformation - 2D rotation matrix
    let cos_r = cos(params.rotation);
    let sin_r = sin(params.rotation);
    let rotated_pos = vec2<f32>(
        base_pos.x * cos_r - base_pos.y * sin_r,
        base_pos.x * sin_r + base_pos.y * cos_r
    );

    var out: VertexOutput;
    // Aspect ratio correction for 2D rendering
    let xy_ratio = 0.75;  // 480/640 for typical canvas size
    out.pos = vec4<f32>(rotated_pos.x * xy_ratio, rotated_pos.y, 0.0, 1.0);
    out.color = vec4<f32>(colors[index], 1.0);
    return out;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    // Gamma correction for proper color display
    let physical_color = pow(in.color.rgb, vec3<f32>(2.2));
    return vec4<f32>(physical_color, in.color.a);
}
"""

    def _pack_uniform_data(self) -> bytes:
        """
        Pack triangle parameters into 16-byte aligned uniform buffer
        Layout: [size: f32, rotation: f32, padding: f32, padding: f32]
        """
        return struct.pack(
            "=ffff",  # Little-endian: 4 floats for 16-byte alignment
            self.parameters["size"],
            self.parameters["rotation"],
            0.0,  # padding for 16-byte alignment
            0.0,  # padding for 16-byte alignment
        )
