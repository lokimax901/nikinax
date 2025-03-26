import psycopg2
from psycopg2 import pool
from config import Config
import logging

logger = logging.getLogger(__name__)

class DatabasePool:
    _pool = None
    
    @classmethod
    def get_pool(cls):
        """Get or create a connection pool"""
        if cls._pool is None:
            try:
                cls._pool = pool.SimpleConnectionPool(
                    1,  # minconn
                    20, # maxconn
                    Config.get_db_connection_string()
                )
                logger.info("Database connection pool created successfully")
            except Exception as e:
                logger.error(f"Error creating connection pool: {e}")
                raise
        return cls._pool
    
    @classmethod
    def get_connection(cls):
        """Get a connection from the pool"""
        try:
            return cls.get_pool().getconn()
        except Exception as e:
            logger.error(f"Error getting connection from pool: {e}")
            raise
    
    @classmethod
    def return_connection(cls, conn):
        """Return a connection to the pool"""
        if conn:
            try:
                cls.get_pool().putconn(conn)
            except Exception as e:
                logger.error(f"Error returning connection to pool: {e}")
                conn.close()
    
    @classmethod
    def close_pool(cls):
        """Close all connections in the pool"""
        if cls._pool:
            try:
                cls._pool.closeall()
                cls._pool = None
                logger.info("Database connection pool closed")
            except Exception as e:
                logger.error(f"Error closing connection pool: {e}") 