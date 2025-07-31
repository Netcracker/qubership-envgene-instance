# CRED_ROTATION_PAYLOAD Error Fix

## Problem

JSON parsing error in `creds_rotation_handler.py`:

```
json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
```

## Root Cause

The issue was caused by incorrect `CRED_ROTATION_PAYLOAD` format in `.github/pipeline_vars.yaml`.

### Incorrect format (before fix):
```yaml
CRED_ROTATION_PAYLOAD: |
  {"rotation_items":[...]}
```

### Correct format (after fix):
```yaml
CRED_ROTATION_PAYLOAD: '{"rotation_items":[{"namespace":"e02-bss","application":"postgres","context":"deployment","parameter_key":"POSTGRES_DBA_USER","parameter_value":"new_postgres_user"}]}'
```

## Explanation

1. **YAML Block Scalar (|)** - YAML interpreted JSON as a multi-line string, causing issues when passed to Python
2. **Quote loss** - During processing, JSON lost quotes around keys
3. **Environment variables** - Format could be corrupted when passed through GitHub Actions
4. **Base64 encoding** - Prevents quote loss by encoding JSON as base64 string

## Solution

**Root Cause Found:** JSON quotes are being stripped during environment variable processing.

**Solution:** Use base64 encoding to prevent quote loss:

```yaml
# The format in pipeline_vars.yaml remains the same:
CRED_ROTATION_PAYLOAD: '{"rotation_items":[{"namespace":"e02-bss","application":"postgres","context":"deployment","parameter_key":"POSTGRES_DBA_USER","parameter_value":"new_postgres_user"}]}'
```

**But the processing has changed:**
- `load_env_variables.py` now encodes JSON as base64
- `creds_rotation_handler.py` now decodes base64 before parsing JSON

## Verification

Format tested and works correctly:
- ✅ YAML parsing
- ✅ JSON validation in `load_env_variables.py`
- ✅ Base64 encoding in `load_env_variables.py`
- ✅ Base64 decoding in `creds_rotation_handler.py`
- ✅ JSON parsing in `creds_rotation_handler.py`

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
4. **Test the format** before using in production
