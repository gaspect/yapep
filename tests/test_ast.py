import unittest
from yapep.ast import Node, File, Interchange, Message, Segment, Element, Component, Visitor


class TestAst(unittest.TestCase):
    def test_component(self):
        """Test Component class."""
        component = Component("test_value")
        self.assertEqual(component.value, "test_value")
    
    def test_element(self):
        """Test Element class."""
        components = [Component("comp1"), Component("comp2")]
        element = Element(components)
        self.assertEqual(len(element.components), 2)
        self.assertEqual(element.components[0].value, "comp1")
        self.assertEqual(element.components[1].value, "comp2")
    
    def test_segment(self):
        """Test Segment class."""
        elements = [
            Element([Component("comp1")]),
            Element([Component("comp2"), Component("comp3")])
        ]
        segment = Segment("SEG", elements)
        self.assertEqual(segment.tag, "SEG")
        self.assertEqual(len(segment.elements), 2)
        self.assertEqual(segment.elements[0].components[0].value, "comp1")
        self.assertEqual(segment.elements[1].components[0].value, "comp2")
        self.assertEqual(segment.elements[1].components[1].value, "comp3")
    
    def test_message(self):
        """Test Message class."""
        header = Segment("UNH", [Element([Component("1")])])
        trailer = Segment("UNT", [Element([Component("1")])])
        segments = [Segment("SEG", [Element([Component("data")])])]
        message = Message(header, trailer, segments)
        self.assertEqual(message.header.tag, "UNH")
        self.assertEqual(message.trailer.tag, "UNT")
        self.assertEqual(len(message.segments), 1)
        self.assertEqual(message.segments[0].tag, "SEG")
    
    def test_interchange(self):
        """Test Interchange class."""
        header = Segment("UNB", [Element([Component("UNOA")])])
        trailer = Segment("UNZ", [Element([Component("1")])])
        
        # Create a message
        msg_header = Segment("UNH", [Element([Component("1")])])
        msg_trailer = Segment("UNT", [Element([Component("1")])])
        msg_segments = [Segment("SEG", [Element([Component("data")])])]
        message = Message(msg_header, msg_trailer, msg_segments)
        
        interchange = Interchange(header, trailer, [message])
        self.assertEqual(interchange.header.tag, "UNB")
        self.assertEqual(interchange.trailer.tag, "UNZ")
        self.assertEqual(len(interchange.messages), 1)
        self.assertEqual(interchange.messages[0].header.tag, "UNH")
    
    def test_file(self):
        """Test File class."""
        una = Segment("UNA", [])
        
        # Create an interchange
        int_header = Segment("UNB", [Element([Component("UNOA")])])
        int_trailer = Segment("UNZ", [Element([Component("1")])])
        
        # Create a message
        msg_header = Segment("UNH", [Element([Component("1")])])
        msg_trailer = Segment("UNT", [Element([Component("1")])])
        msg_segments = [Segment("SEG", [Element([Component("data")])])]
        message = Message(msg_header, msg_trailer, msg_segments)
        
        interchange = Interchange(int_header, int_trailer, [message])
        
        file = File(una, [interchange])
        self.assertEqual(file.una.tag, "UNA")
        self.assertEqual(len(file.interchanges), 1)
        self.assertEqual(file.interchanges[0].header.tag, "UNB")
    
    def test_visitor_pattern(self):
        """Test the Visitor pattern implementation."""
        # Create a test visitor that counts nodes
        class CountingVisitor(Visitor):
            def __init__(self):
                self.file_count = 0
                self.interchange_count = 0
                self.message_count = 0
                self.segment_count = 0
                self.element_count = 0
                self.component_count = 0
            
            def visit_file(self, file):
                self.file_count += 1
            
            def visit_interchange(self, interchange):
                self.interchange_count += 1
            
            def visit_message(self, message):
                self.message_count += 1
            
            def visit_segment(self, segment):
                self.segment_count += 1
            
            def visit_element(self, element):
                self.element_count += 1
            
            def visit_component(self, component):
                self.component_count += 1
        
        # Create a simple EDI structure
        component1 = Component("comp1")
        component2 = Component("comp2")
        element = Element([component1, component2])
        segment = Segment("SEG", [element])
        msg_header = Segment("UNH", [Element([Component("1")])])
        msg_trailer = Segment("UNT", [Element([Component("1")])])
        message = Message(msg_header, msg_trailer, [segment])
        int_header = Segment("UNB", [Element([Component("UNOA")])])
        int_trailer = Segment("UNZ", [Element([Component("1")])])
        interchange = Interchange(int_header, int_trailer, [message])
        file = File(None, [interchange])
        
        # Apply the visitor
        visitor = CountingVisitor()
        file.accept(visitor)
        
        # Check counts
        self.assertEqual(visitor.file_count, 1)
        self.assertEqual(visitor.interchange_count, 1)
        self.assertEqual(visitor.message_count, 1)
        # 4 segments: UNB, UNH, SEG, UNT, UNZ
        self.assertEqual(visitor.segment_count, 1)
        # Each segment has at least one element
        self.assertGreaterEqual(visitor.element_count, 1)
        # Each element has at least one component
        self.assertGreaterEqual(visitor.component_count, 1)


if __name__ == '__main__':
    unittest.main()