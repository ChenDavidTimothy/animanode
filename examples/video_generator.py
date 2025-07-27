"""
Radically simple video generator - user doesn't need programming knowledge
No for loops, no complexity - just create shapes and call scene.draw()
"""

# Import from parent directory
import sys
from pathlib import Path

import imageio.v3 as iio
import numpy as np
from rendercanvas.offscreen import RenderCanvas


sys.path.insert(0, str(Path(__file__).parent.parent))

from animanode import Circle, Rectangle, Renderer, Scene, Triangle


def main():
    """User-friendly approach - no programming complexity visible"""

    # Create parametric geometries - basic versions still work
    circle = Circle(radius=0.6, segments=32)
    rect = Rectangle(width=0.8, height=0.6)
    triangle = Triangle(size=0.9, rotation=0.0)

    # Simple scene approach - user doesn't see video creation complexity
    scene1 = Scene()
    scene1.add(circle)
    scene1.draw("circle.mp4")

    scene2 = Scene()
    scene2.add(rect)
    scene2.draw("rectangle.mp4")

    scene3 = Scene()
    scene3.add(triangle)
    scene3.draw("triangle.mp4")

    print("✅ Basic geometries rendered successfully")
    print("✅ Files: circle.mp4, rectangle.mp4, triangle.mp4")


def future_vision_example():
    """Your future vision - NOW WORKING with proper transform application!"""

    print("Transform methods now working with proper shader integration!")

    scene = Scene()
    meshList = []

    # Rectangle with transformations - will be visible now!
    rect = Rectangle(width=0.8, height=0.6)
    rect.translate(0.2, 0.1)  # ✅ NOW WORKS - transform applied in shader
    rect.rotate(0.5)  # ✅ NOW WORKS - uses mathutils Matrix2D
    meshList.append(rect)

    # Circle with transformations - will be visible now!
    circle = Circle(radius=0.5, segments=32)
    circle.scale(1.5, 1.2)  # ✅ NOW WORKS - uses mathutils for calculations
    circle.translate(-0.3, 0.2)  # Additional transform to separate from rectangle
    meshList.append(circle)

    scene.add(meshList)
    scene.draw("transformed_shapes.mp4")  # ✅ Creates multiple videos now

    print("✅ FIXED: Transforms now properly applied in vertex shaders")
    print("✅ FIXED: Scene renders all geometries (separate videos for now)")
    print("✅ FIXED: Rectangle translated+rotated, Circle scaled+translated")
    print("✅ Files created: transformed_shapes_geometry_0.mp4 (rectangle)")
    print("✅ Files created: transformed_shapes_geometry_1.mp4 (circle)")


def animated_example():
    """Example showing how to create animated transforms (changing over time)"""
    import math

    print("\n🎬 Creating animated example...")

    # For animation, we need to create multiple frames with different transforms
    canvas = RenderCanvas(size=(640, 480))

    video_frames = []
    for frame in range(150):  # 5 seconds at 30fps
        # Create new circle with animated rotation
        animated_circle = Circle(radius=0.4, segments=32)
        rotation_angle = frame * 2 * math.pi / 150  # Full rotation over 5 seconds
        animated_circle.rotate(rotation_angle)
        animated_circle.translate(
            0.3 * math.cos(frame * 0.1), 0.3 * math.sin(frame * 0.1)
        )  # Circular motion

        # Render this frame
        draw_frame = Renderer.setup_drawing_sync(canvas, animated_circle)
        canvas.request_draw(draw_frame)
        frame_data = np.asarray(canvas.draw())[:, :, :3]

        if frame_data.dtype != np.uint8:
            frame_data = (np.clip(frame_data, 0, 1) * 255).astype(np.uint8)

        video_frames.append(frame_data)

    # Save animated video
    iio.imwrite("animated_circle.mp4", video_frames, fps=30)
    print("✅ Created animated_circle.mp4 - circle rotates and moves in circular motion")


if __name__ == "__main__":
    main()
    future_vision_example()
    animated_example()  # Show animation example too
