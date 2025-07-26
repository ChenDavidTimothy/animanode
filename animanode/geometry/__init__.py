"""
Animanode Geometry Package - WebGPU geometries inspired by three.js
"""

from .base import SurfaceGeometry, WGPUGeometry
from .box import WGPUBoxGeometry
from .circle import WGPUCircleGeometry
from .curve import WGPUCurveGeometry
from .cylinder import WGPUConeGeometry, WGPUCylinderGeometry
from .icosahedron import WGPUIcosahedronGeometry
from .line import WGPULineGeometry
from .octahedron import WGPUOctahedronGeometry
from .plane import WGPUPlaneGeometry
from .point import WGPUPointGeometry
from .polygon import WGPUPolygonGeometry
from .prism import WGPUPrismGeometry
from .pyramid import WGPUPyramidGeometry
from .ring import WGPURingGeometry
from .sphere import WGPUSphereGeometry
from .torus import WGPUTorusGeometry
from .tube import WGPUTubeGeometry


__all__ = [
    # Base classes
    "SurfaceGeometry",
    # Basic geometries
    "WGPUBoxGeometry",
    "WGPUCircleGeometry",
    "WGPUConeGeometry",
    "WGPUCurveGeometry",
    "WGPUCylinderGeometry",
    "WGPUGeometry",
    "WGPUIcosahedronGeometry",
    "WGPULineGeometry",
    "WGPUOctahedronGeometry",
    "WGPUPlaneGeometry",
    "WGPUPointGeometry",
    "WGPUPolygonGeometry",
    "WGPUPrismGeometry",
    "WGPUPyramidGeometry",
    "WGPURingGeometry",
    "WGPUSphereGeometry",
    "WGPUTorusGeometry",
    "WGPUTubeGeometry",
]
