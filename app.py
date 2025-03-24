from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import csv
import io
from dotenv import load_dotenv
import requests
import asyncio

# Load environment variables
load_dotenv()

# Debug print
print("Bot Token:", os.getenv('TELEGRAM_BOT_TOKEN'))
print("Chat ID:", os.getenv('TELEGRAM_CHAT_ID'))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Telegram bot configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    service = db.Column(db.String(50), nullable=False)
    verification_code = db.Column(db.String(20))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    issue_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Replacement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    old_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    new_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def send_telegram_notification(message):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
        except Exception as e:
            print(f"Error sending Telegram notification: {e}")

@app.route('/')
def index():
    accounts = Account.query.filter_by(is_available=True).all()
    return render_template('index.html', accounts=accounts)

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    accounts = Account.query.filter_by(is_available=True).all()
    return jsonify([{
        'id': acc.id,
        'email': acc.email,
        'password': acc.password,
        'service': acc.service,
        'verification_code': acc.verification_code
    } for acc in accounts])

@app.route('/api/accounts/new', methods=['GET'])
def get_new_account():
    # Get the first available account
    account = Account.query.filter_by(is_available=True).first()
    if account:
        account.is_available = False
        db.session.commit()
        return jsonify({
            'id': account.id,
            'email': account.email,
            'password': account.password,
            'service': account.service,
            'verification_code': account.verification_code
        })
    return jsonify({'error': 'No accounts available'}), 404

@app.route('/api/issues', methods=['POST'])
def report_issue():
    data = request.json
    account_id = data.get('account_id')
    issue_type = data.get('issue_type')
    description = data.get('description')

    issue = Issue(
        account_id=account_id,
        issue_type=issue_type,
        description=description
    )
    db.session.add(issue)
    db.session.commit()

    # Send notification to Telegram
    account = Account.query.get(account_id)
    message = f"New Issue Reported:\nAccount: {account.email}\nService: {account.service}\nIssue Type: {issue_type}\nDescription: {description}"
    send_telegram_notification(message)

    return jsonify({'message': 'Issue reported successfully'})

@app.route('/api/replacements', methods=['POST'])
def request_replacement():
    data = request.json
    old_account_id = data.get('account_id')
    
    # Get old account
    old_account = Account.query.get(old_account_id)
    if not old_account:
        return jsonify({'error': 'Account not found'}), 404

    # Get new account of the same service
    new_account = Account.query.filter_by(
        service=old_account.service,
        is_available=True
    ).first()

    if not new_account:
        return jsonify({'error': 'No replacement account available'}), 404

    # Mark new account as unavailable
    new_account.is_available = False
    
    # Record the replacement
    replacement = Replacement(
        old_account_id=old_account_id,
        new_account_id=new_account.id,
        reason="Automatic replacement"
    )
    
    db.session.add(replacement)
    db.session.commit()

    # Send notification to Telegram
    message = f"Account Replaced:\nOld Account: {old_account.email}\nNew Account: {new_account.email}\nService: {new_account.service}"
    send_telegram_notification(message)

    return jsonify({
        'message': 'Account replaced successfully',
        'account': {
            'id': new_account.id,
            'email': new_account.email,
            'password': new_account.password,
            'service': new_account.service,
            'verification_code': new_account.verification_code
        }
    })

@app.route('/api/accounts/import', methods=['POST'])
def import_accounts():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be CSV format'}), 400

    try:
        # Read CSV file
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        accounts_added = 0
        for row in csv_reader:
            account = Account(
                email=row['email'],
                password=row['password'],
                service=row['service'],
                verification_code=row.get('verification_code'),
                is_available=True
            )
            db.session.add(account)
            accounts_added += 1
        
        db.session.commit()
        return jsonify({'message': f'{accounts_added} accounts imported successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/accounts/export', methods=['GET'])
def export_accounts():
    accounts = Account.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['email', 'password', 'service', 'verification_code', 'is_available'])
    
    # Write data
    for account in accounts:
        writer.writerow([
            account.email,
            account.password,
            account.service,
            account.verification_code,
            account.is_available
        ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='accounts.csv'
    )

def create_test_account():
    # Check if test account already exists
    if not Account.query.filter_by(email='test@example.com').first():
        test_account = Account(
            email='test@example.com',
            password='testpass123',
            service='Netflix',
            verification_code='123456',
            is_available=True
        )
        db.session.add(test_account)
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_test_account()
    app.run(debug=True) 