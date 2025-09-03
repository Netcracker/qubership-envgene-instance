#!/usr/bin/env python3
"""
Simple test to verify the updated script logic
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from load_pipeline_vars import get_pipeline_vars
    
    print("Testing load_pipeline_vars.py...")
    
    # Test with current pipeline_vars.yaml
    try:
        variables = get_pipeline_vars(".github/pipeline_vars.yaml")
        print(f"✅ Successfully loaded {len(variables)} variables:")
        for key, value in variables.items():
            print(f"  {key}: {value}")
    except ValueError as e:
        print(f"❌ Validation error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
