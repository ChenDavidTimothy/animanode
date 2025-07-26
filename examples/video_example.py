"""
Example showing how to use animanode geometries with offscreen video rendering.

This demonstrates the integration with the offscreen_video.py workflow using
different geometries instead of the hardcoded cube.
"""

from pathlib import Path

import imageio.v3 as iio
import numpy as np
from rendercanvas.offscreen import RenderCanvas

# Import animanode geometries and rendering
from animanode import (
    WGPUBoxGeometry,
    WGPUConeGeometry,
    WGPUCylinderGeometry,
    WGPUPlaneGeometry,
    WGPUSphereGeometry,
    setup_geometry_drawing_sync,
)


def create_geometry_video(
    geometry_type: str = "sphere",
    output_path: str = "geometry_video.mp4",
    video_width: int = 1280,
    video_height: int = 960,
    fps: int = 60,
    duration: float = 5.0,
    quality: int = 9,
    **geometry_kwargs,
) -> str:
    """
    Create a video with any animanode geometry

    Args:
        geometry_type: Type of geometry ("sphere", "box", "cylinder", "cone", "plane")
        output_path: Output video file path
        video_width: Video width in pixels
        video_height: Video height in pixels
        fps: Frames per second
        duration: Video duration in seconds
        quality: Video quality (1-10, higher is better)
        **geometry_kwargs: Additional arguments for geometry constructor

    Returns:
        Path to created video file
    """
    # Validate FFmpeg backend - Evidence from offscreen_video.py
    try:
        test_frame = [np.zeros((16, 16, 3), dtype=np.uint8)]
        iio.imwrite("test.mp4", test_frame, fps=1)
        Path("test.mp4").unlink(missing_ok=True)
    except Exception as e:
        raise RuntimeError(
            f"FFmpeg not available. Install: pip install imageio[ffmpeg]. Error: {e}"
        ) from e

    # Create geometry based on type
    geometry_map = {
        "sphere": WGPUSphereGeometry,
        "box": WGPUBoxGeometry,
        "cylinder": WGPUCylinderGeometry,
        "cone": WGPUConeGeometry,
        "plane": WGPUPlaneGeometry,
    }

    if geometry_type not in geometry_map:
        raise ValueError(
            f"Unknown geometry type: {geometry_type}. Available: {list(geometry_map.keys())}"
        )

    geometry_class = geometry_map[geometry_type]
    geometry = geometry_class(**geometry_kwargs)

    # Setup rendering - Evidence from offscreen_video.py pattern
    total_frames = int(fps * duration)
    canvas = RenderCanvas(size=(video_width, video_height))

    # KEY DIFFERENCE: Use setup_geometry_drawing_sync instead of setup_drawing_sync
    draw_frame = setup_geometry_drawing_sync(canvas, geometry)

    print(f"Rendering {total_frames} frames of {geometry_type} at {video_width}x{video_height}...")

    # Render frames - Evidence from offscreen_video.py workflow
    frames = []
    for i in range(total_frames):
        canvas.request_draw(draw_frame)
        frame = np.asarray(canvas.draw())

        # Convert to RGB uint8 - Evidence from offscreen_video.py
        if frame.shape[2] == 4:  # RGBA -> RGB
            frame = frame[:, :, :3]
        if frame.dtype != np.uint8:
            frame = np.clip(frame, 0, 1) if frame.dtype.kind == "f" else frame
            frame = (
                (frame * 255).astype(np.uint8)
                if frame.dtype.kind == "f"
                else frame.astype(np.uint8)
            )

        frames.append(frame)

        if (i + 1) % (total_frames // 10) == 0:
            print(f"Progress: {i + 1}/{total_frames}")

    # Write video - Evidence from offscreen_video.py
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    print(f"Encoding video: {output_path}")

    iio.imwrite(
        output_path, frames, fps=fps, codec="libx264", quality=quality, pixelformat="yuv420p"
    )

    file_size = Path(output_path).stat().st_size / (1024 * 1024)
    print(f"Video saved: {output_path} ({file_size:.1f}MB)")

    return output_path


if __name__ == "__main__":
    # Example usage - create videos with different geometries

    # Sphere video
    create_geometry_video(
        geometry_type="sphere",
        output_path="sphere.mp4",
        video_width=1280,
        video_height=960,
        duration=5.0,
        radius=1.0,
        width_segments=32,
        height_segments=16,
    )

    # Box video
    create_geometry_video(
        geometry_type="box",
        output_path="box.mp4",
        video_width=1280,
        video_height=960,
        duration=5.0,
        width=2.0,
        height=2.0,
        depth=2.0,
    )

    # Cylinder video
    create_geometry_video(
        geometry_type="cylinder",
        output_path="cylinder.mp4",
        video_width=1280,
        video_height=960,
        duration=5.0,
        radius_top=1.0,
        radius_bottom=1.0,
        height=2.0,
        radial_segments=32,
    )

    # Cone video
    create_geometry_video(
        geometry_type="cone",
        output_path="cone.mp4",
        video_width=1280,
        video_height=960,
        duration=5.0,
        radius=1.0,
        height=2.0,
        radial_segments=32,
    )

    print("All geometry videos created successfully!")
