import os 
from dotenv import load_dotenv
import psycopg2

# 1. Determine the environment (defaults to "development" if 'ENV' is not set)
ENV = os.getenv("ENV", "development")

# 2. Dynamically load the matching .env file (e.g., .env.development, .env.test)
load_dotenv(f".env.{ENV}")

def get_db_connection():
    try:
        return psycopg2.connect(
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            host=os.environ.get("DB_HOST", "localhost"),
            port=os.environ.get("DB_PORT", "5432"),
        )
    except KeyError as e:
        raise RuntimeError(f"Missing environment variable {e}. Add it to your .env.{ENV} file.") from e