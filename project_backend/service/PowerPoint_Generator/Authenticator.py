
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import sys
import os

# Add the root directory of your project to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..' ,'..')))
class Auth:
    @staticmethod   
    def authenticate_with_google():
        """
        Authenticate with Google Slides API using a service account.
        """
        SCOPES = ['https://www.googleapis.com/auth/presentations']
        creds = Credentials.from_service_account_file(
            os.path.join(os.path.dirname(__file__), '../../../text-summarization-demo-96388d7f1502.json'), scopes=SCOPES
        )
        service = build('slides', 'v1', credentials=creds)
        return service
    
    def authenticate_with_google_drive():
        """
        Authenticate with the Google Drive API.
        """
        SCOPES = ['https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(
            os.path.join(os.path.dirname(__file__), '../../../text-summarization-demo-96388d7f1502.json'), scopes=SCOPES
        )
        return build('drive', 'v3', credentials=creds)
