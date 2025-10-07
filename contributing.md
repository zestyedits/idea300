# Contributing to Session Architect

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🎯 Ways to Contribute

- **Bug Reports**: Found a bug? Open an issue with detailed reproduction steps
- **Feature Requests**: Have an idea? Share it in the discussions or issues
- **Code Contributions**: Submit pull requests for bug fixes or new features
- **Documentation**: Improve README, add examples, or clarify instructions
- **Clinical Feedback**: As a clinician, provide feedback on accuracy and utility

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/YOUR_USERNAME/idea300.git
cd idea300
```

### 2. Set Up Development Environment

```bash
# Run the setup script
chmod +x setup.sh
./setup.sh

# Or manually:
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

## 📋 Development Guidelines

### Code Style

- Follow **PEP 8** for Python code
- Use **4 spaces** for indentation (no tabs)
- Maximum line length: **100 characters**
- Use descriptive variable and function names

### Python Conventions

```python
# Good
def generate_session_plan(topic, modality, style, profession):
    """Generate a structured session plan using OpenAI API.
    
    Args:
        topic: Client presenting concern (de-identified)
        modality: Therapeutic approach (e.g., 'CBT', 'DBT')
        style: Output tone ('professional', 'balanced', 'creative')
        profession: Clinician type ('Psychologist', 'Social Worker', etc.)
    
    Returns:
        str: Generated session plan in HTML format
    """
    # Implementation
    pass

# Bad
def gsp(t, m, s, p):  # Unclear names
    # No docstring
    pass
```

### Commit Messages

Follow the **Conventional Commits** specification:

```
feat: add EMDR protocol template
fix: correct CBT intervention citation
docs: update README installation steps
style: format code with black
refactor: reorganize route handlers
test: add unit tests for plan parsing
chore: update dependencies
```

### Git Workflow

```bash
# Make changes
git add .
git commit -m "feat: add new feature"

# Keep your branch updated
git fetch origin
git rebase origin/main

# Push changes
git push origin feature/your-feature-name

# Open a pull request on GitHub
```

## 🧪 Testing

### Before Submitting

Test your changes thoroughly:

```bash
# Run the application
python planner.py

# Test checklist:
# [ ] All routes load without errors
# [ ] Session generation works for multiple modalities
# [ ] Professional lens changes affect output
# [ ] Templates work correctly
# [ ] Forms validate properly
# [ ] Responsive design works on mobile
# [ ] No console errors in browser
```

### Testing Specific Features

```python
# Test session generation with different parameters
Topic: "Adult with social anxiety in work settings"
Modality: CBT, DBT, ACT (test each)
Tone: Professional, Balanced, Creative (test each)
Profession: All 5 types (test each)
```

## 📝 Pull Request Process

### 1. Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No merge conflicts with main

### 2. PR Description Template

```markdown
## Description
Brief description of what this PR does

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
How was this tested?

## Screenshots (if applicable)
Add screenshots for UI changes

## Related Issues
Fixes #123
```

### 3. Review Process

1. Maintainer reviews code
2. Feedback is addressed
3. PR is approved and merged
4. Branch is deleted

## 🏗️ Project Structure

```
idea300/
├── planner.py              # Main Flask application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── setup.sh               # Setup automation script
├── static/
│   └── style.css          # Global styles
├── templates/
│   ├── index.html         # Landing page
│   ├── login.html         # Authentication
│   ├── signup.html
│   ├── dashboard.html     # User dashboard
│   ├── generator.html     # Main generator interface
│   ├── history.html       # Generation history
│   ├── billing.html       # Subscription management
│   ├── faq.html          # Help center
│   ├── personalize.html  # Settings
│   ├── 404.html          # Error pages
│   └── 500.html
└── docs/
    ├── README.md
    ├── CONTRIBUTING.md
    └── CHANGELOG.md
```

## 🎨 Frontend Guidelines

### HTML

