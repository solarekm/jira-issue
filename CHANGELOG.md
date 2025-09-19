# Changelog

All notable changes to the Jira Issue Action will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Support for custom fields
- Bulk issue creation
- Issue templates
- Enhanced attachment validation

## [2.1.1] - 2025-09-19

### 🔧 **Documentation & Workflow Improvements**

This patch release focuses on comprehensive documentation updates and workflow fixes.

### ✨ Added
- **📚 Complete Documentation Review**: Comprehensive analysis and updates of all *.md files
- **🔗 Documentation Links**: Added missing links to docs/SECURITY_CONSTRAINTS.md in README
- **📁 Project Structure**: Updated file structure documentation to match reality

### 🐛 Fixed
- **🔧 Release Workflow**: Replaced deprecated actions/create-release@v1 with modern gh CLI
- **📝 Duplicate Headers**: Removed duplicate header in README.md and SECURITY.md
- **📦 Version References**: Updated all examples from @v1 to @v2 for consistency
- ** File Structure**: Corrected tests/ structure documentation (removed non-existent test_integration.py, added missing files)
- **🔧 README Corruption**: Fixed corrupted file structure and emoji encoding issues

## [2.1.0] - 2025-09-19

### 🔧 **Production Hardening & Quality Assurance**

This release focuses on strict CI/CD enforcement and production-grade code quality standards.

### ✨ Added
- **🚫 Zero-tolerance CI Policy**: Strict enforcement of all quality gates
- **🎨 Black Code Formatting**: 100% PEP8 compliance with automated formatting
- **📏 Enhanced Flake8 Linting**: Comprehensive style checking with 100-character line limits
- **🔍 MyPy Type Checking**: Full type safety with `--disallow-untyped-defs`
- **🔒 Bandit Security Analysis**: Automated security vulnerability scanning
- **🛡️ Safety Dependency Scanning**: Known vulnerability detection in dependencies
- **📊 Matrix Testing**: Python 3.9, 3.10, 3.11, 3.12 compatibility validation

### 🐛 Fixed
- **ValidationError Double-wrapping**: Corrected exception handling in validators module
- **Import Statement Cleanup**: Removed unused imports causing F401 violations
- **Code Quality Violations**: Fixed 100+ PEP8 and style violations across all modules
- **Type Annotation Issues**: Added proper type hints for MyPy compliance
- **Line Length Violations**: Reformatted long lines to meet 100-character limit
- **Test Security Validation**: Updated tests to work with enhanced security patterns

### 🛡️ Security
- **Enhanced Pattern Detection**: Improved malicious content validation patterns
- **File Path Security**: Strengthened attachment path validation against directory traversal
- **Input Sanitization**: Additional protection against injection attacks
- **Error Message Safety**: Prevented sensitive data leakage in error outputs

### 🔧 Changed
- **BREAKING**: Stricter input validation may reject previously accepted edge cases
- **CI Pipeline**: No tolerance for quality violations - all checks must pass
- **Error Handling**: More specific error messages with security considerations
- **Test Coverage**: Enhanced test scenarios for edge cases and security validation

### 🔄 **Dependabot Workflow Improvements**
- **🤖 Workflow Naming**: Renamed "🤖 Dependency Updates" to "🔀 Auto-merge Dependencies"
- **📝 Enhanced Descriptions**: Clearer job and step descriptions for better UI clarity
- **🔗 Documentation Updates**: Comprehensive README and CONTRIBUTING.md updates

### 🧪 Testing
- **Security Test Cases**: Comprehensive validation of security pattern detection
- **Edge Case Coverage**: Additional test scenarios for malicious input handling
- **CI Integration**: All 75 tests passing across all Python versions
- **Quality Gates**: Integrated black, flake8, mypy, bandit, and safety checks

### 📚 Documentation
- **README Enhancement**: Updated with latest security features and CI status
- **CONTRIBUTING Updates**: Comprehensive Dependabot workflow explanation
- **Development Guide**: Enhanced development workflow documentation

---

## [2.0.0] - 2024-09-19

### 🚀 Major Refactoring Release

This is a complete rewrite of the action with focus on security, maintainability, and reliability.

### ✨ Added
- **Modular Architecture**: Separated code into logical modules (validators, client, utils)
- **Comprehensive Input Validation**: Protection against injection attacks and malicious content
- **Enhanced Error Handling**: Detailed, actionable error messages with proper HTTP status handling
- **Security Features**: Input sanitization, secure token handling, and vulnerability protection
- **Type Safety**: Full type hints throughout the codebase
- **Comprehensive Testing**: 95%+ test coverage with unit and integration tests
- **CI/CD Pipeline**: Automated testing, linting, and security scanning
- **Detailed Logging**: Configurable log levels with structured logging
- **GitHub Integration**: Enhanced step summaries and output generation
- **Documentation**: Complete API documentation with examples

### 🛡️ Security
- **Injection Protection**: Validation against shell injection, XSS, and other attacks
- **Input Sanitization**: Comprehensive filtering of malicious patterns
- **Secure Secrets Handling**: Environment variable based secret management
- **Error Message Safety**: No sensitive data leaked in error messages
- **Dependency Security**: Updated to latest secure versions of all dependencies

