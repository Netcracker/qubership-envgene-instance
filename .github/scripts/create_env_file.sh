#!/bin/bash
# Script to create .env file compatible with GitHub Actions
# Automatically detects and fixes multiline environment variables
# For multiline values, replaces newlines with spaces to keep format valid
# This ensures all secrets are properly passed between workflow steps

# First, fix any multiline variables in GITHUB_ENV
# This handles cases where vars from env: section were split into multiple variables
if [ -n "$GITHUB_ENV" ] && [ -f "$GITHUB_ENV" ]; then
    # Read GITHUB_ENV file directly to see how variables are stored
    # When multiline values are split, orphaned lines appear without KEY= format
    # Use temporary file to avoid reading and writing to same file simultaneously
    temp_file=$(mktemp)
    current_var=""
    current_value=""
    declare -A processed_vars
    
    # Read GITHUB_ENV file line by line and reconstruct split variables
    while IFS= read -r line || [ -n "$line" ]; do
        [ -z "$line" ] && continue
        
        # Check if line has format KEY=value
        if [[ "$line" =~ ^([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]]; then
            # Save previous variable if exists
            if [ -n "$current_var" ] && [ -n "$current_value" ]; then
                single_line_value=$(printf '%s' "$current_value" | tr '\n' ' ' | sed 's/[[:space:]]*$//' | sed 's/[[:space:]]\+/ /g')
                echo "${current_var}=${single_line_value}" >> "$temp_file"
                processed_vars["$current_var"]=1
            fi
            
            # Start new variable
            current_var="${BASH_REMATCH[1]}"
            current_value="${BASH_REMATCH[2]}"
        else
            # This is an orphaned line (no =, likely continuation of multiline value)
            # Add it to current variable if we have one
            if [ -n "$current_var" ]; then
                current_value="${current_value} ${line}"
            fi
        fi
    done < "$GITHUB_ENV"
    
    # Save last variable if exists
    if [ -n "$current_var" ] && [ -n "$current_value" ]; then
        single_line_value=$(printf '%s' "$current_value" | tr '\n' ' ' | sed 's/[[:space:]]*$//' | sed 's/[[:space:]]\+/ /g')
        echo "${current_var}=${single_line_value}" >> "$temp_file"
        processed_vars["$current_var"]=1
    fi
    
    # Append fixed variables to GITHUB_ENV
    if [ -f "$temp_file" ] && [ -s "$temp_file" ]; then
        cat "$temp_file" >> "$GITHUB_ENV"
        rm -f "$temp_file"
    fi
    
    # Also process all valid variables to fix any that contain newlines
    # Skip variables that were already processed above
    var_names=$(printenv | cut -d= -f1 2>/dev/null || compgen -e 2>/dev/null || true)
    
    while IFS= read -r var_name; do
        [ -z "$var_name" ] && continue
        
        # Skip if already processed
        [[ -n "${processed_vars[$var_name]}" ]] && continue
        
        # Skip certain internal variables
        case "$var_name" in
            _|SHLVL|PWD|OLDPWD|GITHUB_ENV)
                continue
                ;;
        esac
        
        # Skip GitHub internal variables
        if [[ "$var_name" =~ ^GITHUB_ ]]; then
            continue
        fi
        
        # Skip variables with invalid names
        if [[ "$var_name" =~ [:\ ] ]] || [[ "$var_name" =~ ^[0-9] ]]; then
            continue
        fi
        
        # Get value and check for newlines
        var_value=$(printenv "$var_name" 2>/dev/null || true)
        [ -z "$var_value" ] && continue
        
        if printf '%s' "$var_value" | grep -q $'\n'; then
            single_line_value=$(printf '%s' "$var_value" | tr '\n' ' ' | sed 's/[[:space:]]*$//' | sed 's/[[:space:]]\+/ /g')
            echo "${var_name}=${single_line_value}" >> "$GITHUB_ENV"
        fi
    done <<EOF
$var_names
EOF
fi

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
    
    # Skip variables with invalid names (contain colons, spaces, or start with numbers)
    # These are likely continuation lines from multiline values that were split
    if [[ "$var_name" =~ [:\ ] ]] || [[ "$var_name" =~ ^[0-9] ]]; then
        continue
    fi
    
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

