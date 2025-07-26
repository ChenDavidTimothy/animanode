from collections.abc import Callable
from pathlib import Path

import imageio.v3 as iio
import numpy as np

from ..core.canvas import Canvas


class VideoExporter:
    """Export 2D animations to video files"""

    def __init__(self, canvas: Canvas):
        self.canvas = canvas

    def export_video(
        self,
        output_path: str,
        duration: float = 5.0,
        fps: int = 60,
        animation_func: Callable[[float], None] | None = None,
        quality: int = 9,
    ) -> str:
        """
        Export animation to video file

        Args:
            output_path: Output video file path
            duration: Video duration in seconds
            fps: Frames per second
            animation_func: Function called each frame with time parameter
            quality: Video quality (1-10, higher is better)

        Returns:
            Path to created video file
        """
        # Validate FFmpeg backend
        try:
            test_frame = [np.zeros((16, 16, 3), dtype=np.uint8)]
            test_path = "test_ffmpeg.mp4"
            iio.imwrite(test_path, test_frame, fps=1)
            Path(test_path).unlink(missing_ok=True)
        except Exception as e:
            raise RuntimeError(
                f"FFmpeg not available. Install: pip install imageio[ffmpeg]. Error: {e}"
            ) from e

        total_frames = int(fps * duration)
        width, height = self.canvas.get_size()

        print(f"Rendering {total_frames} frames at {width}x{height}...")

        # Render frames
        frames = []
        for frame_idx in range(total_frames):
            # Calculate current time
            current_time = frame_idx / fps

            # Call animation function if provided
            if animation_func:
                animation_func(current_time)

            # Render frame
            frame = self.canvas.render_frame()

            # Ensure frame is RGB uint8
            if frame.shape[2] == 4:  # RGBA -> RGB
                frame = frame[:, :, :3]
            if frame.dtype != np.uint8:
                frame = np.clip(frame, 0, 255).astype(np.uint8)

            frames.append(frame)

            # Progress logging
            if (frame_idx + 1) % max(1, total_frames // 10) == 0:
                print(f"Progress: {frame_idx + 1}/{total_frames}")

        # Write video
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        print(f"Encoding video: {output_path}")

        iio.imwrite(
            output_path, frames, fps=fps, codec="libx264", quality=quality, pixelformat="yuv420p"
        )

        file_size = Path(output_path).stat().st_size / (1024 * 1024)
        print(f"Video saved: {output_path} ({file_size:.1f}MB)")

        return output_path

    def export_frame_sequence(
        self,
        output_dir: str,
        duration: float = 5.0,
        fps: int = 60,
        animation_func: Callable[[float], None] | None = None,
        image_format: str = "png",
    ) -> list[str]:
        """
        Export animation as sequence of image files

        Args:
            output_dir: Directory to save images
            duration: Animation duration in seconds
            fps: Frames per second
            animation_func: Function called each frame with time parameter
            image_format: Image format (png, jpg, etc.)

        Returns:
            List of created image file paths
        """
        total_frames = int(fps * duration)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        width, height = self.canvas.get_size()
        print(f"Rendering {total_frames} frames at {width}x{height}...")

        created_files = []

        for frame_idx in range(total_frames):
            # Calculate current time
            current_time = frame_idx / fps

            # Call animation function if provided
            if animation_func:
                animation_func(current_time)

            # Render frame
            frame = self.canvas.render_frame()

            # Save frame
            frame_filename = f"frame_{frame_idx:06d}.{image_format}"
            frame_path = output_path / frame_filename

            # Convert to RGB if needed
            if frame.shape[2] == 4:  # RGBA -> RGB
                frame = frame[:, :, :3]

            iio.imwrite(str(frame_path), frame)
            created_files.append(str(frame_path))

            # Progress logging
            if (frame_idx + 1) % max(1, total_frames // 10) == 0:
                print(f"Progress: {frame_idx + 1}/{total_frames}")

        print(f"Frame sequence saved to: {output_dir}")
        return created_files
