from flask import Flask, render_template, request, redirect, url_for, flash
from psycopg2 import Error
import psycopg2
import bcrypt
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Database connection parameters
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

def init_db():
    """Initialize the database and create tables if they don't exist"""
    try:
        # First connect to default postgres database to create our database if it doesn't exist
        conn = psycopg2.connect(
            dbname='postgres',
            user=DB_PARAMS['user'],
            password=DB_PARAMS['password'],
            host=DB_PARAMS['host'],
            port=DB_PARAMS['port']
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Create database if it doesn't exist
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_PARAMS['dbname']}'")
        if not cur.fetchone():
            cur.execute(f'CREATE DATABASE {DB_PARAMS["dbname"]}')
            logger.info(f"Created database {DB_PARAMS['dbname']}")
        
        cur.close()
        conn.close()
        
        # Now connect to our database and create the table
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # Create accounts table if it doesn't exist
        cur.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                status VARCHAR(50) DEFAULT 'active',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        logger.info("Database and tables initialized successfully")
        
    except Error as e:
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        logger.info("Database connection established successfully")
        return conn
    except Error as e:
        logger.error(f"Error connecting to PostgreSQL: {e}")
        return None

def hash_password(password):
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def get_table_name():
    """Get the appropriate table name based on testing mode"""
    return 'test_accounts' if app.config.get('TESTING') else 'accounts'

@app.route('/')
def index():
    """Display all accounts"""
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error', 'error')
        return render_template('index.html', accounts=[])
    
    try:
        cur = conn.cursor()
        table_name = get_table_name()
        cur.execute(f'SELECT * FROM {table_name} ORDER BY created_at DESC')
        accounts = cur.fetchall()
        logging.info(f"Retrieved {len(accounts)} accounts from database")
        return render_template('index.html', accounts=accounts)
    except Error as e:
        logger.error(f'Database error: {e}')
        flash(f'Database error: {e}', 'error')
        return render_template('index.html', accounts=[])
    finally:
        if conn:
            cur.close()
            conn.close()

@app.route('/add_account', methods=['POST'])
def add_account():
    """Add a new account"""
    email = request.form.get('email')
    password = request.form.get('password')
    status = request.form.get('status', 'active')
    
    if not email or not password:
        logging.warning("Missing email or password in add_account request")
        flash('Email and password are required', 'error')
        return redirect(url_for('index'))
    
    logging.info(f"Attempting to add new account: {email}")
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error', 'error')
        return redirect(url_for('index'))
    
    try:
        cur = conn.cursor()
        table_name = get_table_name()
        cur.execute(
            f'INSERT INTO {table_name} (email, password, status) VALUES (%s, %s, %s)',
            (email, hash_password(password), status)
        )
        conn.commit()
        logging.info(f"Successfully added new account: {email}")
        flash('Account added successfully', 'success')
    except Error as e:
        logging.error(f"Error adding account: {e}")
        conn.rollback()
        flash(f'Error adding account: {str(e)}', 'error')
    finally:
        if conn:
            cur.close()
            conn.close()
    
    return redirect(url_for('index'))

@app.route('/update_status', methods=['POST'])
def update_status():
    """Update account status"""
    account_id = request.form.get('account_id')
    status = request.form.get('status')
    
    if not account_id or not status:
        flash('Account ID and status are required', 'error')
        return redirect(url_for('index'))
    
    logging.info(f"Attempting to update status for account ID: {account_id} to {status}")
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error', 'error')
        return redirect(url_for('index'))
    
    try:
        cur = conn.cursor()
        table_name = get_table_name()
        cur.execute(
            f'UPDATE {table_name} SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s',
            (status, account_id)
        )
        conn.commit()
        logging.info(f"Successfully updated status for account ID: {account_id}")
        flash('Status updated successfully', 'success')
    except Error as e:
        logging.error(f"Error updating status: {e}")
        conn.rollback()
        flash(f'Error updating status: {str(e)}', 'error')
    finally:
        if conn:
            cur.close()
            conn.close()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    logger.info("Starting Flask application")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Error as e:
        logger.error(f"Failed to initialize database: {e}")
        exit(1)
    app.run(debug=True) 