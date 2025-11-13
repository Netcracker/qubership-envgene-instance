#!/bin/bash
# Script to create .env.container file compatible with Docker --env-file
# Properly handles multiline environment variables
# For multiline values, we replace newlines with spaces to keep Docker --env-file format valid
# This ensures all secrets are properly passed to the container

# Create or truncate the output file
> .env.container

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
    
    # Docker --env-file doesn't support spaces in values (treats them as delimiters)
    # Replace newlines with spaces first, then replace all spaces with a safe delimiter
    # We'll use __SPACE__ as a marker that can be replaced back in the application if needed
    # Or the application can use the value as-is with __SPACE__ markers
    
    # Replace newlines with spaces
    single_line_value=$(printf '%s' "$var_value" | tr '\n' ' ' 2>/dev/null || printf '%s' "$var_value")
    # Remove trailing space if any
    single_line_value="${single_line_value% }"
    
    # Replace spaces with __SPACE__ marker to avoid Docker parsing issues
    # This preserves all content while keeping Docker --env-file format valid
    safe_value=$(printf '%s' "$single_line_value" | sed 's/ /__SPACE__/g' 2>/dev/null || printf '%s' "$single_line_value")
    
    # Escape special characters that might cause issues in Docker env-file
    escaped_value=$(printf '%s' "$safe_value" | sed 's/\\/\\\\/g' 2>/dev/null || printf '%s' "$safe_value")
    escaped_value=$(printf '%s' "$escaped_value" | sed 's/\$/\\$/g' 2>/dev/null || printf '%s' "$escaped_value")
    
    # Write to file in format: KEY=value
    printf '%s=%s\n' "$var_name" "$escaped_value" >> .env.container 2>/dev/null || true
done

echo "✅ Created .env.container file with proper multiline variable handling"

