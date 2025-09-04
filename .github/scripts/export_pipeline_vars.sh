#!/bin/bash
# 
# Export Pipeline Variables Script (Simplified)
# Exports only pipeline variables from JSON to current shell session
#

set -euo pipefail

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

# Main function
main() {
    local variables_json="${1:-}"
    
    if [ -z "$variables_json" ] || [ "$variables_json" = "{}" ] || [ "$variables_json" = "null" ]; then
        log "⚠️ No variables to export (empty or null JSON)"
        return 0
    fi
    
    log "🔧 Exporting pipeline variables from JSON..."
    
    # Validate JSON
    if ! echo "$variables_json" | jq . >/dev/null 2>&1; then
        log "❌ Invalid JSON format"
        log "Raw input: $variables_json"
        return 1
    fi
    
    local exported_count=0
    
    # Export variables using process substitution to avoid subshell issues
    while IFS= read -r export_cmd; do
        if [ -n "$export_cmd" ]; then
            eval "$export_cmd"
            ((exported_count++))
        fi
    done < <(echo "$variables_json" | jq -r 'to_entries[] | select(.value != null and .value != "") | "export \(.key)=\"\(.value)\""')
    
    log "✅ Successfully exported $exported_count pipeline variables to GITHUB_ENV"
    return 0
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
