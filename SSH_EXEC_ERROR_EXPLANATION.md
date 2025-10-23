# SSH Exec Error Explanation

## 🔍 Error Analysis

The error you encountered:
```json
{
  "level": "INFO",
  "logger": "mcp.main", 
  "message": "tool_error",
  "extra": {
    "tool": "ssh_exec",
    "target": null,
    "error": "2 validation errors for SSHExecRequest\ntarget\n  Field required [type=missing, input_value={}, input_type=dict]\ncommand\n  Field required [type=missing, input_value={}, input_type=dict]"
  }
}
```

## 🚨 What This Means

1. **Tool Called**: `ssh_exec`
2. **Request Body**: Empty `{}`
3. **Missing Fields**: `target` and `command` (both required)
4. **Root Cause**: OpenAPI tool sent empty parameters

## 🛠️ Solutions Implemented

### 1. **Better Error Messages**
- Added validation before Pydantic parsing
- Clear error messages showing what's missing
- Examples of correct usage

### 2. **Debug Logging**
- Logs incoming request details
- Shows what parameters were received
- Identifies the source of the request

### 3. **Parameter Validation**
- Validates required fields before processing
- Provides helpful error messages
- Shows what was received vs. what's needed

## 📋 Correct Usage Examples

### ✅ Valid Request
```json
{
  "name": "ssh_exec",
  "arguments": {
    "target": "pi-lan",
    "command": "ls -la /home/pi"
  }
}
```

### ✅ With Optional Parameters
```json
{
  "name": "ssh_exec",
  "arguments": {
    "target": "pi-lan",
    "command": "python script.py",
    "cwd": "/home/pi/project",
    "env": {"PYTHONPATH": "/home/pi/lib"},
    "timeout": 30
  }
}
```

### ❌ Invalid Requests (Will Now Show Clear Errors)

**Empty Request:**
```json
{
  "name": "ssh_exec",
  "arguments": {}
}
```
*Error: "ssh_exec requires parameters: target, command. Received empty request."*

**Missing Target:**
```json
{
  "name": "ssh_exec", 
  "arguments": {
    "command": "ls -la"
  }
}
```
*Error: "ssh_exec missing required parameters: target. Received: ['command']"*

**Missing Command:**
```json
{
  "name": "ssh_exec",
  "arguments": {
    "target": "pi-lan"
  }
}
```
*Error: "ssh_exec missing required parameters: command. Received: ['target']"*

## 🔧 OpenAPI Tool Configuration

For OpenAPI tools (like in your image), configure:

1. **URL**: `http://localhost:8000/openapi.json`
2. **Type**: OpenAPI
3. **Parameters**: The tool should map its inputs to:
   - `target`: Target name (e.g., "pi-lan")
   - `command`: Shell command to execute

## 🧪 Testing

Run the validation test:
```bash
python test_ssh_exec_validation.py
```

This will show you exactly what error messages you'll get for different scenarios.

## 🚀 Next Steps

1. **Check OpenAPI Tool Configuration**: Ensure your OpenAPI tool is properly configured to send the required parameters
2. **Verify Target Configuration**: Make sure you have a valid target configured in `config/hosts.yaml`
3. **Test with Simple Commands**: Start with basic commands like `echo "Hello World"`

The improved error handling will now give you clear, actionable error messages instead of cryptic Pydantic validation errors!
