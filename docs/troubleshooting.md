# Troubleshooting Guide

This guide helps you diagnose and fix common issues with the Jira Issue Action.

## 🔍 Quick Diagnosis

### Check Your Setup

1. **Verify Action Version**
   ```yaml
   uses: solarekm/jira-issue@v2  # Use latest stable version
   ```

2. **Check Required Secrets**
   - `JIRA_USERNAME` - Your Jira email/username
   - `JIRA_API_TOKEN` - Your Jira API token (not password!)
   - `JIRA_SERVER` - Optional if provided as input

3. **Enable Debug Mode**
   ```yaml
   - name: Create Jira Issue
     uses: solarekm/jira-issue@v2
     with:
       log_level: "DEBUG"
       # ... other parameters
   ```

## 🚨 Common Error Messages

### Authentication Errors

#### Error: `Authentication failed (401)`
```
JiraConnectionError: Authentication failed. Please check your credentials.
```

**Causes:**
- Invalid API token
- Incorrect username format
- Expired token
- Wrong server URL

**Solutions:**
1. **Regenerate API Token**
   - Go to Jira → Profile → Security → API tokens
   - Create new token and update secret

2. **Check Username Format**
   ```yaml
   # ✅ Correct formats
   jira_username: "john.doe@company.com"  # Email format
   jira_username: "john.doe"              # Username format
   
   # ❌ Incorrect
   jira_username: "John Doe"              # Display name
   ```

3. **Verify Server URL**
   ```yaml
   # ✅ Correct formats
   jira_server: "https://company.atlassian.net"
   jira_server: "https://jira.company.com"
   
   # ❌ Incorrect
   jira_server: "company.atlassian.net"    # Missing protocol
   jira_server: "https://company.atlassian.net/" # Trailing slash
   ```

#### Error: `Access forbidden (403)`
```
JiraConnectionError: Access forbidden. Check your permissions.
```

**Solutions:**
- User needs project access permissions
- API token requires appropriate scopes
- Check if user account is active

### Project and Issue Errors

#### Error: `Project not found (404)`
```
JiraOperationError: Resource not found. Check project key and permissions.
```

**Solutions:**
1. **Verify Project Key**
   ```yaml
   # ✅ Correct format
   project_key: "PROJ"        # Uppercase
   project_key: "DEV_TEAM"    # Underscores allowed
   
   # ❌ Incorrect
   project_key: "proj"        # Lowercase
   project_key: "PROJ-123"    # Issue key format
   ```

2. **Check Project Access**
   - User must have "Browse Projects" permission
   - Project must exist and be accessible

#### Error: `Issue type not supported`
```
ValidationError: Issue type 'task' is not supported. Valid types: Task, Bug, Story, Sub-task, Epic
```

**Solution:**
```yaml
# ✅ Correct (case-sensitive)
issue_type: "Task"
issue_type: "Bug"
issue_type: "Story"
issue_type: "Sub-task"
issue_type: "Epic"

# ❌ Incorrect
issue_type: "task"        # Wrong case
issue_type: "feature"     # Not supported
```

#### Error: `Priority not supported`
```
ValidationError: Priority 'critical' is not supported. Valid priorities: Highest, High, Medium, Low, Lowest
```

**Solution:**
```yaml
# ✅ Correct priorities
issue_priority: "Highest"
issue_priority: "High"
issue_priority: "Medium"
issue_priority: "Low"
issue_priority: "Lowest"

# ❌ Incorrect
issue_priority: "Critical"   # Not standard
issue_priority: "Normal"     # Not standard
```

### Sub-task Errors

#### Error: `Parent issue key required for Sub-task`
```
ValidationError: Parent issue key is required for Sub-task type
```

**Solution:**
```yaml
- name: Create Sub-task
  uses: solarekm/jira-issue@v2
  with:
    issue_type: "Sub-task"
    parent_issue_key: "PROJ-123"  # Required for Sub-tasks
    # ... other parameters
```

#### Error: `Parent issue not found`
```
JiraOperationError: Parent issue 'PROJ-999' not found
```

**Solutions:**
- Verify parent issue exists: `https://your-jira.com/browse/PROJ-999`
- Check issue key format: `PROJECT-NUMBER`
- Ensure parent issue is accessible to user

### Validation Errors

#### Error: `Malicious content detected`
```
ValidationError: Potentially malicious content detected in summary. Please review your input for security issues.
```

**Cause:** Input contains security patterns like:
- Shell injection characters: `;`, `&`, `|`, `$`, `(`, `)`
- Script tags: `<script>`
- JavaScript: `javascript:`

**Solution:**
```yaml
# ❌ Triggers security validation
issue_summary: "Fix login $(whoami) issue"
issue_description: "Error in <script>alert('test')</script>"

# ✅ Safe alternatives
issue_summary: "Fix login issue"
issue_description: "Error in JavaScript validation code"
```

#### Error: `Invalid file path - potential security risk`
```
ValidationError: Invalid file path '/etc/passwd' - potential security risk
```

**Solution:**
```yaml
# ✅ Correct - relative paths only
attachment_paths: "./logs/error.log,./screenshots/bug.png"

# ❌ Incorrect - absolute paths blocked
attachment_paths: "/etc/passwd,/tmp/secret.txt"
attachment_paths: "../../../sensitive/file.txt"
```

### Network and Timeout Errors

#### Error: `Connection timeout`
```
JiraConnectionError: Connection to Jira failed: timeout
```

**Solutions:**
- Check Jira server status
- Verify network connectivity
- Try again (may be temporary)

