# Simple test to verify our validation logic
def test_validation():
    test_content = '''---
ENV_INVENTORY_INIT: false
ENV_TEMPLATE_NAME: "test"
SD_DATA: {}
'''
    
    variables = {}
    errors = []
    lines = test_content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        # Skip empty lines and commented lines
        if not line or line.startswith("#"):
            continue
        
        content = line
        
        # Check if it's a variable assignment
        if ":" in content:
            key, value = content.split(":", 1)
            key = key.strip()
            value = value.strip()
            
            # Validate string type
            if value.lower() in ["true", "false"] and not (value.startswith('"') or value.startswith("'")):
                errors.append(f"Line {line_num}: Variable '{key}' has boolean value '{value}' without quotes.")
                continue
            
            if (value.startswith('{') or value.startswith('[')) and not (value.startswith('"') or value.startswith("'")):
                errors.append(f"Line {line_num}: Variable '{key}' has JSON value '{value}' without quotes.")
                continue
            
            # Remove quotes if present
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            
            variables[key] = value
            print(f"Loaded variable: {key} = {value}")
    
    if errors:
        print("❌ Validation errors:")
        for error in errors:
            print(f"  {error}")
    else:
        print("✅ All variables are valid strings")
    
    return variables, errors

if __name__ == "__main__":
    test_validation()
