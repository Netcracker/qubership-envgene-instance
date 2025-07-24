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

## Common Issues and Solutions

### "ENV_NAMES is required but not provided in API input"

This error indicates that the `ENV_NAMES` parameter is missing or empty. Check:

1. **JSON Escaping**: Ensure quotes are properly escaped in JSON strings:
   ```json
   ✅ Correct: "GITHUB_PIPELINE_API_INPUT": "{\"ENV_NAMES\": \"test-cluster/e01\"}"
   ❌ Wrong: "GITHUB_PIPELINE_API_INPUT": "{"ENV_NAMES": "test-cluster/e01"}"
   ```

2. **Empty Values**: Make sure ENV_NAMES has a non-empty value:
   ```json
   ✅ Correct: {"ENV_NAMES": "test-cluster/e01"}
   ❌ Wrong: {"ENV_NAMES": ""}
   ```

3. **Debug Steps**:
   - Use the "Debug - Test ENV_NAMES Only" request in Postman collection
   - Check GitHub Actions logs for parsing details
   - Verify the input string in the workflow logs

### Example Debug Request

```json
{
  "ref": "main",
  "inputs": {
    "GITHUB_PIPELINE_API_INPUT": "{\"ENV_NAMES\": \"test-cluster/e01\"}"
  }
}
```

If this minimal request fails, the issue is with JSON escaping or repository setup.

### Local Testing Scripts

#### Quick Test (Command Line)
Test your exact input string:

```bash
cd .github/scripts
python quick_test.py '{"ENV_NAMES": "test-cluster/e02", "ENV_BUILDER": "true"}'
```

#### Interactive Test
Full testing with multiple formats:

```bash
cd .github/scripts
python test_api_input.py
```

Both scripts will:
- Test your input string for parsing errors
- Validate ENV_NAMES presence
- Show exactly what variables are extracted
- Preview the environment matrix generation
- Confirm readiness for API calls

## Testing with Postman

### Quick Start

📥 **Import Ready-to-Use Collection**: Download and import [EnvGene-Pipeline-API.postman_collection.json](../postman/EnvGene-Pipeline-API.postman_collection.json) directly into Postman.

⚡ **5-minute setup**: See [Postman Quick Start Guide](postman-quick-start.md) for step-by-step instructions.

### Setup

1. **Create GitHub Personal Access Token**:
   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token with `actions:write` scope
   - Copy the token for use in Postman

2. **Base Configuration**:
   - **Method**: `POST`
   - **URL**: `https://api.github.com/repos/OWNER/REPO/actions/workflows/pipeline-api.yml/dispatches`
   - Replace `OWNER/REPO` with your actual repository

### Headers

```
Authorization: token YOUR_GITHUB_TOKEN
Accept: application/vnd.github.v3+json
Content-Type: application/json
```

### Body Examples

#### Example 1: Minimal Setup (JSON Body)

```json
{
  "ref": "main",
  "inputs": {
    "GITHUB_PIPELINE_API_INPUT": "{\"ENV_NAMES\": \"test-cluster/e01\", \"ENV_INVENTORY_INIT\": \"true\"}"
  }
}
```

#### Example 2: Complete Setup (JSON Body)

```json
{
  "ref": "main",
  "inputs": {
    "GITHUB_PIPELINE_API_INPUT": "{\"ENV_NAMES\": \"test-cluster/e01,test-cluster/e02\", \"DEPLOYMENT_TICKET_ID\": \"DEPLOY-12345\", \"ENV_TEMPLATE_VERSION\": \"2.1.0\", \"ENV_BUILDER\": \"true\", \"GET_PASSPORT\": \"false\", \"CMDB_IMPORT\": \"true\", \"ENV_INVENTORY_INIT\": \"true\", \"GENERATE_EFFECTIVE_SET\": \"true\", \"ENV_TEMPLATE_TEST\": \"false\", \"ENV_TEMPLATE_NAME\": \"production-template\", \"SD_DATA\": \"{\\\"region\\\": \\\"us-east-1\\\", \\\"instanceType\\\": \\\"m5.large\\\"}\", \"SD_VERSION\": \"3.2.1\", \"SD_SOURCE_TYPE\": \"git\", \"SD_DELTA\": \"false\", \"ENV_SPECIFIC_PARAMETERS\": \"{\\\"replicas\\\": 3, \\\"memory\\\": \\\"2Gi\\\"}\"}"
  }
}
```

