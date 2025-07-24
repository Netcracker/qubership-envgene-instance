# Troubleshooting Matrix Generation Errors

## 🚨 Common Error Messages

### "Matrix vector 'environment' does not contain any values"
- **Cause**: The `env_matrix` output is empty or contains `[]`
- **Location**: Occurs in jobs that use `fromJson(needs.show_environment_variables.outputs.env_matrix)`

### "Error from function 'fromJson': empty input"
- **Cause**: The `env_matrix` output is completely empty (null or "")
- **Location**: Same as above

## 🔍 Debugging Steps

### 1. Check the First Job Logs
Look at the **"API Input Parameters Processing"** job logs:

```
🔧 Generating environment matrix from ENV_NAMES...
ENV_NAMES value: 'test-cluster/e02'
All environment variables starting with ENV_:
ENV_NAMES=test-cluster/e02
ENV_BUILDER=true
...
Processing environment: 'test-cluster/e02'
Generated matrix with 1 environment(s): ["test-cluster/e02"]
```

### 2. Expected vs Problematic Outputs

**✅ Good Output:**
```
Generated matrix with 2 environment(s): ["test-cluster/e01","test-cluster/e02"]
```

**❌ Problem Indicators:**
```
❌ ERROR: ENV_NAMES is empty or not set!
Creating empty matrix to skip downstream jobs...
```

## 🛠️ Fix Steps

### Step 1: Verify API Input Processing
Check that the **"Process API Input Variables"** step shows:

**Expected logs:**
```
🔍 Raw GitHub input received:
Input value: '{"ENV_NAMES": "test-cluster/e02", "ENV_BUILDER": "true"}'
🐍 Python script started
✅ Processing GITHUB_PIPELINE_API_INPUT: {"ENV_NAMES": "test-cluster/e02", ...}
Parsed variables from API input:
  ENV_NAMES=test-cluster/e02
  ...
```

**Problem indicators:**
```
🔍 Raw GitHub input received:
Input value: ''
🐍 Python script started
❌ No GITHUB_PIPELINE_API_INPUT provided, skipping API input processing
```

### Step 2: Check Matrix Generation
Look for the **"Prepare Parameters"** step output:
- Should show ENV_ variables
- Should process each environment
- Should generate valid JSON array

### Step 3: Verify Downstream Jobs
Jobs with matrix should either:
- **Run normally** if matrix is valid: `["env1","env2"]`
- **Skip completely** if matrix is empty: `[]`

## 🧪 Test Requests

### Simple Input Test
Use **"Debug - Simple Test"** to check if input is received at all:

```json
{
  "ref": "main",
  "inputs": {
    "GITHUB_PIPELINE_API_INPUT": "test"
  }
}
```

### Minimal JSON Test
Use **"Debug - Test ENV_NAMES Only"**:

```json
{
  "ref": "main",
  "inputs": {
    "GITHUB_PIPELINE_API_INPUT": "{\"ENV_NAMES\": \"test-cluster/e01\"}"
  }
}
```

### Matrix Generation Test
Use **"Debug - Matrix Generation"**:

```json
{
  "ref": "main",
  "inputs": {
    "GITHUB_PIPELINE_API_INPUT": "{\"ENV_NAMES\": \"test-cluster/e01,test-cluster/e02\"}"
  }
}
```

## 🔧 Common Fixes

### 1. JSON Escaping Issues
**Problem**: `ENV_NAMES` not parsed correctly
**Solution**: Ensure proper escaping in API requests

```json
✅ Correct: "GITHUB_PIPELINE_API_INPUT": "{\"ENV_NAMES\": \"test-cluster/e01\"}"
❌ Wrong:   "GITHUB_PIPELINE_API_INPUT": "{"ENV_NAMES": "test-cluster/e01"}"
```

### 2. Empty ENV_NAMES
**Problem**: ENV_NAMES is empty or whitespace
**Solution**: Provide valid environment names

```json
✅ Correct: {"ENV_NAMES": "test-cluster/e01"}
❌ Wrong:   {"ENV_NAMES": ""}
❌ Wrong:   {"ENV_NAMES": "   "}
```

### 3. Input Not Received
**Problem**: Raw input shows empty value `Input value: ''`
**Solution**: 
- Check Postman request format
- Verify GitHub token has `actions:write` permission
- Ensure repository path is correct
- Try **"Debug - Simple Test"** first

### 4. Missing Default Variables
**Problem**: Jobs fail with `KeyError: 'ENV_INVENTORY_INIT'` or similar
**Solution**: 
- Check that **"Set Default Values and Load Fallbacks"** step shows all variables being set
- Look for logs like: `Setting fallback value: ENV_INVENTORY_INIT=false`
- This is now fixed - all required variables get default values

### 5. Workflow Step Order
**Problem**: Variables not available when matrix is generated
**Solution**: Check that steps run in this order:
1. Process API Input Variables
2. Set Default Values and Load Fallbacks  
3. Prepare Parameters (matrix generation)

## 📋 Default Variables Reference

The following variables are automatically set with default values:
```
ENV_BUILDER=true
GET_PASSPORT=false
CMDB_IMPORT=false
DEPLOYMENT_TICKET_ID=""
ENV_TEMPLATE_VERSION=""
ENV_INVENTORY_INIT=false
GENERATE_EFFECTIVE_SET=false
ENV_TEMPLATE_TEST=false
ENV_TEMPLATE_NAME=""
SD_DATA={}
SD_VERSION=""
SD_SOURCE_TYPE=""
SD_DELTA=false
ENV_SPECIFIC_PARAMETERS={}
```

## 📋 Monitoring Checklist

- [ ] API input processing completed successfully
- [ ] ENV_NAMES variable is set and non-empty
- [ ] All required default variables are set
- [ ] Matrix generation produces valid JSON array
- [ ] Downstream jobs either run or skip appropriately
- [ ] No "fromJson: empty input" errors

## 🚀 Expected Workflow Flow

```
API Request → Process Input → Set Defaults → Generate Matrix → Run Jobs
     ✅            ✅            ✅           ✅        ✅
```

If any step fails, the matrix becomes `[]` and downstream jobs are skipped safely. 