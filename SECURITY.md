# Security Policy

## 🔒 Security Overview

The Jira Issue Action handles sensitive information including Jira API tokens and potentially sensitive issue content. We take security seriously and have implemented multiple layers of protection.

## 🛡️ Security Features

### 🤖 Automated Security
- **Dependabot**: Automatic dependency updates for security vulnerabilities
- **CodeQL**: Static analysis security testing on every commit
- **Auto-merge**: Safe security updates are automatically merged
- **Secret Scanning**: Automatic detection of exposed secrets in code

### Input Validation
- **Injection Protection**: All inputs are validated against malicious patterns
- **Type Validation**: Strict validation of data types and formats
- **Length Limits**: Enforced limits to prevent buffer overflow attacks
- **Character Filtering**: Removal of potentially dangerous characters

### Secure Data Handling
- **Environment Variables**: Sensitive data passed via environment variables
- **No Logging of Secrets**: API tokens and sensitive data are masked in logs
- **Memory Safety**: Sensitive data is not stored longer than necessary
- **Secure Transmission**: All API calls use HTTPS with certificate verification

### Access Control
- **Principle of Least Privilege**: Action requests minimal permissions
- **Authentication Validation**: Verifies credentials before operations
- **Permission Checks**: Validates user permissions for operations

### Continuous Security Monitoring
- **Weekly CodeQL Scans**: Automated security analysis every Sunday
- **Dependency Alerts**: Real-time notifications for vulnerable dependencies
- **Security Update Automation**: Critical patches applied automatically
- **Audit Trail**: Comprehensive logging for security monitoring

## 🚨 Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.x     | ✅ Yes            |
| 1.x     | ⚠️ Limited Support |
| < 1.0   | ❌ No             |

**Recommendation**: Always use the latest version for the best security.

## 🔍 Security Best Practices

### For Users

#### 1. API Token Security
```yaml
# ✅ DO: Use GitHub Secrets
- name: Create Jira Issue
  uses: solarekm/jira-issue@v2
  with:
    jira_api_token: ${{ secrets.JIRA_API_TOKEN }}

# ❌ DON'T: Hard-code tokens
- name: Create Jira Issue
  uses: solarekm/jira-issue@v2
  with:
    jira_api_token: "ATATT3xFfGF0..."  # Never do this!
```

#### 2. URL Validation
```yaml
# ✅ DO: Use your organization's Jira URL
jira_server: "https://yourcompany.atlassian.net"

# ❌ DON'T: Use untrusted or dynamic URLs
jira_server: ${{ github.event.inputs.jira_server }}  # Can be manipulated
```

#### 3. Input Sanitization
```yaml
# ✅ DO: Validate inputs in your workflow
- name: Validate Issue Summary
  run: |
    if [[ "${{ github.event.inputs.summary }}" =~ [';`$(){}'] ]]; then
      echo "Invalid characters in summary"
      exit 1
    fi
```

#### 4. Least Privilege
- Use Jira API tokens with minimal required permissions
- Restrict token scope to specific projects if possible
- Regularly rotate API tokens

### For Developers

#### 1. Secure Coding Practices
- Never log sensitive information
- Use parameterized queries and prepared statements
- Validate all inputs before processing
- Implement proper error handling

#### 2. Dependency Management
- Keep dependencies updated
- Use dependency scanning tools
- Monitor for security advisories

#### 3. Testing Security
- Include security tests in the test suite
- Test for injection vulnerabilities
- Validate error handling doesn't leak information

## 🚨 Reporting Security Vulnerabilities

### Supported Channels

#### Critical Security Issues
For critical security vulnerabilities, please **DO NOT** create a public GitHub issue. Instead:

1. **Email**: Send details to [security@example.com](mailto:security@example.com)
2. **GitHub Security Advisories**: Use GitHub's private vulnerability reporting
3. **GPG**: Encrypt sensitive details using our [public key](https://keybase.io/solarekm)

#### Non-Critical Security Issues
For non-critical security issues, you may create a GitHub issue with the "security" label.

### What to Include

Please include the following information:
- **Description**: Clear description of the vulnerability
- **Impact**: What could an attacker achieve?
- **Reproduction**: Step-by-step instructions to reproduce
- **Environment**: Versions, configurations, etc.
- **Suggested Fix**: If you have ideas for remediation

### Example Report
```
Subject: [SECURITY] Input validation bypass in issue description

