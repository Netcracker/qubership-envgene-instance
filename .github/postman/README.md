# Postman Collections for EnvGene Pipeline API

This directory contains Postman collections for testing the EnvGene Pipeline API functionality.

## Available Collections

### EnvGene-Pipeline-API.postman_collection.json

Complete collection for testing `GITHUB_PIPELINE_API_INPUT` with all supported formats.

**Includes:**
- 🔧 Setup & Auth Test
- 📋 Test - Minimal JSON
- 📋 Test - Complete JSON  
- 📋 Test - YAML Format
- 📋 Test - Key=Value Format
- 🚀 Test - Dynamic Generation (with pre-request script)
- 🔍 Check Workflow Runs

## How to Import

1. **Download the collection file**:
   - Click on `EnvGene-Pipeline-API.postman_collection.json`
   - Download or copy the raw content

2. **Import into Postman**:
   - Open Postman
   - Click "Import" button
   - Drag & drop the JSON file or paste the content
   - Click "Import"

3. **Configure variables**:
   - Go to Collection → Variables tab
   - Set these required variables:
     - `github_owner`: Your GitHub username or organization
     - `github_repo`: Your repository name
     - `github_token`: Your GitHub Personal Access Token
     - `github_branch`: Target branch (default: main)

## GitHub Token Setup

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with **`actions:write`** scope
3. Copy the token and set it as `github_token` variable in Postman

## Testing Workflow

1. **Start with "Setup & Auth Test"** to verify your token and repository access
2. **Try "Test - Minimal JSON"** for basic functionality
3. **Experiment with different formats** (YAML, Key=Value)
4. **Use "Test - Dynamic Generation"** for automated testing with random data
5. **Monitor execution** with "Check Workflow Runs"

## Expected Responses

- **Success**: HTTP 204 No Content
- **Authentication Error**: HTTP 401
- **Repository Not Found**: HTTP 404
- **Invalid Workflow**: HTTP 422

## Troubleshooting

- Ensure your token has `actions:write` permission
- Verify the workflow file `pipeline-api.yml` exists in `.github/workflows/`
- Check that `ENV_NAMES` is provided in all test requests
- Use Postman Console to debug pre-request scripts 