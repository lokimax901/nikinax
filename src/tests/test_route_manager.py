import pytest
from datetime import datetime, timedelta
from route_manager import RouteManager
import json
from concurrent.futures import ThreadPoolExecutor

def test_route_manager_initialization(app):
    """Test RouteManager initialization"""
    route_manager = RouteManager(app)
    assert route_manager.app == app
    assert isinstance(route_manager.routes, dict)
    assert isinstance(route_manager.route_stats, dict)

def test_route_monitoring(client):
    """Test basic route monitoring"""
    # Make a request to generate stats
    client.get('/clients')
    
    response = client.get('/health/routes')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, dict)
    assert 'routes' in data
    assert '/clients' in data['routes']

def test_error_tracking(client):
    """Test error tracking"""
    # Generate a 404 error
    client.get('/nonexistent-route')
    
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data

def test_response_time_tracking(client):
    """Test response time tracking"""
    # Make requests
    client.get('/clients')
    
    response = client.get('/health/routes')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, dict)
    assert 'routes' in data
    assert '/clients' in data['routes']
    assert 'avg_response_time' in data['routes']['/clients']

def test_route_decorators(client):
    """Test route decorators functionality"""
    # Test a monitored route
    response = client.get('/health')
    assert response.status_code == 200
    
    # Check if route was monitored
    stats_response = client.get('/health/routes')
    assert stats_response.status_code == 200
    data = json.loads(stats_response.data)
    assert '/health' in data['routes']

def test_route_stats_reset(app):
    """Test resetting route statistics"""
    route_manager = RouteManager(app)
    
    # Add some test stats
    route_manager.route_stats['/test'] = {
        'hits': 10,
        'errors': 2,
        'total_response_time': 1.5,
        'min_response_time': 0.1,
        'max_response_time': 0.5
    }
    
    # Reset stats
    route_manager.reset_stats()
    
    # Verify stats were reset
    assert '/test' not in route_manager.route_stats

def test_route_report_generation(client):
    """Test route report generation"""
    # Generate some activity
    client.get('/clients')
    client.get('/health')
    client.get('/nonexistent')
    
    response = client.get('/health/routes')
    data = response.json
    
    assert 'routes' in data
    assert isinstance(data['routes'], list)
    for route in data['routes']:
        assert 'path' in route
        assert 'method' in route
        assert 'hits' in route
        assert 'error_rate' in route
        assert 'avg_response_time' in route

def test_concurrent_requests(client):
    """Test handling of concurrent requests"""
    # Simulate concurrent requests
    def make_request():
        return client.get('/clients')
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        responses = list(executor.map(lambda _: make_request(), range(3)))
    
    # All requests should succeed
    assert all(r.status_code == 200 for r in responses)
    
    # Check statistics
    stats_response = client.get('/health/routes')
    assert stats_response.status_code == 200
    data = json.loads(stats_response.data)
    assert '/clients' in data['routes']
    assert data['routes']['/clients']['hits'] >= 3