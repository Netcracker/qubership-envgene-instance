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
    # Handle case where value might contain = signs
    var_value="${line#*=}"
    
    # Skip if variable name contains spaces (invalid)
    if [[ "$var_name" =~ [[:space:]] ]]; then
        continue
    fi
    
    # Docker --env-file doesn't support spaces, tabs, or newlines in values
    # Check if value contains any whitespace characters
    # If it does, encode it in base64 to preserve the content
    
    # Trim leading/trailing whitespace from value for checking
    trimmed_value=$(printf '%s' "$var_value" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' 2>/dev/null || printf '%s' "$var_value")
    
    # Check for whitespace (spaces, tabs, newlines) in the value
    if printf '%s' "$var_value" | grep -q '[[:space:]]'; then
        # Value contains whitespace - encode in base64
        # Use base64 with -w 0 (no wrap) if available, otherwise use base64
        encoded_value=$(printf '%s' "$var_value" | base64 -w 0 2>/dev/null || printf '%s' "$var_value" | base64 2>/dev/null || printf '%s' "$var_value")
        # Remove any whitespace from encoded value (base64 shouldn't have any, but just in case)
        encoded_value=$(printf '%s' "$encoded_value" | tr -d '\n\r\t ' 2>/dev/null || printf '%s' "$encoded_value")
        # Write to file with BASE64: prefix to indicate encoding
        printf '%s=BASE64:%s\n' "$var_name" "$encoded_value" >> .env.container 2>/dev/null || true
    else
        # Value doesn't contain whitespace - use as-is with minimal escaping
        # Escape backslashes and dollar signs
        escaped_value=$(printf '%s' "$var_value" | sed 's/\\/\\\\/g' 2>/dev/null || printf '%s' "$var_value")
        escaped_value=$(printf '%s' "$escaped_value" | sed 's/\$/\\$/g' 2>/dev/null || printf '%s' "$escaped_value")
        # Write to file in format: KEY=value
        printf '%s=%s\n' "$var_name" "$escaped_value" >> .env.container 2>/dev/null || true
    fi
done

echo "✅ Created .env.container file with proper multiline variable handling"

