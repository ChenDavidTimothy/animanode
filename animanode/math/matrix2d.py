import math

import numpy as np


class Matrix2D:
    """2D transformation matrix using 3x3 homogeneous coordinates for translation support"""

    def __init__(self):
        self.matrix = np.array(
            [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]], dtype=np.float32
        )

    @staticmethod
    def identity():
        """Create identity matrix"""
        return Matrix2D()

    @staticmethod
    def translation(x, y):
        """Create translation matrix"""
        m = Matrix2D()
        m.matrix[0, 2] = x
        m.matrix[1, 2] = y
        return m

    @staticmethod
    def rotation(angle_radians):
        """Create rotation matrix"""
        m = Matrix2D()
        cos_a = math.cos(angle_radians)
        sin_a = math.sin(angle_radians)
        m.matrix[0, 0] = cos_a
        m.matrix[0, 1] = -sin_a
        m.matrix[1, 0] = sin_a
        m.matrix[1, 1] = cos_a
        return m

    @staticmethod
    def scale(sx, sy):
        """Create scale matrix"""
        m = Matrix2D()
        m.matrix[0, 0] = sx
        m.matrix[1, 1] = sy
        return m

    def multiply(self, other):
        """Multiply this matrix with another"""
        result = Matrix2D()
        result.matrix = self.matrix @ other.matrix
        return result

    def translate(self, x, y):
        """Apply translation"""
        translation_matrix = Matrix2D.translation(x, y)
        self.matrix = translation_matrix.matrix @ self.matrix

    def rotate(self, angle_radians):
        """Apply rotation"""
        rotation_matrix = Matrix2D.rotation(angle_radians)
        self.matrix = rotation_matrix.matrix @ self.matrix

    def scale_by(self, sx, sy):
        """Apply scaling"""
        scale_matrix = Matrix2D.scale(sx, sy)
        self.matrix = scale_matrix.matrix @ self.matrix

    def to_uniform_data(self):
        """Convert to format suitable for GPU uniform buffer (flatten to 9 floats)"""
        return self.matrix.flatten().astype(np.float32)
