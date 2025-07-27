"""
Scene class for AnimaNode - hides video creation complexity
Prepares architecture for future transform methods
"""

import imageio.v3 as iio
import numpy as np
from rendercanvas.offscreen import RenderCanvas

from .renderer import Renderer


class Scene:
    """
    Scene manages geometries and automatically creates videos
    Users just call scene.draw() - no programming knowledge needed
    """

    def __init__(self):
        self.geometries = []

    def add(self, geometry_or_list):
        """Add geometry or list of geometries to scene"""
        if isinstance(geometry_or_list, list):
            self.geometries.extend(geometry_or_list)
        else:
            self.geometries.append(geometry_or_list)

    def draw(self, filename="output.mp4"):
        """
        Automatically create video - hides all complexity
        User doesn't need to understand for loops or video creation
        """
        if not self.geometries:
            print("No geometries in scene")
            return

        # For now, render first geometry (multi-geometry coming later)
        geometry = self.geometries[0]

        # Internal video creation - user doesn't see this complexity
        canvas = RenderCanvas(size=(640, 480))
        draw_frame = Renderer.setup_drawing_sync(canvas, geometry)

        print("Creating video...")

        # Hidden complexity - user doesn't need to understand
        video_frames = []
        for i in range(150):
            canvas.request_draw(draw_frame)
            frame = np.asarray(canvas.draw())[:, :, :3]

            if frame.dtype != np.uint8:
                frame = (np.clip(frame, 0, 1) * 255).astype(np.uint8)

            video_frames.append(frame)

        iio.imwrite(filename, video_frames, fps=30)
        print(f"Video saved: {filename}")
