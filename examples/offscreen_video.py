from pathlib import Path

import imageio.v3 as iio
import numpy as np
from rendercanvas.offscreen import RenderCanvas

from animanode.cube import setup_drawing_sync


def create_video(
    output_path: str,
    width: int = 1280,
    height: int = 960,
    fps: int = 60,
    duration: float = 5.0,
    quality: int = 9,
) -> str:
    # Validate FFmpeg backend
    try:
        test_frame = [np.zeros((16, 16, 3), dtype=np.uint8)]
        iio.imwrite("test.mp4", test_frame, fps=1)
        Path("test.mp4").unlink(missing_ok=True)
    except Exception as e:
        raise RuntimeError(
            f"FFmpeg not available. Install: pip install imageio[ffmpeg]. Error: {e}"
        ) from e

    # Setup rendering
    total_frames = int(fps * duration)
    canvas = RenderCanvas(size=(width, height))
    draw_frame = setup_drawing_sync(canvas)

    print(f"Rendering {total_frames} frames at {width}x{height}...")

    # Render frames
    frames = []
    for i in range(total_frames):
        canvas.request_draw(draw_frame)
        frame = np.asarray(canvas.draw())

        # Convert to RGB uint8
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

    # Write video
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    print(f"Encoding video: {output_path}")

    iio.imwrite(
        output_path, frames, fps=fps, codec="libx264", quality=quality, pixelformat="yuv420p"
    )

    file_size = Path(output_path).stat().st_size / (1024 * 1024)
    print(f"Video saved: {output_path} ({file_size:.1f}MB)")

    return output_path


if __name__ == "__main__":
    # Create HD video with perfect cube proportions
    create_video("cube.mp4", width=1280, height=960, fps=60, duration=5.0, quality=9)
