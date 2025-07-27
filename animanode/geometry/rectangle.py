"""
Parametric rectangle geometry for AnimaNode
Based on three/geometry/QuadGeometry.py mathematical approach
"""

import struct

from .parametric import GeometryParameters, ParametricGeometry


class Rectangle(ParametricGeometry):
    """
    Parametric rectangle using mathematical corner calculation

    Inspired by three/geometry/QuadGeometry.py:
    - Configurable width and height dimensions
    - Mathematical corner positioning: (±width/2, ±height/2)
    - Two-triangle quad construction
    """

    def __init__(self, width: float = 1.0, height: float = 1.0):
        """
        Create parametric rectangle

        Args:
            width: Rectangle width (must be positive)
            height: Rectangle height (must be positive)
        """
        # Validate parameters following three directory's validation pattern
        width = GeometryParameters.validate_positive_float(width, "width")
        height = GeometryParameters.validate_positive_float(height, "height")

        super().__init__({"width": width, "height": height})

    def _calculate_vertex_count(self) -> int:
        """
        Calculate vertices for two-triangle quad: 2 triangles * 3 vertices each
        """
        return 6

    def _generate_shader(self) -> str:
        """
        Generate WGSL shader with parametric rectangle mathematics

        Mathematical approach:
        - Corner calculation: (±width/2, ±height/2)
        - Two triangles forming a quad
        - Vertex color interpolation across corners
        """
        return """
struct GeometryParams {
    width: f32,
    height: f32,
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
    // Mathematical corner calculation: (±width/2, ±height/2)
    let half_w = params.width * 0.5;
    let half_h = params.height * 0.5;

    // Two triangles forming a quad - following three directory's quad construction
    var positions = array<vec2<f32>, 6>(
        vec2<f32>(-half_w, -half_h),  // Triangle 1: bottom-left
        vec2<f32>(half_w, -half_h),   // Triangle 1: bottom-right
        vec2<f32>(half_w, half_h),    // Triangle 1: top-right
        vec2<f32>(-half_w, -half_h),  // Triangle 2: bottom-left
        vec2<f32>(half_w, half_h),    // Triangle 2: top-right
        vec2<f32>(-half_w, half_h),   // Triangle 2: top-left
    );

    // Color mapping for vertices - following three's vertex color pattern
    var colors = array<vec3<f32>, 6>(
        vec3<f32>(1.0, 0.0, 0.0),  // Red - bottom-left
        vec3<f32>(0.0, 1.0, 0.0),  // Green - bottom-right
        vec3<f32>(0.0, 0.0, 1.0),  // Blue - top-right
        vec3<f32>(1.0, 0.0, 0.0),  // Red - bottom-left (triangle 2)
        vec3<f32>(0.0, 0.0, 1.0),  // Blue - top-right (triangle 2)
        vec3<f32>(1.0, 1.0, 0.0),  // Yellow - top-left
    );

    let index = i32(in.vertex_index);
    var out: VertexOutput;
    out.pos = vec4<f32>(positions[index], 0.0, 1.0);
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
        Pack rectangle parameters into 16-byte aligned uniform buffer
        Layout: [width: f32, height: f32, padding: f32, padding: f32]
        """
        return struct.pack(
            "=ffff",  # Little-endian: 4 floats for 16-byte alignment
            self.parameters["width"],
            self.parameters["height"],
            0.0,  # padding for 16-byte alignment
            0.0,  # padding for 16-byte alignment
        )