#### Example 3: YAML Format (JSON Body)

```json
{
  "ref": "main",
  "inputs": {
    "GITHUB_PIPELINE_API_INPUT": "ENV_NAMES: \"test-cluster/e01\"\nENV_INVENTORY_INIT: true\nGENERATE_EFFECTIVE_SET: true\nENV_TEMPLATE_NAME: \"my-template\""
  }
}
```

#### Example 4: Key=Value Format (JSON Body)

```json
{
  "ref": "main",
  "inputs": {
    "GITHUB_PIPELINE_API_INPUT": "ENV_NAMES=test-cluster/e01\nENV_INVENTORY_INIT=true\nGENERATE_EFFECTIVE_SET=true\nENV_TEMPLATE_NAME=my-template"
  }
}
```

### Postman Environment Variables

Create these variables in your Postman environment for easier testing:

```
GITHUB_TOKEN = your_personal_access_token
GITHUB_OWNER = your_github_username_or_org
GITHUB_REPO = your_repository_name
GITHUB_BRANCH = main
```

Then use in your requests:

- **URL**: `https://api.github.com/repos/{{GITHUB_OWNER}}/{{GITHUB_REPO}}/actions/workflows/pipeline-api.yml/dispatches`
- **Authorization**: `token {{GITHUB_TOKEN}}`
- **Body ref**: `{{GITHUB_BRANCH}}`

### Postman Collection Structure

```
📁 EnvGene Pipeline API
├── 🔧 Setup & Auth Test
├── 📋 Test - Minimal JSON
├── 📋 Test - Complete JSON  
├── 📋 Test - YAML Format
├── 📋 Test - Key=Value Format
└── 🔍 Check Workflow Runs
```

### Response Examples

#### Success Response (HTTP 204)
```
Status: 204 No Content
```

#### Error Responses

**Invalid Token (HTTP 401)**:
```json
{
  "message": "Bad credentials",
  "documentation_url": "https://docs.github.com/rest"
}
```

**Repository Not Found (HTTP 404)**:
```json
{
  "message": "Not Found",
  "documentation_url": "https://docs.github.com/rest"
}
```

**Invalid Workflow (HTTP 422)**:
```json
{
  "message": "Workflow does not have 'workflow_dispatch' trigger",
  "documentation_url": "https://docs.github.com/rest/reference/actions#create-a-workflow-dispatch-event"
}
```

### Testing Checklist

- [ ] GitHub token has `actions:write` permission
- [ ] Repository path is correct (`OWNER/REPO`)
- [ ] Workflow file `pipeline-api.yml` exists in `.github/workflows/`
- [ ] `ENV_NAMES` is provided in the API input
- [ ] JSON strings are properly escaped (use `\"` for inner quotes)
- [ ] YAML/Key=Value formats use `\n` for line breaks

### Pre-request Script (Optional)

Add this script to automatically generate test data:

```javascript
// Generate random deployment ticket ID
const ticketId = "DEPLOY-" + Math.floor(Math.random() * 99999);

// Set current timestamp
const timestamp = new Date().toISOString();

// Create dynamic API input
const apiInput = {
    ENV_NAMES: "test-cluster/e01",
    DEPLOYMENT_TICKET_ID: ticketId,
    ENV_INVENTORY_INIT: "true",
    GENERATE_EFFECTIVE_SET: "true",
    ENV_TEMPLATE_NAME: "test-template-" + timestamp.slice(0,10)
};

// Set as environment variable
pm.environment.set("DYNAMIC_API_INPUT", JSON.stringify(apiInput));
```

Then use in body:
```json
{
  "ref": "main",
  "inputs": {
    "GITHUB_PIPELINE_API_INPUT": "{{DYNAMIC_API_INPUT}}"
  }
}
```

### Monitoring Workflow Execution

After successful trigger, monitor the execution:

**Get Workflow Runs**:
- **Method**: `GET`
- **URL**: `https://api.github.com/repos/{{GITHUB_OWNER}}/{{GITHUB_REPO}}/actions/runs`
- **Headers**: `Authorization: token {{GITHUB_TOKEN}}`

Check the most recent run for your pipeline execution results. 