# Create Jira Issue Action

This Action creates a Jira issue or sub-task with a given summary, description, type, priority, and labels. It can be triggered manually through the GitHub Actions workflow dispatch feature.

## Table of Contents

- [Usage](#usage)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Example Workflow](#example-workflow)
- [Contributing](#contributing)
- [License](#license)

## Usage

To use this action, include it in your workflow YAML file. This action requires the Jira server URL, username, and API token, along with the project key and other issue details.

## Inputs

| Input                  | Description                                              | Required | Default               |
|------------------------|----------------------------------------------------------|----------|-----------------------|
| `jira_server`          | The Jira server URL                                      | Yes      |                       |
| `project_key`          | The Jira project key                                     | Yes      |                       |
| `issue_type`           | The type of the issue (e.g., Task, Bug, Story, Sub-task) | Yes      | `Task`                |
| `parent_issue_key`     | The key of the parent issue if creating a Sub-task       | No       |                       |
| `assignee`             | Assignee username (optional)                             | No       |                       |
| `issue_summary`        | The summary of the issue                                 | Yes      |                       |
| `issue_description`    | The description of the issue                             | Yes      |                       |
| `issue_priority`       | The priority of the issue (High, Medium, Low)            | Yes      | `Medium`              |
| `issue_labels`         | Comma-separated labels for the issue                     | No       |                       |
| `attachment_paths`     | Comma-separated paths of attachments                     | No       |                       |

## Outputs

This action does not return any specific outputs.

## Example Workflow

Below is an example of how to set up a workflow that uses this action:

```yaml
name: Create Jira Issue

on:
  workflow_dispatch:
    inputs:
      jira_server:
        description: "Jira server URL"
        required: true
      project_key:
        description: "Jira project key"
        required: true
      issue_type:
        description: "Type of the issue (Task, Bug, Story, Sub-task, Epic)"
        required: true
        default: "Task"
        type: choice
        options:
          - "Task"
          - "Bug"
          - "Story"
          - "Sub-task"
          - "Epic"
      parent_issue_key:
        description: "Parent issue key (only for Sub-task)"
        required: false
      assignee:
        description: "Assignee username (optional)"
        required: false
      issue_summary:
        description: "Summary of the issue"
        required: true
      issue_description:
        description: "Description of the issue"
        required: true
      issue_priority:
        description: "Priority of the issue (High, Medium, Low)"
        required: true
        default: "Medium"
        type: choice
        options:
          - "High"
          - "Medium"
          - "Low"
      issue_labels:
        description: "Comma-separated labels for the issue"
        required: false
      attachment_paths:
        description: "Comma-separated paths of attachments"
        required: false

jobs:
  create_jira_issue:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Create Jira Issue
        uses: solarekm/jira-issue@v1
        with:
          jira_server: ${{ github.event.inputs.jira_server }}
          jira_username: ${{ secrets.JIRA_USERNAME }}
          jira_api_token: ${{ secrets.JIRA_API_TOKEN }}
          project_key: ${{ github.event.inputs.project_key }}
          issue_type: ${{ github.event.inputs.issue_type }}
          parent_issue_key: ${{ github.event.inputs.parent_issue_key }}
          assignee: ${{ github.event.inputs.assignee }}
          issue_summary: ${{ github.event.inputs.issue_summary }}
          issue_description: ${{ github.event.inputs.issue_description }}
          issue_priority: ${{ github.event.inputs.issue_priority }}
          issue_labels: ${{ github.event.inputs.issue_labels }}
          attachment_paths: ${{ github.event.inputs.attachment_paths }}
