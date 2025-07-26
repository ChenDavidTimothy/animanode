"""
Basic shapes example demonstrating the animanode 2D node-based system.

This example shows how to:
1. Create geometry nodes (Triangle, Rectangle, Circle)
2. Apply transforms using Transform2DNode
3. Connect nodes together
4. Export to video

Usage:
  python examples/basic_shapes.py              # Export static video
  python examples/basic_shapes.py --animate    # Export animated video
"""

import math

import animanode as an


def create_static_scene():
    """Create a simple scene with three shapes"""

    # Create a canvas (1920x1080 with black background)
    canvas = an.Canvas(1920, 1080).set_background_color(0.0, 0.0, 0.2, 1.0)
    canvas.set_material_color(1.0, 0.5, 0.0, 1.0)  # Orange shapes

    # Create geometry nodes
    triangle = an.TriangleNode(width=0.3, height=0.3)
    rectangle = an.RectangleNode(width=0.4, height=0.2)
    circle = an.CircleNode(radius=0.15, segments=32)

    # Create transform nodes with input geometry (no explicit connections needed)
    triangle_transform = an.Transform2DNode(triangle).translate(-0.5, 0.3).rotate(45)
    rectangle_transform = an.Transform2DNode(rectangle).translate(0.0, 0.0).scale(1.2, 0.8)
    circle_transform = an.Transform2DNode(circle).translate(0.5, -0.3).scale(1.5)

    # Add root nodes to canvas
    canvas.add_node(triangle_transform)
    canvas.add_node(rectangle_transform)
    canvas.add_node(circle_transform)

    return canvas


def create_animated_scene():
    """Create an animated scene with rotating shapes"""

    canvas = an.Canvas(1920, 1080).set_background_color(0.1, 0.1, 0.2, 1.0)
    canvas.set_material_color(0.9, 0.3, 0.4, 1.0)  # Pink shapes

    # Create shapes
    triangle = an.TriangleNode(width=0.25, height=0.25)
    rectangle = an.RectangleNode(width=0.3, height=0.15)
    circle = an.CircleNode(radius=0.12)

    # Create transforms with input geometry
    triangle_transform = an.Transform2DNode(triangle).translate(-0.4, 0.3)
    rectangle_transform = an.Transform2DNode(rectangle).translate(0.0, 0.0)
    circle_transform = an.Transform2DNode(circle).translate(0.4, -0.3)

    # Add to canvas
    canvas.add_node(triangle_transform)
    canvas.add_node(rectangle_transform)
    canvas.add_node(circle_transform)

    def animate(time: float):
        """Animation function called each frame"""
        # Convert time to degrees
        angle = time * 90.0  # 90 degrees per second

        # Update transforms with animation
        triangle_transform.rotate(angle)
        rectangle_transform.rotate(-angle * 0.5)

        # Pulsating circle
        scale = 1.0 + 0.3 * math.sin(time * 4.0)
        circle_transform.rotate(angle * 1.5).scale(scale, scale)

    return canvas, animate


def main():
    """Run the examples"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--animate":
        # Create animated scene
        canvas, animate_func = create_animated_scene()
        exporter = an.VideoExporter(canvas)

        # Export animated video
        exporter.export_video(
            "output/animated_shapes.mp4",
            duration=5.0,
            fps=60,
            animation_func=animate_func,
            quality=9,
        )

    else:
        # Create static scene
        canvas = create_static_scene()
        exporter = an.VideoExporter(canvas)

        # Export static video (same frame repeated)
        exporter.export_video("output/static_shapes.mp4", duration=3.0, fps=30, quality=9)

    print("Video export complete!")


if __name__ == "__main__":
    main()
