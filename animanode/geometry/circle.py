"""
Circle geometry definition
"""


class Circle:
    vertex_count = 48  # 16 triangles * 3 vertices each

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
    // Circle as 16 triangles (48 vertices total)
    // Each triangle: center -> point N -> point N+1
    let PI = 3.14159265359;
    let SEGMENTS = 16;
    let RADIUS = 0.5;

    let index = i32(in.vertex_index);
    let triangle_id = index / 3;
    let vertex_in_triangle = index % 3;

    var position: vec2<f32>;
    var color: vec3<f32>;

    if (vertex_in_triangle == 0) {
        // Center vertex
        position = vec2<f32>(0.0, 0.0);
        color = vec3<f32>(1.0, 1.0, 1.0); // white center
    } else {
        // Circumference vertex
        var point_id: i32;
        if (vertex_in_triangle == 1) {
            point_id = triangle_id;
        } else {
            point_id = (triangle_id + 1) % SEGMENTS;
        }
        let angle = 2.0 * PI * f32(point_id) / f32(SEGMENTS);

        position = vec2<f32>(
            RADIUS * cos(angle),
            RADIUS * sin(angle)
        );
        color = vec3<f32>(
            0.5 + 0.5 * cos(angle),
            0.5 + 0.5 * sin(angle),
            0.8
        );
    }

    var out: VertexOutput;
    let xy_ratio = 0.75;  // hardcoded for 640x480 canvas size (480/640)
    out.pos = vec4<f32>(position.x * xy_ratio, position.y, 0.0, 1.0);
    out.color = vec4<f32>(color, 1.0);
    return out;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    let physical_color = pow(in.color.rgb, vec3<f32>(2.2));  // gamma correct
    return vec4<f32>(physical_color, in.color.a);
}
"""
