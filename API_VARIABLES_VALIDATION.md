# API Variables Validation Guide

## Overview
This document describes all available variables for the EnvGene pipeline when triggered via API, their validation rules, and usage examples.

## Available Variables

### Required Variables (API Mode)
| Variable | Type | Description | Validation |
|----------|------|-------------|------------|
| `ENV_NAMES` | string | Comma-separated list of environment names | Must contain at least one valid environment name with "/" separator |

### Recommended Variables (API Mode)
| Variable | Type | Description | Validation |
|----------|------|-------------|------------|
| `DEPLOYMENT_TICKET_ID` | string | ID of the deployment ticket | Optional but recommended for tracking |
| `ENV_TEMPLATE_VERSION` | string | Version of the environment template | Optional but recommended for reproducibility |

### Boolean Variables
| Variable | Default | Description | Validation |
|----------|---------|-------------|------------|
| `ENV_BUILDER` | true | Enable environment building | Must be "true" or "false" |
| `GET_PASSPORT` | false | Enable passport retrieval | Must be "true" or "false" |
| `CMDB_IMPORT` | false | Enable CMDB import | Must be "true" or "false" |
| `ENV_INVENTORY_INIT` | false | Initialize environment inventory | Must be "true" or "false" |
| `GENERATE_EFFECTIVE_SET` | false | Generate effective set | Must be "true" or "false" |
| `ENV_TEMPLATE_TEST` | false | Test environment template | Must be "true" or "false" |
| `SD_DELTA` | false | Enable SD delta processing | Must be "true" or "false" |
| `CRED_ROTATION_FORCE` | false | Force credential rotation | Must be "true" or "false" |

### String Variables
| Variable | Default | Description | Validation |
|----------|---------|-------------|------------|
| `ENV_TEMPLATE_NAME` | "" | Name of the environment template | String |
| `SD_VERSION` | "" | Version of SD data | String |
| `SD_SOURCE_TYPE` | "" | Type of SD source | String |

### JSON Variables
| Variable | Default | Description | Validation |
|----------|---------|-------------|------------|
| `SD_DATA` | "{}" | SD data in JSON format | Valid JSON object |
| `ENV_SPECIFIC_PARAMETERS` | "{}" | Environment-specific parameters | Valid JSON object |
| `CRED_ROTATION_PAYLOAD` | "{}" | Credential rotation payload | Complex JSON structure (see below) |

## CRED_ROTATION_PAYLOAD Structure

The `CRED_ROTATION_PAYLOAD` must follow this structure:

```json
{
  "rotation_items": [
    {
      "namespace": "<namespace>",
      "application": "<application-name>",  // optional
      "context": "enum[`pipeline`,`deployment`, `runtime`]",
      "parameter_key": "<parameter-key>",
      "parameter_value": "<new-parameter-value>"
    }
  ]
}
```

### CRED_ROTATION_PAYLOAD Validation Rules:
- Must be valid JSON
- Must contain `rotation_items` array
- Each item must have required fields: `namespace`, `context`, `parameter_key`, `parameter_value`
- `application` field is optional
- `context` must be one of: `pipeline`, `deployment`, `runtime`
- All string values must be non-empty

## API Input Format Examples

### Basic Example
```json
{
  "ref": "main",
  "inputs": {
    "GITHUB_PIPELINE_API_INPUT": "{\"ENV_NAMES\": \"test-cluster/e01,test-cluster/e02\", \"ENV_BUILDER\": \"true\", \"DEPLOYMENT_TICKET_ID\": \"TEST-TICKET-1\", \"ENV_TEMPLATE_VERSION\": \"qubership_envgene_templates:0.0.2\"}"
  }
}
```

### Advanced Example with Credential Rotation
```json
{
  "ref": "main",
  "inputs": {
    "GITHUB_PIPELINE_API_INPUT": "{\"ENV_NAMES\": \"test-cluster/e01\", \"ENV_BUILDER\": \"true\", \"DEPLOYMENT_TICKET_ID\": \"TEST-TICKET-1\", \"ENV_TEMPLATE_VERSION\": \"qubership_envgene_templates:0.0.2\", \"CRED_ROTATION_PAYLOAD\": \"{\\\"rotation_items\\\":[{\\\"namespace\\\":\\\"e01-bss\\\",\\\"application\\\":\\\"postgres\\\",\\\"context\\\":\\\"deployment\\\",\\\"parameter_key\\\":\\\"POSTGRES_DBA_USER\\\",\\\"parameter_value\\\":\\\"new_user\\\"}]}\", \"CRED_ROTATION_FORCE\": \"true\"}"
  }
}
```

### Key-Value Format Example
```json
{
  "ref": "main",
  "inputs": {
    "GITHUB_PIPELINE_API_INPUT": "ENV_NAMES=test-cluster/e01,test-cluster/e02\nENV_BUILDER=true\nDEPLOYMENT_TICKET_ID=TEST-TICKET-1\nENV_TEMPLATE_VERSION=qubership_envgene_templates:0.0.2"
  }
}
```

## Validation Rules

### API Mode Specific Validations:
1. **ENV_NAMES is required** - Must be provided and contain at least one valid environment
2. **Environment name format** - Must contain "/" separator (e.g., "test-cluster/e01")
3. **No empty environment names** - Each environment name must be non-empty
4. **CRED_ROTATION_PAYLOAD validation** - If provided, must follow the specified structure
5. **JSON validation** - All JSON variables must be valid JSON objects

### Error Handling:
- Missing required variables will cause the pipeline to fail with clear error messages
- Invalid JSON will cause validation errors with helpful suggestions
- Malformed environment names will trigger warnings but may not fail the pipeline
- Empty or whitespace-only values will be treated as missing values

## Debug Information

The pipeline provides extensive debug information for API mode:
- Shows which variables were loaded from API input vs. defaults
- Validates and reports on each environment name
- Provides detailed error messages for validation failures
- Shows the final processed values for all variables

## Troubleshooting

### Common Issues:
1. **ENV_NAMES not found** - Ensure the JSON string is properly formatted
2. **YAML parsing issues** - Use proper JSON format instead of YAML-like strings
3. **Missing required variables** - Check that all required variables are included
4. **Invalid JSON** - Validate JSON structure before sending

### Debug Commands:
- Check pipeline logs for detailed validation information
- Look for "🔍" prefixed debug messages
- Verify environment variable processing in the "Input Parameters Processing" job 