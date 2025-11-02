# Contributing

Thank you for your interest in contributing to layercode-create-app! This guide will help you get started.

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone
git clone https://github.com/svilupp/layercode-create-app.git
cd layercode-create-app
```

### 2. Install Dependencies

```bash
# Install all dependencies including dev tools
uv sync --group dev --group docs
```

### 3. Setup Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your credentials
nano .env
```

### 4. Verify Setup

```bash
# Run tests
make test

# Run type checking
make typecheck

# Run linting
make lint

# Format code
make format

# Run all checks
make check
```

## Development Workflow

### 1. Create a Branch

```bash
# Create a feature branch
git checkout -b feature/my-new-feature

# Or a bugfix branch
git checkout -b fix/issue-123
```

### 2. Make Changes

Follow these guidelines:

- Write clear, concise code
- Add type hints to all functions
- Document public APIs with docstrings
- Write tests for new features
- Keep commits atomic and well-described

### 3. Run Checks

Before committing:

```bash
# Format code
make format

# Run all checks
make check
```

### 4. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add feature: custom tool decorators"
```

### 5. Push and Create PR

```bash
# Push to your fork
git push origin feature/my-new-feature

# Create pull request on GitHub
```

## Code Style

### Python Style

We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting:

- Line length: 100 characters
- Quote style: double quotes
- Indent style: spaces (4 spaces)

### Type Hints

All code must include type hints:

```python
# Good
async def process(self, event: LayercodeEvent) -> str:
    pass

# Bad
async def process(self, event):
    pass
```

### Docstrings

Use Google-style docstrings:

```python
async def my_function(param1: str, param2: int) -> bool:
    """Brief description of function.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When something goes wrong
    """
    pass
```

## Testing

### Writing Tests

Tests use pytest and should be in the `tests/` directory:

```python
import pytest
from layercode_create_app.agents.my_agent import MyAgent

@pytest.mark.asyncio
async def test_my_feature():
    """Test my new feature."""
    agent = MyAgent(model="openai:gpt-5-nano")
    result = await agent.my_method()
    assert result == "expected"
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
uv run pytest tests/test_my_feature.py

# Run with coverage
uv run pytest --cov=layercode_create_app

# Run specific test
uv run pytest tests/test_my_feature.py::test_specific_case -v
```

### Test Guidelines

1. **Test behavior, not implementation**
2. **Use fixtures for common setup**
3. **Mock external dependencies**
4. **Test edge cases and errors**
5. **Keep tests fast and isolated**

## Documentation

### Updating Docs

Documentation uses MkDocs and is in the `docs/` directory:

```bash
# Install docs dependencies
uv sync --group docs

# Serve docs locally
uv run mkdocs serve

# Build docs
uv run mkdocs build
```

### Writing Documentation

- Use clear, concise language
- Include code examples
- Add links to related pages
- Use proper markdown formatting

## Pull Request Process

### PR Checklist

Before submitting:

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Type checking passes
- [ ] Documentation updated
- [ ] CHANGELOG updated (if applicable)
- [ ] PR description is clear and complete

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How has this been tested?

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
```

### Review Process

1. Maintainers will review your PR
2. Address any feedback
3. Once approved, maintainers will merge

## Adding New Agents

To contribute a new agent:

### 1. Create Prompt File

Create `src/src/layercode_create_app/agents/prompts/my_agent.txt`:

```text
You are a helpful assistant that...

Guidelines:
- Be concise
- Be helpful
```

### 2. Implement Agent

Create `src/layercode_create_app/agents/my_agent.py`:

```python
from pydantic_ai import Agent
from layercode_create_app.agents.base import BaseLayercodeAgent, agent

@agent("my-agent")
class MyAgent(BaseLayercodeAgent):
    """Description of what this agent does."""

    async def process(self, event: LayercodeEvent) -> str:
        # Implementation
        pass
```

### 3. Add Tests

Create `tests/test_my_agent.py`:

```python
import pytest
from layercode_create_app.agents.my_agent import MyAgent

@pytest.mark.asyncio
async def test_my_agent():
    agent = MyAgent(model="openai:gpt-5-nano")
    # Test cases
```

### 4. Update Documentation

Add documentation in `docs/agents/built-in.md` describing your agent.

## Reporting Issues

### Bug Reports

Include:

- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version)
- Logs and error messages

### Feature Requests

Include:

- Clear description of the feature
- Use case and motivation
- Example API or usage
- Any relevant context

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help create a welcoming environment

## Questions?

- Open a GitHub Discussion
- Join the community chat
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
