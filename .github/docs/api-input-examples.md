# GITHUB_PIPELINE_API_INPUT Examples

The new `GITHUB_PIPELINE_API_INPUT` variable allows passing all pipeline parameters through a single string in various formats.

> **Important**: This variable is only used in the API workflow (`pipeline-api.yml`). For regular UI use, use standard inputs in `pipeline.yml`.

## Supported Formats

### 1. JSON Format

```json
{
  "ENV_NAMES": "test-cluster/e01",
  "ENV_TEMPLATE_VERSION": "1.0.0",
  "ENV_INVENTORY_INIT": "true",
  "GENERATE_EFFECTIVE_SET": "false",
  "ENV_TEMPLATE_TEST": "false",
  "ENV_TEMPLATE_NAME": "my-template",
  "SD_DATA": "{\"key\": \"value\"}",
  "SD_VERSION": "1.0.0",
  "SD_SOURCE_TYPE": "git",
  "SD_DELTA": "false",
  "ENV_SPECIFIC_PARAMETERS": "{\"param1\": \"value1\"}"
}
```

> Note: Only `ENV_NAMES` is required. `ENV_TEMPLATE_VERSION` can be omitted if template data is stored in env_definition files.

### 2. YAML Format

```yaml
ENV_NAMES: "test-cluster/e01"
ENV_TEMPLATE_VERSION: "1.0.0"  # Optional
ENV_INVENTORY_INIT: true
GENERATE_EFFECTIVE_SET: false
ENV_TEMPLATE_TEST: false
ENV_TEMPLATE_NAME: my-template
SD_DATA: '{"key": "value"}'
SD_VERSION: "1.0.0"
SD_SOURCE_TYPE: git
SD_DELTA: false
ENV_SPECIFIC_PARAMETERS: '{"param1": "value1"}'
```

### 3. Key=Value Format

```
ENV_NAMES=test-cluster/e01
ENV_TEMPLATE_VERSION=1.0.0
ENV_INVENTORY_INIT=true
GENERATE_EFFECTIVE_SET=false
ENV_TEMPLATE_TEST=false
ENV_TEMPLATE_NAME=my-template
SD_DATA={"key": "value"}
SD_VERSION=1.0.0
SD_SOURCE_TYPE=git
SD_DELTA=false
ENV_SPECIFIC_PARAMETERS={"param1": "value1"}
```

## Variable Priority

Variables are processed in the following order:

1. **Required inputs** (ENV_NAMES, etc.) - always have priority
2. **GITHUB_PIPELINE_API_INPUT** - overrides default values
3. **pipeline_vars.yaml** - used as fallback for unset variables

## Validation

The script automatically validates variables by type:

- **Boolean variables**: `ENV_INVENTORY_INIT`, `GENERATE_EFFECTIVE_SET`, `ENV_TEMPLATE_TEST`, `SD_DELTA`, `ENV_BUILDER`, `GET_PASSPORT`, `CMDB_IMPORT`
- **JSON variables**: `SD_DATA`, `ENV_SPECIFIC_PARAMETERS`
- **String variables**: all others

## API Usage Examples

### Example 1: Minimal JSON Set (without template version)

```bash
curl -X POST \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/OWNER/REPO/actions/workflows/pipeline-api.yml/dispatches \
  -d '{
    "ref": "main",
    "inputs": {
      "GITHUB_PIPELINE_API_INPUT": "{\"ENV_NAMES\": \"test-cluster/e01\", \"ENV_INVENTORY_INIT\": \"true\", \"GENERATE_EFFECTIVE_SET\": \"true\"}"
    }
  }'
```

### Example 1.1: With template version

```bash
curl -X POST \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/OWNER/REPO/actions/workflows/pipeline-api.yml/dispatches \
  -d '{
    "ref": "main",
    "inputs": {
      "GITHUB_PIPELINE_API_INPUT": "{\"ENV_NAMES\": \"test-cluster/e01\", \"ENV_TEMPLATE_VERSION\": \"1.0.0\", \"ENV_INVENTORY_INIT\": \"true\", \"GENERATE_EFFECTIVE_SET\": \"true\"}"
    }
  }'
```

### Example 2: Full YAML Format Set

```bash
GITHUB_PIPELINE_API_INPUT='
ENV_NAMES: "test-cluster/e01,test-cluster/e02"
ENV_TEMPLATE_VERSION: "2.1.0"
ENV_INVENTORY_INIT: true
GENERATE_EFFECTIVE_SET: true
ENV_TEMPLATE_TEST: false
ENV_TEMPLATE_NAME: my-template
SD_DATA: "{\"environment\": \"production\"}"
SD_VERSION: "2.1.0"
SD_SOURCE_TYPE: git
SD_DELTA: false
ENV_SPECIFIC_PARAMETERS: "{\"cluster_size\": \"large\"}"
'

curl -X POST \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/OWNER/REPO/actions/workflows/pipeline-api.yml/dispatches \
  -d "{
    \"ref\": \"main\",
    \"inputs\": {
      \"GITHUB_PIPELINE_API_INPUT\": \"$GITHUB_PIPELINE_API_INPUT\"
    }
  }"
```

### Example 3: Key=Value Format (minimal)

```bash
curl -X POST \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/OWNER/REPO/actions/workflows/pipeline-api.yml/dispatches \
  -d '{
    "ref": "main",
    "inputs": {
      "GITHUB_PIPELINE_API_INPUT": "ENV_NAMES=test-cluster/e01\nENV_INVENTORY_INIT=true\nGENERATE_EFFECTIVE_SET=true\nENV_TEMPLATE_NAME=my-template"
    }
  }'
```

### Example 4: Complete Parameter Set (All Available Variables)