### 🔧 Changed
- **BREAKING**: Moved from embedded Python code to modular structure
- **BREAKING**: Enhanced input validation may reject previously accepted inputs
- **BREAKING**: Error message format changes for clarity and security
- **Performance**: Improved error handling and retry logic
- **Reliability**: Better connection management and timeout handling

### 🐛 Fixed
- **Assignee Validation**: Proper handling of non-existent users
- **Attachment Handling**: Better file validation and error recovery
- **Parent Issue Validation**: Improved Sub-task parent validation
- **Connection Errors**: More specific error messages for different failure scenarios
- **Memory Leaks**: Proper cleanup of resources and sensitive data

### 📚 Documentation
- **README**: Complete rewrite with examples and troubleshooting
- **CONTRIBUTING**: Comprehensive contributor guidelines
- **SECURITY**: Detailed security policy and vulnerability reporting
- **API Documentation**: Full documentation of all modules and functions

### 🧪 Testing
- **Unit Tests**: Comprehensive test suite for all modules
- **Integration Tests**: End-to-end testing of action functionality
- **Security Tests**: Validation of security features and protections
- **Performance Tests**: Validation of error handling and edge cases

### 🔄 Migration Guide
For users upgrading from v1.x:

1. **Action Reference**: Update to `solarekm/jira-issue@v2`
2. **Input Validation**: Review inputs for newly enforced validation rules
3. **Error Handling**: Update workflows to handle new error message formats
4. **Priority Values**: Use new priority values (Highest, High, Medium, Low, Lowest)

Example migration:
```yaml
# Before (v1.x)
- uses: solarekm/jira-issue@v1
  with:
    issue_priority: "Critical"  # No longer supported

# After (v2.x)
- uses: solarekm/jira-issue@v2
  with:
    issue_priority: "Highest"  # Use new priority value
```

## [1.2.1] - 2024-08-15

### 🐛 Fixed
- Fixed attachment handling for files with spaces in names
- Improved error messages for network connectivity issues
- Fixed issue with long descriptions being truncated

### 🔧 Changed
- Updated Jira library to version 3.7.0
- Improved retry logic for API calls

## [1.2.0] - 2024-07-20

### ✨ Added
- Support for multiple file attachments
- Enhanced GitHub step summary with issue links
- Configurable timeout for API calls

### 🐛 Fixed
- Fixed parent issue validation for Sub-tasks
- Improved handling of special characters in issue descriptions
- Fixed edge case with empty label handling

## [1.1.2] - 2024-06-10

### 🐛 Fixed
- Fixed assignee validation when user doesn't exist
- Improved error handling for project permission issues
- Fixed issue with comma-separated labels containing spaces

### 🔧 Changed
- Updated Python dependencies for security patches
- Improved logging output for debugging

## [1.1.1] - 2024-05-15

### 🐛 Fixed
- Fixed issue creation when assignee field is empty
- Corrected Sub-task parent assignment logic
- Fixed error handling for 429 rate limit responses

## [1.1.0] - 2024-04-22

### ✨ Added
- Support for Epic issue type
- Enhanced error messages with HTTP status codes
- Assignee validation before issue creation
- Support for comma-separated labels

### 🔧 Changed
- Improved connection error handling
- Updated action to use Python 3.x instead of specific version
- Enhanced logging for better debugging

### 🐛 Fixed
- Fixed Sub-task creation without parent issue
- Corrected label handling for empty values
- Fixed timeout issues with large attachments

## [1.0.1] - 2024-03-18

### 🐛 Fixed
- Fixed issue with special characters in project keys
- Corrected attachment upload for binary files
- Fixed error handling for invalid server URLs

### 📚 Documentation
- Updated README with better examples
- Added troubleshooting section
- Improved input parameter documentation

## [1.0.0] - 2024-03-01

### 🎉 Initial Release

### ✨ Added
- Basic Jira issue creation functionality
- Support for Task, Bug, Story, and Sub-task issue types
- Assignee assignment capability
- Priority setting (High, Medium, Low)
- Label support
- File attachment functionality
- GitHub Actions integration
- Basic error handling

### 📚 Documentation
- Initial README with usage examples
- Basic input/output documentation
- MIT license

---

## Release Notes Format

### Types of Changes
- **✨ Added** for new features
- **🔧 Changed** for changes in existing functionality
- **🗑️ Deprecated** for soon-to-be removed features
- **🗑️ Removed** for now removed features
- **🐛 Fixed** for any bug fixes
- **🛡️ Security** for vulnerability fixes
- **📚 Documentation** for documentation changes
- **🧪 Testing** for testing improvements
- **🔄 Migration** for breaking changes requiring user action

### Version Numbering
- **Major** (X.0.0): Breaking changes, major new features
- **Minor** (0.X.0): New features, non-breaking changes
- **Patch** (0.0.X): Bug fixes, security patches

### Breaking Changes
Breaking changes are clearly marked with **BREAKING** and include migration instructions.

### Security Updates
Security fixes are marked with **🛡️ Security** and may trigger patch releases outside the normal cycle.