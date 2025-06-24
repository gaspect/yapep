import unittest
from yapep.tokenizer import Tokenizer, Token, TokenType
from yapep.parser import Parser
from yapep.ast import File, Interchange, Message, Segment, Element, Component


class TestParser(unittest.TestCase):
    def test_parse_segment(self):
        """Test parsing a single segment."""
        # Create tokens for a simple segment
        tokens = [
            Token(TokenType.SEGMENT_TAG, "SEG"),
            Token(TokenType.ELEMENT_SEPARATOR, "+"),
            Token(TokenType.COMPONENT_DATA, "123"),
            Token(TokenType.ELEMENT_SEPARATOR, "+"),
            Token(TokenType.COMPONENT_DATA, "456"),
            Token(TokenType.SEGMENT_TERMINATOR, "'")
        ]
        
        parser = Parser(tokens)
        segment = parser._parse_segment()
        
        # Check segment properties
        self.assertEqual(segment.tag, "SEG")
        self.assertEqual(len(segment.elements), 2)
        
        # Check first element
        self.assertEqual(len(segment.elements[0].components), 1)
        self.assertEqual(segment.elements[0].components[0].value, "123")
        
        # Check second element
        self.assertEqual(len(segment.elements[1].components), 1)
        self.assertEqual(segment.elements[1].components[0].value, "456")
    
    def test_parse_segment_with_components(self):
        """Test parsing a segment with component separators."""
        # Create tokens for a segment with components
        tokens = [
            Token(TokenType.SEGMENT_TAG, "SEG"),
            Token(TokenType.ELEMENT_SEPARATOR, "+"),
            Token(TokenType.COMPONENT_DATA, "123"),
            Token(TokenType.COMPONENT_SEPARATOR, ":"),
            Token(TokenType.COMPONENT_DATA, "456"),
            Token(TokenType.SEGMENT_TERMINATOR, "'")
        ]
        
        parser = Parser(tokens)
        segment = parser._parse_segment()
        
        # Check segment properties
        self.assertEqual(segment.tag, "SEG")
        self.assertEqual(len(segment.elements), 1)
        
        # Check element with components
        self.assertEqual(len(segment.elements[0].components), 2)
        self.assertEqual(segment.elements[0].components[0].value, "123")
        self.assertEqual(segment.elements[0].components[1].value, "456")
    
    def test_parse_message(self):
        """Test parsing a message (UNH to UNT)."""
        # Create tokens for a simple message
        tokens = [
            # UNH segment
            Token(TokenType.SEGMENT_TAG, "UNH"),
            Token(TokenType.ELEMENT_SEPARATOR, "+"),
            Token(TokenType.COMPONENT_DATA, "1"),
            Token(TokenType.ELEMENT_SEPARATOR, "+"),
            Token(TokenType.COMPONENT_DATA, "ORDERS"),
            Token(TokenType.SEGMENT_TERMINATOR, "'"),
            
            # Content segment
            Token(TokenType.SEGMENT_TAG, "SEG"),
            Token(TokenType.ELEMENT_SEPARATOR, "+"),
            Token(TokenType.COMPONENT_DATA, "data"),
            Token(TokenType.SEGMENT_TERMINATOR, "'"),
            
            # UNT segment
            Token(TokenType.SEGMENT_TAG, "UNT"),
            Token(TokenType.ELEMENT_SEPARATOR, "+"),
            Token(TokenType.COMPONENT_DATA, "2"),
            Token(TokenType.ELEMENT_SEPARATOR, "+"),
            Token(TokenType.COMPONENT_DATA, "1"),
            Token(TokenType.SEGMENT_TERMINATOR, "'")
        ]
        
        parser = Parser(tokens)
        message = parser._parse_message()
        
        # Check message properties
        self.assertEqual(message.header.tag, "UNH")
        self.assertEqual(message.trailer.tag, "UNT")
        self.assertEqual(len(message.segments), 1)
        self.assertEqual(message.segments[0].tag, "SEG")
    
    def test_parse_interchange(self):
        """Test parsing an interchange (UNB to UNZ)."""
        # Create tokens for a simple interchange with one message
        tokens = [
            # UNB segment
            Token(TokenType.SEGMENT_TAG, "UNB"),
            Token(TokenType.ELEMENT_SEPARATOR, "+"),
            Token(TokenType.COMPONENT_DATA, "UNOA"),
            Token(TokenType.SEGMENT_TERMINATOR, "'"),
            
            # UNH segment
            Token(TokenType.SEGMENT_TAG, "UNH"),
            Token(TokenType.ELEMENT_SEPARATOR, "+"),
            Token(TokenType.COMPONENT_DATA, "1"),
            Token(TokenType.ELEMENT_SEPARATOR, "+"),
            Token(TokenType.COMPONENT_DATA, "ORDERS"),
            Token(TokenType.SEGMENT_TERMINATOR, "'"),
            
            # Content segment
            Token(TokenType.SEGMENT_TAG, "SEG"),
            Token(TokenType.ELEMENT_SEPARATOR, "+"),
            Token(TokenType.COMPONENT_DATA, "data"),
            Token(TokenType.SEGMENT_TERMINATOR, "'"),
            
            # UNT segment
            Token(TokenType.SEGMENT_TAG, "UNT"),
            Token(TokenType.ELEMENT_SEPARATOR, "+"),
            Token(TokenType.COMPONENT_DATA, "2"),
            Token(TokenType.ELEMENT_SEPARATOR, "+"),
            Token(TokenType.COMPONENT_DATA, "1"),
            Token(TokenType.SEGMENT_TERMINATOR, "'"),
            
            # UNZ segment
            Token(TokenType.SEGMENT_TAG, "UNZ"),
            Token(TokenType.ELEMENT_SEPARATOR, "+"),
            Token(TokenType.COMPONENT_DATA, "1"),
            Token(TokenType.ELEMENT_SEPARATOR, "+"),
            Token(TokenType.COMPONENT_DATA, "1"),
            Token(TokenType.SEGMENT_TERMINATOR, "'")
        ]
        
        parser = Parser(tokens)
        interchange = parser._parse_interchange()
        
        # Check interchange properties
        self.assertEqual(interchange.header.tag, "UNB")
        self.assertEqual(interchange.trailer.tag, "UNZ")
        self.assertEqual(len(interchange.messages), 1)
        self.assertEqual(interchange.messages[0].header.tag, "UNH")
    
    def test_parse_file(self):
        """Test parsing a complete EDI file."""
        # Create tokens for a simple EDI file with one interchange and one message
        tokens = [
            # UNA segment (optional)
            Token(TokenType.SEGMENT_TAG, "UNA"),
            Token(TokenType.COMPONENT_SEPARATOR, ":"),
            Token(TokenType.ELEMENT_SEPARATOR, "+"),
            Token(TokenType.ELEMENT_DATA, "."),
            Token(TokenType.ESCAPE, "?"),
            Token(TokenType.ELEMENT_DATA, " "),
            Token(TokenType.SEGMENT_TERMINATOR, "'"),
            
            # UNB segment
            Token(TokenType.SEGMENT_TAG, "UNB"),
            Token(TokenType.ELEMENT_SEPARATOR, "+"),
            Token(TokenType.COMPONENT_DATA, "UNOA"),
            Token(TokenType.SEGMENT_TERMINATOR, "'"),
            
            # UNH segment
            Token(TokenType.SEGMENT_TAG, "UNH"),
            Token(TokenType.ELEMENT_SEPARATOR, "+"),
            Token(TokenType.COMPONENT_DATA, "1"),
            Token(TokenType.ELEMENT_SEPARATOR, "+"),
            Token(TokenType.COMPONENT_DATA, "ORDERS"),
            Token(TokenType.SEGMENT_TERMINATOR, "'"),
            
            # Content segment
            Token(TokenType.SEGMENT_TAG, "SEG"),
            Token(TokenType.ELEMENT_SEPARATOR, "+"),
            Token(TokenType.COMPONENT_DATA, "data"),
            Token(TokenType.SEGMENT_TERMINATOR, "'"),
            
            # UNT segment
            Token(TokenType.SEGMENT_TAG, "UNT"),
            Token(TokenType.ELEMENT_SEPARATOR, "+"),
            Token(TokenType.COMPONENT_DATA, "2"),
            Token(TokenType.ELEMENT_SEPARATOR, "+"),
            Token(TokenType.COMPONENT_DATA, "1"),
            Token(TokenType.SEGMENT_TERMINATOR, "'"),
            
            # UNZ segment
            Token(TokenType.SEGMENT_TAG, "UNZ"),
            Token(TokenType.ELEMENT_SEPARATOR, "+"),
            Token(TokenType.COMPONENT_DATA, "1"),
            Token(TokenType.ELEMENT_SEPARATOR, "+"),
            Token(TokenType.COMPONENT_DATA, "1"),
            Token(TokenType.SEGMENT_TERMINATOR, "'")
        ]
        
        parser = Parser(tokens)
        edi_file = parser.parse()
        
        # Check file properties
        self.assertIsNotNone(edi_file.una)
        self.assertEqual(edi_file.una.tag, "UNA")
        self.assertEqual(len(edi_file.interchanges), 1)
        
        # Check interchange
        interchange = edi_file.interchanges[0]
        self.assertEqual(interchange.header.tag, "UNB")
        self.assertEqual(interchange.trailer.tag, "UNZ")
        self.assertEqual(len(interchange.messages), 1)
        
        # Check message
        message = interchange.messages[0]
        self.assertEqual(message.header.tag, "UNH")
        self.assertEqual(message.trailer.tag, "UNT")
        self.assertEqual(len(message.segments), 1)
        self.assertEqual(message.segments[0].tag, "SEG")


if __name__ == '__main__':
    unittest.main()