from enum import Enum, auto
from dataclasses import dataclass
from typing import List


class TokenType(Enum):
    SEGMENT_TAG = auto()
    ELEMENT_DATA = auto()
    COMPONENT_DATA = auto()
    SEGMENT_TERMINATOR = auto()
    ELEMENT_SEPARATOR = auto()
    COMPONENT_SEPARATOR = auto()
    ESCAPE = auto()


@dataclass
class Token:
    type: TokenType
    value: str


class Tokenizer:
    def __init__(self, data: str):
        self._raw_data = data.strip()
        self._component_sep = ':'
        self._element_sep = '+'
        self._segment_terminator = '\''
        self._release_char = '?'
        self._tokens: List[Token] = []

    def _init_delimiters(self):
        if self._raw_data.startswith("UNA"):
            self._component_sep = self._raw_data[3]
            self._element_sep = self._raw_data[4]
            self._release_char = self._raw_data[6]
            self._segment_terminator = self._raw_data[8]
            self._tokens.append(Token(TokenType.SEGMENT_TAG, "UNA"))
            for i, char in enumerate(self._raw_data[3:9]):
                if i == 0:
                    self._tokens.append(Token(TokenType.COMPONENT_SEPARATOR, char))
                elif i == 1:
                    self._tokens.append(Token(TokenType.ELEMENT_SEPARATOR, char))
                elif i == 2:
                    self._tokens.append(Token(TokenType.ELEMENT_DATA, char))  # decimal mark
                elif i == 3:
                    self._tokens.append(Token(TokenType.ESCAPE, char))
                elif i == 4:
                    self._tokens.append(Token(TokenType.ELEMENT_DATA, char))  # repetition sep
                elif i == 5:
                    self._tokens.append(Token(TokenType.SEGMENT_TERMINATOR, char))
            self._raw_data = self._raw_data[9:].lstrip()

    def tokenize(self):
        self._init_delimiters()
        buffer = ''
        i = 0
        length = len(self._raw_data)
        while i < length:
            char = self._raw_data[i]
            if char == self._release_char and i + 1 < length:
                buffer += self._raw_data[i + 1]
                self._tokens.append(Token(TokenType.ESCAPE, self._release_char))
                i += 2
                continue
            if char == self._segment_terminator:
                if buffer:
                    self._split_segment(buffer.strip())
                    buffer = ''
                self._tokens.append(Token(TokenType.SEGMENT_TERMINATOR, char))
                i += 1
            elif char.isspace():
                i += 1
            else:
                buffer += char
                i += 1
        if buffer:
            self._split_segment(buffer.strip())
        return self._tokens

    def _split_segment(self, text: str):
        parts = text.split(self._element_sep)
        if not parts:
            return
        self._tokens.append(Token(TokenType.SEGMENT_TAG, parts[0].strip()))
        for element in parts[1:]:
            self._tokens.append(Token(TokenType.ELEMENT_SEPARATOR, self._element_sep))
            components = element.split(self._component_sep)
            for j, comp in enumerate(components):
                self._tokens.append(Token(TokenType.COMPONENT_DATA, comp))
                if j < len(components) - 1:
                    self._tokens.append(Token(TokenType.COMPONENT_SEPARATOR, self._component_sep))
