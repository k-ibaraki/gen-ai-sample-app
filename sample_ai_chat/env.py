import os
from dotenv import load_dotenv

load_dotenv(".env")

# Google Cloudの設定 #
GOOGLE_CLOUD_QUOTA_PROJECT: str | None = os.getenv("GOOGLE_CLOUD_QUOTA_PROJECT")
GOOGLE_CLOUD_PROJECT: str | None = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_REGION: str = os.getenv("GOOGLE_CLOUD_REGION", "asia-northeast1")

# Google OAuth2の設定 #
GOOGLE_AUTH_ON: bool = os.getenv("GOOGLE_AUTH_ON", "True") != "False"
GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "")
GOOGLE_GROUP_ID: str = os.getenv("GOOGLE_GROUP_ID", "")

# UIの設定 #
UI_TITLE: str = os.getenv("UI_TITLE", "Sample App")

# Debugモード #
DEBUG: bool = os.getenv("DEBUG", "False") == "True"
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
