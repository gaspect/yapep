import unittest
from yapep.tokenizer import Tokenizer, Token, TokenType


class TestTokenizer(unittest.TestCase):
    def test_tokenize_simple_segment(self):
        """Test tokenizing a simple segment without UNA header."""
        data = "SEG+123+456'"
        tokenizer = Tokenizer(data)
        tokens = tokenizer.tokenize()

        # Check the number of tokens
        self.assertEqual(len(tokens), 6)

        # Check segment tag
        self.assertEqual(tokens[0].type, TokenType.SEGMENT_TAG)
        self.assertEqual(tokens[0].value, "SEG")

        # Check element separator
        self.assertEqual(tokens[1].type, TokenType.ELEMENT_SEPARATOR)
        self.assertEqual(tokens[1].value, "+")

        # Check first element
        self.assertEqual(tokens[2].type, TokenType.COMPONENT_DATA)
        self.assertEqual(tokens[2].value, "123")

        # Check second element separator
        self.assertEqual(tokens[3].type, TokenType.ELEMENT_SEPARATOR)
        self.assertEqual(tokens[3].value, "+")

        # Check second element
        self.assertEqual(tokens[4].type, TokenType.COMPONENT_DATA)
        self.assertEqual(tokens[4].value, "456")

        # Check segment terminator
        self.assertEqual(tokens[5].type, TokenType.SEGMENT_TERMINATOR)
        self.assertEqual(tokens[5].value, "'")

    def test_tokenize_with_components(self):
        """Test tokenizing a segment with component separators."""
        data = "SEG+123:456:789'"
        tokenizer = Tokenizer(data)
        tokens = tokenizer.tokenize()

        # Check the number of tokens
        self.assertEqual(len(tokens), 8)

        # Check segment tag
        self.assertEqual(tokens[0].type, TokenType.SEGMENT_TAG)
        self.assertEqual(tokens[0].value, "SEG")

        # Check element separator
        self.assertEqual(tokens[1].type, TokenType.ELEMENT_SEPARATOR)
        self.assertEqual(tokens[1].value, "+")

        # Check first component
        self.assertEqual(tokens[2].type, TokenType.COMPONENT_DATA)
        self.assertEqual(tokens[2].value, "123")

        # Check component separator
        self.assertEqual(tokens[3].type, TokenType.COMPONENT_SEPARATOR)
        self.assertEqual(tokens[3].value, ":")

        # Check second component
        self.assertEqual(tokens[4].type, TokenType.COMPONENT_DATA)
        self.assertEqual(tokens[4].value, "456")

        # Check component separator
        self.assertEqual(tokens[5].type, TokenType.COMPONENT_SEPARATOR)
        self.assertEqual(tokens[5].value, ":")

        # Check third component
        self.assertEqual(tokens[6].type, TokenType.COMPONENT_DATA)
        self.assertEqual(tokens[6].value, "789")

        # Check segment terminator
        self.assertEqual(tokens[7].type, TokenType.SEGMENT_TERMINATOR)
        self.assertEqual(tokens[7].value, "'")

    def test_tokenize_with_una(self):
        """Test tokenizing with UNA header that defines custom separators."""
        data = "UNA:+.? '\nSEG+123:456'"
        tokenizer = Tokenizer(data)
        tokens = tokenizer.tokenize()

        # Check that UNA was processed correctly
        self.assertEqual(tokens[0].type, TokenType.SEGMENT_TAG)
        self.assertEqual(tokens[0].value, "UNA")

        # Check that custom separators were recognized
        self.assertEqual(tokenizer._component_sep, ":")
        self.assertEqual(tokenizer._element_sep, "+")
        self.assertEqual(tokenizer._release_char, "?")
        self.assertEqual(tokenizer._segment_terminator, "'")

        # Check that the segment after UNA was tokenized correctly
        seg_tag_index = 7  # Index of SEG tag after UNA tokens
        self.assertEqual(tokens[seg_tag_index].type, TokenType.SEGMENT_TAG)
        self.assertEqual(tokens[seg_tag_index].value, "SEG")

    def test_tokenize_with_escape(self):
        """Test tokenizing with escape characters."""
        data = "SEG+12?+3+456'"  # ?+ is an escaped + character
        tokenizer = Tokenizer(data)
        tokens = tokenizer.tokenize()

        # Check that we have an ESCAPE token
        escape_found = False
        for token in tokens:
            if token.type == TokenType.ESCAPE:
                escape_found = True
                break

        self.assertTrue(escape_found, "ESCAPE token not found")

        # Check that we have the expected tokens
        # The tokenizer should produce tokens for SEG, +, 12, +, 3, +, 456, '
        self.assertEqual(tokens[1].type, TokenType.SEGMENT_TAG)
        self.assertEqual(tokens[1].value, "SEG")
        self.assertEqual(tokens[3].type, TokenType.COMPONENT_DATA)
        self.assertEqual(tokens[3].value, "12")
        self.assertEqual(tokens[5].type, TokenType.COMPONENT_DATA)
        self.assertEqual(tokens[5].value, "3")
        self.assertEqual(tokens[7].type, TokenType.COMPONENT_DATA)
        self.assertEqual(tokens[7].value, "456")


if __name__ == '__main__':
    unittest.main()
