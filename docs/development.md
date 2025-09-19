# Development Guide

This guide provides detailed information for developers working on the Jira Issue Action.

## 🏗️ Architecture Overview

### High-Level Architecture
```
GitHub Actions Workflow
         ↓
    action.yml (Entry Point)
         ↓
   Environment Variables
         ↓
     src/main.py
         ↓
    ┌─────────────────┐
    │   Validation    │ ← src/validators.py
    │   (Security)    │
    └─────────────────┘
         ↓
    ┌─────────────────┐
    │  Jira Client    │ ← src/jira_client.py  
    │  (API Wrapper)  │
    └─────────────────┘
         ↓
    ┌─────────────────┐
    │ GitHub Output   │ ← src/utils.py
    │ (Integration)   │
    └─────────────────┘
```

### Module Responsibilities

#### src/main.py
- **Purpose**: Entry point and orchestration
- **Responsibilities**: 
  - Environment variable extraction
  - Error handling and logging setup
  - Workflow coordination
  - GitHub Actions integration

#### src/validators.py
- **Purpose**: Input validation and security
- **Responsibilities**:
  - Injection attack prevention
  - Data format validation
  - Security pattern detection
  - Input sanitization

#### src/jira_client.py
- **Purpose**: Jira API interaction
- **Responsibilities**:
  - Authentication handling
  - Issue creation and management
  - Attachment processing
  - API error handling

#### src/exceptions.py
- **Purpose**: Custom exception definitions
- **Responsibilities**:
  - Structured error handling
  - Error categorization
  - User-friendly error messages

#### src/utils.py
- **Purpose**: Utility functions
- **Responsibilities**:
  - GitHub Actions integration
  - Environment variable handling
  - Logging configuration
  - Helper functions

## 🔧 Development Environment

### Local Setup
```bash
# Clone repository
git clone https://github.com/solarekm/jira-issue.git
cd jira-issue

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov pytest-mock responses
pip install black flake8 mypy bandit safety
```

### IDE Configuration

#### VS Code Settings (.vscode/settings.json)
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        ".coverage": true,
        "htmlcov": true
    }
}
```

#### PyCharm Configuration
- **Interpreter**: Set to virtual environment Python
- **Code Style**: Configure Black formatter
- **Inspections**: Enable type checking and security inspections
- **Test Runner**: Configure pytest as default

## 🧪 Testing Strategy

### Test Structure
```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_main.py             # Main module tests
├── test_validators.py       # Validation logic tests
├── test_jira_client.py      # Jira client tests
├── test_utils.py            # Utility function tests
├── fixtures/
│   └── test_data.json       # Test data and scenarios
└── run_tests.py             # Test runner script
```

### Test Categories

#### Unit Tests
- **Purpose**: Test individual functions and methods
- **Scope**: Single module or function
- **Mocking**: Mock external dependencies
- **Coverage**: Aim for 95%+ coverage

#### Integration Tests
- **Purpose**: Test module interactions
- **Scope**: Multiple modules working together
- **Mocking**: Mock only external services
- **Focus**: Data flow and error propagation

#### Security Tests
- **Purpose**: Validate security features
- **Scope**: Input validation and injection prevention
- **Focus**: Malicious input handling

### Running Tests

#### All Tests
```bash
# Using test runner
python tests/run_tests.py

# Using pytest directly
pytest tests/ -v --cov=src --cov-report=html
```

#### Specific Test Categories
```bash
# Unit tests only
pytest tests/test_validators.py -v

# Security tests
pytest tests/ -v -k "malicious or security"

# Integration tests
pytest tests/test_main.py -v
```

#### Test Coverage
```bash
# Generate coverage report
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html  # View in browser
```

## 🔒 Security Development

### Security Principles
1. **Defense in Depth**: Multiple layers of security
2. **Fail Secure**: Fail closed, not open
3. **Least Privilege**: Minimal required permissions
4. **Input Validation**: Validate all inputs
5. **Output Encoding**: Encode all outputs

### Security Testing
```bash
# Static security analysis
bandit -r src/ -f json -o security-report.json

# Dependency vulnerability scan
safety check

# Manual security testing
python -c "
from src.validators import InputValidator
validator = InputValidator()
# Test malicious inputs
test_inputs = [
    'test; rm -rf /',
    '<script>alert(1)</script>',
    '$(whoami)',
    '../../../etc/passwd'
]
for inp in test_inputs:
    try:
        validator.validate_summary(inp)
        print(f'SECURITY ISSUE: {inp} was not blocked!')
    except Exception as e:
        print(f'OK: {inp} blocked with {type(e).__name__}')
"
```

### Common Security Patterns

#### Input Validation
```python
def validate_input(self, value: str, field_name: str) -> str:
    # 1. Type checking
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string")
    
    # 2. Length validation
    if len(value) > MAX_LENGTH:
        raise ValidationError(f"{field_name} too long")
    
    # 3. Pattern validation
    if not re.match(VALID_PATTERN, value):
        raise ValidationError(f"{field_name} format invalid")
    
    # 4. Security validation
    self._check_malicious_content(value, field_name)
    
    return value.strip()
