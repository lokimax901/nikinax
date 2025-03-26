import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import request, current_app
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RouteManager:
    def __init__(self, app=None):
        self.app = app
        self.routes = {}
        self.route_stats = {}  # Store route statistics
        self.start_time = datetime.now()

    def monitor(self, route=None, required_params=None, description=None):
        """Decorator to monitor route performance and validate parameters"""
        def decorator(f):
            # Register the route
            endpoint = route or f.__name__
            self.routes[endpoint] = {
                'description': description or f.__doc__ or 'No description',
                'required_params': required_params or {},
                'status': 'healthy',
                'last_check': None,
                'path': route or f.__name__
            }
            self.route_stats[endpoint] = {
                'hits': 0,
                'errors': 0,
                'total_response_time': 0,
                'min_response_time': float('inf'),
                'max_response_time': 0,
                'last_access': None
            }

            @wraps(f)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    # Validate required parameters
                    if required_params and request.method in required_params:
                        # Get parameters from appropriate source
                        if request.is_json:
                            params = request.get_json()
                        elif request.method == 'POST':
                            params = request.form
                        else:
                            params = request.args
                            
                        # Handle case where params might be None
                        params = params or {}
                        
                        # Validate each required parameter
                        for param, param_type in required_params[request.method].items():
                            if param not in params:
                                raise ValueError(f"Missing required parameter: {param}")
                            
                            # Get the value and validate type if needed
                            value = params[param]
                            if value is None:
                                raise ValueError(f"Parameter {param} cannot be null")
                            
                            # Special handling for certain types
                            if param_type == int:
                                try:
                                    int(value)
                                except (TypeError, ValueError):
                                    raise ValueError(f"Parameter {param} must be an integer")
                            elif param_type == float:
                                try:
                                    float(value)
                                except (TypeError, ValueError):
                                    raise ValueError(f"Parameter {param} must be a number")
                            elif param_type == bool:
                                if not isinstance(value, bool) and str(value).lower() not in ['true', 'false', '0', '1']:
                                    raise ValueError(f"Parameter {param} must be a boolean")
                            
                    result = f(*args, **kwargs)
                    
                    # Update statistics
                    response_time = time.time() - start_time
                    stats = self.route_stats[endpoint]
                    stats['hits'] += 1
                    stats['total_response_time'] += response_time
                    stats['min_response_time'] = min(stats['min_response_time'], response_time)
                    stats['max_response_time'] = max(stats['max_response_time'], response_time)
                    stats['last_access'] = datetime.now()
                    
                    # Update route health
                    self.routes[endpoint]['status'] = 'healthy'
                    self.routes[endpoint]['last_check'] = datetime.now()
                    
                    return result
                    
                except Exception as e:
                    # Update error statistics
                    self.route_stats[endpoint]['errors'] += 1
                    self.routes[endpoint]['status'] = 'unhealthy'
                    self.routes[endpoint]['last_error'] = str(e)
                    self.routes[endpoint]['last_check'] = datetime.now()
                    logger.error(f"Route {endpoint} failed: {e}")
                    raise
                    
            return wrapper
        return decorator

    def generate_report(self):
        """Generate a report of route statistics"""
        try:
            report = {'routes': []}
            for endpoint, stats in self.route_stats.items():
                hits = stats.get('hits', 0)
                errors = stats.get('errors', 0)
                total_time = stats.get('total_response_time', 0)
                
                # Calculate error rate and average response time
                error_rate = (errors / hits * 100) if hits > 0 else 0
                avg_response_time = (total_time / hits) if hits > 0 else 0
                
                # Get the route path from the routes dictionary
                route_info = {
                    'endpoint': endpoint,
                    'path': self.routes[endpoint]['path'],
                    'method': request.method if request else 'GET',
                    'hits': hits,
                    'errors': errors,
                    'avg_response_time': f"{avg_response_time:.3f}s",
                    'error_rate': f"{error_rate:.2f}%",
                    'last_error': self.routes[endpoint].get('last_error'),
                    'status': 'healthy' if error_rate < 5 else 'degraded',
                    'last_check': self.routes[endpoint].get('last_check')
                }
                report['routes'].append(route_info)
            return report
        except Exception as e:
            logger.error(f"Error generating route report: {e}")
            return {'routes': []}

    def reset_stats(self):
        """Reset all route statistics"""
        for endpoint in self.route_stats:
            self.route_stats[endpoint] = {
                'hits': 0,
                'errors': 0,
                'total_response_time': 0,
                'min_response_time': float('inf'),
                'max_response_time': 0,
                'last_access': None
            }

# Create a global instance
route_manager = RouteManager() 