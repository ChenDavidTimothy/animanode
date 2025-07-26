import math

from ..core.node import GeometryNode, Node
from ..math.matrix2d import Matrix2D


class Transform2DNode(Node):
    """2D transformation node with translate, rotate, scale operations"""

    def __init__(self, input_node: Node | None = None, name: str = "Transform2D"):
        super().__init__(name)
        self.input_node = input_node
        self.transform = Matrix2D()
        self._translation = [0.0, 0.0]
        self._rotation = 0.0
        self._scale = [1.0, 1.0]

    def set_input(self, input_node: Node) -> "Transform2DNode":
        """Set the input node and return self for chaining"""
        self.input_node = input_node
        self.mark_dirty()
        return self

    def translate(self, x: float, y: float) -> "Transform2DNode":
        """Set translation and return self for chaining"""
        self._translation = [x, y]
        self._update_transform()
        return self

    def rotate(self, angle_degrees: float) -> "Transform2DNode":
        """Set rotation in degrees and return self for chaining"""
        self._rotation = math.radians(angle_degrees)
        self._update_transform()
        return self

    def rotate_radians(self, angle_radians: float) -> "Transform2DNode":
        """Set rotation in radians and return self for chaining"""
        self._rotation = angle_radians
        self._update_transform()
        return self

    def scale(self, sx: float, sy: float = None) -> "Transform2DNode":
        """Set scale and return self for chaining. If sy is None, uses sx for uniform scaling"""
        if sy is None:
            sy = sx
        self._scale = [sx, sy]
        self._update_transform()
        return self

    def reset(self) -> "Transform2DNode":
        """Reset to identity transform and return self for chaining"""
        self._translation = [0.0, 0.0]
        self._rotation = 0.0
        self._scale = [1.0, 1.0]
        self._update_transform()
        return self

    def _update_transform(self) -> None:
        """Rebuild the transformation matrix from current values"""
        # Apply transformations in order: Scale -> Rotate -> Translate
        # This is the standard 2D transformation order

        # Start with identity
        self.transform = Matrix2D()

        # Apply scale
        if self._scale != [1.0, 1.0]:
            scale_matrix = Matrix2D.scale(self._scale[0], self._scale[1])
            self.transform = self.transform.multiply(scale_matrix)

        # Apply rotation
        if self._rotation != 0.0:
            rotation_matrix = Matrix2D.rotation(self._rotation)
            self.transform = self.transform.multiply(rotation_matrix)

        # Apply translation
        if self._translation != [0.0, 0.0]:
            translation_matrix = Matrix2D.translation(self._translation[0], self._translation[1])
            self.transform = self.transform.multiply(translation_matrix)

        self.mark_dirty()

    def get_translation(self) -> list[float]:
        """Get current translation values"""
        return self._translation.copy()

    def get_rotation_degrees(self) -> float:
        """Get current rotation in degrees"""
        return math.degrees(self._rotation)

    def get_rotation_radians(self) -> float:
        """Get current rotation in radians"""
        return self._rotation

    def get_scale(self) -> list[float]:
        """Get current scale values"""
        return self._scale.copy()

    def get_input_geometry(self) -> GeometryNode | None:
        """Get the geometry node if input is geometry"""
        if isinstance(self.input_node, GeometryNode):
            return self.input_node
        elif isinstance(self.input_node, Transform2DNode):
            return self.input_node.get_input_geometry()
        return None

    def compute(self) -> "Transform2DNode":
        """Return self as the computed result"""
        # Evaluate input if present
        if self.input_node:
            self.input_node.evaluate()
        return self
