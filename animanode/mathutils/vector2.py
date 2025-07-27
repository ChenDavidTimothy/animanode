"""
Pure 2D vector mathematics for AnimaNode
Following three/mathutils pattern - only pure math, no rendering logic
"""

import math


class Vector2:
    """
    2D vector with mathematical operations
    Inspired by three/mathutils but radically simplified for 2D only
    """

    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other: "Vector2") -> "Vector2":
        """Vector addition"""
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2") -> "Vector2":
        """Vector subtraction"""
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector2":
        """Scalar multiplication"""
        return Vector2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> "Vector2":
        """Reverse scalar multiplication"""
        return self.__mul__(scalar)

    def length(self) -> float:
        """Calculate vector magnitude"""
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalize(self) -> "Vector2":
        """Return normalized vector (unit vector)"""
        length = self.length()
        if length == 0:
            return Vector2(0, 0)
        return Vector2(self.x / length, self.y / length)

    def dot(self, other: "Vector2") -> float:
        """Dot product"""
        return self.x * other.x + self.y * other.y

    def to_list(self) -> list[float]:
        """Convert to list [x, y]"""
        return [self.x, self.y]

    def to_tuple(self) -> tuple[float, float]:
        """Convert to tuple (x, y)"""
        return (self.x, self.y)

    def __repr__(self) -> str:
        return f"Vector2({self.x}, {self.y})"


class Vector2Utils:
    """
    Pure mathematical utility functions for 2D vectors
    Following three/mathutils pattern - static methods for common operations
    """

    @staticmethod
    def distance(v1: Vector2, v2: Vector2) -> float:
        """Calculate distance between two vectors"""
        return (v2 - v1).length()

    @staticmethod
    def lerp(v1: Vector2, v2: Vector2, t: float) -> Vector2:
        """Linear interpolation between two vectors"""
        return v1 + (v2 - v1) * t

    @staticmethod
    def angle_between(v1: Vector2, v2: Vector2) -> float:
        """Calculate angle between two vectors in radians"""
        dot = v1.normalize().dot(v2.normalize())
        # Clamp to avoid floating point errors
        dot = max(-1.0, min(1.0, dot))
        return math.acos(dot)

    @staticmethod
    def rotate(vector: Vector2, angle: float) -> Vector2:
        """Rotate vector by angle (radians) around origin"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Vector2(vector.x * cos_a - vector.y * sin_a, vector.x * sin_a + vector.y * cos_a)

    @staticmethod
    def from_polar(radius: float, angle: float) -> Vector2:
        """Create vector from polar coordinates"""
        return Vector2(radius * math.cos(angle), radius * math.sin(angle))
