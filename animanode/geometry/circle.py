"""
Parametric circle geometry for AnimaNode
Based on three/geometry/CircleGeometry.py mathematical approach
"""

import struct

from .parametric import GeometryParameters, ParametricGeometry


class Circle(ParametricGeometry):
    """
    Parametric circle using mathematical function P(t) = (r*cos(t), r*sin(t))

    Inspired by three/geometry/CircleGeometry.py:
    - Configurable radius and segment resolution
    - Center + circumference triangle fan approach
    - Mathematical parameterization over hardcoding
    """

    def __init__(self, radius: float = 0.5, segments: int = 16):
        """
        Create parametric circle

        Args:
            radius: Circle radius (must be positive)
            segments: Number of triangular segments (minimum 3)
        """
        # Validate parameters following three directory's validation pattern
        radius = GeometryParameters.validate_positive_float(radius, "radius")
        segments = GeometryParameters.validate_min_segments(segments, minimum=3)

        super().__init__({"radius": radius, "segments": segments})

    def _calculate_vertex_count(self) -> int:
        """
        Calculate vertices for triangle fan: segments triangles * 3 vertices each
        Each triangle: center -> point N -> point N+1
        """
        return self.parameters["segments"] * 3

    def _generate_shader(self) -> str:
        """
        Generate WGSL shader with parametric circle mathematics AND transforms

        Mathematical approach:
        - Parametric circle: P(t) = (r*cos(2πt/n), r*sin(2πt/n))
        - Triangle fan from center to circumference
        - Transform matrix applied to all vertices
        """
        return """
struct GeometryParams {
    radius: f32,
    segments: u32,
    padding1: u32,  // 16-byte alignment
    padding2: u32,
};

struct TransformMatrix {
    m00: f32, m01: f32, m02: f32, pad0: f32,
    m10: f32, m11: f32, m12: f32, pad1: f32,
    m20: f32, m21: f32, m22: f32, pad2: f32,
};

@group(0) @binding(0)
var<uniform> params: GeometryParams;

@group(0) @binding(1)
var<uniform> transform: TransformMatrix;

struct VertexInput {
    @builtin(vertex_index) vertex_index : u32,
};

struct VertexOutput {
    @location(0) color : vec4<f32>,
    @builtin(position) pos: vec4<f32>,
};

@vertex
fn vs_main(in: VertexInput) -> VertexOutput {
    let PI = 3.14159265359;
    let index = i32(in.vertex_index);
    let triangle_id = index / 3;
    let vertex_in_triangle = index % 3;

    var position: vec2<f32>;
    var color: vec3<f32>;

    if (vertex_in_triangle == 0) {
        // Center vertex - mathematical origin
        position = vec2<f32>(0.0, 0.0);
        color = vec3<f32>(1.0, 1.0, 1.0);  // White center
    } else {
        // Circumference vertex using parametric circle equation
        var point_id: i32;
        if (vertex_in_triangle == 1) {
            point_id = triangle_id;
        } else {
            point_id = (triangle_id + 1) % i32(params.segments);
        }

        // Parametric angle: t = 2π * point_id / segments
        let angle = 2.0 * PI * f32(point_id) / f32(params.segments);

        // Parametric circle: P(t) = (r*cos(t), r*sin(t))
        position = vec2<f32>(
            params.radius * cos(angle),
            params.radius * sin(angle)
        );

        // Color function based on angular position
        color = vec3<f32>(
            0.5 + 0.5 * cos(angle),
            0.5 + 0.5 * sin(angle),
            0.8
        );
    }

    // FIXED: Apply transform matrix to position
    let transformed_pos = vec2<f32>(
        transform.m00 * position.x + transform.m01 * position.y + transform.m02,
        transform.m10 * position.x + transform.m11 * position.y + transform.m12
    );

    var out: VertexOutput;
    // Aspect ratio correction for 2D rendering
    let xy_ratio = 0.75;  // 480/640 for typical canvas size
    out.pos = vec4<f32>(transformed_pos.x * xy_ratio, transformed_pos.y, 0.0, 1.0);
    out.color = vec4<f32>(color, 1.0);
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
        Pack circle parameters AND transform matrix into uniform buffer
        Layout: [GeometryParams (16 bytes), TransformMatrix (48 bytes)]
        """
        # Pack geometry parameters (16 bytes)
        geometry_data = struct.pack(
            "=fIII",  # Little-endian: float, uint32, uint32, uint32
            self.parameters["radius"],
            self.parameters["segments"],
            0,  # padding for 16-byte alignment
            0,  # padding for 16-byte alignment
        )

        # Pack transform matrix (48 bytes = 12 floats for 3x4 matrix layout)
        transform_matrix = self.transform.get_matrix().to_list()
        transform_data = struct.pack(
            "=ffffffffffff",  # 12 floats total (3 rows * 4 floats per row)
            transform_matrix[0],
            transform_matrix[1],
            transform_matrix[2],
            0.0,  # Row 0 + padding
            transform_matrix[3],
            transform_matrix[4],
            transform_matrix[5],
            0.0,  # Row 1 + padding
            transform_matrix[6],
            transform_matrix[7],
            transform_matrix[8],
            0.0,  # Row 2 + padding
        )

        return geometry_data + transform_data
