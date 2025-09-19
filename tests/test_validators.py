"""
Tests for input validators.
"""

import pytest
from src.validators import InputValidator
from src.exceptions import ValidationError


class TestInputValidator:
    def setup_method(self):
        self.validator = InputValidator()

    def test_validate_url_valid(self):
        """Test valid URL validation."""
        valid_urls = [
            "https://company.atlassian.net",
            "http://localhost:8080",
            "https://jira.example.com:8443",
            "https://test-jira.company.com",
        ]
        for url in valid_urls:
            result = self.validator.validate_url(url)
            assert result == url.rstrip("/")

    def test_validate_url_strips_trailing_slash(self):
        """Test that trailing slashes are removed."""
        url = "https://company.atlassian.net/"
        result = self.validator.validate_url(url)
        assert result == "https://company.atlassian.net"

    def test_validate_url_invalid(self):
        """Test invalid URL validation."""
        invalid_urls = [
            "",
            "not-a-url",
            "ftp://invalid.com",
            "javascript:alert(1)",
            "https://evil.com/$(rm -rf /)",
        ]
        for url in invalid_urls:
            with pytest.raises(ValidationError):
                self.validator.validate_url(url)

    def test_validate_project_key_valid(self):
        """Test valid project key validation."""
        valid_keys = ["PROJ", "TEST123", "A", "PROJECT_1", "DEV"]
        for key in valid_keys:
            result = self.validator.validate_project_key(key)
            assert result == key.upper()

    def test_validate_project_key_case_insensitive(self):
        """Test that project keys are converted to uppercase."""
        result = self.validator.validate_project_key("proj")
        assert result == "PROJ"

    def test_validate_project_key_invalid(self):
        """Test invalid project key validation."""
        invalid_keys = [
            "",
            "123",  # Cannot start with number
            "PROJ-123",  # Cannot contain dash
            "TOOLONGPROJECTKEY",  # Too long
            "PR@J",  # Invalid characters
        ]
        for key in invalid_keys:
            with pytest.raises(ValidationError):
                self.validator.validate_project_key(key)

    def test_validate_issue_type_valid(self):
        """Test valid issue type validation."""
        valid_types = ["Task", "Bug", "Story", "Sub-task", "Epic"]
        for issue_type in valid_types:
            result = self.validator.validate_issue_type(issue_type)
            assert result == issue_type

    def test_validate_issue_type_invalid(self):
        """Test invalid issue type validation."""
        invalid_types = ["", "CustomType", "task", "TASK"]
        for issue_type in invalid_types:
            with pytest.raises(ValidationError):
                self.validator.validate_issue_type(issue_type)

    def test_validate_summary_valid(self):
        """Test valid summary validation."""
        valid_summaries = [
            "Simple summary",
            "A" * 255,  # Maximum length
            "Summary with numbers 123",
            "Summary with special chars: - _ .",
        ]
        for summary in valid_summaries:
            result = self.validator.validate_summary(summary)
            assert result == summary.strip()

    def test_validate_summary_strips_whitespace(self):
        """Test that summary whitespace is stripped."""
        summary = "  Test summary  "
        result = self.validator.validate_summary(summary)
        assert result == "Test summary"

    def test_validate_summary_invalid(self):
        """Test invalid summary validation."""
        invalid_summaries = [
            "",
            "   ",  # Only whitespace
            "A" * 256,  # Too long
            "Summary with $(malicious) code",
        ]
        for summary in invalid_summaries:
            with pytest.raises(ValidationError):
                self.validator.validate_summary(summary)

    def test_validate_description_valid(self):
        """Test valid description validation."""
        valid_descriptions = [
            "Simple description",
            "A" * 32767,  # Maximum length
            "Description\\nwith\\nmultiple\\nlines",
            "Description with various chars: !@#%^*[]{}:,.",
        ]
        for description in valid_descriptions:
            result = self.validator.validate_description(description)
            assert result == description.strip()

    def test_validate_description_invalid(self):
        """Test invalid description validation."""
        invalid_descriptions = [
            "",
            "   ",  # Only whitespace
            "A" * 32768,  # Too long
            "Description with <script>alert(1)</script>",
        ]
        for description in invalid_descriptions:
            with pytest.raises(ValidationError):
                self.validator.validate_description(description)

    def test_validate_priority_valid(self):
        """Test valid priority validation."""
        valid_priorities = ["Highest", "High", "Medium", "Low", "Lowest"]
        for priority in valid_priorities:
            result = self.validator.validate_priority(priority)
            assert result == priority

    def test_validate_priority_invalid(self):
        """Test invalid priority validation."""
        invalid_priorities = ["", "Critical", "Normal", "high", "HIGH"]
        for priority in invalid_priorities:
            with pytest.raises(ValidationError):
                self.validator.validate_priority(priority)

    def test_validate_username_valid(self):
        """Test valid username validation."""
        valid_usernames = ["john.doe", "user@example.com", "test_user123", "user-name"]
        for username in valid_usernames:
            result = self.validator.validate_username(username)
            assert result == username

    def test_validate_username_invalid(self):
        """Test invalid username validation."""
        invalid_usernames = [
            "",
            "user with spaces",
            "user$(malicious)",
            "a" * 255,  # Too long
        ]
        for username in invalid_usernames:
            with pytest.raises(ValidationError):
                self.validator.validate_username(username)

    def test_validate_token_valid(self):
        """Test valid token validation."""
        valid_token = "ATATT3xFfGF0" + "x" * 20  # Simulated Atlassian token
        result = self.validator.validate_token(valid_token)
        assert result == valid_token

    def test_validate_token_invalid(self):
        """Test invalid token validation."""
        invalid_tokens = [
            "",
            "short",  # Too short
            "password",  # Obvious placeholder
            "token",
        ]
        for token in invalid_tokens:
            with pytest.raises(ValidationError):
                self.validator.validate_token(token)

    def test_validate_parent_issue_key_valid(self):
        """Test valid parent issue key validation."""
        valid_keys = ["PROJ-123", "TEST-1", "DEV-999"]
        for key in valid_keys:
            result = self.validator.validate_parent_issue_key(key)
            assert result == key.upper()

    def test_validate_parent_issue_key_empty(self):
        """Test that empty parent issue key returns None."""
        result = self.validator.validate_parent_issue_key("")
        assert result is None

        result = self.validator.validate_parent_issue_key(None)
        assert result is None

    def test_validate_parent_issue_key_invalid(self):
        """Test invalid parent issue key validation."""
        invalid_keys = [
            "PROJ123",  # Missing dash
            "123-PROJ",  # Wrong format
            "PROJ-",  # Missing number
            "-123",  # Missing project
        ]
        for key in invalid_keys:
            with pytest.raises(ValidationError):
                self.validator.validate_parent_issue_key(key)

    def test_validate_labels_valid(self):
        """Test valid labels validation."""
        test_cases = [
            ("", []),
            ("label1", ["label1"]),
            ("label1,label2,label3", ["label1", "label2", "label3"]),
            ("bug,frontend,urgent", ["bug", "frontend", "urgent"]),
            ("  label1  ,  label2  ", ["label1", "label2"]),  # Strips whitespace
        ]
        for input_labels, expected in test_cases:
            result = self.validator.validate_labels(input_labels)
            assert result == expected

    def test_validate_labels_invalid(self):
        """Test invalid labels validation."""
        invalid_labels = [
            "label with spaces",
            "label1,label with spaces",
            "label$(malicious)",
            "a" * 256,  # Too long
        ]
        for labels in invalid_labels:
            with pytest.raises(ValidationError):
                self.validator.validate_labels(labels)

    def test_validate_attachment_paths_valid(self, temp_file):
        """Test valid attachment paths validation."""
        # Use relative path for testing
        import os

        relative_temp = os.path.basename(temp_file)

        # Create file in current directory for testing
        with open(relative_temp, "w") as f:
            f.write("Test content")

        try:
            result = self.validator.validate_attachment_paths(relative_temp)
            assert result == [relative_temp]

            # Multiple files - create second relative file
            relative_temp2 = "test_file_2.txt"
            with open(relative_temp2, "w") as f:
                f.write("Second test file")

            try:
                result = self.validator.validate_attachment_paths(
                    f"{relative_temp},{relative_temp2}"
                )
                assert result == [relative_temp, relative_temp2]
            finally:
                if os.path.exists(relative_temp2):
                    os.unlink(relative_temp2)
        finally:
            # Cleanup
            if os.path.exists(relative_temp):
                os.unlink(relative_temp)

    def test_validate_attachment_paths_empty(self):
        """Test that empty attachment paths return empty list."""
        result = self.validator.validate_attachment_paths("")
        assert result == []

        result = self.validator.validate_attachment_paths(None)
        assert result == []

    def test_validate_attachment_paths_invalid(self):
        """Test invalid attachment paths validation."""
        invalid_paths = [
            "/etc/passwd",  # Absolute path
            "../../../etc/passwd",  # Directory traversal
            "nonexistent_file.txt",  # File doesn't exist
        ]
        for path in invalid_paths:
            with pytest.raises(ValidationError):
                self.validator.validate_attachment_paths(path)

    def test_malicious_content_detection(self):
        """Test detection of malicious content."""
        malicious_inputs = [
            "test; rm -rf /",
            "test && malicious",
            "<script>alert(1)</script>",
            "javascript:void(0)",
            "test$(whoami)",
            "test`whoami`",
        ]
        for malicious in malicious_inputs:
            with pytest.raises(ValidationError, match="malicious content"):
                self.validator.validate_summary(malicious)
