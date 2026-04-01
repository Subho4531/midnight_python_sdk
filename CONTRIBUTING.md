# 🤝 Contributing to Midnight Python SDK

Thank you for your interest in contributing to the Midnight Python SDK! We welcome contributions from the community.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Style Guide](#style-guide)

## 📜 Code of Conduct

Be respectful, inclusive, and professional. We're all here to build something great together.

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Node.js 22+
- Git

### Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/yourusername/midnight-python-sdk.git
cd midnight-python-sdk

# Add upstream remote
git remote add upstream https://github.com/original/midnight-python-sdk.git
```

## 💻 Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install Node.js dependencies
npm install

# Start services
docker-compose up -d

# Verify
python check_services.py
```

## 🔨 Making Changes

1. Create a branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Add tests
4. Update documentation
5. Test locally: `pytest tests/`

## 📤 Submitting Changes

```bash
# Commit with clear message
git commit -m "feat: add new feature"

# Push to your fork
git push origin feature/your-feature

# Create Pull Request on GitHub
```

### Commit Message Format

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring

## 📝 Style Guide

- Follow PEP 8
- Use type hints
- Add docstrings
- Write clear comments
- Keep functions focused

## 🙏 Thank You!

Your contributions make this project better for everyone!
