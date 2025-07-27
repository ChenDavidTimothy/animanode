"""
AnimaNode - Parametric 2D WebGPU geometry rendering library

Inspired by three directory's mathematical philosophy:
- Parametric geometries over hardcoded values
- Mathematical functions for shape generation
- Configurable resolution and parameters
- Radical simplicity for 2D use cases

Example usage:
    from animanode import Circle, Rectangle, Triangle, Renderer
    from rendercanvas.auto import RenderCanvas, loop

    # Create parametric geometries with mathematical parameters
    circle = Circle(radius=0.7, segments=32)      # High-resolution circle
    rect = Rectangle(width=0.8, height=0.6)       # Custom rectangle
    tri = Triangle(size=1.2, rotation=0.5)        # Scaled and rotated triangle

    # Render with WebGPU
    canvas = RenderCanvas(size=(640, 480), title="Parametric AnimaNode")
    draw_frame = Renderer.setup_drawing_sync(canvas, circle)
    canvas.request_draw(draw_frame)
    loop.run()
"""

from .geometry import Circle, GeometryParameters, ParametricGeometry, Rectangle, Triangle
from .renderer import Renderer
from .scene import Scene


__version__ = "1.0.0"

__all__ = [
    "Circle",
    "GeometryParameters",
    "ParametricGeometry",
    "Rectangle",
    "Renderer",
    "Scene",
    "Triangle",
]

# Version info following semantic versioning
VERSION_INFO = {"major": 1, "minor": 0, "patch": 0, "stage": "stable"}
