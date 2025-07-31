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

## Solution

Changed format to simple string in single quotes and optimized JSON formatting:

```yaml
# Before (incorrect):
CRED_ROTATION_PAYLOAD: |
  {"rotation_items":[{"namespace":"e02-bss",...}]}

# After (correct):
CRED_ROTATION_PAYLOAD: '{"rotation_items":[{"namespace":"e02-bss","application":"postgres","context":"deployment","parameter_key":"POSTGRES_DBA_USER","parameter_value":"new_postgres_user"}]}'
```

## Verification

Format tested and works correctly:
- ✅ YAML parsing
- ✅ JSON validation in `load_env_variables.py`
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
3. **Optimize JSON formatting** in `load_env_variables.py`
4. **Test the format** before using in production
