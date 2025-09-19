# Examples and Use Cases

This document provides practical examples and common use cases for the Jira Issue Action.

## 📋 Table of Contents

- [Basic Examples](#basic-examples)
- [Advanced Use Cases](#advanced-use-cases)
- [Integration Patterns](#integration-patterns)
- [Troubleshooting](#troubleshooting)

## 🚀 Basic Examples

### 1. Simple Issue Creation

```yaml
name: Create Simple Jira Issue

on:
  workflow_dispatch:
    inputs:
      summary:
        description: "Issue summary"
        required: true
      description:
        description: "Issue description"
        required: true

jobs:
  create_issue:
    runs-on: ubuntu-latest
    steps:
      - name: Create Jira Issue
        uses: solarekm/jira-issue@v2
        with:
          jira_server: "https://mycompany.atlassian.net"
          jira_username: ${{ secrets.JIRA_USERNAME }}
          jira_api_token: ${{ secrets.JIRA_API_TOKEN }}
          project_key: "PROJ"
          issue_type: "Task"
          issue_summary: ${{ github.event.inputs.summary }}
          issue_description: ${{ github.event.inputs.description }}
          issue_priority: "Medium"
```

### 2. Bug Report with Attachments

```yaml
name: 🐛 Create Bug Report

on:
  workflow_dispatch:
    inputs:
      bug_summary:
        description: "Bug summary"
        required: true
      steps_to_reproduce:
        description: "Steps to reproduce"
        required: true
      expected_behavior:
        description: "Expected behavior"
        required: true
      actual_behavior:
        description: "Actual behavior"  
        required: true

jobs:
  create_bug_report:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Generate bug report logs
        run: |
          mkdir -p logs
          echo "Bug reproduction logs" > logs/bug-report.log
          echo "System information: $(uname -a)" >> logs/bug-report.log
          echo "Timestamp: $(date)" >> logs/bug-report.log

      - name: Create Bug Issue
        uses: solarekm/jira-issue@v2
        with:
          jira_server: ${{ secrets.JIRA_SERVER }}
          jira_username: ${{ secrets.JIRA_USERNAME }}
          jira_api_token: ${{ secrets.JIRA_API_TOKEN }}
          project_key: "BUG"
          issue_type: "Bug"
          issue_summary: "🐛 ${{ github.event.inputs.bug_summary }}"
          issue_description: |
            ## Steps to Reproduce
            ${{ github.event.inputs.steps_to_reproduce }}
            
            ## Expected Behavior
            ${{ github.event.inputs.expected_behavior }}
            
            ## Actual Behavior
            ${{ github.event.inputs.actual_behavior }}
            
            ## Environment
            - Repository: ${{ github.repository }}
            - Branch: ${{ github.ref }}
            - Workflow: ${{ github.workflow }}
            - Run: ${{ github.run_number }}
          issue_priority: "High"
          issue_labels: "bug,reproduction,investigation"
          attachment_paths: "logs/bug-report.log"
```

### 3. Sub-task Creation

```yaml
name: Create Sub-task

on:
  workflow_dispatch:
    inputs:
      parent_issue:
        description: "Parent issue key (e.g., PROJ-123)"
        required: true
      subtask_title:
        description: "Sub-task title"
        required: true
      assignee:
        description: "Assignee username"
        required: false

jobs:
  create_subtask:
    runs-on: ubuntu-latest
    steps:
      - name: Create Sub-task
        uses: solarekm/jira-issue@v2
        with:
          jira_server: ${{ secrets.JIRA_SERVER }}
          jira_username: ${{ secrets.JIRA_USERNAME }}
          jira_api_token: ${{ secrets.JIRA_API_TOKEN }}
          project_key: "PROJ"
          issue_type: "Sub-task"
          parent_issue_key: ${{ github.event.inputs.parent_issue }}
          issue_summary: ${{ github.event.inputs.subtask_title }}
          issue_description: |
            Sub-task created via GitHub Actions
            
            Parent Issue: ${{ github.event.inputs.parent_issue }}
            Created by: ${{ github.actor }}
            Repository: ${{ github.repository }}
          issue_priority: "Medium"
          assignee: ${{ github.event.inputs.assignee }}
```

## 🔧 Advanced Use Cases

### 1. Automated Testing Issue Creation

```yaml
name: Create Test Failure Issues

on:
  workflow_run:
    workflows: ["CI Tests"]
    types: [completed]
    
jobs:
  create_test_issue:
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    runs-on: ubuntu-latest
    steps:
      - name: Get failed workflow details
        id: workflow_details
        run: |
          echo "workflow_name=${{ github.event.workflow_run.name }}" >> $GITHUB_OUTPUT
          echo "run_url=${{ github.event.workflow_run.html_url }}" >> $GITHUB_OUTPUT
          
      - name: Create Test Failure Issue
        uses: solarekm/jira-issue@v2
        with:
          jira_server: ${{ secrets.JIRA_SERVER }}
          jira_username: ${{ secrets.JIRA_USERNAME }}
          jira_api_token: ${{ secrets.JIRA_API_TOKEN }}
          project_key: "CI"
          issue_type: "Bug"
          issue_summary: "🚨 Test Failure: ${{ steps.workflow_details.outputs.workflow_name }}"
          issue_description: |
            ## Test Failure Report
            
            **Workflow:** ${{ steps.workflow_details.outputs.workflow_name }}
            **Repository:** ${{ github.repository }}
            **Branch:** ${{ github.event.workflow_run.head_branch }}
            **Commit:** ${{ github.event.workflow_run.head_sha }}
            **Run URL:** ${{ steps.workflow_details.outputs.run_url }}
            
            ## Investigation Required
            - [ ] Analyze test failure logs
            - [ ] Identify root cause
            - [ ] Create fix or update tests
            - [ ] Verify fix works
            
            **Created automatically by GitHub Actions**
          issue_priority: "High"
          issue_labels: "ci,test-failure,automation"
          assignee: "qa-team"
```

### 2. Multi-Environment Deployment Issues

```yaml
name: Create Deployment Issues

on:
  workflow_dispatch:
    inputs:
      release_version:
        description: "Release version"
        required: true
      environments:
        description: "Environments (comma-separated)"
        required: true
        default: "staging,production"

jobs:
  create_deployment_issues:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        environment: ${{ fromJson(format('["{0}"]', join(split(github.event.inputs.environments, ','), '","'))) }}
    steps:
      - name: Create Deployment Issue
        uses: solarekm/jira-issue@v2
        with:
          jira_server: ${{ secrets.JIRA_SERVER }}
          jira_username: ${{ secrets.JIRA_USERNAME }}
          jira_api_token: ${{ secrets.JIRA_API_TOKEN }}
          project_key: "DEPLOY"
          issue_type: "Task"
          issue_summary: "🚀 Deploy v${{ github.event.inputs.release_version }} to ${{ matrix.environment }}"
          issue_description: |
            ## Deployment Task
            
            **Version:** ${{ github.event.inputs.release_version }}
            **Environment:** ${{ matrix.environment }}
            **Repository:** ${{ github.repository }}
            **Requested by:** ${{ github.actor }}
            
            ## Deployment Checklist
            - [ ] Pre-deployment verification
            - [ ] Deploy to ${{ matrix.environment }}
            - [ ] Post-deployment testing
            - [ ] Health checks
            - [ ] Rollback plan ready
            
            ## Resources
            - [Release Notes](https://github.com/${{ github.repository }}/releases/tag/v${{ github.event.inputs.release_version }})
            - [Deployment Guide](https://docs.company.com/deployment)
          issue_priority: "High"
          issue_labels: "deployment,${{ matrix.environment }},v${{ github.event.inputs.release_version }}"
          assignee: "devops-team"
```

### 3. Security Incident Response

```yaml
name: 🚨 Security Incident Response

on:
  repository_dispatch:
    types: [security_incident]

jobs:
  create_security_issue:
    runs-on: ubuntu-latest
    steps:
      - name: Create Security Incident Issue
        uses: solarekm/jira-issue@v2
        with:
          jira_server: ${{ secrets.JIRA_SERVER }}
          jira_username: ${{ secrets.JIRA_USERNAME }}
          jira_api_token: ${{ secrets.JIRA_API_TOKEN }}
          project_key: "SEC"
          issue_type: "Bug"
          issue_summary: "🚨 SECURITY INCIDENT: ${{ github.event.client_payload.incident_type }}"
          issue_description: |
            ## 🚨 SECURITY INCIDENT ALERT
            
            **Incident Type:** ${{ github.event.client_payload.incident_type }}
            **Severity:** ${{ github.event.client_payload.severity }}
            **Detected At:** ${{ github.event.client_payload.timestamp }}
            **Repository:** ${{ github.repository }}
            
            ## Incident Details
            ${{ github.event.client_payload.details }}
            
            ## Immediate Actions Required
            - [ ] Incident response team notified
            - [ ] Impact assessment
            - [ ] Containment measures
            - [ ] Investigation
            - [ ] Resolution and recovery
            - [ ] Post-incident review
            
            **This is an automated security alert**
          issue_priority: "Highest"
          issue_labels: "security,incident,urgent,p0"
          assignee: "security-team"
```

## 🔗 Integration Patterns

### 1. Issue Creation with Approval Workflow

```yaml
name: Issue Creation with Approval

on:
  issues:
    types: [labeled]

jobs:
  create_approved_jira_issue:
    if: contains(github.event.label.name, 'approved-for-jira')
    runs-on: ubuntu-latest
    steps:
      - name: Create Approved Jira Issue
        uses: solarekm/jira-issue@v2
        with:
          jira_server: ${{ secrets.JIRA_SERVER }}
          jira_username: ${{ secrets.JIRA_USERNAME }}
          jira_api_token: ${{ secrets.JIRA_API_TOKEN }}
          project_key: "APPROVED"
          issue_type: "Task"
          issue_summary: "GitHub Issue: ${{ github.event.issue.title }}"
          issue_description: |
            ## Original GitHub Issue
            
            **Link:** ${{ github.event.issue.html_url }}
            **Author:** ${{ github.event.issue.user.login }}
            **Created:** ${{ github.event.issue.created_at }}
            
            ## Description
            ${{ github.event.issue.body }}
            
            ---
            *Automatically created from approved GitHub issue*
          issue_priority: "Medium"
          issue_labels: "github-import,approved"
      
      - name: Comment on GitHub Issue
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '✅ Jira issue created successfully! Issue key: ${{ steps.create-issue.outputs.issue_key }}'
            })
```

### 2. Scheduled Maintenance Issues

```yaml
name: Create Monthly Maintenance Issues

on:
  schedule:
    - cron: '0 0 1 * *'  # First day of every month

jobs:
  create_maintenance_issues:
    runs-on: ubuntu-latest
    steps:
      - name: Get current month
        id: date
        run: |
          echo "month=$(date +'%B %Y')" >> $GITHUB_OUTPUT
          echo "next_month=$(date -d '+1 month' +'%B %Y')" >> $GITHUB_OUTPUT
      
      - name: Create Security Updates Issue
        uses: solarekm/jira-issue@v2
        with:
          jira_server: ${{ secrets.JIRA_SERVER }}
          jira_username: ${{ secrets.JIRA_USERNAME }}
          jira_api_token: ${{ secrets.JIRA_API_TOKEN }}
          project_key: "MAINT"
          issue_type: "Task"
          issue_summary: "🔒 Monthly Security Updates - ${{ steps.date.outputs.month }}"
          issue_description: |
            ## Monthly Security Maintenance
            
            **Month:** ${{ steps.date.outputs.month }}
            **Due Date:** End of ${{ steps.date.outputs.month }}
            
            ## Tasks
            - [ ] Review security advisories
            - [ ] Update dependencies
            - [ ] Security patches
            - [ ] Vulnerability scans
            - [ ] Documentation updates
            
            ## Dependencies
            - Node.js packages
            - Python packages  
            - System packages
            - Docker images
          issue_priority: "High"
          issue_labels: "maintenance,security,monthly"
          assignee: "security-team"
```

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. Authentication Errors
```
Error: Authentication failed (401)
```

**Solution:**
- Verify API token is correct and not expired
- Check username format (email vs username)
- Ensure API token has required permissions

#### 2. Project Not Found
```
Error: Project 'PROJ' not found (404)
```

**Solution:**
- Verify project key exists and is accessible
- Check user permissions for the project
- Ensure project key is in correct format (uppercase)

#### 3. Invalid Issue Type
```
Error: Issue type 'story' is not supported
```

**Solution:**
- Use correct case: "Story" not "story"
- Valid types: Task, Bug, Story, Sub-task, Epic
- Check if issue type is enabled in your Jira project

#### 4. Parent Issue Required
```
Error: Parent issue key is required for Sub-task type
```

**Solution:**
- Provide parent_issue_key for Sub-task type
- Verify parent issue exists and is accessible
- Use correct format: PROJECT-123

#### 5. Attachment Upload Failed
```
Error: Attachment file not found: ./logs/error.log
```

**Solution:**
- Ensure file exists before action runs
- Use relative paths from repository root
- Check file permissions and accessibility

### Debug Mode

Enable detailed logging:

```yaml
- name: Create Jira Issue (Debug)
  uses: solarekm/jira-issue@v2
  with:
    # ... your parameters ...
    log_level: "DEBUG"
```

### Testing Locally

Use the test script for local debugging:

```bash
cd jira-issue
export INPUT_JIRA_SERVER="https://test.atlassian.net"
export INPUT_JIRA_USERNAME="test@example.com"
export INPUT_JIRA_API_TOKEN="your_token"
export INPUT_PROJECT_KEY="TEST"
export INPUT_ISSUE_TYPE="Task"
export INPUT_ISSUE_SUMMARY="Test issue"
export INPUT_ISSUE_DESCRIPTION="Test description"
export INPUT_ISSUE_PRIORITY="Medium"
export INPUT_LOG_LEVEL="DEBUG"

python src/main.py
```

## 📚 Additional Resources

- [Jira REST API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Security Best Practices](../SECURITY.md)
- [Contributing Guidelines](../CONTRIBUTING.md)