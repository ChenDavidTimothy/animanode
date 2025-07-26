# animanode - 2D Node-based Animation System using WebGPU

from .core.canvas import Canvas
from .core.renderer import Renderer2D
from .export.video import VideoExporter
from .geometry.circle import CircleNode
from .geometry.rectangle import RectangleNode
from .geometry.triangle import TriangleNode
from .material.basic import Basic2DMaterial
from .math.matrix2d import Matrix2D
from .transform.transform import Transform2DNode


__version__ = "0.1.0"
__all__ = [
    # Core
    "Canvas",
    "Renderer2D",
    # Geometry
    "TriangleNode",
    "RectangleNode",
    "CircleNode",
    # Transform
    "Transform2DNode",
    # Material
    "Basic2DMaterial",
    # Math
    "Matrix2D",
    # Export
    "VideoExporter",
]
