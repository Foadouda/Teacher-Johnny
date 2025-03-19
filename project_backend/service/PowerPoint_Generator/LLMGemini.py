import sys
import os

# Add the root directory of your project to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..', '..')))

from project_backend.core.settings import Settings

# Initialize the Settings class
settings = Settings()

GEMINI_MODEL = settings.GEMINI_MODEL    # 'gemini-1.5-flash'