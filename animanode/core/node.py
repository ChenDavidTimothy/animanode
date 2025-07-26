from abc import ABC, abstractmethod
from typing import Any


class Node(ABC):
    """Base class for all nodes in the animation system"""

    def __init__(self, name: str = "Node"):
        self.name = name
        self._cached_result: Any | None = None
        self._dirty = True

    def mark_dirty(self) -> None:
        """Mark this node as needing re-evaluation"""
        self._dirty = True
        self._cached_result = None

    def evaluate(self) -> Any:
        """Evaluate this node, using cache if clean"""
        if not self._dirty and self._cached_result is not None:
            return self._cached_result

        # Compute this node's result
        self._cached_result = self.compute()
        self._dirty = False
        return self._cached_result

    @abstractmethod
    def compute(self) -> Any:
        """Override this method to define node behavior"""
        pass


class GeometryNode(Node):
    """Base class for geometry nodes that produce vertex data"""

    def __init__(self, name: str = "Geometry"):
        super().__init__(name)

    @abstractmethod
    def get_vertices(self) -> "np.ndarray":
        """Return vertex data as numpy array"""
        pass

    @abstractmethod
    def get_indices(self) -> "np.ndarray":
        """Return index data as numpy array"""
        pass
