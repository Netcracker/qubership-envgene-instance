# Postman Quick Start Guide

⚡ **5-minute setup** for testing GITHUB_PIPELINE_API_INPUT

## Testing Workflow

```mermaid
graph TD
    A[1. Create GitHub Token<br/>actions:write scope] --> B[2. Download Postman Collection<br/>EnvGene-Pipeline-API.json]
    B --> C[3. Import into Postman<br/>File → Import]
    C --> D[4. Configure Variables<br/>github_owner, github_repo, github_token]
    D --> E[5. Test Authentication<br/>Setup & Auth Test]
    E --> F{Auth Success?}
    F -->|HTTP 200| G[6. Run Minimal Test<br/>Test - Minimal JSON]
    F -->|HTTP 401/404| H[Fix Token/Repository]
    H --> E
    G --> I{Pipeline Triggered?}
    I -->|HTTP 204| J[7. Check Execution<br/>Check Workflow Runs]
    I -->|Error| K[Debug Request]
    K --> G
    J --> L[8. Try Other Formats<br/>YAML, Key=Value, Complete]
    L --> M[9. Monitor Results<br/>GitHub Actions Tab]
    
    style A fill:#e1f5fe
    style G fill:#e8f5e8
    style J fill:#e8f5e8
    style M fill:#f3e5f5
```

## Step 1: Get GitHub Token
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select `actions:write` scope
4. Copy the token

## Step 2: Import Collection
1. Download: [EnvGene-Pipeline-API.postman_collection.json](../postman/EnvGene-Pipeline-API.postman_collection.json)
2. Open Postman → Import → Select file
3. Collection imported ✅

## Step 3: Configure Variables
1. Click on collection → Variables tab
2. Set values:
   ```
   github_owner = your-username
   github_repo = your-repo-name  
   github_token = ghp_xxxxxxxxxxxx
   github_branch = main
   ```

## Step 4: Test!

### Test 1: Basic Auth ✅
- Run: "Setup & Auth Test"
- Expected: HTTP 200 with workflow list

### Test 2: Minimal API Call ✅
- Run: "Test - Minimal JSON"
- Expected: HTTP 204 (workflow triggered)

### Test 3: Check Execution ✅
- Run: "Check Workflow Runs"
- Expected: Your workflow in the list

## Ready Requests

| Request | Purpose | Format |
|---------|---------|---------|
| Setup & Auth Test | Verify credentials | - |
| Test - Minimal JSON | Basic functionality | JSON |
| Test - Complete JSON | All parameters | JSON |
| Test - YAML Format | YAML input | YAML |
| Test - Key=Value Format | Simple format | Key=Value |
| Test - Dynamic Generation | Auto-generated data | JSON |
| Check Workflow Runs | Monitor execution | - |

## Quick Examples

### Minimal Request Body:
```json
{
  "ref": "main",
  "inputs": {
    "GITHUB_PIPELINE_API_INPUT": "{\"ENV_NAMES\": \"test-cluster/e01\", \"ENV_INVENTORY_INIT\": \"true\"}"
  }
}
```

### YAML Format:
```json
{
  "ref": "main", 
  "inputs": {
    "GITHUB_PIPELINE_API_INPUT": "ENV_NAMES: \"test-cluster/e01\"\nENV_INVENTORY_INIT: true"
  }
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| HTTP 401 | Check token permissions |
| HTTP 404 | Verify repository path |
| HTTP 422 | Ensure workflow file exists |
| No trigger | Check `ENV_NAMES` parameter |

🎉 **You're ready to test!** 