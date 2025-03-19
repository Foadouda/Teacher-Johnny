import sys
import os
from Logging import time_logger, error_logger, gemini_logger , process_logger

# Add the root directory of your project to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..', '..')))

class handling:
    @staticmethod
    def make_presentation_public(drive_service, file_id):
        """
        Update the permissions of the file to make it public.
        """
        permissions = {
            'type': 'anyone',
            'role': 'reader'  # Allows viewing
        }
        try:
            drive_service.permissions().create(
                fileId=file_id,
                body=permissions
            ).execute()
            #print(f"https://docs.google.com/presentation/d/{file_id}/edit")
        except Exception as e:
            error_logger.error(f"An error occurred while sharing the presentation: {e}")