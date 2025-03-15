# File: project_backend/core/settings.py

from dotenv import load_dotenv
import sys
import os
import google.generativeai as genai

# Add the root directory of your project to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
load_dotenv()

class Settings:
    def __init__(self):
        self.DEBUG = True
        self.DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'db.sqlite3',
            }
        }
        
        # Configure Google Generative AI with your API key
        #genai.configure(api_key='AIzaSyDTIyXtEr13KtwWxg65x8HEoWNb_vhXhoQ')
        #genai.configure(api_key='AIzaSyBwv1nw6Ve1v_vQauvXJkJyP9EyuqutlP4')
        genai.configure(api_key='AIzaSyAc2nZakfUxp-u8tygf7Xw82sb1eKie13Y')
        self.TTS_API_KEY = "sk_04e26bb82e8c944ad87f77521505173d3b67580619a7a111"  

        # Initialize the specific Gemini model
        self.GEMINI_MODEL = genai.GenerativeModel('gemini-2.0-flash')

        # List of template IDs for the presentation
        self.template_ids = [
        #"1KcMJdY_DbEz7DLyeA46KJkRnFJUjUfKV_mvRGEYdfY4", #orange template
        "118ALaGB4r_Ix0_f2UfyleZl7V1GEniKf7XFMpZY8h6g", #black template
        "1usymvgJLh2GJpKkdVN5DOCUz5jhcwNuKu7nYmysO0gI", #white template 
        "1vAVSGRQez4mcRr45Z7-xPLKGTAh3k-YimJQzY3iX-og" #green template
        ]