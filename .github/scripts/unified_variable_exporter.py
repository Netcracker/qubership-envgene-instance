#!/usr/bin/env python3
"""
Unified Variable Exporter for EnvGene Pipeline Steps
====================================================

This script provides a unified way to export all environment variables needed for:
- Generate inventory
- Credential Rotation  
- Build Env
- Generate Effective Set
- Git Commit

It handles variables from multiple sources:
1. Pipeline variables (pipeline_vars.yaml)
2. GitHub workflow inputs
3. API input (GITHUB_PIPELINE_API_INPUT)
4. System environment variables
5. Job-specific variables

Usage:
    python unified_variable_exporter.py [--step STEP_NAME] [--matrix-env ENV_NAME] [--variables-json JSON_STRING]
"""

import os
import sys
import json
import yaml
import argparse
from typing import Dict, Any, Optional, List
from pathlib import Path


class UnifiedVariableExporter:
    """Unified variable exporter for all pipeline steps"""
    
    def __init__(self, step_name: str = None, matrix_environment: str = None, variables_json: str = None):
        self.step_name = step_name
        self.matrix_environment = matrix_environment
        self.variables_json = variables_json
        self.exported_vars = {}
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with step context"""
        step_prefix = f"[{self.step_name}]" if self.step_name else "[UNIFIED]"
        print(f"🔧 {step_prefix} {message}")
    
    def export_pipeline_vars_from_yaml(self) -> int:
        """Export variables from pipeline_vars.yaml file"""
        self.log("Loading variables from pipeline_vars.yaml...")
        
        pipeline_vars_file = ".github/pipeline_vars.yaml"
        if not os.path.exists(pipeline_vars_file):
            self.log("⚠️  pipeline_vars.yaml not found, skipping", "WARN")
            return 0
        
        try:
            with open(pipeline_vars_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Parse YAML-like format (key: value pairs)
            variables = {}
            for line_num, line in enumerate(content.split('\n'), 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    
                    variables[key] = value
                    self.log(f"  Found: {key} = {value}")
            
            # Export to environment
            for key, value in variables.items():
                os.environ[key] = value
                self.exported_vars[key] = value
            
            self.log(f"✅ Exported {len(variables)} variables from pipeline_vars.yaml")
            return len(variables)
            
        except Exception as e:
            self.log(f"❌ Error loading pipeline_vars.yaml: {e}", "ERROR")
            return 0
    
    def export_github_inputs(self) -> int:
        """Export GitHub workflow input variables"""
        self.log("Loading GitHub workflow input variables...")
        
        # Common GitHub inputs that are available in all steps
        github_inputs = {
            'DEPLOYMENT_TICKET_ID': os.getenv('DEPLOYMENT_TICKET_ID', ''),
            'ENV_NAMES': os.getenv('ENV_NAMES', ''),
            'ENV_BUILDER': os.getenv('ENV_BUILDER', ''),
            'GET_PASSPORT': os.getenv('GET_PASSPORT', ''),
            'CMDB_IMPORT': os.getenv('CMDB_IMPORT', ''),
            'ENV_TEMPLATE_VERSION': os.getenv('ENV_TEMPLATE_VERSION', ''),
            'GENERATE_EFFECTIVE_SET': os.getenv('GENERATE_EFFECTIVE_SET', ''),
            'GITHUB_PIPELINE_API_INPUT': os.getenv('GITHUB_PIPELINE_API_INPUT', '')
        }
        
        # Export non-empty values
        exported_count = 0
        for key, value in github_inputs.items():
            if value and value.strip():
                os.environ[key] = value
                self.exported_vars[key] = value
                self.log(f"  Input: {key} = {value}")
                exported_count += 1
        
        self.log(f"✅ Exported {exported_count} GitHub input variables")
        return exported_count
    
    def export_api_input_variables(self) -> int:
        """Export variables from GITHUB_PIPELINE_API_INPUT"""
        api_input = os.getenv('GITHUB_PIPELINE_API_INPUT', '')
        
        if not api_input or api_input.strip() == '':
            self.log("No API input provided, skipping API variable export")
            return 0
        
        self.log(f"Processing API input ({len(api_input)} chars)...")
        
        try:
            # Try to parse as JSON first
            try:
                api_vars = json.loads(api_input)
                if isinstance(api_vars, dict):
                    self.log("Parsed API input as JSON")
                else:
                    raise ValueError("API input is not a JSON object")
            except (json.JSONDecodeError, ValueError):
                # Fall back to key=value format
                self.log("Parsing API input as key=value pairs")
                api_vars = {}
                for line in api_input.split('\n'):
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        api_vars[key] = value
            
            # Export API variables
            exported_count = 0
            for key, value in api_vars.items():
                if value and str(value).strip() and str(value) != 'null':
                    os.environ[key] = str(value)
                    self.exported_vars[key] = str(value)
                    self.log(f"  API: {key} = {str(value)}")
                    exported_count += 1
            
            self.log(f"✅ Exported {exported_count} variables from API input")
            return exported_count
            
        except Exception as e:
            self.log(f"❌ Error processing API input: {e}", "ERROR")
            return 0
    
    def export_variables_from_json(self) -> int:
        """Export variables from provided JSON string"""
        if not self.variables_json or self.variables_json.strip() in ['{}', 'null', '']:
            self.log("No variables JSON provided, skipping JSON export")
            return 0
        
        try:
            variables = json.loads(self.variables_json)
            if not isinstance(variables, dict):
                self.log("❌ Variables JSON is not a dictionary", "ERROR")
                return 0
            
            exported_count = 0
            for key, value in variables.items():
                if value is not None and str(value).strip() and str(value) != 'null':
                    os.environ[key] = str(value)
                    self.exported_vars[key] = str(value)
                    self.log(f"  JSON: {key} = {str(value)}")
                    exported_count += 1
            
            self.log(f"✅ Exported {exported_count} variables from JSON")
            return exported_count
            
        except json.JSONDecodeError as e:
            self.log(f"❌ Error parsing variables JSON: {e}", "ERROR")
            return 0
    
    def export_system_variables(self) -> int:
        """Export essential system variables"""
        self.log("Exporting system variables...")
        
        # Essential system variables that should be available in all steps
        system_vars = {
            'CI_PROJECT_DIR': os.getenv('CI_PROJECT_DIR', ''),
            'SECRET_KEY': os.getenv('SECRET_KEY', ''),
            'GITHUB_ACTIONS': os.getenv('GITHUB_ACTIONS', ''),
            'GITHUB_REPOSITORY': os.getenv('GITHUB_REPOSITORY', ''),
            'GITHUB_REF_NAME': os.getenv('GITHUB_REF_NAME', ''),
            'GITHUB_USER_EMAIL': os.getenv('GITHUB_USER_EMAIL', ''),
            'GITHUB_USER_NAME': os.getenv('GITHUB_USER_NAME', ''),
            'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN', ''),
            'ENVGENE_AGE_PUBLIC_KEY': os.getenv('ENVGENE_AGE_PUBLIC_KEY', ''),
            'ENVGENE_AGE_PRIVATE_KEY': os.getenv('ENVGENE_AGE_PRIVATE_KEY', ''),
            'DOCKER_IMAGE_PIPEGENE': os.getenv('DOCKER_IMAGE_PIPEGENE', ''),
            'DOCKER_IMAGE_ENVGENE': os.getenv('DOCKER_IMAGE_ENVGENE', ''),
            'DOCKER_IMAGE_EFFECTIVE_SET_GENERATOR': os.getenv('DOCKER_IMAGE_EFFECTIVE_SET_GENERATOR', '')
        }
        
        exported_count = 0
        for key, value in system_vars.items():
            if value and value.strip():
                os.environ[key] = value
                self.exported_vars[key] = value
                self.log(f"  System: {key} = {value}")
                exported_count += 1
        
        self.log(f"✅ Exported {exported_count} system variables")
        return exported_count
    
    def export_job_specific_variables(self) -> int:
        """Export job-specific variables based on matrix environment"""
        if not self.matrix_environment:
            self.log("No matrix environment provided, skipping job-specific variables")
            return 0
        
        self.log(f"Exporting job-specific variables for: {self.matrix_environment}")
        
        # Extract environment components
        cluster_name = self.matrix_environment.split('/')[0] if '/' in self.matrix_environment else self.matrix_environment
        environment_name = self.matrix_environment.split('/')[1].strip() if '/' in self.matrix_environment else self.matrix_environment
        
        job_vars = {
            'FULL_ENV': self.matrix_environment,
            'ENV_NAMES': self.matrix_environment,
            'CLUSTER_NAME': cluster_name,
            'ENVIRONMENT_NAME': environment_name,
            'ENV_NAME': environment_name,
            'ENV_NAME_SHORT': environment_name.split('/')[-1] if '/' in environment_name else environment_name,
            'SANITIZED_NAME': self.matrix_environment.replace('/', '_'),
            'PROJECT_DIR': os.getcwd()
        }
        
        # Add step-specific variables
        if self.step_name:
            step_vars = self._get_step_specific_variables()
            job_vars.update(step_vars)
        
        # Export job variables
        for key, value in job_vars.items():
            os.environ[key] = value
            self.exported_vars[key] = value
            self.log(f"  Job: {key} = {value}")
        
        self.log(f"✅ Exported {len(job_vars)} job-specific variables")
        return len(job_vars)
    
    def _get_step_specific_variables(self) -> Dict[str, str]:
        """Get step-specific variables based on the current step"""
        if not self.step_name:
            return {}
        
        step_vars = {}
        
        if self.step_name in ['generate_inventory', 'credential_rotation', 'env_build', 'generate_effective_set', 'git_commit']:
            # Common variables for all steps
            ci_project_dir = os.getenv('CI_PROJECT_DIR', os.getcwd())
            
            step_vars.update({
                'INSTANCES_DIR': f"{ci_project_dir}/environments",
                'module_ansible_dir': "/module/ansible",
                'module_inventory': f"{ci_project_dir}/configuration/inventory.yaml",
                'module_ansible_cfg': "/module/ansible/ansible.cfg",
                'module_config_default': "/module/templates/defaults.yaml",
                'envgen_args': " -vvv",
                'envgen_debug': "true",
                'GIT_STRATEGY': "none",
                'COMMIT_ENV': "true"
            })
        
        if self.step_name == 'credential_rotation':
            step_vars.update({
                'CRED_ROTATION_FORCE': os.getenv('CRED_ROTATION_FORCE', ''),
                'CRED_ROTATION_PAYLOAD': os.getenv('CRED_ROTATION_PAYLOAD', ''),
                'PUBLIC_AGE_KEYS': os.getenv('PUBLIC_AGE_KEYS', '')
            })
        
        return step_vars
    
    def export_all_variables(self) -> Dict[str, Any]:
        """Export all variables from all sources"""
        self.log("🚀 Starting unified variable export process...")
        
        total_exported = 0
        
        # 1. Export pipeline variables from YAML
        total_exported += self.export_pipeline_vars_from_yaml()
        
        # 2. Export GitHub workflow inputs
        total_exported += self.export_github_inputs()
        
        # 3. Export API input variables
        total_exported += self.export_api_input_variables()
        
        # 4. Export variables from JSON
        total_exported += self.export_variables_from_json()
        
        # 5. Export system variables
        total_exported += self.export_system_variables()
        
        # 6. Export job-specific variables
        total_exported += self.export_job_specific_variables()
        
        self.log(f"🎉 Variable export completed successfully! Total: {total_exported} variables")
        
        return {
            'total_exported': total_exported,
            'exported_vars': self.exported_vars,
            'step_name': self.step_name,
            'matrix_environment': self.matrix_environment
        }
    
    def generate_export_script(self, output_file: str = None) -> str:
        """Generate a shell script with all export commands"""
        if not output_file:
            output_file = f"export_vars_{self.step_name or 'all'}.sh"
        
        script_content = f"""#!/bin/bash
