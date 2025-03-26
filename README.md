# Account Manager

A simple Flask application for managing user accounts with PostgreSQL database.

## Features

- View all accounts
- Add new accounts
- Update account status
- Secure password hashing
- Modern Bootstrap UI

## Prerequisites

- Python 3.8 or higher
- PostgreSQL
- pip (Python package manager)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd submax
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update the database credentials and secret key in `.env`

5. Initialize the database:
   - Make sure PostgreSQL is running
   - The application will automatically create the database and tables on first run

## Running the Application

1. Start the Flask development server:
```bash
python src/app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## Project Structure

```
submax/
├── src/
│   ├── app.py              # Main application file
│   ├── templates/          # HTML templates
│   │   └── index.html     # Main page template
│   ├── static/            # Static files (CSS, JS)
│   └── database/          # Database scripts
│       └── schema.sql     # Database schema
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
└── README.md            # This file
```

## Security Notes

- Passwords are hashed using bcrypt
- Environment variables are used for sensitive data
- Flash messages auto-dismiss after 5 seconds
- Input validation is performed on all forms

## License

MIT License 