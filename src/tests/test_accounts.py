import pytest
import json
from datetime import datetime

def test_add_account(client, db):
    """Test adding a new account"""
    data = {
        'email': 'test@example.com',
        'password': 'Test123!',
        'status': 'active'
    }
    response = client.post('/add_account', data=data)
    assert response.status_code == 302  # Redirect after success

    # Verify account was added
    cur = db.cursor()
    cur.execute("SELECT email FROM accounts WHERE email = %s", ('test@example.com',))
    result = cur.fetchone()
    assert result is not None
    assert result[0] == 'test@example.com'

def test_add_account_duplicate_email(client, test_data):
    """Test adding an account with duplicate email"""
    data = {
        'email': 'test1@example.com',  # Using existing email
        'password': 'Test123!',
        'status': 'active'
    }
    response = client.post('/add_account', data=data)
    assert response.status_code == 302  # Redirect with error message

def test_add_account_weak_password(client):
    """Test adding an account with weak password"""
    data = {
        'email': 'weak@example.com',
        'password': 'weak',
        'status': 'active'
    }
    response = client.post('/add_account', data=data)
    assert response.status_code == 302  # Redirect with error message

def test_update_status_success(client, test_data, db):
    """Test successfully updating account status"""
    account_id = test_data['account_ids'][0]
    data = {
        'account_id': account_id,
        'status': 'inactive'
    }
    response = client.post('/update_status', data=data)
    assert response.status_code == 302  # Redirect after success

    # Verify status was updated
    cur = db.cursor()
    cur.execute("SELECT status FROM accounts WHERE id = %s", (account_id,))
    result = cur.fetchone()
    assert result is not None
    assert result[0] == 'inactive'

def test_update_status_invalid_account(client):
    """Test updating status of non-existent account"""
    data = {
        'account_id': 9999,
        'status': 'active'
    }
    response = client.post('/update_status', data=data)
    assert response.status_code == 302  # Redirect with error message

def test_get_account_clients(client, test_data):
    """Test getting clients linked to an account"""
    account_id = test_data['account_ids'][0]
    response = client.get(f'/account_clients/{account_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)

def test_get_account_clients_no_clients(client, test_data):
    """Test getting clients for an account with no clients"""
    account_id = test_data['account_ids'][0]
    response = client.get(f'/account_clients/{account_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 0

def test_get_account_clients_invalid_account(client):
    """Test getting clients for non-existent account"""
    response = client.get('/account_clients/9999')
    assert response.status_code == 404

def test_delete_account_success(client, test_data, db):
    """Test successfully deleting an account"""
    account_id = test_data['account_ids'][0]
    response = client.post('/delete_account', data={'account_id': account_id})
    assert response.status_code == 302  # Redirect after success

    # Verify account was deleted
    cur = db.cursor()
    cur.execute("SELECT id FROM accounts WHERE id = %s", (account_id,))
    result = cur.fetchone()
    assert result is None

def test_delete_account_nonexistent(client):
    """Test deleting a non-existent account"""
    response = client.post('/delete_account', data={'account_id': 9999})
    assert response.status_code == 302  # Redirect with error message