"""
Rectangle geometry definition
"""


class Rectangle:
    vertex_count = 6  # 2 triangles * 3 vertices each

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
