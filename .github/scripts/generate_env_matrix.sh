#!/bin/bash
# 
# Generate environment matrix from ENV_NAMES
# Creates a JSON array of environments for GitHub Actions matrix strategy
#

set -euo pipefail

# Function to log messages
log() {
    echo "🔧 [env_matrix] $*"
}

# Function to generate environment matrix
generate_env_matrix() {
    local env_names="${1:-}"
    
    log "Generating environment matrix from ENV_NAMES..."
    log "ENV_NAMES value: '$env_names'"
    log "ENV_NAMES length: ${#env_names}"
    log "ENV_NAMES contains comma: $(echo "$env_names" | grep -c ',' || echo '0')"
    
    # Check if ENV_NAMES is empty
    if [ -z "$env_names" ]; then
        log "❌ ERROR: ENV_NAMES is empty or not set!"
        log "This likely means the input processing failed."
        log "Creating empty matrix to skip downstream jobs..."
        echo 'env_matrix=[]'
        return 0
    fi

    # Validate ENV_NAMES is not just whitespace
    if [ -z "$(echo "$env_names" | tr -d '[:space:]')" ]; then
        log "❌ ERROR: ENV_NAMES contains only whitespace!"
        log "Creating empty matrix to skip downstream jobs..."
        echo 'env_matrix=[]'
        return 0
    fi

    # Build JSON array
    local arr="["
    local first=1
    local count=0
    
    for name in $(echo "$env_names" | tr ',' ' '); do
        # Skip empty names
        if [ -n "$(echo "$name" | tr -d '[:space:]')" ]; then
            log "Processing environment: '$name'"
            if [ "$first" = 1 ]; then
                first=0
            else
                arr="$arr,"
            fi
            arr="$arr\"$name\""
            count=$((count + 1))
        fi
    done
    arr="$arr]"

    # Check if any valid environments were found
    if [ "$count" -eq 0 ]; then
        log "❌ ERROR: No valid environments found in ENV_NAMES!"
        log "Creating empty matrix to skip downstream jobs..."
        echo 'env_matrix=[]'
        return 0
    fi

    log "Generated matrix with $count environment(s): $arr"
    echo "env_matrix=$arr"
}

# Main execution
main() {
    local env_names="${ENV_NAMES:-}"
    
    # Generate matrix and output to GitHub Actions output
    local matrix_output
    matrix_output=$(generate_env_matrix "$env_names")
    
    # Write to GitHub Actions output
    if [ -n "${GITHUB_OUTPUT:-}" ]; then
        echo "$matrix_output" >> "$GITHUB_OUTPUT"
        log "✅ Matrix written to GITHUB_OUTPUT"
    else
        echo "$matrix_output"
        log "⚠️  GITHUB_OUTPUT not available, printing to stdout"
    fi
}

# Run main function
main "$@"
