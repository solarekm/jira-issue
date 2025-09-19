"""
Custom exceptions for Jira Action.

This module defines all custom exceptions used throughout the application
for better error handling and debugging.
"""


class JiraActionError(Exception):
    """Base exception for all Jira Action errors."""
    
    def __init__(self, message: str, details: str = None):
        super().__init__(message)
        self.message = message
        self.details = details
    
    def __str__(self):
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class ValidationError(JiraActionError):
    """Raised when input validation fails."""
    pass


class JiraConnectionError(JiraActionError):
    """Raised when connection to Jira fails."""
    pass


class JiraOperationError(JiraActionError):
    """Raised when Jira operation fails."""
    pass


class ConfigurationError(JiraActionError):
    """Raised when configuration is invalid."""
    pass


class AttachmentError(JiraActionError):
    """Raised when attachment operations fail."""
    pass