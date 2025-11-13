#!/bin/bash
# Script to create .env file compatible with GitHub Actions
# Automatically detects and fixes multiline environment variables
# For multiline values, replaces newlines with spaces to keep format valid
# This ensures all secrets are properly passed between workflow steps

# First, fix any multiline variables in GITHUB_ENV
# This handles cases where vars from env: section were split into multiple variables
if [ -n "$GITHUB_ENV" ]; then
    # Read env output directly to catch orphaned variables (those with invalid names)
    # These appear when multiline values are split
    env_output=$(/usr/bin/env 2>/dev/null || printenv 2>/dev/null || true)
    
    # Process env output line by line to reconstruct split variables
    current_var=""
    current_value=""
    orphaned_lines=()
    
    while IFS= read -r line || [ -n "$line" ]; do
        [ -z "$line" ] && continue
        
        # Check if line has format KEY=value
        if [[ "$line" =~ ^([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]]; then
            # Save previous variable if it exists
            if [ -n "$current_var" ]; then
                single_line_value=$(printf '%s' "$current_value" | tr '\n' ' ' | sed 's/[[:space:]]*$//' | sed 's/[[:space:]]\+/ /g')
                echo "${current_var}=${single_line_value}" >> "$GITHUB_ENV"
            fi
            
            # Start new variable
            current_var="${BASH_REMATCH[1]}"
            current_value="${BASH_REMATCH[2]}"
            orphaned_lines=()
        else
            # This is an orphaned line (no =, likely continuation of multiline value)
            # Check if it looks like a continuation (starts with Key: or just a value)
            if [[ "$line" =~ ^[A-Za-z0-9_]+:[[:space:]] ]] || [[ "$line" =~ ^[A-Za-z0-9_]+:[[:space:]]*$ ]]; then
                # This looks like a continuation - add to current value
                if [ -n "$current_var" ]; then
                    current_value="${current_value} ${line}"
                else
                    orphaned_lines+=("$line")
                fi
            fi
        fi
    done <<EOF
$env_output
EOF
    
    # Save last variable if exists
    if [ -n "$current_var" ]; then
        single_line_value=$(printf '%s' "$current_value" | tr '\n' ' ' | sed 's/[[:space:]]*$//' | sed 's/[[:space:]]\+/ /g')
        echo "${current_var}=${single_line_value}" >> "$GITHUB_ENV"
    fi
    
    # Also process all valid variables to fix any that contain newlines
    var_names=$(printenv | cut -d= -f1 2>/dev/null || compgen -e 2>/dev/null || true)
    
    while IFS= read -r var_name; do
        [ -z "$var_name" ] && continue
        
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

