"""
Parametric 2D geometry base class for AnimaNode
Inspired by three directory's mathematical approach with radical simplicity for 2D
"""

from abc import ABC, abstractmethod
from typing import Any


class ParametricGeometry(ABC):
    """
    Base class for parametric 2D geometries following three directory philosophy:
    - Mathematical parameterization over hardcoding
    - Resolution control through parameters
    - Uniform buffer pattern for GPU parameters
    - Architecture prepared for transform methods
    """

    def __init__(self, parameters: dict[str, Any]):
        """
        Initialize parametric geometry with mathematical parameters

        Args:
            parameters: Dictionary of mathematical parameters (radius, width, segments, etc.)
        """
        self.parameters = parameters
        # Transform state - architecture for future transform methods
        self._transforms = {"translate": [0.0, 0.0], "rotate": 0.0, "scale": [1.0, 1.0]}
        self.vertex_count = self._calculate_vertex_count()
        self.shader_source = self._generate_shader()
        self._uniform_data = self._pack_uniform_data()

    @abstractmethod
    def _calculate_vertex_count(self) -> int:
        """
        Calculate vertex count based on mathematical parameters

        Returns:
            Number of vertices needed for procedural generation
        """
        pass

    @abstractmethod
    def _generate_shader(self) -> str:
        """
        Generate WGSL shader with parametric mathematical functions

        Returns:
            Complete WGSL shader source code
        """
        pass

    @abstractmethod
    def _pack_uniform_data(self) -> bytes:
        """
        Pack parameters into uniform buffer data

        Returns:
            Binary data for GPU uniform buffer (16-byte aligned)
        """
        pass

    def get_uniform_data(self) -> bytes:
        """
        Get packed uniform buffer data

        Returns:
            Binary uniform data ready for GPU upload
        """
        return self._uniform_data

    def get_uniform_size(self) -> int:
        """
        Get size of uniform buffer in bytes

        Returns:
            Size in bytes (always 16-byte aligned)
        """
        return len(self._uniform_data)

    def update_parameter(self, name: str, value: Any) -> None:
        """
        Update a single parameter and regenerate dependent data

        Args:
            name: Parameter name
            value: New parameter value
        """
        if name not in self.parameters:
            raise ValueError(f"Parameter '{name}' not found in geometry")

        self.parameters[name] = value
        self.vertex_count = self._calculate_vertex_count()
        self.shader_source = self._generate_shader()
        self._uniform_data = self._pack_uniform_data()

    # Transform methods - architecture prepared for future implementation
    def translate(self, x: float, y: float):
        """Transform method - to be implemented"""
        # Architecture prepared - implementation coming later
        raise NotImplementedError("Transform methods coming in future version")

    def rotate(self, angle: float):
        """Transform method - to be implemented"""
        # Architecture prepared - implementation coming later
        raise NotImplementedError("Transform methods coming in future version")

    def scale(self, x: float, y: float = None):
        """Transform method - to be implemented"""
        # Architecture prepared - implementation coming later
        raise NotImplementedError("Transform methods coming in future version")


class GeometryParameters:
    """
    Type-safe parameter validation for geometries
    Following three directory's validation patterns
    """

    @staticmethod
    def validate_positive_float(value: float, name: str) -> float:
        """Validate positive float parameter"""
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f"{name} must be a positive number, got {value}")
        return float(value)

    @staticmethod
    def validate_positive_int(value: int, name: str) -> int:
        """Validate positive integer parameter"""
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f"{name} must be a positive integer, got {value}")
        return value

    @staticmethod
    def validate_min_segments(segments: int, minimum: int = 3) -> int:
        """Validate minimum segment count for valid geometry"""
        segments = GeometryParameters.validate_positive_int(segments, "segments")
        if segments < minimum:
            raise ValueError(f"segments must be at least {minimum}, got {segments}")
        return segments
