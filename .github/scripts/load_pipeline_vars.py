#!/usr/bin/env python3
"""
Simple utility to load variables from pipeline_vars.yaml file.
All variables must be of string type - validation will fail otherwise.
"""

import os
import json
from typing import Dict, Any, Optional


def validate_string_type(value: str, var_name: str) -> None:
    """
    Validate that the value is a proper string type.
    
    Args:
        value: The value to validate
        var_name: Name of the variable for error reporting
        
    Raises:
        ValueError: If the value is not a valid string type
    """
    # Check for common non-string patterns
    if value.lower() in ["true", "false"] and not (value.startswith('"') or value.startswith("'")):
        raise ValueError(f"Variable '{var_name}' has boolean value '{value}' without quotes. All variables must be strings. Use '{var_name}: \"{value}\"' instead.")
    
    # Check for unquoted numbers
    try:
        float(value)
        if not (value.startswith('"') or value.startswith("'")):
            raise ValueError(f"Variable '{var_name}' has numeric value '{value}' without quotes. All variables must be strings. Use '{var_name}: \"{value}\"' instead.")
    except ValueError:
        pass  # Not a number, which is fine
    
    # Check for unquoted JSON objects/arrays
    if (value.startswith('{') or value.startswith('[')) and not (value.startswith('"') or value.startswith("'")):
        raise ValueError(f"Variable '{var_name}' has JSON value '{value}' without quotes. All variables must be strings. Use '{var_name}: \"{value}\"' instead.")


def parse_pipeline_vars_yaml(file_path: str = ".github/pipeline_vars.yaml") -> Dict[str, str]:
    """
    Parse pipeline_vars.yaml file and extract commented variables.
    Validates that all variables are of string type.
    
    Args:
        file_path: Path to the pipeline_vars.yaml file
        
    Returns:
        Dictionary with variable names and their string values
        
    Raises:
        ValueError: If any variable is not of string type
    """
    variables = {}
    errors = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            # Skip empty lines and commented lines
            if not line or line.startswith("#"):
                continue
            
            # Use the line content directly (no comment prefix to remove)
            content = line
            
            # Check if it's a variable assignment
            if ":" in content:
                key, value = content.split(":", 1)
                key = key.strip()
                value = value.strip()
                
                # Validate string type before processing
                try:
                    validate_string_type(value, key)
                except ValueError as e:
                    errors.append(f"Line {line_num}: {str(e)}")
                    continue
                
                # Remove quotes if present
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                
                variables[key] = value
                print(f"Loaded variable: {key} = {value}")
    
    except FileNotFoundError:
        print(f"Warning: pipeline_vars.yaml file not found at {file_path}")
    except Exception as e:
        print(f"Error parsing pipeline_vars.yaml: {e}")
    
    # If there were validation errors, raise them
    if errors:
        error_message = "String type validation failed:\n" + "\n".join(errors)
        raise ValueError(error_message)
    
    return variables


def get_pipeline_var(var_name: str, default: str = "", file_path: str = ".github/pipeline_vars.yaml") -> str:
    """
    Get a specific pipeline variable by name.
    
    Args:
        var_name: Name of the variable to retrieve
        default: Default value if variable is not found
        file_path: Path to the pipeline_vars.yaml file
        
    Returns:
        Variable value as string, or default if not found
        
    Raises:
        ValueError: If any variable in the file is not of string type
    """
    variables = parse_pipeline_vars_yaml(file_path)
    return variables.get(var_name, default)


def get_pipeline_vars(file_path: str = ".github/pipeline_vars.yaml") -> Dict[str, str]:
    """
    Get all pipeline variables as a dictionary.
    
    Args:
        file_path: Path to the pipeline_vars.yaml file
        
    Returns:
        Dictionary with all pipeline variables
        
    Raises:
        ValueError: If any variable in the file is not of string type
    """
    return parse_pipeline_vars_yaml(file_path)


def main():
    """
    Main function for command-line usage.
    """
    import sys
    
    try:
        if len(sys.argv) > 1:
            var_name = sys.argv[1]
            value = get_pipeline_var(var_name)
            print(value)
        else:
            # Print all variables and write to github_output
            variables = get_pipeline_vars()
            print("Available pipeline variables:")
            
            # Write to github_output if available
            github_output = os.getenv("GITHUB_OUTPUT")
            print(f"🔍 Debug: GITHUB_OUTPUT = {github_output}")
            print(f"🔍 Debug: Found {len(variables)} variables")
            
            if github_output:
                with open(github_output, "a", encoding="utf-8") as f:
                    for key, value in variables.items():
                        print(f"  {key}: {value}")
                        # Write to github_output for use in other jobs
                        f.write(f"{key}={value}\n")
                print(f"\n✅ Written {len(variables)} variables to github_output")
            else:
                # Fallback: just print variables
                for key, value in variables.items():
                    print(f"  {key}: {value}")
                print("\n⚠️  GITHUB_OUTPUT not available - variables not written to output")
                
    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