# Auto-generated export script for {self.step_name or 'all steps'}
# Generated by unified_variable_exporter.py

"""
        
        for key, value in self.exported_vars.items():
            # Escape special characters in value
            escaped_value = str(value).replace('"', '\\"').replace('$', '\\$')
            script_content += f'export {key}="{escaped_value}"\n'
        
        script_content += "\n# End of auto-generated exports\n"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(script_content)
            self.log(f"✅ Export script generated: {output_file}")
        except Exception as e:
            self.log(f"❌ Error generating export script: {e}", "ERROR")
        
        return script_content


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='Unified Variable Exporter for EnvGene Pipeline')
    parser.add_argument('--step', help='Pipeline step name (generate_inventory, credential_rotation, env_build, generate_effective_set, git_commit)')
    parser.add_argument('--matrix-env', help='Matrix environment name (e.g., test-cluster/e01)')
    parser.add_argument('--variables-json', help='JSON string containing variables to export')
    parser.add_argument('--generate-script', help='Generate shell script file with export commands')
    parser.add_argument('--list-vars', action='store_true', help='List all exported variables')
    
    args = parser.parse_args()
    
    # Create exporter instance
    exporter = UnifiedVariableExporter(
        step_name=args.step,
        matrix_environment=args.matrix_env,
        variables_json=args.variables_json
    )
    
    # Export all variables
    result = exporter.export_all_variables()
    
    # Generate export script if requested
    if args.generate_script:
        exporter.generate_export_script(args.generate_script)
    
    # List variables if requested
    if args.list_vars:
        print("\n📋 Exported Variables:")
        for key, value in sorted(result['exported_vars'].items()):
            # Mask sensitive values
            if any(keyword in key.upper() for keyword in ['SECRET', 'KEY', 'TOKEN', 'PASSWORD', 'PRIVATE']):
                print(f"  {key}: ***")
            else:
                print(f"  {key}: {value}")
    
    return result


if __name__ == "__main__":
    main()
