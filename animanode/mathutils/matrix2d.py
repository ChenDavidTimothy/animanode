"""
2D transformation matrices for AnimaNode
Inspired by three/mathutils/MatrixFactory.py but simplified for 2D only
"""

import math

from .vector2 import Vector2


class Matrix2D:
    """
    2D transformation matrix (3x3 for homogeneous coordinates)
    Following three/mathutils/MatrixFactory.py patterns but 2D only
    """

    def __init__(self, values: list[float] = None):
        """Initialize matrix - row-major order"""
        if values is None:
            # Identity matrix
            self.m = [1, 0, 0, 0, 1, 0, 0, 0, 1]
        else:
            if len(values) != 9:
                raise ValueError("Matrix2D requires 9 values")
            self.m = list(values)

    def __mul__(self, other: "Matrix2D") -> "Matrix2D":
        """Matrix multiplication"""
        result = [0] * 9
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    result[i * 3 + j] += self.m[i * 3 + k] * other.m[k * 3 + j]
        return Matrix2D(result)

    def transform_point(self, point: Vector2) -> Vector2:
        """Transform a 2D point using this matrix"""
        x = self.m[0] * point.x + self.m[1] * point.y + self.m[2]
        y = self.m[3] * point.x + self.m[4] * point.y + self.m[5]
        return Vector2(x, y)

    def to_list(self) -> list[float]:
        """Convert to list for shader uniforms"""
        return self.m.copy()

    def __repr__(self) -> str:
        return f"Matrix2D({self.m})"


class Matrix2DFactory:
    """
    Factory for creating 2D transformation matrices
    Following three/mathutils/MatrixFactory.py patterns
    """

    @staticmethod
    def identity() -> Matrix2D:
        """Create identity matrix"""
        return Matrix2D()

    @staticmethod
    def translation(x: float, y: float) -> Matrix2D:
        """Create translation matrix"""
        return Matrix2D([1, 0, x, 0, 1, y, 0, 0, 1])

    @staticmethod
    def rotation(angle: float) -> Matrix2D:
        """Create rotation matrix (angle in radians)"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Matrix2D([cos_a, -sin_a, 0, sin_a, cos_a, 0, 0, 0, 1])

    @staticmethod
    def scale(sx: float, sy: float = None) -> Matrix2D:
        """Create scale matrix"""
        if sy is None:
            sy = sx  # Uniform scaling
        return Matrix2D([sx, 0, 0, 0, sy, 0, 0, 0, 1])

    @staticmethod
    def combine(*matrices: Matrix2D) -> Matrix2D:
        """
        Combine multiple transformation matrices
        Order: matrices are applied right-to-left (like matrix multiplication)
        """
        if not matrices:
            return Matrix2DFactory.identity()

        result = matrices[0]
        for matrix in matrices[1:]:
            result = result * matrix
        return result
