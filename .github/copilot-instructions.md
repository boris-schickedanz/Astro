<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Purpose
This Python project calculates astrological data including:
- Astrological charts (natal charts based on birth data)
- Aspects (angular relationships between planets)
- Transits (current planetary positions and their interactions with natal charts)

All output is text-based only.

## Code Guidelines
- Follow PEP 8 style guide for Python code.
- Use descriptive variable and function names.
- Write docstrings for all functions and classes.
- Keep functions small and focused on a single responsibility.
- Use type hints for better code readability and IDE support.
- Handle exceptions appropriately with try-except blocks.
- Avoid global variables; use class attributes or pass parameters instead.

## Architecture Guidelines
- Use object-oriented design with classes for celestial bodies, charts, and calculations.
- Separate concerns: data models, calculation logic, and output formatting.
- Implement a main module that orchestrates the flow.
- Use modular structure with separate files for different functionalities (e.g., planets.py, aspects.py, transits.py).
- Follow SOLID principles: Single responsibility, Open-closed, Liskov substitution, Interface segregation, Dependency inversion.

## Testing Guidelines
- Write unit tests for all calculation functions using pytest.
- Aim for high test coverage (>80%).
- Use descriptive test names that explain what is being tested.
- Test edge cases and invalid inputs.
- Use fixtures for reusable test data.
- Run tests before committing code changes.
- Follow TDD (Test-Driven Development) where possible.

## Best Practices
- Use virtual environments for dependency management.
- Keep requirements.txt up to date with pinned versions.
- Use Git for version control with meaningful commit messages.
- Document complex algorithms and formulas used in calculations.
- Validate input data thoroughly.
- Provide clear error messages for invalid inputs.
- Optimize performance for calculations but prioritize correctness.
- Check all package versions, created code, and APIs against the available local version.
- If new packages or libraries are added, look up the latest API online.
- Always search online for information on how to use APIs if not clear from local code.
- Always reference `birth_chart_calculation.md` for technical details on calculating ASC, houses, and planet positions.
- When implementing astrological calculations, follow the instructions in `birth_chart_calculation.md` precisely.
- If new requirements or rules for calculations are identified, add them to `birth_chart_calculation.md`.

## Execution Instructions
- Always activate the virtual environment before running Python commands: `source .venv/bin/activate`
- Use the virtual environment's Python executable for running scripts: `.venv/bin/python main.py`
- Ensure the working directory is the project root when executing commands.
- For running tests, use: `.venv/bin/python -m pytest`
- For installing dependencies, activate venv first: `source .venv/bin/activate && pip install -r requirements.txt`

## Agent instructions
- If you are a Claude Sonnet AI agent, do not create an .md file inless explicitely instructed by the user.   
