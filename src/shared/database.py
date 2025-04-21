import os
import asyncpg
from pgvector.asyncpg import register_vector
from dotenv import load_dotenv

load_dotenv()


class PGVectorDatabase:
    """
    A class for interacting with a Postgres database using pgvector.
    """

    CONN_POOL = None

    @staticmethod
    async def get_connection_pool():
        """
        Get a connection to the pgvector database and register the vector extension.

        Returns:
            asyncpg.Connection: A connection to the pgvector database.
        """

        if PGVectorDatabase.CONN_POOL is None:
            
            user = os.environ.get("PGVECTOR_USER")
            password = os.environ.get("PGVECTOR_PASSWORD")
            database = os.environ.get("PGVECTOR_DATABASE")
            host = os.environ.get("PGVECTOR_HOST")
            port = os.environ.get("PGVECTOR_PORT")

            if not all([user, password, database, host, port]):
                raise ValueError("One or more PGVECTOR_ environment variables are not set.")

            PGVectorDatabase.CONN_POOL = await asyncpg.create_pool(
                user=user,
                password=password,
                database=database,
                host=host,
                port=int(port),
                min_size=5,
                max_size=20
            )
            connection = await PGVectorDatabase.CONN_POOL.acquire()
            await register_vector(connection)
            await PGVectorDatabase.CONN_POOL.release(connection)

        return PGVectorDatabase.CONN_POOL
    