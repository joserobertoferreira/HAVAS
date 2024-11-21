import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup environment variables
BASE_DIR = Path(__file__).resolve().parent.parent.parent

SERVER_BASE_ADDRESS = os.environ.get('SERVER_BASE_ADDRESS', '')

API_USER = os.environ.get('API_USER', 'admin')
API_PASSWORD = os.environ.get('API_PASSWORD', 'admin')

FOLDER_XML_IN = os.environ.get('FOLDER_XML_IN', BASE_DIR / 'uploads')
FOLDER_XML_OUT = os.environ.get('FOLDER_XML_OUT', BASE_DIR / 'downloads')

SENDER = os.environ.get('SENDER', 'admin')
RECEIVER = os.environ.get('RECEIVER', 'urn:netdoc:qa')

# Database connection parameters
DB_SERVER = os.environ.get('DB_SERVER', '')
DB_DATABASE = os.environ.get('DB_DATABASE', '')
DB_SCHEMA = os.environ.get('DB_SCHEMA', '')
DB_USERNAME = os.environ.get('DB_USERNAME', '')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
