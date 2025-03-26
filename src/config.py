import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration."""
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
    
    # Database configuration for Supabase
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'db.nusligglyvgsmuvauyce.supabase.co'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'postgres'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': 'require',  # Required for Supabase
        'options': '-c search_path=public'  # Set schema to public
    }
    
    # Supabase configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://nusligglyvgsmuvauyce.supabase.co')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    # Flask configuration
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    TESTING = False
    
    # Rate limiting
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Health check configuration
    HEALTH_CHECK_CACHE_TIMEOUT = 300  # 5 minutes
    
    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    @classmethod
    def get_db_connection_string(cls):
        """Returns the database connection string"""
        return f"dbname={cls.DB_CONFIG['database']} user={cls.DB_CONFIG['user']} password={cls.DB_CONFIG['password']} host={cls.DB_CONFIG['host']} port={cls.DB_CONFIG['port']}" 