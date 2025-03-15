import sys
import os
from PyPDF2 import PdfReader
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from Logging import time_logger, error_logger, gemini_logger , process_logger

#i need is when i upload a pdf book it would start to create a json files for this book but before it i want it to create a folder with name book in ppt_jsons anad in that folder is to create the json files

# Add the root directory of your project to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..' ,'..', '..')))

from project_backend.core.settings import Settings

# Initialize the Settings class
settings = Settings()

# Debug print statement to verify GEMINI_MODEL
GEMINI_MODEL = settings.GEMINI_MODEL


def extract_chapters_from_pdf(pdf_path):
    """
    Extract chapters from the PDF.
    """
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def get_number_of_chapters_with_gemini(text):
    """
    Use the Gemini AI model to get the number of chapters from the text.
    """
    try:
        prompt = (
            "Extract the number of chapters and their titles from the following text.\n"
            "Return the output in JSON format with the following structure:\n"
            "{\n"
            "  \"number_of_chapters\": <number>,\n"
            "  \"chapters\": [\n"
            "    {\"chapter\": 1, \"title\": \"Chapter 1 Title\"},\n"
            "    {\"chapter\": 2, \"title\": \"Chapter 2 Title\"},\n"
            "    ...\n"
            "  ]\n"
            "}\n\n"
            f"Text:\n{text}"
        )
        time.sleep(10)
        response = GEMINI_MODEL.generate_content(prompt)
        #print("Gemini Response:", response.text)
        
        # Clean the response: Remove backticks and extra spaces if they exist
        clean_response = response.text.strip()
        if clean_response.startswith("```json"):
            clean_response = clean_response[7:]
        if clean_response.endswith("```"):
            clean_response = clean_response[:-3]
        
        return json.loads(clean_response.strip())
    except Exception as e:
        error_logger.error(f"Error during chapter extraction: {e}")
        return None

def create_chapter_file(chapter, text, book_name, output_dir):
    """
    Create a JSON file for a single chapter with its title and summarized content in bullet points for PPT slides.
    Also create a script file for the virtual teacher for each slide.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    chapter_number = chapter["chapter"]
    chapter_title = chapter["title"]
    
    # Extract and summarize the content for the chapter
    prompt = (
        f"Extract and summarize the content for Chapter {chapter_number} titled '{chapter_title}' from the following text.\n"
        "Summarize the content into 10 to 15 slides for a PowerPoint presentation.\n"
        "Each slide should:\n"
        "- Have a title.\n"
        "- Contain 4 to 7 bullet points.\n"
        "- Each bullet point must be concise, with a minimum of 60 characters and a maximum of 100 characters.\n"
        "Additionally, generate a script for the virtual teacher for each slide.\n"
        "The script should:\n"
        "- Provide a brief introduction to the slide.\n"
        "- Cover the main points of the slide.\n"
        "Return the output in JSON format with the following structure:\n"
        "{\n"
        "  \"book_name\": \"<book_name>\",\n"
        "  \"chapter\": <number>,\n"
        "  \"title\": \"<title>\",\n"
        "  \"slides\": [\n"
        "    {\"slide_number\": <number>, \"title\": \"Slide 1 Title\", \"content\": [\"Bullet 1\", \"Bullet 2\", \"Bullet 3\"], \"script\": \"Script for Slide 1\"},\n"
        "    {\"slide_number\": <number>, \"title\": \"Slide 2 Title\", \"content\": [\"Bullet 1\", \"Bullet 2\"], \"script\": \"Script for Slide 2\"},\n"
        "    ...\n"
        "  ]\n"
        "}\n\n"
        f"Text:\n{text}"
    )
    
    retry_count = 0
    max_retries = 4  # Increase the number of retries
    while retry_count < max_retries:
        try:
            response = GEMINI_MODEL.generate_content(prompt)
            clean_response = response.text.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            clean_response = clean_response.replace('\\n', '\n').replace('\\r', '\r')
            chapter_json = json.loads(clean_response.strip())
            chapter_json["book_name"] = book_name
            
            chapter_filename = os.path.join(output_dir, f"chapter_{chapter_number}.json")
            with open(chapter_filename, "w") as json_file:
                json.dump(chapter_json, json_file, indent=4)
            process_logger.info(f"Saved {chapter_filename}")
            """
            # Create the script file for the virtual teacher
            script = {
                "book_name": book_name,
                "chapter": chapter_number,
                "title": chapter_title,
                "slides": []
            }
            for slide in chapter_json["slides"]:
                script["slides"].append({
                    "slide_number": slide["slide_number"],
                    "title": slide["title"],
                    "content": slide["content"],
                    "script": slide["script"]
                })
            
            """
            break  # Exit the retry loop if successful
        except Exception as e:
            error_logger.error(f"Error during content generation for Chapter {chapter_number}: {e}")
            retry_count += 1
            if retry_count < max_retries:
                wait_time = 2 ** retry_count  # Exponential backoff
                error_logger.error(f"Retrying content generation for Chapter {chapter_number} ({retry_count}/{max_retries}) after {wait_time} seconds...")
                time.sleep(20)  # Wait before retrying
            else:
                error_logger.error(f"Failed to generate content for Chapter {chapter_number} after {max_retries} retries.")