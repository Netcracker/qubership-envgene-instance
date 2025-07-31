# CRED_ROTATION_PAYLOAD Error Fix

## Problem

Two main issues were encountered:

### 1. JSON Parsing Error
JSON parsing error in `creds_rotation_handler.py`:

```
json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
```

### 2. File Structure Error
After fixing JSON parsing, encountered file structure error:

```
[ENVGENE-8001] Error: File not found: Target namespace/application file not found in environment instance for parameter key POSTGRES_DBA_USER.
```

## Root Cause

### 1. JSON Quote Loss Issue
The issue was caused by incorrect `CRED_ROTATION_PAYLOAD` format in `.github/pipeline_vars.yaml` and quote loss during environment variable processing.

### Incorrect format (before fix):
```yaml
CRED_ROTATION_PAYLOAD: |
  {"rotation_items":[...]}
```

### Correct format (after fix):
```yaml
CRED_ROTATION_PAYLOAD: '{"rotation_items":[{"namespace":"e02-bss","application":"postgres","context":"deployment","parameter_key":"POSTGRES_DBA_USER","parameter_value":"new_postgres_user"}]}'
```

### 2. File Structure Issue
The script expects application files in `Applications/` directory, but they were missing for `postgres` and `postgres-service`.

## Explanation

1. **YAML Block Scalar (|)** - YAML interpreted JSON as a multi-line string, causing issues when passed to Python
2. **Quote loss** - During processing, JSON lost quotes around keys
3. **Environment variables** - Format could be corrupted when passed through GitHub Actions
4. **Base64 encoding** - Prevents quote loss by encoding JSON as base64 string

## Solution

### 1. JSON Quote Loss Fix
**Root Cause Found:** JSON quotes are being stripped during environment variable processing.

**Solution:** Use base64 encoding to prevent quote loss:

```yaml
# The format in pipeline_vars.yaml remains the same:
CRED_ROTATION_PAYLOAD: '{"rotation_items":[{"namespace":"e02-bss","application":"postgres","context":"deployment","parameter_key":"POSTGRES_DBA_USER","parameter_value":"new_postgres_user"}]}'
```

**But the processing has changed:**
- `load_env_variables.py` now encodes JSON as base64
- `creds_rotation_handler.py` now decodes base64 before parsing JSON

### 2. File Structure Fix
**Solution:** Create missing application files in `Applications/` directory:

```yaml
# environments/test-cluster/e02/Applications/postgres.yml
name: "postgres"
deployParameters:
  POSTGRES_DBA_USER: "test"
  POSTGRES_DBA_PASSWORD: "test"

# environments/test-cluster/e02/Applications/postgres-service.yml
name: "postgres-service"
deployParameters:
  POSTGRES_DBA_USER: "test"
  POSTGRES_DBA_PASSWORD: "test"
```

## Verification

Both issues resolved and tested:

### JSON Processing:
- ✅ YAML parsing
- ✅ JSON validation in `load_env_variables.py`
- ✅ Base64 encoding in `load_env_variables.py`
- ✅ Base64 decoding in `creds_rotation_handler.py`
- ✅ JSON parsing in `creds_rotation_handler.py`

### File Structure:
- ✅ Application files created in `Applications/` directory
- ✅ Correct namespace mapping (`e02-bss` → `bss`)
- ✅ Correct application mapping (`postgres`, `postgres-service`)
- ✅ Parameter keys found in application files

## Alternative Formats

If issues arise, you can use:

```yaml
# Option 1: Double quotes with escaping
CRED_ROTATION_PAYLOAD: "{\"rotation_items\":[...]}"

# Option 2: YAML block scalar with proper indentation
CRED_ROTATION_PAYLOAD: |
  {
    "rotation_items": [...]
  }

# Option 3: Simple string in single quotes (recommended)
CRED_ROTATION_PAYLOAD: '{"rotation_items":[...]}'
```

## Recommendations

1. **Use simple string in single quotes** for JSON data
2. **Avoid YAML block scalar** for JSON - they may lose quotes
3. **Use base64 encoding** to prevent quote loss in environment variables
4. **Ensure application files exist** in `Applications/` directory
5. **Test the format** before using in production
