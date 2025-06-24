from typing import List, TypeVar, Any
from dataclasses import dataclass

_T = TypeVar("_T")


class Node:
    def accept(self, visitor: "Visitor") -> Any:
        ...


@dataclass
class Scoped(Node):
    header: 'Segment'  # started segment
    trailer: 'Segment'  # end segment


@dataclass
class Component(Node):
    value: str

    def accept(self, visitor: "Visitor") -> None:
        visitor.visit_component(self)


@dataclass
class Element(Node):
    components: List[Component]

    def accept(self, visitor: "Visitor") -> None:
        visitor.visit_element(self)
        for component in self.components:
            component.accept(visitor)


@dataclass
class Segment(Node):
    tag: str
    elements: List[Element]

    def accept(self, visitor: "Visitor") -> None:
        visitor.visit_segment(self)
        for element in self.elements:
            element.accept(visitor)


@dataclass
class Message(Scoped):
    segments: List[Segment]

    def accept(self, visitor: "Visitor") -> None:
        visitor.visit_message(self)
        for segment in self.segments:
            segment.accept(visitor)


@dataclass
class Interchange(Scoped):
    messages: List[Message]

    def accept(self, visitor: "Visitor") -> None:
        visitor.visit_interchange(self)
        for msg in self.messages:
            msg.accept(visitor)


@dataclass
class File(Node):
    una: Segment | None  # headless
    interchanges: List[Interchange]

    def accept(self, visitor: "Visitor") -> None:
        visitor.visit_file(self)
        for interchange in self.interchanges:
            interchange.accept(visitor)


class Visitor:
    def visit_file(self, file: File):
        ...

    def visit_interchange(self, interchange: Interchange):
        ...

    def visit_segment(self, segment: Segment):
        ...

    def visit_message(self, message: Message):
        ...

    def visit_element(self, element: Element):
        ...

    def visit_component(self, componen: Component):
        ...
