# Contributing to DataBound AI

Thank you for your interest in contributing! Here's how you can help.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a feature branch (`git checkout -b feature/amazing-feature`)
4. Make your changes
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Code Style

- Python: Follow PEP 8 (use `black` and `flake8`)
- JavaScript: Use ESLint and Prettier

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Pull Request Process

1. Update documentation as needed
2. Add tests for new features
3. Ensure all tests pass
4. Update the README if necessary
5. Request review from maintainers

## Issues

Before creating an issue, please check if it already exists. When creating an issue:

- Use clear, descriptive titles
- Provide detailed descriptions
- Include steps to reproduce for bugs
- Add relevant labels

Thank you for contributing!
