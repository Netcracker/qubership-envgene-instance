#!/bin/bash
# Script to create .env.container file compatible with Docker --env-file
# Properly handles multiline environment variables
# For multiline values, we replace newlines with spaces to keep Docker --env-file format valid
# This ensures all secrets are properly passed to the container

# Create or truncate the output file
> .env.container

# Get all unique environment variable names
# Use compgen -e if available, otherwise fall back to parsing env output
if command -v compgen >/dev/null 2>&1; then
    var_names=$(compgen -e)
else
    var_names=$(env | cut -d= -f1 | sort -u)
fi

# Process each environment variable
while IFS= read -r var_name; do
    # Skip empty variable names
    [ -z "$var_name" ] && continue
    
    # Get the actual value using indirect variable reference
    eval "var_value=\${${var_name}}"
    
    # Skip if variable doesn't exist or is empty (but allow empty strings)
    if ! eval "[ -n \"\${${var_name}+x}\" ]"; then
        continue
    fi
    
    # Replace newlines with spaces (Docker --env-file doesn't support multiline values)
    # This ensures Docker --env-file format is valid while preserving all content
    # All values are converted to single-line format
    single_line_value=$(printf '%s' "$var_value" | tr '\n' ' ')
    # Remove trailing space if any
    single_line_value="${single_line_value% }"
    
    # Escape special characters that might cause issues in Docker env-file
    # Escape backslashes first
    escaped_value=$(printf '%s' "$single_line_value" | sed 's/\\/\\\\/g')
    # Escape dollar signs to prevent variable expansion issues
    escaped_value=$(printf '%s' "$escaped_value" | sed 's/\$/\\$/g')
    
    # Write to file in format: KEY=value
    # Use printf to ensure proper handling of special characters
    printf '%s=%s\n' "$var_name" "$escaped_value" >> .env.container
done <<EOF
$var_names
EOF

echo "✅ Created .env.container file with proper multiline variable handling"