This example demonstrates all possible parameters that can be passed through `GITHUB_PIPELINE_API_INPUT`:

#### JSON Format (Complete)

```bash
curl -X POST \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/OWNER/REPO/actions/workflows/pipeline-api.yml/dispatches \
  -d '{
    "ref": "main",
    "inputs": {
      "GITHUB_PIPELINE_API_INPUT": "{\"ENV_NAMES\": \"test-cluster/e01,test-cluster/e02\", \"DEPLOYMENT_TICKET_ID\": \"DEPLOY-12345\", \"ENV_TEMPLATE_VERSION\": \"2.1.0\", \"ENV_BUILDER\": \"true\", \"GET_PASSPORT\": \"false\", \"CMDB_IMPORT\": \"true\", \"ENV_INVENTORY_INIT\": \"true\", \"GENERATE_EFFECTIVE_SET\": \"true\", \"ENV_TEMPLATE_TEST\": \"false\", \"ENV_TEMPLATE_NAME\": \"production-template\", \"SD_DATA\": \"{\\\"region\\\": \\\"us-east-1\\\", \\\"instanceType\\\": \\\"m5.large\\\"}\", \"SD_VERSION\": \"3.2.1\", \"SD_SOURCE_TYPE\": \"git\", \"SD_DELTA\": \"false\", \"ENV_SPECIFIC_PARAMETERS\": \"{\\\"replicas\\\": 3, \\\"memory\\\": \\\"2Gi\\\"}\"}"
    }
  }'
```

#### YAML Format (Complete)

```bash
GITHUB_PIPELINE_API_INPUT='
ENV_NAMES: "test-cluster/e01,test-cluster/e02"
DEPLOYMENT_TICKET_ID: "DEPLOY-12345"
ENV_TEMPLATE_VERSION: "2.1.0"
ENV_BUILDER: "true"
GET_PASSPORT: "false"
CMDB_IMPORT: "true"
ENV_INVENTORY_INIT: true
GENERATE_EFFECTIVE_SET: true
ENV_TEMPLATE_TEST: false
ENV_TEMPLATE_NAME: "production-template"
SD_DATA: "{\"region\": \"us-east-1\", \"instanceType\": \"m5.large\"}"
SD_VERSION: "3.2.1"
SD_SOURCE_TYPE: "git"
SD_DELTA: false
ENV_SPECIFIC_PARAMETERS: "{\"replicas\": 3, \"memory\": \"2Gi\"}"
'

curl -X POST \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/OWNER/REPO/actions/workflows/pipeline-api.yml/dispatches \
  -d "{
    \"ref\": \"main\",
    \"inputs\": {
      \"GITHUB_PIPELINE_API_INPUT\": \"$GITHUB_PIPELINE_API_INPUT\"
    }
  }"
```

#### Key=Value Format (Complete)

```bash
curl -X POST \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/OWNER/REPO/actions/workflows/pipeline-api.yml/dispatches \
  -d '{
    "ref": "main",
    "inputs": {
      "GITHUB_PIPELINE_API_INPUT": "ENV_NAMES=test-cluster/e01,test-cluster/e02\nDEPLOYMENT_TICKET_ID=DEPLOY-12345\nENV_TEMPLATE_VERSION=2.1.0\nENV_BUILDER=true\nGET_PASSPORT=false\nCMDB_IMPORT=true\nENV_INVENTORY_INIT=true\nGENERATE_EFFECTIVE_SET=true\nENV_TEMPLATE_TEST=false\nENV_TEMPLATE_NAME=production-template\nSD_DATA={\"region\": \"us-east-1\", \"instanceType\": \"m5.large\"}\nSD_VERSION=3.2.1\nSD_SOURCE_TYPE=git\nSD_DELTA=false\nENV_SPECIFIC_PARAMETERS={\"replicas\": 3, \"memory\": \"2Gi\"}"
    }
  }'
```

#### Parameter Descriptions

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ENV_NAMES` | string | **required** | Comma-separated list of environments to process |
| `DEPLOYMENT_TICKET_ID` | string | "" | Optional deployment ticket identifier |
| `ENV_TEMPLATE_VERSION` | string | "" | Template version, can be omitted if stored in env_definition |
| `ENV_BUILDER` | boolean | true | Enable environment building |
| `GET_PASSPORT` | boolean | false | Enable passport retrieval |
| `CMDB_IMPORT` | boolean | false | Enable CMDB import |
| `ENV_INVENTORY_INIT` | boolean | false | Initialize environment inventory |
| `GENERATE_EFFECTIVE_SET` | boolean | false | Generate effective configuration set |
| `ENV_TEMPLATE_TEST` | boolean | false | Enable template testing mode |
| `ENV_TEMPLATE_NAME` | string | "" | Name of the environment template |
| `SD_DATA` | JSON string | "{}" | Service discovery data in JSON format |
| `SD_VERSION` | string | "" | Service discovery version |
| `SD_SOURCE_TYPE` | string | "" | Source type for service discovery (e.g., "git") |
| `SD_DELTA` | boolean | false | Enable delta processing for service discovery |
| `ENV_SPECIFIC_PARAMETERS` | JSON string | "{}" | Environment-specific parameters in JSON format |

## Debugging

The script outputs detailed information about variable processing:

```
Processing GITHUB_PIPELINE_API_INPUT: {"ENV_INVENTORY_INIT": "true"}
Parsed variables from API input:
  ENV_INVENTORY_INIT=true
Successfully processed 1 variables from API input
```

## Error Handling

- If GITHUB_PIPELINE_API_INPUT is empty or not specified - script is skipped
- Invalid JSON/YAML formats are automatically processed as key=value
- Incorrect data types are logged with warnings
- Pipeline continues execution even with parsing errors 