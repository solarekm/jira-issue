"""
Tests for utility functions.
"""

import pytest
import os
import tempfile
from unittest.mock import patch, mock_open

from src.utils import (
    GitHubIntegration,
    EnvironmentHelper,
    setup_logging,
    mask_sensitive_data
)


class TestGitHubIntegration:
    
    def test_update_step_summary_success(self):
        """Test successful step summary update."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Existing content\\n")
            temp_path = f.name
        
        try:
            with patch.dict(os.environ, {'GITHUB_STEP_SUMMARY': temp_path}):
                GitHubIntegration.update_step_summary(
                    "https://test.atlassian.net",
                    "TEST-123"
                )
                
                # Verify content was appended
                with open(temp_path, 'r') as f:
                    content = f.read()
                    assert "TEST-123" in content
                    assert "https://test.atlassian.net/browse/TEST-123" in content
                    assert "Existing content" in content
        finally:
            os.unlink(temp_path)
    
    def test_update_step_summary_no_env_var(self):
        """Test step summary update when environment variable is missing."""
        with patch.dict(os.environ, {}, clear=True):
            # Should not raise exception
            GitHubIntegration.update_step_summary(
                "https://test.atlassian.net",
                "TEST-123"
            )
    
    def test_set_output_success(self):
        """Test successful output setting."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_path = f.name
        
        try:
            with patch.dict(os.environ, {'GITHUB_OUTPUT': temp_path}):
                GitHubIntegration.set_output("issue_key", "TEST-123")
                
                # Verify content was written
                with open(temp_path, 'r') as f:
                    content = f.read()
                    assert "issue_key=TEST-123" in content
        finally:
            os.unlink(temp_path)
    
    def test_set_output_no_env_var(self):
        """Test output setting when environment variable is missing."""
        with patch.dict(os.environ, {}, clear=True):
            # Should not raise exception
            GitHubIntegration.set_output("issue_key", "TEST-123")


class TestEnvironmentHelper:
    
    def test_get_required_env_success(self):
        """Test getting required environment variable."""
        with patch.dict(os.environ, {'TEST_VAR': 'test_value'}):
            result = EnvironmentHelper.get_required_env('TEST_VAR')
            assert result == 'test_value'
    
    def test_get_required_env_missing(self):
        """Test getting missing required environment variable."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Required environment variable"):
                EnvironmentHelper.get_required_env('MISSING_VAR')
    
    def test_get_optional_env_present(self):
        """Test getting optional environment variable that exists."""
        with patch.dict(os.environ, {'TEST_VAR': 'test_value'}):
            result = EnvironmentHelper.get_optional_env('TEST_VAR', 'default')
            assert result == 'test_value'
    
    def test_get_optional_env_missing(self):
        """Test getting optional environment variable that doesn't exist."""
        with patch.dict(os.environ, {}, clear=True):
            result = EnvironmentHelper.get_optional_env('MISSING_VAR', 'default')
            assert result == 'default'
    
    def test_parse_comma_separated_valid(self):
        """Test parsing comma-separated values."""
        test_cases = [
            ("", []),
            ("single", ["single"]),
            ("one,two,three", ["one", "two", "three"]),
            ("  one  ,  two  ,  three  ", ["one", "two", "three"]),
            ("one,,three", ["one", "three"]),  # Empty values filtered out
        ]
        
        for input_str, expected in test_cases:
            result = EnvironmentHelper.parse_comma_separated(input_str)
            assert result == expected
    
    def test_parse_comma_separated_none(self):
        """Test parsing None value."""
        result = EnvironmentHelper.parse_comma_separated(None)
        assert result == []
    
    def test_get_all_inputs_success(self, mock_environment):
        """Test getting all GitHub Actions inputs."""
        result = EnvironmentHelper.get_all_inputs()
        
        assert result['jira_server'] == 'https://test.atlassian.net'
        assert result['jira_username'] == 'test.user@example.com'
        assert result['project_key'] == 'TEST'
        assert result['issue_type'] == 'Task'
    
    def test_get_all_inputs_missing_required(self):
        """Test getting inputs when required ones are missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                EnvironmentHelper.get_all_inputs()


class TestUtilityFunctions:
    
    def test_setup_logging_info_level(self):
        """Test logging setup with INFO level."""
        setup_logging("INFO")
        
        import logging
        logger = logging.getLogger("test")
        assert logger.isEnabledFor(logging.INFO)
        assert not logger.isEnabledFor(logging.DEBUG)
    
    def test_setup_logging_debug_level(self):
        """Test logging setup with DEBUG level."""
        setup_logging("DEBUG")
        
        import logging
        logger = logging.getLogger("test")
        assert logger.isEnabledFor(logging.DEBUG)
        assert logger.isEnabledFor(logging.INFO)
    
    def test_setup_logging_invalid_level(self):
        """Test logging setup with invalid level defaults to INFO."""
        setup_logging("INVALID")
        
        import logging
        logger = logging.getLogger("test")
        assert logger.isEnabledFor(logging.INFO)
    
    def test_mask_sensitive_data_normal(self):
        """Test masking sensitive data with normal input."""
        result = mask_sensitive_data("secretpassword123", visible_chars=3)
        assert result.endswith("123")
        assert "*" in result
        assert "secret" not in result
    
    def test_mask_sensitive_data_short(self):
        """Test masking short sensitive data."""
        result = mask_sensitive_data("abc", visible_chars=4)
        assert result == "********"
    
    def test_mask_sensitive_data_empty(self):
        """Test masking empty sensitive data."""
        result = mask_sensitive_data("", visible_chars=4)
        assert result == "********"
    
    def test_mask_sensitive_data_custom_char(self):
        """Test masking with custom mask character."""
        result = mask_sensitive_data("secretpassword123", mask_char="X", visible_chars=3)
        assert result.endswith("123")
        assert "X" in result
        assert "*" not in result