#### Error: `Rate limit exceeded (429)`
```
JiraOperationError: Rate limit exceeded during create issue. Please try again later.
```

**Solutions:**
- Wait a few minutes and retry
- Consider implementing delays between calls
- Contact Jira admin if persistent

### Attachment Errors

#### Error: `Attachment file not found`
```
ValidationError: Attachment file not found: ./logs/error.log
```

**Solutions:**
1. **Ensure File Exists**
   ```yaml
   steps:
     - name: Generate logs
       run: |
         mkdir -p logs
         echo "Error log content" > logs/error.log
         
     - name: Create Issue with Attachment
       uses: solarekm/jira-issue@v2
       with:
         attachment_paths: "./logs/error.log"
   ```

2. **Check File Permissions**
   ```yaml
   - name: Set file permissions
     run: chmod 644 logs/error.log
   ```

#### Error: `Attachment upload failed`
```
JiraOperationError: Failed to attach file: file too large
```

**Solutions:**
- Check file size limits (usually 10MB for Jira Cloud)
- Compress large files
- Split large attachments

## 🔧 Advanced Debugging

### Enable Maximum Debugging

```yaml
- name: Debug Jira Issue Creation
  uses: solarekm/jira-issue@v2
  with:
    log_level: "DEBUG"
    # Add all your normal parameters
  env:
    ACTIONS_STEP_DEBUG: true  # Enable GitHub Actions debug
```

### Test Connection Separately

```yaml
- name: Test Jira Connection
  run: |
    curl -X GET \
      -H "Authorization: Basic $(echo -n '${{ secrets.JIRA_USERNAME }}:${{ secrets.JIRA_API_TOKEN }}' | base64)" \
      -H "Accept: application/json" \
      "${{ secrets.JIRA_SERVER }}/rest/api/3/myself"
```

### Validate Project Access

```yaml
- name: Check Project Access
  run: |
    curl -X GET \
      -H "Authorization: Basic $(echo -n '${{ secrets.JIRA_USERNAME }}:${{ secrets.JIRA_API_TOKEN }}' | base64)" \
      -H "Accept: application/json" \
      "${{ secrets.JIRA_SERVER }}/rest/api/3/project/PROJ"
```

### Local Testing Setup

```bash
# Set environment variables
export INPUT_JIRA_SERVER="https://your-jira.atlassian.net"
export INPUT_JIRA_USERNAME="your.email@company.com"
export INPUT_JIRA_API_TOKEN="your_api_token"
export INPUT_PROJECT_KEY="TEST"
export INPUT_ISSUE_TYPE="Task"
export INPUT_ISSUE_SUMMARY="Test from local"
export INPUT_ISSUE_DESCRIPTION="Testing locally"
export INPUT_ISSUE_PRIORITY="Medium"
export INPUT_LOG_LEVEL="DEBUG"

# Clone and test
git clone https://github.com/solarekm/jira-issue.git
cd jira-issue
pip install -r requirements.txt
python src/main.py
```

## 📊 Logs Analysis

### Understanding Log Levels

```yaml
log_level: "DEBUG"    # Most verbose, shows everything
log_level: "INFO"     # Default, shows important steps
log_level: "WARNING"  # Only warnings and errors
log_level: "ERROR"    # Only errors
```

### Key Log Messages

#### Success Indicators
```
INFO: Successfully connected to Jira server: Your Company Jira
INFO: Configuration validated successfully
INFO: Successfully created issue: PROJ-123
INFO: === Action completed successfully! Issue created: PROJ-123 ===
```

#### Warning Signs
```
WARNING: Assignee 'nonexistent.user' not found in Jira, issue will be unassigned
WARNING: Failed to attach 1 file(s): large-file.zip
```

#### Error Patterns
```
ERROR: Input validation failed: Invalid project key format
ERROR: Failed to connect to Jira: Authentication failed
ERROR: Failed to create Jira issue: Bad request - Field 'summary' is required
```

## 🆘 Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
2. **Enable debug logging** and review logs
3. **Test with minimal configuration** first
4. **Verify credentials** work in Jira web interface

### Information to Provide

When reporting issues, include:

```yaml
# Your workflow configuration (with secrets redacted)
- name: Create Issue
  uses: solarekm/jira-issue@v2
  with:
    jira_server: "https://company.atlassian.net"
    # ... other parameters

# Error message from logs
Error: [exact error message here]

# Environment details
- GitHub Actions runner: ubuntu-latest
- Action version: v2.1.0
- Jira type: Cloud/Server
```

### Where to Get Help

1. **GitHub Issues**: [Create an issue](https://github.com/solarekm/jira-issue/issues)
2. **Documentation**: Check [README.md](../README.md) and [examples](examples.md)
3. **Security Issues**: Follow [security policy](../SECURITY.md)

## 🔍 Self-Diagnosis Checklist

Before reporting a bug, verify:

- [ ] Using latest action version (`@v2`)
- [ ] All required inputs provided
- [ ] Secrets correctly configured
- [ ] Project key exists and accessible
- [ ] Issue type and priority are valid
- [ ] For Sub-tasks: parent issue key provided
- [ ] For attachments: files exist and readable
- [ ] Debug logs reviewed
- [ ] Tested with minimal configuration

## 📚 Additional Resources

- [Jira REST API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [GitHub Actions Debugging](https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/enabling-debug-logging)
- [Jira Permissions Guide](https://support.atlassian.com/jira-cloud-administration/docs/manage-project-permissions/)
- [API Token Management](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)