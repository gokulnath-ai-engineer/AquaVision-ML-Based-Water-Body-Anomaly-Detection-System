# Contributing to Aqua-Sentinel AI

Thank you for your interest in contributing! We welcome contributions of all kinds including bug reports, feature requests, documentation improvements, and code contributions.

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## How to Contribute

### Reporting Bugs

Before submitting a bug report, please check the issue tracker to ensure the bug hasn't already been reported. When submitting a bug report, include:

- **Title**: Clear, descriptive title
- **Description**: Detailed description of the issue
- **Steps to Reproduce**: Step-by-step reproduction instructions
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**: Python version, OS, dependencies versions
- **Logs/Screenshots**: Any relevant error messages or screenshots

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When submitting an enhancement suggestion, include:

- **Title**: Clear, descriptive title
- **Description**: Detailed description of the enhancement
- **Motivation**: Why this enhancement would be useful
- **Examples**: Examples of how the enhancement would work

### Pull Requests

1. **Fork the repository** and create a new branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the coding style of the project
   - Add comments for complex logic
   - Update documentation as needed

3. **Test your changes**
   ```bash
   python -m pytest
   ```

4. **Commit your changes**
   ```bash
   git commit -m "Add your descriptive commit message"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request**
   - Provide a clear description of your changes
   - Reference any related issues
   - Ensure CI/CD checks pass

## Development Setup

```bash
# Clone the repository
git clone https://github.com/surendra-01-yadav/aqua.git
cd aqua

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies in development mode
pip install -r files/requirements.txt
pip install pytest pytest-cov black flake8

# Format code
black files/

# Run linter
flake8 files/

# Run tests
pytest
```

## Coding Standards

- **Python**: Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- **Naming**: Use descriptive variable and function names
- **Documentation**: Add docstrings to all functions and classes
- **Comments**: Explain the "why", not the "what"
- **Formatting**: Use `black` for code formatting

Example docstring:
```python
def detect_water_bodies(image, confidence_threshold=0.5):
    """
    Detect water bodies in satellite imagery using YOLOv8.
    
    Parameters
    ----------
    image : np.ndarray
        Input satellite image in RGB format
    confidence_threshold : float, optional
        Confidence threshold for detections (default: 0.5)
    
    Returns
    -------
    dict
        Detection results with bounding boxes and confidence scores
    """
```

## Commit Messages

Use clear, descriptive commit messages:

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests liberally after the first line

Example:
```
Add water body detection module

- Implement YOLOv8-based detection
- Add confidence thresholding
- Include GeoJSON output format

Fixes #123
```

## Testing

- Write tests for new features
- Ensure all tests pass before submitting a PR
- Aim for >80% code coverage
- Use descriptive test names

```bash
# Run tests with coverage
pytest --cov=files
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all public functions
- Update configuration examples if applicable
- Include usage examples in docstrings

## Review Process

All submissions require review by maintainers. Please:

- Be patient - reviews may take time
- Be responsive to feedback and changes requested
- Ask questions if you don't understand feedback
- Update your PR based on review comments

## Questions?

Feel free to:
- Open an issue for questions
- Start a discussion for general inquiries
- Email the maintainers

---

**Thank you for contributing to Aqua-Sentinel AI! 🌊**
