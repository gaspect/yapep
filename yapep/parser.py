from typing import List
from .tokenizer import Token, TokenType
from .ast import File, Interchange, Message, Segment, Element, Component


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.index = 0

    def parse(self) -> File:
        una = self._parse_segment()

        interchanges = []
        while self.index < len(self.tokens):
            interchange = self._parse_interchange()
            if interchange:
                interchanges.append(interchange)

        return File(una, interchanges)

    def _parse_interchange(self) -> Interchange | None:
        if self.tokens[self.index].value != "UNB":
            self.index += 1
            return None
        header = self._parse_segment()
        messages = []
        while self.index < len(self.tokens) and self.tokens[self.index].value != "UNZ":
            message = self._parse_message()
            if message:
                messages.append(message)
        trailer = self._parse_segment()

        return Interchange(header=header, messages=messages, trailer=trailer)

    def _parse_message(self) -> Message | None:
        # Parse the UNH segment (start of the message)
        if self.tokens[self.index].value != "UNH":
            self.index += 1
            return None
        header = self._parse_segment()
        segments = []

        # Parse all segments inside the message
        while self.index < len(self.tokens) and self.tokens[self.index].value != "UNT":
            segment = self._parse_segment()
            if segment:
                segments.append(segment)
        # Parse the UNT segment (end of the message)
        trailer = self._parse_segment()
        return Message(header=header, segments=segments, trailer=trailer)

    def _parse_segment(self) -> Segment | None:
        if self.tokens[self.index].type != TokenType.SEGMENT_TAG:
            self.index += 1
            return None

        tag = self.tokens[self.index].value
        self.index += 1
        elements = []
        current_components = []

        while self.index < len(self.tokens):
            token = self.tokens[self.index]
            if token.type == TokenType.ELEMENT_SEPARATOR:
                if current_components:
                    elements.append(Element(current_components))
                    current_components = []
                self.index += 1
            elif token.type == TokenType.COMPONENT_DATA:
                current_components.append(Component(token.value))
                self.index += 1
            elif token.type == TokenType.COMPONENT_SEPARATOR:
                self.index += 1  # just skip separator
            elif token.type == TokenType.SEGMENT_TERMINATOR:
                if current_components:
                    elements.append(Element(current_components))
                self.index += 1
                break
            else:
                self.index += 1

        return Segment(tag=tag, elements=elements)
