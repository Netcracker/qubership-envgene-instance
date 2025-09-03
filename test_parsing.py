#!/usr/bin/env python3
"""Test script to verify parsing logic"""

import json

def test_parse_line():
    # Test the problematic line
    test_line = 'BG_STATE = "{\\"controllerNamespace\\": \\"ns-controller\\", \\"originNamespace\\": {\\"name\\": \\"bss\\", \\"state\\": \\"candidate\\", \\"version\\": \\"v5\\"}, \\"peerNamespace\\": {\\"name\\": \\"core\\", \\"state\\": \\"active\\", \\"version\\": \\"v6\\"}, \\"updateTime\\": \\"2023-07-07T10:00:54Z\\"}"'
    
    print(f"Original line: {test_line}")
    
    # Find the first = that's not inside quotes
    eq_pos = -1
    in_quotes = False
    quote_char = None
    
    for i, char in enumerate(test_line):
        if char in ['"', "'"] and (i == 0 or test_line[i-1] != '\\'):
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char:
                in_quotes = False
                quote_char = None
        elif char == '=' and not in_quotes:
            eq_pos = i
            break
    
    if eq_pos != -1:
        key = test_line[:eq_pos].strip()
        value = test_line[eq_pos + 1:].strip()
        
        print(f"Key: '{key}'")
        print(f"Value: '{value}'")
        
        # Remove outer quotes
        if value.startswith('"') and value.endswith('"'):
            inner_value = value[1:-1]
            print(f"Inner value: '{inner_value}'")
            
            # Try to parse as JSON
            try:
                # Unescape quotes
                unescaped = inner_value.replace('\\"', '"')
                print(f"Unescaped: '{unescaped}'")
                parsed = json.loads(unescaped)
                print(f"Successfully parsed JSON: {parsed}")
            except json.JSONDecodeError as e:
                print(f"JSON parsing failed: {e}")

if __name__ == "__main__":
    test_parse_line()
