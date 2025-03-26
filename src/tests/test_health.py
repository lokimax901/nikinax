import pytest
import json
import time
from datetime import datetime, timedelta
from route_manager import RouteManager

def test_health_endpoint(client):
    """Test health endpoint returns correct status"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data
    assert data['status'] in ['healthy', 'error']

def test_database_health(client):
    """Test database health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data
    assert data['status'] in ['healthy', 'error']

def test_routes_health(client):
    """Test the routes health endpoint"""
    # Make a request to generate some stats
    client.get('/clients')
    
    response = client.get('/health/routes')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, dict)
    assert 'routes' in data

def test_database_health_force_check(client):
    """Test forcing a database health check"""
    response = client.get('/health/database?force=true')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data
    assert data['status'] in ['healthy', 'error']

def test_recommendations_endpoint(client):
    """Test the health recommendations endpoint"""
    response = client.get('/health/recommendations')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'recommendations' in data
    assert isinstance(data['recommendations'], list)

def test_health_check_with_db_error(client, db):
    """Test health check when database connection fails"""
    # Close the database connection to simulate an error
    db.close()
    
    response = client.get('/health/database')
    assert response.status_code == 200  # Should still return 200 but with error status
    data = json.loads(response.data)
    assert data['status'] == 'error'

def test_route_monitoring(client):
    """Test route monitoring functionality"""
    # Make multiple requests to a route
    for _ in range(3):
        client.get('/clients')
    
    response = client.get('/health/routes')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, dict)
    assert 'routes' in data
    assert '/clients' in data['routes']
    
    # Verify route statistics
    client_stats = data['routes']['/clients']
    assert client_stats['hits'] == 3
    assert 'error_rate' in client_stats
    assert 'avg_response_time' in client_stats
    assert 'min_response_time' in client_stats
    assert 'max_response_time' in client_stats
    assert 'last_access' in client_stats

def test_error_tracking(client):
    """Test error tracking in route monitoring"""
    # Generate a 404 error
    response = client.get('/nonexistent-route')
    assert response.status_code == 404
    
    # Check health status
    response = client.get('/health/routes')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, dict)
    assert 'routes' in data
    
    # Verify error tracking
    if '/nonexistent-route' in data['routes']:
        route_stats = data['routes']['/nonexistent-route']
        assert route_stats['errors'] > 0
        assert float(route_stats['error_rate'].rstrip('%')) > 0

def test_live_status(client):
    """Test live status endpoint"""
    response = client.get('/health/live')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data
    assert 'timestamp' in data
    assert 'services' in data
    assert 'database' in data['services']
    assert 'application' in data['services']
    assert 'routes' in data['services'] 