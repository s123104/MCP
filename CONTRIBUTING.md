# Contributing to MCP Docker

Thanks for wanting to contribute! Follow these guidelines to help us review your changes quickly.

## Development Setup

1. Fork the repository and create your branch from `main`.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run tests:
   ```bash
   pytest
   ```
4. Make sure the linter passes:
   ```bash
   flake8
   ```

## Commit Messages

Use [Semantic Commit Messages](https://www.conventionalcommits.org/) such as `feat:`, `fix:`, `docs:`, `test:`, and `chore:`.

## Pull Requests

- Keep PRs focused and describe the purpose clearly.
- Link any related issues.
- Ensure the CI checks pass before requesting review.

Thank you for helping improve the project!
