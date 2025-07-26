"""
Animanode - WebGPU 3D geometry rendering library

Inspired by three.js geometry system but built for pure WebGPU performance.
Compatible with offscreen video rendering.
"""

# Keep original cube functionality for compatibility
from .cube import setup_drawing_async, setup_drawing_sync
from .geometry import (
    SurfaceGeometry,
    WGPUBoxGeometry,
    WGPUCircleGeometry,
    WGPUConeGeometry,
    WGPUCurveGeometry,
    WGPUCylinderGeometry,
    WGPUGeometry,
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
)
from .rendering import (
    setup_geometry_drawing_async,
    setup_geometry_drawing_sync,
)


__version__ = "1.0.0"

__all__ = [
    # Base classes
    "SurfaceGeometry",
    # All geometries from three.js conversion
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
    # Legacy cube support
    "setup_drawing_async",
    "setup_drawing_sync",
    # Rendering
    "setup_geometry_drawing_async",
    "setup_geometry_drawing_sync",
]
