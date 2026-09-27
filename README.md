# Inventory Engine

A robust, modular console/CLI inventory management system built with Python, SQLAlchemy 2.0, Pydantic V2, and Typer.

## Architecture

The project follows a clean multi-layer design pattern:

- **`models/`**: SQLAlchemy declarative ORM models defining database schema and relationships.
- **`schemas/`**: Pydantic models for data validation, integrity checks, and serialization.
- **`crud/`**: Encapsulated database operations (CRUD logic) separating persistence from business rules.
- **`cli/`**: Typer-powered command-line interface handling user interactions and formatted output.

## Tech Stack

- **Language:** Python 3.10+
- **ORM & Database:** SQLAlchemy 2.0, SQLite
- **Validation:** Pydantic V2
- **CLI Framework:** Typer
- **Terminal Formatting:** Rich

## Getting Started

### 1. Setup Virtual Environment
```bash
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate
-------------------
2. Install Dependencies
pip install -r requirements.txt
3. Initialize Database
python init_db.py
4. Run CLI
python app_cli.py --help