```

#### Secure Logging
```python
def log_secure(self, message: str, sensitive_data: str = None):
    if sensitive_data:
        # Mask sensitive data
        masked = self.mask_sensitive_data(sensitive_data)
        message = message.replace(sensitive_data, masked)
    
    self.logger.info(message)
```

## 🐛 Debugging Guide

### Debug Configuration

#### Environment Variables
```bash
# Enable debug logging
export INPUT_LOG_LEVEL=DEBUG

# Test configuration
export INPUT_JIRA_SERVER="https://test.atlassian.net"
export INPUT_JIRA_USERNAME="test@example.com"
export INPUT_JIRA_API_TOKEN="test_token"
export INPUT_PROJECT_KEY="TEST"
export INPUT_ISSUE_TYPE="Task"
export INPUT_ISSUE_SUMMARY="Debug test"
export INPUT_ISSUE_DESCRIPTION="Debug test description"
export INPUT_ISSUE_PRIORITY="Medium"
```

#### Local Testing
```python
# Test validation only
from src.main import validate_and_prepare_config
try:
    config = validate_and_prepare_config()
    print("✓ Validation passed")
    print(f"Config: {config}")
except Exception as e:
    print(f"✗ Validation failed: {e}")

# Test with mock Jira client
from unittest.mock import Mock, patch
from src.main import create_jira_issue

with patch('src.main.JiraClient') as mock_client:
    mock_instance = Mock()
    mock_instance.create_issue.return_value = 'TEST-123'
    mock_client.return_value = mock_instance
    
    result = create_jira_issue(config)
    print(f"✓ Mock issue created: {result}")
```

### Common Issues and Solutions

#### Import Errors
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH="./src:$PYTHONPATH"

# Or use module import
python -m src.main
```

#### Missing Dependencies
```bash
# Install missing packages
pip install -r requirements.txt

# For development
pip install pytest pytest-cov pytest-mock responses black flake8 mypy
```

#### Test Failures
```bash
# Run specific failing test
pytest tests/test_validators.py::TestInputValidator::test_specific_method -v

# Run with debug output
pytest tests/ -v -s --tb=long

# Run with coverage to see missed lines
pytest tests/ --cov=src --cov-report=term-missing
```

## 🔄 Release Process

### Version Numbering
- **Major** (2.0.0): Breaking changes, architecture changes
- **Minor** (2.1.0): New features, non-breaking changes  
- **Patch** (2.1.1): Bug fixes, security patches

### Release Checklist
- [ ] All tests pass
- [ ] Security scan clean
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in relevant files
- [ ] Tag created with proper format
- [ ] Release notes prepared

### Release Commands
```bash
# Create release branch
git checkout -b release/v2.1.0

# Update version numbers
# Edit src/__init__.py, CHANGELOG.md, etc.

# Commit changes
git add .
git commit -m "Prepare release v2.1.0"

# Create tag
git tag -a v2.1.0 -m "Release version 2.1.0"

# Push changes
git push origin release/v2.1.0
git push origin v2.1.0

# Create GitHub release
# This triggers the release workflow
```

## 📊 Performance Considerations

### Response Times
- **Input Validation**: < 10ms for typical inputs
- **Jira API Calls**: 500ms - 2s depending on server
- **Attachment Upload**: Varies by file size
- **Total Action Time**: Typically 5-30 seconds

### Memory Usage
- **Base Memory**: ~50MB for Python runtime
- **Peak Memory**: ~100MB with large attachments
- **Memory Cleanup**: Automatic cleanup after completion

### Optimization Tips
1. **Batch Operations**: Process multiple items together when possible
2. **Connection Reuse**: Reuse Jira client connections
3. **Lazy Loading**: Load data only when needed
4. **Error Recovery**: Implement retry logic for transient failures

## 🔗 External Integrations

### GitHub Actions
- **Inputs**: Received via environment variables
- **Outputs**: Set via GITHUB_OUTPUT file
- **Summaries**: Written to GITHUB_STEP_SUMMARY file
- **Logging**: Structured logging for GitHub UI

### Jira API
- **Authentication**: Basic auth with API tokens
- **Rate Limiting**: Respect Jira rate limits
- **Error Handling**: Comprehensive HTTP status handling
- **Retries**: Automatic retry for transient failures

### Third-party Libraries
- **jira**: Official Python Jira library
- **requests**: HTTP client for API calls
- **pytest**: Testing framework
- **black**: Code formatter

## 📚 Additional Resources

### Documentation
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Jira REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

### Tools
- [Bandit Security Linter](https://bandit.readthedocs.io/)
- [MyPy Type Checker](http://mypy-lang.org/)
- [Pytest Documentation](https://pytest.org/)
- [Black Code Formatter](https://black.readthedocs.io/)

### Community
- [GitHub Discussions](https://github.com/solarekm/jira-issue/discussions)
- [Issues and Bug Reports](https://github.com/solarekm/jira-issue/issues)
- [Security Policy](SECURITY.md)