import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
MONGO_URI = os.getenv("MONGO_URI")
LOGIN_URL = os.getenv("LOGIN_URL")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTHORIZATION_URL = os.getenv("AUTHORIZATION_URL")
FRONTEND_URL = os.getenv("FRONTEND_URL")
TES_URL = os.getenv("TES_URL")

API_KEY = os.getenv("API_KEY")
USER_ID = os.getenv("USER_ID")
USER_INFO_URL = os.getenv("USER_INFO_URL")
