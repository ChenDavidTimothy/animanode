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
    WGPUConeGeometry,
    WGPUCylinderGeometry,
    WGPUGeometry,
    WGPUPlaneGeometry,
    WGPUSphereGeometry,
)
from .rendering import (
    setup_geometry_drawing_async,
    setup_geometry_drawing_sync,
)


__version__ = "1.0.0"

__all__ = [
    "SurfaceGeometry",
    "WGPUBoxGeometry",
    "WGPUConeGeometry",
    "WGPUCylinderGeometry",
    # Geometries
    "WGPUGeometry",
    "WGPUPlaneGeometry",
    "WGPUSphereGeometry",
    "setup_drawing_async",
    # Legacy cube support
    "setup_drawing_sync",
    "setup_geometry_drawing_async",
    # Rendering
    "setup_geometry_drawing_sync",
]
