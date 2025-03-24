# Account Management Web App

A web application for managing account credentials, reporting issues, and requesting replacements. All requests are sent to an admin via Telegram bot notifications.

## Features

- Display account credentials (Email, Password, Service, Verification Code)
- Report issues via dropdown (Incorrect Details, Delayed Delivery, No Subscription, Streaming Limit)
- Request account replacements
- Telegram bot notifications for admin approval
- Modern, responsive UI

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd accgen
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure Telegram Bot:
   - Create a new bot using [@BotFather](https://t.me/botfather) on Telegram
   - Get your bot token and chat ID
   - Copy the `.env.example` file to `.env`
   - Update the `.env` file with your Telegram bot token and chat ID

5. Initialize the database:
```bash
python app.py
```

6. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

1. View all accounts on the main page
2. To report an issue:
   - Click "Report Issue" on any account card
   - Select the issue type from the dropdown
   - Add a description
   - Submit the form

3. To request a replacement:
   - Click "Request Replacement" on any account card
   - Enter the reason for replacement
   - Submit the form

## Admin Notifications

All issues and replacement requests are automatically sent to the configured Telegram chat. The admin can review and take action on these requests.

## Security Notes

- Keep your `.env` file secure and never commit it to version control
- The application uses SQLite for simplicity. For production, consider using a more robust database
- Implement proper authentication before deploying to production 