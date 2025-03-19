import json
import sys
import os
import time
import random
import logging
import ray
from Logging import time_logger, error_logger, gemini_logger , process_logger

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from Authenticator import Auth
from ppt_creator import create_presentation_for_chapter
from EJF import extract_chapters_from_pdf, get_number_of_chapters_with_gemini, create_chapter_file
from EBN import get_book_name_with_gemini
from EJFA import create_chapter_file_parallel , process_chapters
from project_backend.core.settings import Settings



settings = Settings()
GEMINI_MODEL = settings.GEMINI_MODEL
template_ids = settings.template_ids

MAX_REQUESTS_PER_MINUTE = 60
MIN_WAIT_TIME = 1.5


def main(pdf_path):
    print("🚀 Processing the book...")
    process_start_time = time.time()

    text = extract_chapters_from_pdf(pdf_path)
    book_name = get_book_name_with_gemini(text)
    gemini_logger.info(f"Extracted Book Name: {book_name}")

    output_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))), 'pdf-summarizer/ppt_jsons', book_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    chapters_info = get_number_of_chapters_with_gemini(text)
    gemini_logger.info(f"Gemini Response: {chapters_info}")

    if not chapters_info or "chapters" not in chapters_info:
        error_logger.error("❌ No chapters detected. Exiting process.")
        return []

    chapters = chapters_info["chapters"]

    # ✅ Process chapters based on the optimized approach
    process_chapters(chapters, text, book_name, output_dir)

    # Authenticate with Google Slides API
    service = Auth.authenticate_with_google()
    drive_service = Auth.authenticate_with_google_drive()

    presentation_links = []
    links_file = os.path.join(output_dir, 'presentation_links.json')

    if not os.path.exists(links_file):
        with open(links_file, 'w') as f:
            json.dump([], f)

    try:
        with open(links_file, 'r') as f:
            presentation_links = json.load(f)
    except json.JSONDecodeError:
        presentation_links = []

    processed_files = set(presentation_links)

    ppt_start_time = time.time()
    i = 1
    while True:
        json_file = os.path.join(output_dir, f'chapter_{i}.json')
        if not os.path.exists(json_file):
            error_logger.error(f"{json_file} not found. Stopping the loop.")
            break

        retry_count = 0
        max_retries = 5

        while retry_count < max_retries:
            try:
                process_logger.info(f"Processing {json_file}...")
                template_id = random.choice(template_ids)
                public_link = create_presentation_for_chapter(service, drive_service, i, book_name, template_id)

                if public_link and public_link not in processed_files:
                    process_logger.info(f"Slides from {json_file} added successfully!")
                    presentation_links.append(public_link)
                    processed_files.add(public_link)
                    with open(links_file, 'w') as f:
                        json.dump(presentation_links, f, indent=4)
                break

            except FileNotFoundError:
                error_logger.error(f"{json_file} not found. Stopping the loop.")
                return presentation_links

            except Exception as e:
                retry_count += 1
                wait_time = 2 ** retry_count
                error_logger.error(f"Error processing {json_file}: {e}. Retrying ({retry_count}/{max_retries}) after {wait_time} seconds...")
                time.sleep(20)

        i += 1

    ppt_end_time = time.time()
    ppt_duration = ppt_end_time - ppt_start_time
    time_logger.info(f"Total time for PPT creation: {ppt_duration} seconds")

    process_end_time = time.time()
    process_duration = process_end_time - process_start_time
    time_logger.info(f"Total time from upload to PPT links: {process_duration} seconds")

    return presentation_links

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python ppt.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    links = main(pdf_path)
    #for link in links:
        #print(link)
