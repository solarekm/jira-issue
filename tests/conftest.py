"""
Test configuration and fixtures.
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch


@pytest.fixture
def temp_file():
    """Create a temporary file for testing attachments."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Test attachment content")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def mock_jira_client():
    """Mock JIRA client for testing."""
    with patch('src.jira_client.JIRA') as mock_jira:
        mock_instance = Mock()
        mock_jira.return_value = mock_instance
        
        # Mock server info
        mock_instance.server_info.return_value = {'serverTitle': 'Test Jira Server'}
        
        # Mock issue creation
        mock_issue = Mock()
        mock_issue.key = 'TEST-123'
        mock_instance.create_issue.return_value = mock_issue
        
        # Mock user validation
        mock_user = Mock()
        mock_user.displayName = 'Test User'
        mock_instance.user.return_value = mock_user
        
        # Mock parent issue validation
        mock_parent = Mock()
        mock_parent.fields.summary = 'Parent Issue'
        mock_instance.issue.return_value = mock_parent
        
        yield mock_instance


@pytest.fixture
def valid_config():
    """Valid configuration for testing."""
    return {
        'jira_server': 'https://test.atlassian.net',
        'jira_username': 'test.user@example.com',
        'jira_api_token': 'valid_token_12345678901234567890',
        'project_key': 'TEST',
        'issue_type': 'Task',
        'issue_summary': 'Test issue summary',
        'issue_description': 'Test issue description',
        'issue_priority': 'Medium',
        'parent_issue_key': None,
        'assignee': None,
        'labels': [],
        'attachment_paths': []
    }


@pytest.fixture
def mock_environment():
    """Mock environment variables for testing."""
    env_vars = {
        'INPUT_JIRA_SERVER': 'https://test.atlassian.net',
        'INPUT_JIRA_USERNAME': 'test.user@example.com',
        'INPUT_JIRA_API_TOKEN': 'valid_token_12345678901234567890',
        'INPUT_PROJECT_KEY': 'TEST',
        'INPUT_ISSUE_TYPE': 'Task',
        'INPUT_ISSUE_SUMMARY': 'Test issue summary',
        'INPUT_ISSUE_DESCRIPTION': 'Test issue description',
        'INPUT_ISSUE_PRIORITY': 'Medium',
        'INPUT_PARENT_ISSUE_KEY': '',
        'INPUT_ASSIGNEE': '',
        'INPUT_ISSUE_LABELS': '',
        'INPUT_ATTACHMENT_PATHS': '',
        'INPUT_LOG_LEVEL': 'INFO',
        'GITHUB_STEP_SUMMARY': '/tmp/github_step_summary.txt',
        'GITHUB_OUTPUT': '/tmp/github_output.txt'
    }
    
    with patch.dict(os.environ, env_vars, clear=True):
        # Create the files that GitHub Actions would create
        for file_path in ['/tmp/github_step_summary.txt', '/tmp/github_output.txt']:
            with open(file_path, 'w') as f:
                f.write('')
        yield env_vars
        # Cleanup
        for file_path in ['/tmp/github_step_summary.txt', '/tmp/github_output.txt']:
            if os.path.exists(file_path):
                os.unlink(file_path)