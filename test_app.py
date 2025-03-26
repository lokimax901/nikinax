import unittest
from app import app, get_db_connection, hash_password
import psycopg2
from psycopg2 import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TestAccountManager(unittest.TestCase):
    def setUp(self):
        """Set up test database and application context"""
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        
        # Create test database connection
        self.conn = get_db_connection()
        if self.conn:
            self.cur = self.conn.cursor()
            # Create test table
            self.cur.execute('''
                CREATE TABLE IF NOT EXISTS test_accounts (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    status VARCHAR(50) DEFAULT 'active',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Clear any existing test data
            self.cur.execute('TRUNCATE TABLE test_accounts')
            self.conn.commit()

    def tearDown(self):
        """Clean up after tests"""
        if hasattr(self, 'cur'):
            # Clear test data
            self.cur.execute('TRUNCATE TABLE test_accounts')
            self.conn.commit()
            self.cur.close()
        if hasattr(self, 'conn'):
            self.conn.close()
        self.ctx.pop()

    def test_index_page(self):
        """Test if index page loads"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account Manager', response.data)

    def test_add_account(self):
        """Test adding a new account"""
        test_email = 'test@example.com'
        test_password = 'test123'
        
        response = self.client.post('/add_account', data={
            'email': test_email,
            'password': test_password,
            'status': 'active'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account added successfully', response.data)
        
        # Verify account was added to database
        self.cur.execute('SELECT email FROM test_accounts WHERE email = %s', (test_email,))
        result = self.cur.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], test_email)

    def test_update_status(self):
        """Test updating account status"""
        # First add a test account
        test_email = 'test2@example.com'
        test_password = 'test123'
        
        self.cur.execute(
            'INSERT INTO test_accounts (email, password, status) VALUES (%s, %s, %s)',
            (test_email, hash_password(test_password), 'active')
        )
        self.conn.commit()
        
        # Get the account ID
        self.cur.execute('SELECT id FROM test_accounts WHERE email = %s', (test_email,))
        account_id = self.cur.fetchone()[0]
        
        # Update status
        response = self.client.post('/update_status', data={
            'account_id': str(account_id),
            'status': 'inactive'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Status updated successfully', response.data)
        
        # Verify status was updated in database
        self.cur.execute('SELECT status FROM test_accounts WHERE id = %s', (account_id,))
        result = self.cur.fetchone()
        self.assertEqual(result[0], 'inactive')

    def test_invalid_input(self):
        """Test handling of invalid input"""
        # Try to add account without email
        response = self.client.post('/add_account', data={
            'password': 'test123',
            'status': 'active'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email and password are required', response.data)

if __name__ == '__main__':
    unittest.main() 