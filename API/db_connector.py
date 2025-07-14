import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

DB_HOST="crop-yield-db-crop-yield.l.aivencloud.com"
DB_PORT=16505
DB_NAME="defaultdb"
DB_USER="avnadmin"
DB_PASSWORD="AVNS_vAaBqtBoyJVRJiRGoUo"
DB_SSLMODE="require"


# Build DB params from environment (Hardcoded my credentials in case of facilitator testing)
DB_CONFIG = {
    'host': os.getenv('DB_HOST', DB_HOST),
    'port': os.getenv('DB_PORT', DB_PORT),
    'dbname': os.getenv('DB_NAME', DB_NAME),
    'user': os.getenv('DB_USER', DB_USER),
    'password': os.getenv('DB_PASSWORD', DB_PASSWORD),
    'sslmode': os.getenv('DB_SSLMODE', DB_SSLMODE)
}

def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
    return conn
