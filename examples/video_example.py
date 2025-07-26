"""
Example showing how to use all animanode geometries with offscreen video rendering.

This demonstrates the complete set of geometries converted from three.js,
showcasing the full compatibility with the video rendering pipeline.
"""

from pathlib import Path

import imageio.v3 as iio
import numpy as np
from rendercanvas.offscreen import RenderCanvas

# Import all animanode geometries and rendering
from animanode import (
    WGPUBoxGeometry,
    WGPUCircleGeometry,
    WGPUConeGeometry,
    WGPUCurveGeometry,
    WGPUCylinderGeometry,
    WGPUIcosahedronGeometry,
    WGPULineGeometry,
    WGPUOctahedronGeometry,
    WGPUPlaneGeometry,
    WGPUPointGeometry,
    WGPUPolygonGeometry,
    WGPUPrismGeometry,
    WGPUPyramidGeometry,
    WGPURingGeometry,
    WGPUSphereGeometry,
    WGPUTorusGeometry,
    WGPUTubeGeometry,
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
        geometry_type: Type of geometry (see geometry_map below for all options)
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

    # Complete geometry map with all converted geometries
    geometry_map = {
        # Basic shapes
        "box": WGPUBoxGeometry,
        "sphere": WGPUSphereGeometry,
        "plane": WGPUPlaneGeometry,
        "cylinder": WGPUCylinderGeometry,
        "cone": WGPUConeGeometry,
        # Platonic solids
        "icosahedron": WGPUIcosahedronGeometry,
        "octahedron": WGPUOctahedronGeometry,
        # Polygonal shapes
        "circle": WGPUCircleGeometry,
        "ring": WGPURingGeometry,
        "polygon": WGPUPolygonGeometry,
        # Advanced shapes
        "torus": WGPUTorusGeometry,
        "pyramid": WGPUPyramidGeometry,
        "prism": WGPUPrismGeometry,
        # Curve-based shapes
        "line": WGPULineGeometry,
        "curve": WGPUCurveGeometry,
        "tube": WGPUTubeGeometry,
        # Point cloud
        "point": WGPUPointGeometry,
    }

    if geometry_type not in geometry_map:
        raise ValueError(
            f"Unknown geometry type: {geometry_type}. Available: {list(geometry_map.keys())}"
        )

    # Create geometry with provided kwargs
    geometry_class = geometry_map[geometry_type]

    # Handle special cases that need specific data
    if geometry_type == "point":
        if "positions" not in geometry_kwargs:
            # Create a simple point cloud if no positions provided
            geometry_kwargs["positions"] = [
                [0, 0, 0],
                [1, 0, 0],
                [0, 1, 0],
                [0, 0, 1],
                [-1, 0, 0],
                [0, -1, 0],
                [0, 0, -1],
            ]
        geometry = geometry_class(**geometry_kwargs)
    elif geometry_type == "line":
        if "positions" not in geometry_kwargs:
            # Create a simple line if no positions provided
            import math

            geometry_kwargs["positions"] = [
                [math.cos(i * 0.1), math.sin(i * 0.1), i * 0.1] for i in range(20)
            ]
        geometry = geometry_class(**geometry_kwargs)
    elif geometry_type == "curve":
        if "curve_function" not in geometry_kwargs and "positions" not in geometry_kwargs:
            # Create a helix curve by default
            geometry = WGPUCurveGeometry.create_helix_curve()
        else:
            geometry = geometry_class(**geometry_kwargs)
    elif geometry_type == "tube":
        if "curve_function" not in geometry_kwargs:
            # Create a helix curve for the tube
            import math

            def helix_curve(t):
                return [math.cos(t * 4 * math.pi), t * 2 - 1, math.sin(t * 4 * math.pi)]

            geometry_kwargs["curve_function"] = helix_curve
        geometry = geometry_class(**geometry_kwargs)
    else:
        # Standard geometry creation
        geometry = geometry_class(**geometry_kwargs)

    # Setup rendering - Evidence from offscreen_video.py pattern
    total_frames = int(fps * duration)
    canvas = RenderCanvas(size=(video_width, video_height))

    # Use geometry-specific rendering function
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


def create_all_geometry_videos():
    """Create videos showcasing all available geometries"""

    # Focus on geometries that work well with triangle-based rendering
    geometry_demos = [
        # Basic shapes - PROVEN to work
        ("sphere", {"radius": 1.0, "width_segments": 32, "height_segments": 16}),
        ("box", {"width": 2.0, "height": 2.0, "depth": 2.0}),
        ("plane", {"width": 2.0, "height": 2.0, "width_segments": 10, "height_segments": 10}),
        (
            "cylinder",
            {"radius_top": 1.0, "radius_bottom": 1.0, "height": 2.0, "radial_segments": 32},
        ),
        ("cone", {"radius": 1.0, "height": 2.0, "radial_segments": 32}),
        # Platonic solids
        ("icosahedron", {"radius": 1.0}),
        ("octahedron", {"radius": 1.0}),
        # Polygonal shapes
        ("circle", {"radius": 1.0, "segments": 32}),
        ("ring", {"inner_radius": 0.5, "outer_radius": 1.0, "segments": 32}),
        ("polygon", {"radius": 1.0, "number_sides": 6}),
        # Advanced shapes
        (
            "torus",
            {
                "central_radius": 0.6,
                "tube_radius": 0.4,
                "tubular_segments": 32,
                "radial_segments": 16,
            },
        ),
        ("pyramid", {"radius": 1.0, "number_sides": 4, "height": 2.0}),
        ("prism", {"radius": 1.0, "number_sides": 6, "height": 2.0}),
        # Curve-based shapes
        ("tube", {}),  # Will use default helix curve
        # NOTE: Point and Line geometries require different rendering primitives
        # and may not work with the current triangle-based rendering system
    ]

    print("Creating videos for all triangle-based geometry types...")

    for geometry_type, kwargs in geometry_demos:
        try:
            output_path = f"videos/{geometry_type}.mp4"
            create_geometry_video(
                geometry_type=geometry_type,
                output_path=output_path,
                video_width=1280,
                video_height=960,
                duration=3.0,  # Shorter videos for demo
                fps=60,
                quality=9,
                **kwargs,
            )
            print(f"✓ Created {geometry_type} video")
        except Exception as e:
            print(f"✗ Failed to create {geometry_type} video: {e}")

    print("All geometry videos completed!")


def create_experimental_geometry_videos():
    """Create videos for geometries that may need different rendering (points, lines, curves)"""

    experimental_geometries = [
        ("curve", {}),  # Will use default helix
        ("point", {}),  # Will use default point positions
        ("line", {}),  # Will use default line positions
    ]

    print("Creating experimental geometry videos...")
    print("NOTE: These may not render correctly with triangle-based rendering")

    for geometry_type, kwargs in experimental_geometries:
        try:
            output_path = f"videos/experimental_{geometry_type}.mp4"
            create_geometry_video(
                geometry_type=geometry_type,
                output_path=output_path,
                video_width=1280,
                video_height=960,
                duration=3.0,
                fps=60,
                quality=9,
                **kwargs,
            )
            print(f"✓ Created experimental {geometry_type} video")
        except Exception as e:
            print(f"✗ Failed to create experimental {geometry_type} video: {e}")

    print("Experimental geometry videos completed!")


if __name__ == "__main__":
    # Create videos for all triangle-based geometries (recommended)
    create_all_geometry_videos()

    # Uncomment to also try experimental geometries (points, lines, curves)
    # create_experimental_geometry_videos()

    # Single geometry demo (optional - uncomment if you want just one)
    # create_geometry_video(
    #     geometry_type="torus",
    #     output_path="torus_demo.mp4",
    #     video_width=1280,
    #     video_height=960,
    #     duration=5.0,
    #     central_radius=0.8,
    #     tube_radius=0.3,
    #     tubular_segments=64,
    #     radial_segments=32,
    # )

    print("All geometry video examples completed!")
