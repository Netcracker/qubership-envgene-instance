# Workflow Modes: UI vs API

The system supports two different execution modes:

## UI Mode (pipeline.yml)

**Purpose**: For manual execution through GitHub Actions UI

**Features**:
- Uses standard GitHub Actions inputs
- All variables are entered through UI form
- `GITHUB_PIPELINE_API_INPUT` variable is unavailable
- Additional variables are loaded from `pipeline_vars.yaml`

**Usage**:
1. Navigate to GitHub Actions
2. Select "EnvGene Execution"
3. Click "Run workflow"
4. Fill out the form with parameters

**Available inputs**:
- `ENV_NAMES` (required)
- `DEPLOYMENT_TICKET_ID` (optional)
- `ENV_TEMPLATE_VERSION` (optional)
- `ENV_BUILDER` (required, default: true)
- `GET_PASSPORT` (required, default: false)
- `CMDB_IMPORT` (required, default: false)

## API Mode (pipeline-api.yml)

**Purpose**: For automatic execution through GitHub API

**Features**:
- Uses a single input: `GITHUB_PIPELINE_API_INPUT`
- All variables are passed in this string
- Supports JSON, YAML and key=value formats
- Automatic validation of required variables

**Usage**:
```bash
curl -X POST \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/OWNER/REPO/actions/workflows/pipeline-api.yml/dispatches \
  -d '{
    "ref": "main",
    "inputs": {
      "GITHUB_PIPELINE_API_INPUT": "..."
    }
  }'
```

**Required variables in API input**:
- `ENV_NAMES`

**Optional variables** (will be set to defaults):
- `ENV_TEMPLATE_VERSION` (default: empty) - can be specified in env_definition files instead
- `ENV_BUILDER` (default: true)
- `GET_PASSPORT` (default: false)
- `CMDB_IMPORT` (default: false)
- `DEPLOYMENT_TICKET_ID` (default: empty)

## Architectural Decisions

### Why two workflows?

1. **Separation of concerns**: UI and API have different interface requirements
2. **Security**: Prevents accidental use of API input in UI
3. **Convenience**: API gets everything in one variable, UI has convenient form

### Common Components

Both workflows use:
- Same Docker images
- Same job execution logic
- Shared `load_env_variables.py` script for fallback values
- Same validation and execution steps

### Differences

| Aspect | UI Mode | API Mode |
|--------|---------|----------|
| Workflow file | `pipeline.yml` | `pipeline-api.yml` |
| Inputs | Multiple | Single |
| Input form | GitHub UI | API string |
| Input validation | GitHub UI | Custom script |
| Name | "EnvGene Execution" | "EnvGene Execution (API)" |

## Variable Processing

### UI Mode
1. Set variables from GitHub inputs
2. Load additional variables from `pipeline_vars.yaml`
3. Processing and validation

### API Mode
1. Parse `GITHUB_PIPELINE_API_INPUT` (JSON/YAML/key=value)
2. Validate required variables
3. Set default values
4. Load fallbacks from `pipeline_vars.yaml`
5. Processing and validation

## Migration

When transitioning from UI to API or vice versa:

1. **UI → API**: Collect all variables into one string according to examples
2. **API → UI**: Split variables into separate inputs

## Troubleshooting

### UI Mode
- Check that required fields are filled
- Ensure that `pipeline_vars.yaml` contains correct fallback values

### API Mode
- Ensure that `ENV_NAMES` is specified in API input
- Check JSON/YAML syntax correctness
- Use examples from documentation to verify format 