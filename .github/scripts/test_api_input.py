#!/usr/bin/env python3
"""
Test script for validating GITHUB_PIPELINE_API_INPUT parsing locally
"""
import sys
import os

# Add the current directory to Python path so we can import process_api_input
sys.path.insert(0, os.path.dirname(__file__))

from process_api_input import parse_api_input, validate_variable

def test_api_input(test_input):
    """Test API input parsing"""
    print(f"Testing input: {test_input}")
    print(f"Input length: {len(test_input)} characters")
    print("-" * 50)
    
    # Parse the input
    variables = parse_api_input(test_input)
    
    if not variables:
        print("❌ No variables parsed!")
        return False
    
    print(f"✅ Parsed {len(variables)} variables:")
    for key, value in variables.items():
        validated_value = validate_variable(key, value)
        print(f"  {key} = {validated_value}")
    
    # Check if ENV_NAMES is present
    if 'ENV_NAMES' not in variables or not variables['ENV_NAMES'].strip():
        print("❌ ENV_NAMES is missing or empty!")
        return False
    
    print("✅ ENV_NAMES validation passed!")
    return True

def main():
    # Test cases
    test_cases = [
        # User's original input
        '{"ENV_NAMES": "test-cluster/e02", "ENV_BUILDER": "true", "DEPLOYMENT_TICKET_ID": "TEST-TICKET-1", "ENV_TEMPLATE_VERSION": "qubership_envgene_templates:0.0.2"}',
        
        # Minimal case
        '{"ENV_NAMES": "test-cluster/e01"}',
        
        # YAML format
        'ENV_NAMES: "test-cluster/e01"\nENV_BUILDER: true',
        
        # Key=Value format
        'ENV_NAMES=test-cluster/e01\nENV_BUILDER=true'
    ]
    
    print("🧪 GITHUB_PIPELINE_API_INPUT Parser Test\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test Case {i}:")
        success = test_api_input(test_case)
        print(f"Result: {'✅ PASS' if success else '❌ FAIL'}")
        print("=" * 70)
    
    # Interactive testing
    print("\n🔧 Interactive Testing:")
    print("Enter your GITHUB_PIPELINE_API_INPUT string (or 'quit' to exit):")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            if user_input:
                test_api_input(user_input)
                print("-" * 50)
        except KeyboardInterrupt:
            break
    
    print("\n👋 Testing completed!")

if __name__ == "__main__":
    main() 