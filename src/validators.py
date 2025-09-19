"""
Input validation module for Jira Action.

This module provides comprehensive security and data integrity checks
for all input parameters to prevent injection attacks and ensure data quality.
"""

import re
import os
from urllib.parse import urlparse
from typing import Optional, List

from .exceptions import ValidationError


class InputValidator:
    """Validates all input parameters for security and correctness."""
    
    # Security patterns to detect malicious content
    MALICIOUS_PATTERNS = [
        r'[;&|`$()]',          # Shell injection characters
        r'<script[^>]*>',      # XSS script tags
        r'javascript:',        # JavaScript injection
        r'data:',              # Data URI injection
        r'vbscript:',          # VBScript injection
        r'onload\s*=',         # Event handler injection
        r'onerror\s*=',        # Error handler injection
        r'\$\([^)]*\)',        # Command substitution
        r'`[^`]*`',            # Backtick command execution
    ]
    
    # Valid Jira issue types
    VALID_ISSUE_TYPES = ['Task', 'Bug', 'Story', 'Sub-task', 'Epic']
    
    # Valid priority levels
    VALID_PRIORITIES = ['Highest', 'High', 'Medium', 'Low', 'Lowest']
    
    def validate_url(self, url: str) -> str:
        """
        Validate Jira server URL.
        
        Args:
            url: The URL to validate
            
        Returns:
            str: The validated and normalized URL
            
        Raises:
            ValidationError: If URL is invalid or potentially malicious
        """
        if not url or not url.strip():
            raise ValidationError("Jira server URL cannot be empty")
        
        url = url.strip()
        
        try:
            parsed = urlparse(url)
            if not parsed.scheme in ['http', 'https']:
                raise ValidationError("Jira server URL must use HTTP or HTTPS protocol")
            if not parsed.netloc:
                raise ValidationError("Invalid Jira server URL format - missing hostname")
        except Exception as e:
            raise ValidationError(f"Invalid Jira server URL: {str(e)}")
        
        self._check_malicious_content(url, "jira_server")
        return url.rstrip('/')
    
    def validate_project_key(self, project_key: str) -> str:
        """
        Validate Jira project key format.
        
        Args:
            project_key: The project key to validate
            
        Returns:
            str: The validated project key
            
        Raises:
            ValidationError: If project key format is invalid
        """
        if not project_key or not project_key.strip():
            raise ValidationError("Project key cannot be empty")
        
        project_key = project_key.strip().upper()
        
        # Jira project keys must start with a letter and contain only uppercase letters, numbers, and underscores
        if not re.match(r'^[A-Z][A-Z0-9_]*$', project_key):
            raise ValidationError(
                "Project key must start with a letter and contain only uppercase letters, numbers, and underscores"
            )
        
        if len(project_key) > 10:
            raise ValidationError("Project key cannot exceed 10 characters")
        
        return project_key
    
    def validate_issue_type(self, issue_type: str) -> str:
        """
        Validate issue type.
        
        Args:
            issue_type: The issue type to validate
            
        Returns:
            str: The validated issue type
            
        Raises:
            ValidationError: If issue type is not supported
        """
        if not issue_type or not issue_type.strip():
            raise ValidationError("Issue type cannot be empty")
        
        issue_type = issue_type.strip()
        
        if issue_type not in self.VALID_ISSUE_TYPES:
            raise ValidationError(
                f"Issue type '{issue_type}' is not supported. "
                f"Valid types: {', '.join(self.VALID_ISSUE_TYPES)}"
            )
        
        return issue_type
    
    def validate_summary(self, summary: str) -> str:
        """
        Validate issue summary.
        
        Args:
            summary: The issue summary to validate
            
        Returns:
            str: The validated and trimmed summary
            
        Raises:
            ValidationError: If summary is invalid
        """
        if not summary or not summary.strip():
            raise ValidationError("Issue summary cannot be empty")
        
        summary = summary.strip()
        
        if len(summary) > 255:
            raise ValidationError("Issue summary cannot exceed 255 characters")
        
        # Check for control characters
        if any(ord(char) < 32 for char in summary if char not in '\t\n\r'):
            raise ValidationError("Issue summary contains invalid control characters")
        
        self._check_malicious_content(summary, "summary")
        return summary
    
    def validate_description(self, description: str) -> str:
        """
        Validate issue description.
        
        Args:
            description: The issue description to validate
            
        Returns:
            str: The validated and trimmed description
            
        Raises:
            ValidationError: If description is invalid
        """
        if not description or not description.strip():
            raise ValidationError("Issue description cannot be empty")
        
        description = description.strip()
        
        if len(description) > 32767:
            raise ValidationError("Issue description cannot exceed 32767 characters")
        
        self._check_malicious_content(description, "description")
        return description
    
    def validate_priority(self, priority: str) -> str:
        """
        Validate issue priority.
        
        Args:
            priority: The priority to validate
            
        Returns:
            str: The validated priority
            
        Raises:
            ValidationError: If priority is not supported
        """
        if not priority or not priority.strip():
            raise ValidationError("Issue priority cannot be empty")
        
        priority = priority.strip()
        
        if priority not in self.VALID_PRIORITIES:
            raise ValidationError(
                f"Priority '{priority}' is not supported. "
                f"Valid priorities: {', '.join(self.VALID_PRIORITIES)}"
            )
        
        return priority
    
    def validate_username(self, username: str) -> str:
        """
        Validate Jira username.
        
        Args:
            username: The username to validate
            
        Returns:
            str: The validated username
            
        Raises:
            ValidationError: If username format is invalid
        """
        if not username or not username.strip():
            raise ValidationError("Username cannot be empty")
        
        username = username.strip()
        
        # Allow email addresses and typical usernames
        if not re.match(r'^[a-zA-Z0-9@._-]+$', username):
            raise ValidationError("Username contains invalid characters")
        
        if len(username) > 254:  # Email max length
            raise ValidationError("Username cannot exceed 254 characters")
        
        self._check_malicious_content(username, "username")
        return username
    
    def validate_token(self, token: str) -> str:
        """
        Validate API token format.
        
        Args:
            token: The API token to validate
            
        Returns:
            str: The validated token
            
        Raises:
            ValidationError: If token format is invalid
        """
        if not token or not token.strip():
            raise ValidationError("API token cannot be empty")
        
        token = token.strip()
        
        # Basic token format validation - Atlassian tokens are typically long
        if len(token) < 20:
            raise ValidationError("API token appears to be too short (minimum 20 characters)")
        
        # Check for obviously invalid tokens
        if token.lower() in ['password', 'token', 'secret', 'key']:
            raise ValidationError("API token appears to be a placeholder")
        
        return token
    
    def validate_parent_issue_key(self, parent_key: Optional[str]) -> Optional[str]:
        """
        Validate parent issue key for sub-tasks.
        
        Args:
            parent_key: The parent issue key to validate
            
        Returns:
            Optional[str]: The validated parent key or None
            
        Raises:
            ValidationError: If parent key format is invalid
        """
        if not parent_key or not parent_key.strip():
            return None
        
        parent_key = parent_key.strip().upper()
        
        # Jira issue keys format: PROJECT-123
        if not re.match(r'^[A-Z][A-Z0-9_]*-\d+$', parent_key):
            raise ValidationError(
                "Parent issue key must be in format PROJECT-123 (e.g., PROJ-123)"
            )
        
        return parent_key
    
    def validate_labels(self, labels: Optional[str]) -> List[str]:
        """
        Validate and parse issue labels.
        
        Args:
            labels: Comma-separated labels string
            
        Returns:
            List[str]: List of validated labels
            
        Raises:
            ValidationError: If any label is invalid
        """
        if not labels or not labels.strip():
            return []
        
        label_list = [label.strip() for label in labels.split(',') if label.strip()]
        validated_labels = []
        
        for label in label_list:
            if len(label) > 255:
                raise ValidationError(f"Label '{label}' cannot exceed 255 characters")
            
            # Labels cannot contain spaces in Jira
            if ' ' in label:
                raise ValidationError(f"Label '{label}' cannot contain spaces")
            
            # Check for valid label format
            if not re.match(r'^[a-zA-Z0-9_-]+$', label):
                raise ValidationError(f"Label '{label}' contains invalid characters")
            
            self._check_malicious_content(label, f"label '{label}'")
            validated_labels.append(label)
        
        return validated_labels
    
    def validate_attachment_paths(self, paths: Optional[str]) -> List[str]:
        """
        Validate attachment file paths.
        
        Args:
            paths: Comma-separated file paths
            
        Returns:
            List[str]: List of validated file paths
            
        Raises:
            ValidationError: If any path is invalid or file doesn't exist
        """
        if not paths or not paths.strip():
            return []
        
        path_list = [path.strip() for path in paths.split(',') if path.strip()]
        validated_paths = []
        
        for path in path_list:
            # Security check - prevent directory traversal
            if '..' in path or path.startswith('/'):
                raise ValidationError(f"Invalid file path '{path}' - potential security risk")
            
            # Check if file exists and is readable
            if not os.path.exists(path):
                raise ValidationError(f"Attachment file not found: {path}")
            
            if not os.path.isfile(path):
                raise ValidationError(f"Path '{path}' is not a file")
            
            if not os.access(path, os.R_OK):
                raise ValidationError(f"File '{path}' is not readable")
            
            # Check file size (limit to 10MB)
            try:
                file_size = os.path.getsize(path)
                if file_size > 10 * 1024 * 1024:  # 10MB
                    raise ValidationError(f"File '{path}' is too large (max 10MB)")
            except OSError as e:
                raise ValidationError(f"Cannot access file '{path}': {str(e)}")
            
            validated_paths.append(path)
        
        return validated_paths
    
    def _check_malicious_content(self, content: str, field_name: str) -> None:
        """
        Check for potentially malicious content in input fields.
        
        Args:
            content: The content to check
            field_name: Name of the field being validated
            
        Raises:
            ValidationError: If malicious content is detected
        """
        for pattern in self.MALICIOUS_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                raise ValidationError(
                    f"Potentially malicious content detected in {field_name}. "
                    f"Please review your input for security issues."
                )