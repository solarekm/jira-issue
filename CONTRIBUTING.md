# Contributing to Jira Issue Action

We love your input! We want to make contributing to the Jira Issue Action as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## 🚀 Quick Start for Contributors

### Prerequisites
- Python 3.9 or higher
- Git
- GitHub account
- Basic knowledge of GitHub Actions

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/jira-issue.git
   cd jira-issue
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov pytest-mock responses black flake8 mypy
   ```

4. **Run tests to ensure everything works:**
   ```bash
   python tests/run_tests.py
   ```

## 📝 Development Workflow

### 1. Creating a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 2. Making Changes

#### Code Standards
- **Python Style**: Follow PEP 8, use Black for formatting
- **Type Hints**: Use type hints for all function parameters and returns
- **Documentation**: Add docstrings to all modules, classes, and functions
- **Testing**: Write tests for all new functionality

#### File Structure
```
src/
├── __init__.py          # Package initialization
├── main.py              # Entry point
├── jira_client.py       # Jira API wrapper
├── validators.py        # Input validation
├── exceptions.py        # Custom exceptions
└── utils.py             # Utility functions

tests/
├── conftest.py          # Test configuration
├── test_*.py            # Test modules
├── fixtures/            # Test data
└── run_tests.py         # Test runner
```

### 3. Automated Dependency Management

This project uses a two-tier Dependabot system:

#### 🔄 **Dependabot Configuration** (`.github/dependabot.yml`)
- Creates weekly dependency update PRs
- Groups security updates for priority handling
- Smart scheduling (Mondays 04:00-05:00 UTC)

#### 🔀 **Auto-merge Workflow** (`🔀 Auto-merge Dependencies`)
- Automatically merges safe updates (patch/minor)
- Waits for all CI checks to pass
- Security updates are prioritized
- Major version updates require manual review

**What This Means for Contributors:**
- Dependency updates are handled automatically
- Focus on feature development, not maintenance
- Manual review only needed for breaking changes

### 4. Code Quality Checks

Before submitting your changes, run these checks:

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503

# Type checking
mypy src/ --ignore-missing-imports --disallow-untyped-defs

# Security analysis
bandit -r src/

# Run all tests
python tests/run_tests.py
```

### 4. Writing Tests

#### Test Guidelines
- **Coverage**: Aim for 90%+ test coverage
- **Test Names**: Use descriptive names that explain what is being tested
- **Fixtures**: Use pytest fixtures for common test setup
- **Mocking**: Mock external dependencies (Jira API calls)

#### Test Example
```python
def test_validate_project_key_valid(self):
    """Test valid project key validation."""
    validator = InputValidator()
    result = validator.validate_project_key("TEST")
    assert result == "TEST"

def test_validate_project_key_invalid(self):
    """Test invalid project key validation."""
    validator = InputValidator()
    with pytest.raises(ValidationError):
        validator.validate_project_key("invalid-key")
```

### 5. Documentation

#### Code Documentation
- Use Google-style docstrings
- Include parameter types and descriptions
- Document exceptions that may be raised

#### Example Docstring
```python
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
```

## 🐛 Bug Reports

### Before Reporting
1. **Search existing issues** to avoid duplicates
2. **Test with the latest version** to ensure the bug still exists
3. **Gather information** about your environment

### Bug Report Template
```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Use action with inputs: '...'
2. See error

**Expected behavior**
A clear description of what you expected to happen.

**Environment:**
- GitHub Actions runner: [e.g., ubuntu-latest]
- Action version: [e.g., v2.0.0]
- Jira version: [e.g., Cloud/Server 8.x]

**Additional context**
Add any other context about the problem here.
```

## 🚀 Feature Requests

### Before Requesting
1. **Check existing issues** for similar requests
2. **Consider the scope** - is this a general use case?
3. **Think about backwards compatibility**

### Feature Request Template
```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request.
```

## 🔄 Pull Request Process

### 1. Prepare Your PR
- [ ] Code follows the style guidelines
- [ ] Self-review of code has been performed
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Tests have been added that prove the fix/feature works
- [ ] New and existing unit tests pass locally
- [ ] Any dependent changes have been merged and published

### 2. PR Title and Description
- **Title**: Use a clear, descriptive title
- **Description**: Explain what changes were made and why
- **Link Issues**: Reference related issues with "Fixes #123"

### 3. Review Process
1. **Automated Checks**: All CI checks must pass
2. **Code Review**: At least one maintainer review required
3. **Testing**: Manual testing may be requested for significant changes
4. **Documentation**: Update docs if needed

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review performed
- [ ] Tests added/updated
- [ ] Documentation updated
```

## 🏗️ Architecture Guidelines

### Separation of Concerns
- **main.py**: Entry point and orchestration
- **validators.py**: Input validation and sanitization
- **jira_client.py**: Jira API interactions
- **exceptions.py**: Custom exception definitions
- **utils.py**: Helper functions and utilities

### Error Handling
- Use custom exceptions with descriptive messages
- Provide actionable error messages for users
- Log errors appropriately for debugging

### Security Considerations
- Validate all inputs to prevent injection attacks
- Use environment variables for sensitive data
- Mask sensitive information in logs
- Follow security best practices

## 📚 Resources

### Documentation
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Jira REST API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Python Jira Library](https://jira.readthedocs.io/)

### Tools
- [Black Code Formatter](https://black.readthedocs.io/)
- [Flake8 Linter](https://flake8.pycqa.org/)
- [MyPy Type Checker](http://mypy-lang.org/)
- [Pytest Testing Framework](https://pytest.org/)

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Security Issues**: See [SECURITY.md](SECURITY.md)

## 🙏 Recognition

Contributors will be recognized in:
- Release notes
- README acknowledgments
- GitHub contributors list

Thank you for contributing to make this action better for everyone! 🎉