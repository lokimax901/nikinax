import logging
import psycopg2
from datetime import datetime, timedelta
from config import Config
from route_manager import route_manager

logger = logging.getLogger(__name__)

class HealthChecker:
    def __init__(self):
        self.start_time = datetime.now()
        self.db_status = {
            'status': 'unknown',
            'last_check': None,
            'error': None
        }

    def check_database(self):
        """Check database health"""
        try:
            conn = psycopg2.connect(**Config.DB_CONFIG)
            cur = conn.cursor()
            
            # Test connection with simple query
            cur.execute("SELECT 1")
            cur.fetchone()
            
            # Get basic table info
            cur.execute("""
                SELECT table_name, COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                GROUP BY table_name
            """)
            tables = {row[0]: row[1] for row in cur.fetchall()}
            
            cur.close()
            conn.close()
            
            self.db_status.update({
                'status': 'healthy',
                'last_check': datetime.now(),
                'tables': tables
            })
            
            return {
                'status': 'healthy',
                'tables': tables
            }
            
        except Exception as e:
            error_msg = str(e)
            self.db_status.update({
                'status': 'error',
                'last_check': datetime.now(),
                'error': error_msg
            })
            return {
                'status': 'error',
                'message': error_msg
            }

    def check_application(self):
        """Check overall application health"""
        try:
            # Get database status
            db_status = self.check_database()
            
            # Calculate uptime
            uptime = datetime.now() - self.start_time
            uptime_str = str(uptime).split('.')[0]  # Remove microseconds
            
            return {
                'status': db_status['status'],
                'uptime': uptime_str,
                'database_status': db_status['status']
            }
        except Exception as e:
            logger.error(f"Application health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'uptime': 'N/A'
            }

    def get_recommendations(self):
        """Get recommendations for improving application health"""
        recommendations = []
        db_status = self.check_database()

        # Database recommendations
        if db_status['status'] == 'healthy':
            for table_name, table_info in db_status['tables'].items():
                if table_info['exists']:
                    # Check for missing indexes on foreign keys
                    if table_name == 'client_accounts':
                        has_client_id_index = any('client_id' in idx['definition'] 
                                                for idx in table_info['indexes'])
                        has_account_id_index = any('account_id' in idx['definition'] 
                                                 for idx in table_info['indexes'])
                        
                        if not has_client_id_index:
                            recommendations.append({
                                'type': 'index',
                                'priority': 'high',
                                'message': f"Add index on {table_name}.client_id for better query performance"
                            })
                        if not has_account_id_index:
                            recommendations.append({
                                'type': 'index',
                                'priority': 'high',
                                'message': f"Add index on {table_name}.account_id for better query performance"
                            })

                    # Check for large tables that might need archiving
                    row_count = table_info['row_count']
                    if row_count > 1000000:  # 1 million rows
                        recommendations.append({
                            'type': 'performance',
                            'priority': 'medium',
                            'message': f"Consider archiving old data from {table_name} ({row_count:,} rows)"
                        })

        # Route recommendations
        route_status = route_manager.generate_report()
        for route_info in route_status['routes']:
            error_rate = float(route_info['error_rate'].strip('%'))
            if error_rate > 5:  # More than 5% error rate
                recommendations.append({
                    'type': 'reliability',
                    'priority': 'high',
                    'message': f"High error rate ({error_rate:.1f}%) on route {route_info['endpoint']}"
                })

        return recommendations

# Create a global instance
health_checker = HealthChecker() 