- Use semantic HTML5 elements
- Include proper ARIA labels for accessibility
- Keep templates DRY (Don't Repeat Yourself)

### CSS

- Use CSS custom properties (variables)
- Follow BEM naming convention when appropriate
- Ensure responsive design (mobile-first)
- Test on multiple browsers

### JavaScript

- Use vanilla JavaScript (no jQuery)
- Keep functions small and focused
- Add comments for complex logic
- Handle errors gracefully

## 🔐 Security Guidelines

### Never Commit

- API keys or secrets
- `.env` files
- Personal data or PHI
- Database credentials
- Private configuration

### Security Best Practices

```python
# Good: Use environment variables
api_key = os.environ.get("OPENAI_API_KEY")

# Bad: Hardcoded secrets
api_key = "sk-abc123..."  # Never do this!
```

### Input Validation

Always validate and sanitize user input:

```python
# Validate topic length
if len(topic) > 1000:
    return "Topic too long", 400

# Sanitize HTML (use existing libraries)
from markupsafe import escape
safe_topic = escape(topic)
```

## 📚 Documentation

### Code Documentation

```python
def parse_structured_plan(text_plan):
    """Parse the structured text plan into sections.
    
    Extracts sections marked with [SECTION:Title]...[/SECTION] tags
    and converts markdown content to HTML.
    
    Args:
        text_plan (str): Raw text output from OpenAI with section markers
        
    Returns:
        list: List of dicts with 'title' and 'content' keys
        
    Example:
        >>> plan = "[SECTION:Goal]Client will...[/SECTION]"
        >>> sections = parse_structured_plan(plan)
        >>> sections[0]['title']
        'Goal'
    """
    # Implementation
```

### README Updates

When adding features, update:
- Feature list
- Usage instructions
- Screenshots (if UI changed)
- API documentation

## 🐛 Bug Reports

### Good Bug Report Template

```markdown
**Description**
Clear description of the bug

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Screenshots**
If applicable

**Environment**
- OS: [e.g., macOS 14.0]
- Browser: [e.g., Chrome 120]
- Python Version: [e.g., 3.11]
```

## 💡 Feature Requests

### Good Feature Request Template

```markdown
**Problem Statement**
What problem does this solve?

**Proposed Solution**
How would this feature work?

**Alternatives Considered**
Other approaches you've thought of

**Clinical Rationale**
Why is this clinically valuable?

**Additional Context**
Any other relevant information
```

## 🔄 Development Workflow

### Local Development

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Run development server
python planner.py

# 3. Access at http://localhost:5000

# 4. Make changes (auto-reload enabled)

# 5. Test thoroughly

# 6. Commit when ready
git add .
git commit -m "feat: your feature"
```

### Environment Variables

For development, ensure `.env` includes:

```bash
OPENAI_API_KEY=sk-...
FLASK_DEBUG=True
FLASK_ENV=development
```

## 📊 Code Review Checklist

### For Reviewers

- [ ] Code follows project style guidelines
- [ ] Changes are well-documented
- [ ] No security vulnerabilities introduced
- [ ] No hardcoded secrets or credentials
- [ ] Error handling is appropriate
- [ ] UI changes are responsive
- [ ] Accessibility standards maintained
- [ ] Performance impact is acceptable

### For Contributors

Before requesting review:
- [ ] Self-review your code
- [ ] Test all changes
- [ ] Update documentation
- [ ] Add comments for complex logic
- [ ] Remove debug statements
- [ ] Check for typos

## 🎓 Learning Resources

### Flask
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)

### OpenAI API
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Best Practices](https://platform.openai.com/docs/guides/production-best-practices)

### Clinical Resources
- Evidence-based practice guidelines
- Therapeutic modality manuals
- Ethical guidelines (APA, NASW, AAMFT, ACA)

## 🤝 Community

### Getting Help

- **GitHub Issues**: Technical questions and bug reports
- **Discussions**: Feature ideas and general questions
- **Email**: support@sessionarchitect.com

### Code of Conduct

- Be respectful and professional
- Welcome newcomers
- Focus on constructive feedback
- Respect clinical boundaries and ethics
- No harassment or discrimination

## 📜 License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

## 🙏 Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

## 📞 Questions?

If you have questions about contributing:
1. Check existing issues and discussions
2. Review this guide thoroughly
3. Open a new discussion
4. Email: dev@sessionarchitect.com

---

**Thank you for contributing to Session Architect!** 

Every contribution, no matter how small, helps clinicians provide better care to their clients.