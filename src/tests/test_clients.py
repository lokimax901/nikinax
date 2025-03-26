import pytest
import json
from datetime import datetime, timedelta

def test_get_clients(client):
    """Test getting the list of clients"""
    response = client.get('/clients')
    assert response.status_code == 200

def test_add_client(client, db):
    """Test adding a new client"""
    data = {
        'name': 'New Client',
        'email': 'new@example.com',
        'phone': '1234567890',
        'renewal_date': '2024-12-31'
    }
    response = client.post('/add_client', data=data)
    assert response.status_code == 302  # Redirect after success

def test_renew_client(client, test_data):
    """Test renewing a client subscription"""
    client_id = test_data['client_ids'][0]
    response = client.post('/renew_client', data={
        'client_id': client_id,
        'renewal_date': '2025-01-01'
    })
    assert response.status_code == 302  # Redirect after success

def test_get_clients_json(client, test_data):
    """Test getting clients list in JSON format"""
    response = client.get('/clients?format=json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert isinstance(data['clients'], list)

def test_get_clients_html(client, test_data):
    """Test getting clients list in HTML format"""
    response = client.get('/clients')
    assert response.status_code == 200
    assert b'Client List' in response.data

def test_add_client_success(client, db):
    """Test successfully adding a new client"""
    data = {
        'name': 'New Test Client',
        'email': 'newtest@example.com',
        'phone': '5555555555',
        'renewal_date': '2024-12-31'
    }
    response = client.post('/add_client', data=data)
    assert response.status_code == 302  # Redirect after success

    # Verify client was added
    cur = db.cursor()
    cur.execute("SELECT name, email FROM clients WHERE email = %s", ('newtest@example.com',))
    result = cur.fetchone()
    assert result is not None
    assert result[0] == 'New Test Client'
    assert result[1] == 'newtest@example.com'

def test_add_client_duplicate_email(client, test_data):
    """Test adding a client with duplicate email"""
    data = {
        'name': 'Duplicate Client',
        'email': 'test1@example.com',  # Using existing email
        'phone': '5555555555',
        'renewal_date': None
    }
    response = client.post('/add_client', data=data)
    assert response.status_code == 302  # Redirect with error message

def test_add_client_invalid_email(client):
    """Test adding a client with invalid email"""
    data = {
        'name': 'Invalid Email Client',
        'email': 'not-an-email',
        'phone': '5555555555',
        'renewal_date': None
    }
    response = client.post('/add_client', data=data)
    assert response.status_code == 302  # Redirect with error message

def test_renew_client_success(client, test_data):
    """Test successfully renewing a client"""
    client_id = test_data['client_ids'][0]
    new_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
    response = client.post('/renew_client', data={
        'client_id': client_id,
        'renewal_date': new_date
    })
    assert response.status_code == 302  # Redirect after success

def test_renew_client_invalid_date(client, test_data):
    """Test renewing a client with invalid date"""
    client_id = test_data['client_ids'][0]
    response = client.post('/renew_client', data={
        'client_id': client_id,
        'renewal_date': 'invalid-date'
    })
    assert response.status_code == 302  # Redirect with error message

def test_renew_client_nonexistent(client):
    """Test renewing a non-existent client"""
    response = client.post('/renew_client', data={
        'client_id': 9999,
        'renewal_date': '2025-01-01'
    })
    assert response.status_code == 302  # Redirect with error message

def test_check_client_exists(client, test_data):
    """Test checking if a client exists"""
    client_id = test_data['client_ids'][0]
    response = client.post('/check_client', data={'client_id': client_id})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['exists'] is True

def test_check_client_not_exists(client):
    """Test checking a non-existent client"""
    response = client.post('/check_client', data={'client_id': 9999})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['exists'] is False 