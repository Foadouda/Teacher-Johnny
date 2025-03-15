import sys
import os
from PyPDF2 import PdfReader
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from Logging import time_logger, error_logger, gemini_logger , process_logger

# Add the root directory of your project to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..', '..', '..')))

from project_backend.core.settings import Settings

# Initialize the Settings class
settings = Settings()

# Debug print statement to verify GEMINI_MODEL
GEMINI_MODEL = settings.GEMINI_MODEL

def get_book_name_with_gemini(text):
    """
    Use the Gemini AI model to get the book name from the text.
    """
    try:
        prompt = (
            "Extract the book name from the following text.\n"
            "Return the output in JSON format with the following structure:\n"
            "{\n"
            "  \"book_name\": \"<book_name>\"\n"
            "}\n\n"
            f"Text:\n{text}"
        )
        response = GEMINI_MODEL.generate_content(prompt)
        #print("Gemini Response:", response.text)
        
        # Clean the response: Remove backticks and extra spaces if they exist
        clean_response = response.text.strip()
        if clean_response.startswith("```json"):
            clean_response = clean_response[7:]
        if clean_response.endswith("```"):
            clean_response = clean_response[:-3]
        
        book_name = json.loads(clean_response.strip())["book_name"]
        
        # Remove newline characters and extra spaces
        book_name = " ".join(book_name.split())
        
        return book_name
    except Exception as e:
        error_logger.error(f"Error during book name extraction: {e}")
        return "Unknown Book"