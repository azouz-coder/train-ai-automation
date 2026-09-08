Train AI Automation — Library API

A backend library management API built with FastAPI and SQLite as part of my journey toward AI Automation and AI Agent development.

Features

- User registration and management
- User authentication with JWT
- Access and refresh tokens
- Role-based authorization
- Email verification
- Password reset
- Book CRUD operations
- Book search and filtering
- Book image upload
- Borrowing and returning books
- SQLite database
- Automated tests with pytest
- Environment variables for sensitive configuration

Tech Stack

- Python
- FastAPI
- SQLite
- JWT
- pytest
- Git & GitHub
- python-dotenv

Project Structure

train_ai_automation/
├── app/
│   ├── book.py
│   ├── borrowing.py
│   ├── crud_book.py
│   ├── crud_borrowing.py
│   ├── crud_user.py
│   ├── database.py
│   ├── email_verification.py
│   ├── login_config.py
│   ├── login_user.py
│   ├── main.py
│   ├── schemas.py
│   ├── security.py
│   ├── tokens.py
│   └── users.py
├── tests/
├── .gitignore
├── requirements.txt
└── README.md

Installation

Clone the repository and enter the project directory:

git clone https://github.com/azouz-coder/train-ai-automation.git
cd train-ai-automation

Create a virtual environment:

python -m venv .venv

Activate it on Windows:

.venv\Scripts\activate

Install the dependencies:

pip install -r requirements.txt

Environment Variables

Create a ".env" file in the project root:

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
EMAIL=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SECRET_KEY=change_me

Never commit your real ".env" file.

Run the API

uvicorn app.main:app --reload

Then open the FastAPI documentation:

http://127.0.0.1:8000/docs

Run Tests

pytest

Purpose

This project was built to practice backend development fundamentals that are useful for building automation systems and AI-powered applications.

The next stages of the learning path will focus on automation, AI APIs, and AI agents.