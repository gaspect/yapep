# **Yapep**: Yet Another Python EDI Parser

## Overview

Yapep is a lightweight, flexible Python library for parsing EDI (Electronic Data Interchange) files. It uses a tree-based approach with the Visitor pattern to make processing EDI data both simple and powerful.

### Key Features

- **Pure Python** implementation with no external dependencies
- **Tree-based parsing** that preserves the hierarchical structure of EDI files
- **Visitor pattern** support for flexible processing of EDI data
- **Support for custom delimiters** via UNA segments
- **Simple API** for easy integration into your projects

## Installation

```bash
pip install yapep
```

Requires Python 3.14 or higher.

## Quick Start

### Basic Usage

```python
from yapep import Parser, Tokenizer

# Parse an EDI file
with open('your_edi_file.edi', 'r') as f:
    edi_content = f.read()

# Tokenize the EDI content
tokenizer = Tokenizer(edi_content)
tokens = tokenizer.tokenize()

# Parse the tokens into an AST
parser = Parser(tokens)
edi_file = parser.parse()

# Access the parsed data
for interchange in edi_file.interchanges:
    for message in interchange.messages:
        for segment in message.segments:
            print(f"Segment: {segment.tag}")
            for element in segment.elements:
                for component in element.components:
                    print(f"  Component value: {component.value}")
```

### Using the Visitor Pattern

The Visitor pattern allows you to process the EDI data without modifying the AST classes. Here's an example:

```python
from yapep import Visitor

class MyEdiVisitor(Visitor):
    def __init__(self):
        self.segment_count = 0
        self.message_types = set()

    def visit_segment(self, segment):
        self.segment_count += 1
        print(f"Processing segment: {segment.tag}")

    def visit_message(self, message):
        # Extract message type from UNH segment
        if message.header.tag == "UNH" and len(message.header.elements) > 1:
            message_type_element = message.header.elements[1]
            if message_type_element.components:
                self.message_types.add(message_type_element.components[0].value)

# Use the visitor
visitor = MyEdiVisitor()
edi_file.accept(visitor)

print(f"Total segments: {visitor.segment_count}")
print(f"Message types: {visitor.message_types}")
```

## EDI Structure

Yapep models EDI files with the following hierarchy:

- **File**: Contains interchanges and optional UNA segment
- **Interchange**: Starts with UNB and ends with UNZ, contains messages
- **Message**: Starts with UNH and ends with UNT, contains segments
- **Segment**: Has a tag and elements
- **Element**: Contains components
- **Component**: Contains a string value

## API Reference

### Tokenizer

```python
tokenizer = Tokenizer(edi_content)
tokens = tokenizer.tokenize()
```

The `Tokenizer` class converts raw EDI text into tokens. It automatically detects custom delimiters from UNA segments.

### Parser

```python
parser = Parser(tokens)
edi_file = parser.parse()
```

The `Parser` class converts tokens into an AST (Abstract Syntax Tree) representing the EDI file structure.

### AST Classes

- **Node**: Base class for all AST nodes
- **File**: Root node representing an EDI file
- **Interchange**: Represents an EDI interchange
- **Message**: Represents an EDI message
- **Segment**: Represents an EDI segment
- **Element**: Represents an EDI element
- **Component**: Represents an EDI component

### Visitor

```python
class MyVisitor(Visitor):
    def visit_file(self, file):
        # Process file

    def visit_interchange(self, interchange):
        # Process interchange

    def visit_message(self, message):
        # Process message

    def visit_segment(self, segment):
        # Process segment

    def visit_element(self, element):
        # Process element

    def visit_component(self, component):
        # Process component

# Apply visitor to the AST
visitor = MyVisitor()
edi_file.accept(visitor)
```

The `Visitor` class provides a way to traverse and process the AST without modifying the node classes.

## Examples

### Extracting Specific Data

```python
class DataExtractor(Visitor):
    def __init__(self):
        self.invoice_numbers = []
        self.customer_ids = []

    def visit_segment(self, segment):
        # Extract invoice numbers from BGM segments
        if segment.tag == "BGM" and len(segment.elements) > 1:
            invoice_element = segment.elements[1]
            if invoice_element.components:
                self.invoice_numbers.append(invoice_element.components[0].value)

        # Extract customer IDs from NAD+BY segments
        if segment.tag == "NAD" and len(segment.elements) > 0:
            if segment.elements[0].components and segment.elements[0].components[0].value == "BY":
                if len(segment.elements) > 1 and segment.elements[1].components:
                    self.customer_ids.append(segment.elements[1].components[0].value)

# Use the extractor
extractor = DataExtractor()
edi_file.accept(extractor)

print(f"Invoice numbers: {extractor.invoice_numbers}")
print(f"Customer IDs: {extractor.customer_ids}")
```

### Converting EDI to JSON

```python
import json

class JsonConverter(Visitor):
    def __init__(self):
        self.result = {}
        self.current_interchange = None
        self.current_message = None

    def visit_file(self, file):
        self.result = {
            "interchanges": []
        }

    def visit_interchange(self, interchange):
        self.current_interchange = {
            "header": self._segment_to_dict(interchange.header),
            "messages": [],
            "trailer": self._segment_to_dict(interchange.trailer)
        }
        self.result["interchanges"].append(self.current_interchange)

    def visit_message(self, message):
        self.current_message = {
            "header": self._segment_to_dict(message.header),
            "segments": [],
            "trailer": self._segment_to_dict(message.trailer)
        }
        self.current_interchange["messages"].append(self.current_message)

    def visit_segment(self, segment):
        if segment.tag not in ("UNB", "UNZ", "UNH", "UNT"):
            self.current_message["segments"].append(self._segment_to_dict(segment))

    def _segment_to_dict(self, segment):
        return {
            "tag": segment.tag,
            "elements": [
                {
                    "components": [comp.value for comp in element.components]
                }
                for element in segment.elements
            ]
        }

# Convert EDI to JSON
converter = JsonConverter()
edi_file.accept(converter)
json_output = json.dumps(converter.result, indent=2)
print(json_output)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
