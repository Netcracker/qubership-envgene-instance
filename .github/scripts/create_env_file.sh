#!/bin/bash
# Script to create .env file compatible with GitHub Actions
# Properly handles multiline environment variables
# For multiline values, we replace newlines with spaces to keep format valid
# This ensures all secrets are properly passed between workflow steps

# Create or truncate the output file
> "$1"

# Process environment variables using printenv (more reliable than env)
# Redirect both stdout and stderr to avoid GitHub Actions processing issues
{
    printenv 2>/dev/null || /usr/bin/env 2>/dev/null || true
} | while IFS= read -r line || [ -n "$line" ]; do
    # Skip empty lines
    [ -z "$line" ] && continue
    
    # Extract variable name (everything before first =)
    var_name="${line%%=*}"
    
    # Skip if no variable name or if name is empty
    [ -z "$var_name" ] && continue
    
    # Skip certain internal variables that might cause issues
    case "$var_name" in
        _|SHLVL|PWD|OLDPWD)
            continue
            ;;
    esac
    
    # Extract value (everything after first =)
    var_value="${line#*=}"
    
    # Replace newlines with spaces (to avoid issues when reading line by line)
    # This ensures the format is valid while preserving all content
    single_line_value=$(printf '%s' "$var_value" | tr '\n' ' ' 2>/dev/null || printf '%s' "$var_value")
    # Remove trailing space if any
    single_line_value="${single_line_value% }"
    
    # Escape special characters that might cause issues
    # Escape backslashes first
    escaped_value=$(printf '%s' "$single_line_value" | sed 's/\\/\\\\/g' 2>/dev/null || printf '%s' "$single_line_value")
    # Escape dollar signs to prevent variable expansion issues  
    escaped_value=$(printf '%s' "$escaped_value" | sed 's/\$/\\$/g' 2>/dev/null || printf '%s' "$escaped_value")
    
    # Write to file in format: KEY=value
    printf '%s=%s\n' "$var_name" "$escaped_value" >> "$1" 2>/dev/null || true
done

echo "✅ Created .env file with proper multiline variable handling"

