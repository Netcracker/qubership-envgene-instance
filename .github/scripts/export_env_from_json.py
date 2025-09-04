#!/usr/bin/env python3
"""
Export environment variables from JSON
Reads variables from JSON and exports them to GITHUB_ENV file
"""

import os
import sys
import json


def log(message):
    """Log messages with prefix"""
    print(f"🔧 [export_env] {message}")


def export_variables_from_json(variables_json):
    """
    Export variables from JSON to GITHUB_ENV file.
    
    Args:
        variables_json (str): JSON string containing variables
        
    Returns:
        int: Number of variables exported
    """
    log("Exporting environment variables from JSON...")
    
    if not variables_json or variables_json.strip() in ['{}', 'null', '']:
        log("⚠️  No variables to export (empty or null JSON)")
        return 0
    
    try:
        # Parse JSON
        variables = json.loads(variables_json)
        
        if not isinstance(variables, dict):
            log("❌ ERROR: JSON is not a dictionary")
            return 0
            
        if not variables:
            log("⚠️  No variables found in JSON")
            return 0
            
    except json.JSONDecodeError as e:
        log(f"❌ ERROR: Invalid JSON format: {e}")
        return 0
    
    # Get GITHUB_ENV file path
    github_env_file = os.getenv("GITHUB_ENV")
    if not github_env_file:
        log("❌ ERROR: GITHUB_ENV environment variable not set")
        return 0
    
    # Export variables
    exported_count = 0
    
    try:
        with open(github_env_file, "a", encoding="utf-8") as f:
            for key, value in variables.items():
                # Skip null or empty values
                if value is None or value == "" or value == "null":
                    continue
                    
                # Convert value to string
                value_str = str(value)
                
                # Write to GITHUB_ENV file
                f.write(f"{key}={value_str}\n")
                log(f"Setting {key}={value_str}")
                exported_count += 1
                
    except Exception as e:
        log(f"❌ ERROR: Failed to write to GITHUB_ENV file: {e}")
        return 0
    
    log(f"✅ Successfully exported {exported_count} environment variables")
    return exported_count


def main():
    """Main function"""
    # Get variables JSON from command line argument or environment
    if len(sys.argv) > 1:
        variables_json = sys.argv[1]
    else:
        # Try to get from environment variable
        variables_json = os.getenv("VARIABLES_JSON", "")
    
    if not variables_json:
        log("❌ ERROR: No variables JSON provided")
        log("Usage: python export_env_from_json.py '<json_string>'")
        log("   or: VARIABLES_JSON='<json_string>' python export_env_from_json.py")
        sys.exit(1)
    
    # Export variables
    exported_count = export_variables_from_json(variables_json)
    
    if exported_count == 0:
        log("⚠️  No variables were exported")
        sys.exit(0)
    else:
        log(f"🎉 Export completed successfully ({exported_count} variables)")


if __name__ == "__main__":
    main()
