"""
2D transformation system for AnimaNode geometries
Uses mathutils for pure mathematics - handles geometry transformations
"""

from ..mathutils import Matrix2D, Matrix2DFactory, Vector2


class Transform2D:
    """
    2D transformation state for geometries
    Uses mathutils for calculations - manages transformation state
    """

    def __init__(self):
        """Initialize with identity transformation"""
        self.translation = Vector2(0, 0)
        self.rotation = 0.0  # radians
        self.scale = Vector2(1, 1)
        self._matrix_dirty = True
        self._cached_matrix = None

    def translate(self, x: float, y: float) -> "Transform2D":
        """Apply translation"""
        self.translation = self.translation + Vector2(x, y)
        self._matrix_dirty = True
        return self

    def rotate(self, angle: float) -> "Transform2D":
        """Apply rotation (angle in radians)"""
        self.rotation += angle
        self._matrix_dirty = True
        return self

    def scale_by(self, sx: float, sy: float = None) -> "Transform2D":
        """Apply scaling"""
        if sy is None:
            sy = sx
        self.scale = Vector2(self.scale.x * sx, self.scale.y * sy)
        self._matrix_dirty = True
        return self

    def reset(self) -> "Transform2D":
        """Reset to identity transformation"""
        self.translation = Vector2(0, 0)
        self.rotation = 0.0
        self.scale = Vector2(1, 1)
        self._matrix_dirty = True
        return self

    def get_matrix(self) -> Matrix2D:
        """Get combined transformation matrix - uses mathutils for calculation"""
        if self._matrix_dirty or self._cached_matrix is None:
            # Build transformation matrix: Translation * Rotation * Scale (correct order)
            scale_matrix = Matrix2DFactory.scale(self.scale.x, self.scale.y)
            rotation_matrix = Matrix2DFactory.rotation(self.rotation)
            translation_matrix = Matrix2DFactory.translation(self.translation.x, self.translation.y)

            # Combine transformations in correct order: T * R * S
            self._cached_matrix = Matrix2DFactory.combine(
                translation_matrix, rotation_matrix, scale_matrix
            )
            self._matrix_dirty = False

        return self._cached_matrix

    def transform_point(self, point: Vector2) -> Vector2:
        """Transform a point using current transformation"""
        return self.get_matrix().transform_point(point)

    def get_uniform_data(self) -> list[float]:
        """Get transformation as uniform data for shaders"""
        matrix = self.get_matrix()
        # Return as list for uniform buffer
        return matrix.to_list()
