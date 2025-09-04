#!/bin/bash
# 
# Universal Export Variables Script
# Exports pipeline variables and common configuration variables
#

set -euo pipefail

# Function to log messages
log() {
    echo "🔧 [export_vars] $*"
}

# Function to export common configuration variables
export_common_config() {
    log "Exporting common configuration variables..."
    
    # Export CI/GitHub system variables (if they exist)
    [ -n "${CI_PROJECT_DIR:-}" ] && export CI_PROJECT_DIR
    [ -n "${SECRET_KEY:-}" ] && export SECRET_KEY
    [ -n "${GITHUB_ACTIONS:-}" ] && export GITHUB_ACTIONS
    [ -n "${GITHUB_REPOSITORY:-}" ] && export GITHUB_REPOSITORY
    [ -n "${GITHUB_REF_NAME:-}" ] && export GITHUB_REF_NAME
    [ -n "${GITHUB_USER_EMAIL:-}" ] && export GITHUB_USER_EMAIL
    [ -n "${GITHUB_USER_NAME:-}" ] && export GITHUB_USER_NAME
    [ -n "${GITHUB_TOKEN:-}" ] && export GITHUB_TOKEN
    
    # Export common build configuration variables
    export INSTANCES_DIR="${CI_PROJECT_DIR}/environments"
    export module_ansible_dir="/module/ansible"
    export module_inventory="${CI_PROJECT_DIR}/configuration/inventory.yaml"
    export module_ansible_cfg="/module/ansible/ansible.cfg"
    export module_config_default="/module/templates/defaults.yaml"
    export envgen_args=" -vvv"
    export envgen_debug="true"
    export GIT_STRATEGY="none"
    export COMMIT_ENV="true"
    
    log "✅ Common configuration variables exported"
}

# Function to export job-specific variables
export_job_variables() {
    local matrix_environment="${1:-}"
    
    if [ -n "$matrix_environment" ]; then
        log "Exporting job-specific variables for environment: $matrix_environment"
        
        # Extract and export environment-specific variables
        export ENV_NAMES="$matrix_environment"
        export CLUSTER_NAME=$(echo "$matrix_environment" | cut -d'/' -f1)
        export ENVIRONMENT_NAME=$(echo "$matrix_environment" | cut -d'/' -f2 | xargs)
        export ENV_NAME="$ENVIRONMENT_NAME"
        export ENV_NAME_SHORT=$(echo "$ENV_NAME" | awk -F "/" '{print $NF}')
        
        log "  ENV_NAMES: $ENV_NAMES"
        log "  CLUSTER_NAME: $CLUSTER_NAME"
        log "  ENVIRONMENT_NAME: $ENVIRONMENT_NAME"
    fi
}

# Function to export variables from JSON
export_pipeline_variables() {
    local variables_json="${1:-}"
    
    if [ -z "$variables_json" ] || [ "$variables_json" = "{}" ] || [ "$variables_json" = "null" ]; then
        log "⚠️ No pipeline variables to export (empty or null JSON)"
        return 0
    fi
    
    log "Exporting pipeline variables from JSON..."
    
    # Validate JSON
    if ! echo "$variables_json" | jq . >/dev/null 2>&1; then
        log "❌ Invalid JSON format: $variables_json"
        return 1
    fi
    
    local exported_count=0
    
    # Export variables using process substitution to avoid subshell issues
    while IFS= read -r export_cmd; do
        if [ -n "$export_cmd" ]; then
            echo "  $export_cmd"
            eval "$export_cmd"
            ((exported_count++))
        fi
    done < <(echo "$variables_json" | jq -r 'to_entries[] | select(.value != null and .value != "") | "export \(.key)=\"\(.value)\""')
    
    log "✅ Successfully exported $exported_count pipeline variables"
    return 0
}

# Main function
main() {
    local variables_json="${1:-}"
    local matrix_environment="${2:-}"
    
    log "🚀 Starting variable export process..."
    
    # 1. Export pipeline variables from JSON
    export_pipeline_variables "$variables_json"
    
    # 2. Export common configuration variables
    export_common_config
    
    # 3. Export job-specific variables (if matrix environment provided)
    export_job_variables "$matrix_environment"
    
    log "🎉 Variable export completed successfully"
}

# Auto-run main function when script is sourced with arguments
if [ "$#" -gt 0 ]; then
    main "$@"
fi
