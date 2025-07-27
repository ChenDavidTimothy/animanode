"""
AnimaNode - Parametric 2D WebGPU geometry rendering library

Inspired by three directory's mathematical philosophy with proper module separation:
- mathutils/ - Pure mathematical utilities (Vector2, Matrix2D)
- transform/ - Transformation system using mathutils
- geometry/ - Parametric geometries with transforms
- scene.py - High-level scene management

Example usage:
    from animanode import Circle, Rectangle, Triangle, Scene

    # Create parametric geometries with mathematical parameters
    circle = Circle(radius=0.7, segments=32)      # High-resolution circle
    rect = Rectangle(width=0.8, height=0.6)       # Custom rectangle
    tri = Triangle(size=1.2, rotation=0.5)        # Scaled and rotated triangle

    # Apply transformations (using mathutils and transform modules)
    circle.translate(0.2, 0.1).rotate(0.5)

    # Simple scene rendering
    scene = Scene()
    scene.add(circle)
    scene.draw("output.mp4")  # Automatically creates video
"""

from . import mathutils, transform
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
    "mathutils",
    "transform",
]

# Version info following semantic versioning
VERSION_INFO = {"major": 1, "minor": 0, "patch": 0, "stage": "stable"}
