"""
Radically simple video generator - user doesn't need programming knowledge
No for loops, no complexity - just create shapes and call scene.draw()
"""

from animanode import Circle, Rectangle, Scene, Triangle


def main():
    """User-friendly approach - no programming complexity visible"""

    # Create parametric geometries
    circle = Circle(radius=0.6, segments=32)
    rect = Rectangle(width=0.8, height=0.6)
    triangle = Triangle(size=0.9, rotation=0.0)

    # Simple scene approach - user doesn't see video creation complexity
    scene1 = Scene()
    scene1.add(circle)
    scene1.draw("circle.mp4")

    scene2 = Scene()
    scene2.add(rect)
    scene2.draw("rectangle.mp4")

    scene3 = Scene()
    scene3.add(triangle)
    scene3.draw("triangle.mp4")


def future_vision_example():
    """This is your future vision - architecture prepared"""

    # This will work in future version:
    # scene = Scene()
    # meshList = []
    #
    # rect = Rectangle(width=0.8, height=0.6)
    # rect.translate(0.2, 0.1)  # Architecture prepared
    # rect.rotate(0.5)          # Architecture prepared
    # meshList.append(rect)
    #
    # circle = Circle(radius=0.5)
    # circle.scale(1.5, 1.5)    # Architecture prepared
    # meshList.append(circle)
    #
    # scene.add(meshList)
    # scene.draw()              # Automatically creates video

    print("Transform methods architecture prepared for future implementation")


if __name__ == "__main__":
    main()
    future_vision_example()
