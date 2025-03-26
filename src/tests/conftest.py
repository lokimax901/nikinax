import os
import sys
import pytest
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from flask import Flask
import time
from psycopg2 import pool
from datetime import datetime
import random

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import Config

# Test configuration
class TestConfig(Config):
    TESTING = True
    DB_CONFIG = {
        'database': 'submax_test',
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '5432'))
    }

# Create a test connection pool
test_db_pool = pool.SimpleConnectionPool(
    1,  # minconn
    20,  # maxconn
    **TestConfig.DB_CONFIG
)

@pytest.fixture(scope='session')
def app():
    """Create a Flask application configured for testing."""
    from app import app as flask_app
    flask_app.config.from_object(TestConfig)
    flask_app.config['db'] = None  # Will be set by the db fixture
    return flask_app

@pytest.fixture(scope='session')
def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture(scope='function')
def db():
    """Get a database connection from the pool"""
    conn = test_db_pool.getconn()
    conn.autocommit = True
    
    yield conn
    
    test_db_pool.putconn(conn)

@pytest.fixture(autouse=True)
def setup_test_db(db):
    """Setup test database before each test"""
    cur = db.cursor()
    
    # Truncate all tables
    cur.execute("""
        TRUNCATE TABLE client_accounts, clients, accounts, route_stats, error_logs 
        RESTART IDENTITY CASCADE
    """)
    
    db.commit()
    cur.close()

@pytest.fixture
def test_data(db):
    """Create test data and return IDs"""
    cur = db.cursor()
    
    # Create test accounts
    account_ids = []
    for i in range(2):
        cur.execute("""
            INSERT INTO accounts (email, password, status)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (f'test{i+1}@example.com', 'Test123!', 'active'))
        account_ids.append(cur.fetchone()[0])
    
    # Create test clients
    client_ids = []
    for i in range(2):
        cur.execute("""
            INSERT INTO clients (name, email, phone, renewal_date, account_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (f'Test Client {i+1}_{random.randint(100000, 999999)}', 
              f'client{i+1}_{random.randint(100000, 999999)}@example.com',
              '1234567890', datetime.now().date(), account_ids[0]))
        client_ids.append(cur.fetchone()[0])
    
    db.commit()
    cur.close()
    
    yield {
        'account_ids': account_ids,
        'client_ids': client_ids
    }

@pytest.fixture(autouse=True)
def setup_app_context(app):
    """Set up application context for each test."""
    with app.app_context():
        yield 

@pytest.fixture(scope='session', autouse=True)
def create_test_db():
    """Create test database and schema."""
    # Connect to default database to create test database
    conn = psycopg2.connect(
        dbname='postgres',
        user=TestConfig.DB_CONFIG['user'],
        password=TestConfig.DB_CONFIG['password'],
        host=TestConfig.DB_CONFIG['host'],
        port=TestConfig.DB_CONFIG['port']
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    test_db_name = TestConfig.DB_CONFIG['database']

    # Create test database
    try:
        # Terminate existing connections
        cur.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{test_db_name}'
            AND pid <> pg_backend_pid();
        """)

        cur.execute(f"DROP DATABASE IF EXISTS {test_db_name}")
        cur.execute(f"CREATE DATABASE {test_db_name}")
    finally:
        cur.close()
        conn.close()

    # Connect to test database and set up schema
    conn = psycopg2.connect(**TestConfig.DB_CONFIG)
    try:
        cur = conn.cursor()
        
        # Drop existing tables if they exist
        cur.execute("""
            DROP TABLE IF EXISTS client_accounts CASCADE;
            DROP TABLE IF EXISTS clients CASCADE;
            DROP TABLE IF EXISTS accounts CASCADE;
            DROP TABLE IF EXISTS route_stats CASCADE;
            DROP TABLE IF EXISTS error_logs CASCADE;
        """)
        conn.commit()
        
        # Read and execute schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql')
        with open(schema_path, 'r') as f:
            cur.execute(f.read())
        conn.commit()
    finally:
        cur.close()
        conn.close()

def pytest_sessionfinish(session, exitstatus):
    """Clean up the connection pool after all tests are done"""
    test_db_pool.closeall() 