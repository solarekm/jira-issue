"""
Tests for Jira client functionality.
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from jira import JIRAError

from src.jira_client import JiraClient
from src.exceptions import JiraConnectionError, JiraOperationError


class TestJiraClient:
    
    def test_init_success(self, mock_jira_client):
        """Test successful Jira client initialization."""
        client = JiraClient(
            server="https://test.atlassian.net",
            username="test.user@example.com",
            api_token="valid_token_12345678901234567890"
        )
        assert client.server == "https://test.atlassian.net"
        assert client.username == "test.user@example.com"
    
    def test_init_connection_error(self):
        """Test Jira client initialization with connection error."""
        with patch('src.jira_client.JIRA') as mock_jira:
            mock_jira.side_effect = JIRAError(status_code=401, text="Unauthorized")
            
            with pytest.raises(JiraConnectionError, match="Authentication failed"):
                JiraClient(
                    server="https://test.atlassian.net",
                    username="invalid",
                    api_token="invalid"
                )
    
    def test_create_issue_success(self, mock_jira_client, valid_config):
        """Test successful issue creation."""
        client = JiraClient(
            server=valid_config['jira_server'],
            username=valid_config['jira_username'],
            api_token=valid_config['jira_api_token']
        )
        
        issue_key = client.create_issue(valid_config)
        assert issue_key == "TEST-123"
        
        # Verify issue creation was called
        mock_jira_client.create_issue.assert_called_once()
    
    def test_create_issue_with_assignee(self, mock_jira_client, valid_config):
        """Test issue creation with valid assignee."""
        valid_config['assignee'] = 'test.user'
        
        client = JiraClient(
            server=valid_config['jira_server'],
            username=valid_config['jira_username'],
            api_token=valid_config['jira_api_token']
        )
        
        issue_key = client.create_issue(valid_config)
        assert issue_key == "TEST-123"
        
        # Verify assignee validation was called
        mock_jira_client.user.assert_called_once_with('test.user')
    
    def test_create_issue_with_invalid_assignee(self, mock_jira_client, valid_config):
        """Test issue creation with invalid assignee."""
        valid_config['assignee'] = 'invalid.user'
        
        # Mock user validation to fail
        mock_jira_client.user.side_effect = JIRAError(status_code=404, text="User not found")
        
        client = JiraClient(
            server=valid_config['jira_server'],
            username=valid_config['jira_username'],
            api_token=valid_config['jira_api_token']
        )
        
        # Should still create issue but without assignee
        issue_key = client.create_issue(valid_config)
        assert issue_key == "TEST-123"
    
    def test_create_subtask_with_parent(self, mock_jira_client, valid_config):
        """Test sub-task creation with parent issue."""
        valid_config['issue_type'] = 'Sub-task'
        valid_config['parent_issue_key'] = 'TEST-100'
        
        client = JiraClient(
            server=valid_config['jira_server'],
            username=valid_config['jira_username'],
            api_token=valid_config['jira_api_token']
        )
        
        issue_key = client.create_issue(valid_config)
        assert issue_key == "TEST-123"
        
        # Verify parent issue validation was called
        mock_jira_client.issue.assert_called_once_with('TEST-100')
    
    def test_create_subtask_invalid_parent(self, mock_jira_client, valid_config):
        """Test sub-task creation with invalid parent issue."""
        valid_config['issue_type'] = 'Sub-task'
        valid_config['parent_issue_key'] = 'INVALID-999'
        
        # Mock parent issue validation to fail
        mock_jira_client.issue.side_effect = JIRAError(status_code=404, text="Issue not found")
        
        client = JiraClient(
            server=valid_config['jira_server'],
            username=valid_config['jira_username'],
            api_token=valid_config['jira_api_token']
        )
        
        with pytest.raises(JiraOperationError, match="Parent issue.*not found"):
            client.create_issue(valid_config)
    
    def test_create_issue_with_labels(self, mock_jira_client, valid_config):
        """Test issue creation with labels."""
        valid_config['labels'] = ['bug', 'frontend', 'urgent']
        
        client = JiraClient(
            server=valid_config['jira_server'],
            username=valid_config['jira_username'],
            api_token=valid_config['jira_api_token']
        )
        
        issue_key = client.create_issue(valid_config)
        assert issue_key == "TEST-123"
        
        # Verify issue data includes labels
        call_args = mock_jira_client.create_issue.call_args
        issue_data = call_args[1]['fields']
        assert 'labels' in issue_data
        assert issue_data['labels'] == ['bug', 'frontend', 'urgent']
    
    def test_create_issue_jira_error(self, mock_jira_client, valid_config):
        """Test issue creation with Jira API error."""
        mock_jira_client.create_issue.side_effect = JIRAError(
            status_code=400, 
            text="Bad Request"
        )
        
        client = JiraClient(
            server=valid_config['jira_server'],
            username=valid_config['jira_username'],
            api_token=valid_config['jira_api_token']
        )
        
        with pytest.raises(JiraOperationError, match="Bad request"):
            client.create_issue(valid_config)
    
    @patch('builtins.open', new_callable=mock_open, read_data="test content")
    @patch('os.path.exists', return_value=True)
    @patch('os.access', return_value=True)
    @patch('os.path.getsize', return_value=1024)
    def test_add_attachments_success(self, mock_getsize, mock_access, mock_exists, mock_file, mock_jira_client, valid_config):
        """Test successful attachment addition."""
        valid_config['attachment_paths'] = ['test_file.txt']
        
        client = JiraClient(
            server=valid_config['jira_server'],
            username=valid_config['jira_username'],
            api_token=valid_config['jira_api_token']
        )
        
        # Mock attachment response
        mock_attachment = Mock()
        mock_attachment.filename = 'test_file.txt'
        mock_jira_client.add_attachment.return_value = mock_attachment
        
        issue_key = client.create_issue(valid_config)
        assert issue_key == "TEST-123"
        
        # Verify attachment was added
        mock_jira_client.add_attachment.assert_called_once()
    
    @patch('os.path.exists', return_value=False)
    def test_add_attachments_file_not_found(self, mock_exists, mock_jira_client, valid_config):
        """Test attachment handling when file doesn't exist."""
        valid_config['attachment_paths'] = ['nonexistent_file.txt']
        
        client = JiraClient(
            server=valid_config['jira_server'],
            username=valid_config['jira_username'],
            api_token=valid_config['jira_api_token']
        )
        
        # Should not raise error, just log warning
        issue_key = client.create_issue(valid_config)
        assert issue_key == "TEST-123"
        
        # Verify attachment was not attempted
        mock_jira_client.add_attachment.assert_not_called()
    
    def test_handle_connection_error_401(self):
        """Test connection error handling for 401 Unauthorized."""
        with patch('src.jira_client.JIRA') as mock_jira:
            mock_jira.side_effect = JIRAError(status_code=401, text="Unauthorized")
            
            with pytest.raises(JiraConnectionError) as exc_info:
                JiraClient("https://test.atlassian.net", "user", "token")
            
            assert "Authentication failed" in str(exc_info.value)
    
    def test_handle_connection_error_403(self):
        """Test connection error handling for 403 Forbidden."""
        with patch('src.jira_client.JIRA') as mock_jira:
            mock_jira.side_effect = JIRAError(status_code=403, text="Forbidden")
            
            with pytest.raises(JiraConnectionError) as exc_info:
                JiraClient("https://test.atlassian.net", "user", "token")
            
            assert "Access forbidden" in str(exc_info.value)
    
    def test_handle_connection_error_404(self):
        """Test connection error handling for 404 Not Found."""
        with patch('src.jira_client.JIRA') as mock_jira:
            mock_jira.side_effect = JIRAError(status_code=404, text="Not Found")
            
            with pytest.raises(JiraConnectionError) as exc_info:
                JiraClient("https://test.atlassian.net", "user", "token")
            
            assert "Jira server not found" in str(exc_info.value)
    
    def test_handle_operation_error_400(self, mock_jira_client, valid_config):
        """Test operation error handling for 400 Bad Request."""
        mock_jira_client.create_issue.side_effect = JIRAError(
            status_code=400, 
            text="Field 'project' is required"
        )
        
        client = JiraClient(
            server=valid_config['jira_server'],
            username=valid_config['jira_username'],
            api_token=valid_config['jira_api_token']
        )
        
        with pytest.raises(JiraOperationError) as exc_info:
            client.create_issue(valid_config)
        
        assert "Bad request" in str(exc_info.value)
    
    def test_handle_operation_error_404(self, mock_jira_client, valid_config):
        """Test operation error handling for 404 Not Found."""
        mock_jira_client.create_issue.side_effect = JIRAError(
            status_code=404, 
            text="Project not found"
        )
        
        client = JiraClient(
            server=valid_config['jira_server'],
            username=valid_config['jira_username'],
            api_token=valid_config['jira_api_token']
        )
        
        with pytest.raises(JiraOperationError) as exc_info:
            client.create_issue(valid_config)
        
        assert "Resource not found" in str(exc_info.value)