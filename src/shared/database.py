import os
import asyncpg
from pgvector.asyncpg import register_vector
from dotenv import load_dotenv
from contextlib import asynccontextmanager


load_dotenv()


class PGVectorDatabase:
    """
    A class for interacting with a Postgres database using pgvector.
    """

    _pool = None

    @classmethod 
    async def create_connection_pool(cls):
        """
        Create a connection pool to the pgvector database.
        """
        user = os.environ.get("PGVECTOR_USER")
        password = os.environ.get("PGVECTOR_PASSWORD")
        database = os.environ.get("PGVECTOR_DATABASE")
        host = os.environ.get("PGVECTOR_HOST")
        port = int(os.environ.get("PGVECTOR_PORT"))
        min_connections = int(os.environ.get("PGVECTOR_MIN_POOL_CONNECTIONS"))
        max_connections = int(os.environ.get("PGVECTOR_MAX_POOL_CONNECTIONS"))

        if not all([user, password, database, host, port]):
            raise ValueError("One or more PGVECTOR_ environment variables are not set.")

        pool = await asyncpg.create_pool(user=user, password=password, database=database, host=host, port=port, min_size=min_connections, max_size=max_connections)
        return pool

    @classmethod
    async def get_connection_pool(cls):
        """
        Get a connection to the pgvector database and register the vector extension.

        Returns:
            asyncpg.Connection: A connection to the pgvector database.
        """
        if cls._pool is None or  cls._pool._closed:  
            cls._pool = await cls.create_connection_pool()
        return cls._pool

        
            
    @classmethod
    @asynccontextmanager
    async def get_connection(cls):
        """
        Get a connection from the connection pool.

        Returns:
            asyncpg.Connection: A connection from the pool.
        """
        pool = await cls.get_connection_pool() 
        conn = await pool.acquire()
        await register_vector(conn) 
        try:
            yield conn
        finally:
            await pool.release(conn)    
