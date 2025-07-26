from typing import Any

from .renderer import Renderer2D


class Canvas:
    """2D rendering canvas for node-based animation system"""

    def __init__(
        self, width: int = 1920, height: int = 1080, background_color: tuple = (0.0, 0.0, 0.0, 1.0)
    ):
        self.width = width
        self.height = height
        self.background_color = background_color
        self.renderer = Renderer2D(width, height, background_color)
        self.root_nodes: list[Any] = []

    def add_node(self, node: Any) -> "Canvas":
        """Add a root node to be rendered"""
        if node not in self.root_nodes:
            self.root_nodes.append(node)
        return self

    def remove_node(self, node: Any) -> "Canvas":
        """Remove a root node"""
        if node in self.root_nodes:
            self.root_nodes.remove(node)
        return self

    def clear_nodes(self) -> "Canvas":
        """Remove all nodes"""
        self.root_nodes.clear()
        return self

    def set_background_color(self, r: float, g: float, b: float, a: float = 1.0) -> "Canvas":
        """Set background color"""
        self.background_color = (r, g, b, a)
        self.renderer.clear_color = self.background_color
        return self

    def set_material_color(self, r: float, g: float, b: float, a: float = 1.0) -> "Canvas":
        """Set default material color for all shapes"""
        self.renderer.set_material_color(r, g, b, a)
        return self

    def render_frame(self):
        """Render current frame and return as numpy array"""
        return self.renderer.render_frame(self.root_nodes)

    def get_size(self) -> tuple:
        """Get canvas dimensions"""
        return (self.width, self.height)