Description:
The issue description field does not properly validate for script injection,
allowing malicious JavaScript to be executed in certain Jira configurations.

Impact:
An attacker could potentially execute arbitrary JavaScript in the context
of other users viewing the Jira issue.

Reproduction:
1. Create issue with description: '<script>alert("XSS")</script>'
2. View issue in Jira web interface
3. Script executes in browser

Environment:
- Action version: v2.0.0
- Jira version: Cloud
- Browser: Chrome 119

Suggested Fix:
Implement HTML entity encoding for issue descriptions before submission.
```

## ⚡ Response Timeline

- **Acknowledgment**: Within 24 hours
- **Initial Assessment**: Within 72 hours
- **Regular Updates**: Every 7 days until resolved
- **Fix Timeline**: Depends on severity
  - **Critical**: 1-7 days
  - **High**: 7-30 days
  - **Medium**: 30-90 days
  - **Low**: Next regular release

## 🛠️ Security Updates

### Notification Channels
- **GitHub Releases**: Security fixes mentioned in release notes
- **GitHub Security Advisories**: For significant vulnerabilities
- **Repository Watch**: Watch releases for notifications

### Update Process
1. Security fix is developed and tested
2. Release is created with security advisory
3. Users are notified via GitHub
4. Documentation is updated

## 🔐 Vulnerability Disclosure Policy

### Coordinated Disclosure
We follow responsible disclosure practices:

1. **Private Reporting**: Vulnerabilities reported privately
2. **Investigation**: We investigate and develop fixes
3. **Coordination**: We work with reporters on disclosure timeline
4. **Public Disclosure**: After fix is available and deployed

### Recognition
Security researchers who responsibly disclose vulnerabilities will be:
- Credited in release notes (if desired)
- Listed in our security acknowledgments
- Invited to test fixes before public release

## 🔒 Security Architecture

### Data Flow Security
```
User Input → Input Validation → Sanitization → Jira API → Response Processing
     ↓              ↓              ↓            ↓            ↓
   Reject      Pattern Check   Encoding    HTTPS/TLS    Safe Output
  Malicious      & Length      & Escape               No Sensitive
   Content       Limits        Chars                   Data Logged
```

### Security Layers
1. **Input Layer**: Validation and sanitization
2. **Processing Layer**: Secure API calls and error handling
3. **Output Layer**: Safe response processing and logging
4. **Infrastructure Layer**: GitHub Actions security model

## 📋 Security Checklist

### For Maintainers
- [ ] All dependencies are up to date
- [ ] Security tests pass
- [ ] Code review includes security considerations
- [ ] No secrets in logs or error messages
- [ ] Input validation covers all attack vectors
- [ ] Error messages don't leak sensitive information

### For Users
- [ ] API tokens stored in GitHub Secrets
- [ ] Using latest version of the action
- [ ] Jira URL is trusted and validated
- [ ] Input sanitization in workflows
- [ ] Regular token rotation

## 📚 Security Resources

### External Resources
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [GitHub Security Best Practices](https://docs.github.com/en/actions/security-guides)
- [Atlassian Security Guidelines](https://developer.atlassian.com/cloud/jira/platform/security-overview/)

### Tools
- [Bandit](https://bandit.readthedocs.io/) - Python security linter
- [Safety](https://pyup.io/safety/) - Dependency vulnerability checker
- [CodeQL](https://codeql.github.com/) - Static analysis

## 🙏 Acknowledgments

We thank the security researchers and users who have responsibly disclosed vulnerabilities and helped improve the security of this action.

---

**Remember**: Security is a shared responsibility. While we work hard to make this action secure, users must also follow security best practices in their workflows and environments.