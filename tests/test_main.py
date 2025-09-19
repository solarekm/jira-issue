"""
Integration tests for the main module.
"""

import pytest
import os
from unittest.mock import patch, Mock

from src.main import validate_and_prepare_config, create_jira_issue, main
from src.exceptions import ValidationError, JiraConnectionError


class TestMainModule:
    
    def test_validate_and_prepare_config_success(self, mock_environment):
        """Test successful configuration validation."""
        config = validate_and_prepare_config()
        
        assert config['jira_server'] == 'https://test.atlassian.net'
        assert config['project_key'] == 'TEST'
        assert config['issue_type'] == 'Task'
        assert config['issue_summary'] == 'Test issue summary'
        assert config['labels'] == []
        assert config['attachment_paths'] == []
    
    def test_validate_and_prepare_config_with_labels(self, mock_environment):
        """Test configuration validation with labels."""
        mock_environment['INPUT_ISSUE_LABELS'] = 'bug,frontend,urgent'
        
        with patch.dict(os.environ, mock_environment):
            config = validate_and_prepare_config()
            assert config['labels'] == ['bug', 'frontend', 'urgent']
    
    def test_validate_and_prepare_config_subtask_validation(self, mock_environment):
        """Test sub-task validation requires parent issue."""
        mock_environment['INPUT_ISSUE_TYPE'] = 'Sub-task'
        mock_environment['INPUT_PARENT_ISSUE_KEY'] = ''
        
        with patch.dict(os.environ, mock_environment):
            with pytest.raises(ValidationError, match="Parent issue key is required"):
                validate_and_prepare_config()
    
    def test_validate_and_prepare_config_subtask_with_parent(self, mock_environment):
        """Test sub-task validation with valid parent."""
        mock_environment['INPUT_ISSUE_TYPE'] = 'Sub-task'
        mock_environment['INPUT_PARENT_ISSUE_KEY'] = 'TEST-100'
        
        with patch.dict(os.environ, mock_environment):
            config = validate_and_prepare_config()
            assert config['issue_type'] == 'Sub-task'
            assert config['parent_issue_key'] == 'TEST-100'
    
    def test_validate_and_prepare_config_invalid_url(self, mock_environment):
        """Test configuration validation with invalid URL."""
        mock_environment['INPUT_JIRA_SERVER'] = 'invalid-url'
        
        with patch.dict(os.environ, mock_environment):
            with pytest.raises(ValidationError):
                validate_and_prepare_config()
    
    def test_validate_and_prepare_config_missing_env(self):
        """Test configuration validation with missing environment variables."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValidationError, match="Environment variable error"):
                validate_and_prepare_config()
    
    @patch('src.main.JiraClient')
    def test_create_jira_issue_success(self, mock_client_class, valid_config):
        """Test successful Jira issue creation."""
        mock_client = Mock()
        mock_client.create_issue.return_value = 'TEST-123'
        mock_client_class.return_value = mock_client
        
        result = create_jira_issue(valid_config)
        assert result == 'TEST-123'
        
        mock_client_class.assert_called_once_with(
            server=valid_config['jira_server'],
            username=valid_config['jira_username'],
            api_token=valid_config['jira_api_token']
        )
        mock_client.create_issue.assert_called_once_with(valid_config)
    
    @patch('src.main.JiraClient')
    def test_create_jira_issue_connection_error(self, mock_client_class, valid_config):
        """Test Jira issue creation with connection error."""
        mock_client_class.side_effect = JiraConnectionError("Connection failed")
        
        with pytest.raises(JiraConnectionError):
            create_jira_issue(valid_config)
    
    @patch('src.main.create_jira_issue')
    @patch('src.main.validate_and_prepare_config')
    @patch('src.main.GitHubIntegration')
    def test_main_success(self, mock_github, mock_validate, mock_create, mock_environment):
        """Test successful main execution."""
        mock_validate.return_value = {
            'jira_server': 'https://test.atlassian.net',
            'issue_summary': 'Test summary',
            'issue_type': 'Task',
            'project_key': 'TEST'
        }
        mock_create.return_value = 'TEST-123'
        
        with patch.dict(os.environ, mock_environment):
            main()
        
        mock_validate.assert_called_once()
        mock_create.assert_called_once()
        mock_github.set_output.assert_called()
        mock_github.update_step_summary.assert_called_once()
    
    @patch('src.main.validate_and_prepare_config')
    @patch('sys.exit')
    def test_main_validation_error(self, mock_exit, mock_validate, mock_environment):
        """Test main execution with validation error."""
        mock_validate.side_effect = ValidationError("Invalid input")
        
        with patch.dict(os.environ, mock_environment):
            main()
        
        mock_exit.assert_called_once_with(1)
    
    @patch('src.main.validate_and_prepare_config')
    @patch('src.main.create_jira_issue')
    @patch('sys.exit')
    def test_main_connection_error(self, mock_exit, mock_create, mock_validate, mock_environment):
        """Test main execution with connection error."""
        mock_validate.return_value = {'test': 'config'}
        mock_create.side_effect = JiraConnectionError("Connection failed")
        
        with patch.dict(os.environ, mock_environment):
            main()
        
        mock_exit.assert_called_once_with(1)
    
    @patch('src.main.validate_and_prepare_config')
    @patch('sys.exit')
    def test_main_unexpected_error(self, mock_exit, mock_validate, mock_environment):
        """Test main execution with unexpected error."""
        mock_validate.side_effect = Exception("Unexpected error")
        
        with patch.dict(os.environ, mock_environment):
            main()
        
        mock_exit.assert_called_once_with(1)