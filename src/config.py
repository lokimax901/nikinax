import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
if os.path.exists('.env'):
    load_dotenv()

class Config:
    """Application configuration."""
    # Flask configuration
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False
    
    # Database configuration for Supabase
    DB_CONFIG = {
        'host': os.environ.get('DB_HOST'),
        'port': os.environ.get('DB_PORT', '5432'),
        'database': os.environ.get('DB_NAME', 'postgres'),
        'user': os.environ.get('DB_USER', 'postgres'),
        'password': os.environ.get('DB_PASSWORD'),
        'sslmode': 'require',  # Required for Supabase
        'options': '-c search_path=public'  # Set schema to public
    }
    
    # Supabase configuration
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    
    # Rate limiting
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Health check configuration
    HEALTH_CHECK_CACHE_TIMEOUT = 300  # 5 minutes
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    @classmethod
    def validate_config(cls):
        """Validates required configuration variables"""
        required_vars = [
            ('DB_HOST', cls.DB_CONFIG['host']),
            ('DB_PASSWORD', cls.DB_CONFIG['password']),
            ('SUPABASE_URL', cls.SUPABASE_URL),
            ('SUPABASE_KEY', cls.SUPABASE_KEY)
        ]
        
        missing_vars = [var[0] for var in required_vars if not var[1]]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    @classmethod
    def get_db_connection_string(cls):
        """Returns the database connection string"""
        return f"postgresql://{cls.DB_CONFIG['user']}:{cls.DB_CONFIG['password']}@{cls.DB_CONFIG['host']}:{cls.DB_CONFIG['port']}/{cls.DB_CONFIG['database']}?sslmode=require" 