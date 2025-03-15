import os
import time
import ray
from concurrent.futures import ThreadPoolExecutor, as_completed
from Logging import time_logger, error_logger, process_logger
from EJF import create_chapter_file

# ✅ Initialize Ray
ray.init(local_mode=True, log_to_driver=True)

@ray.remote
def create_chapter_file_parallel(chapter, text, book_name, output_dir):
    """Ray remote function for parallel JSON file creation with logging."""
    chapter_number = chapter["chapter"] if isinstance(chapter, dict) else chapter
    process_logger.info(f"🔄 Processing Chapter {chapter_number} (Ray)...")
    
    try:
        create_chapter_file(chapter, text, book_name, output_dir)
        process_logger.info(f"✅ Chapter {chapter_number} processed successfully (Ray).")
        return None
    except Exception as e:
        error_logger.error(f"❌ Error processing Chapter {chapter_number} (Ray): {e}")
        return None

def get_json_file_path(output_dir, chapter):
    """Returns the correct JSON file path by extracting the chapter number."""
    chapter_number = chapter["chapter"] if isinstance(chapter, dict) else chapter
    return os.path.join(output_dir, f'chapter_{chapter_number}.json')

def check_and_retry_missing_jsons(chapters, text, book_name, output_dir, use_ray=False):
    """
    Checks if all expected JSON files exist. If any are missing, retries their creation.
    - `use_ray=True` → Uses Ray for parallel retry.
    - `use_ray=False` → Uses ThreadPoolExecutor for retry.
    """
    missing_chapters = []
    found_chapters = []

    process_logger.info(f"🔍 Checking JSON files in: {output_dir}")

    for chapter in chapters:
        json_file = get_json_file_path(output_dir, chapter)

        # ✅ Debug: Print the exact corrected file path
        process_logger.info(f"🔍 Checking corrected file path: {json_file}")

        if os.path.exists(json_file):
            found_chapters.append(chapter)
        else:
            missing_chapters.append(chapter)

    process_logger.info(f"✅ Found JSON files: {[ch['chapter'] if isinstance(ch, dict) else ch for ch in found_chapters]}")

    if not missing_chapters:
        process_logger.info("✅ All JSON files have been successfully created.")
        return True  # No retry needed

    process_logger.warning(f"⚠️ {len(missing_chapters)} JSON files are missing. Retrying: {[ch['chapter'] if isinstance(ch, dict) else ch for ch in missing_chapters]}")

    time.sleep(5)  # Prevent race conditions

    if use_ray:
        ray_futures = [create_chapter_file_parallel.remote(ch, text, book_name, output_dir) for ch in missing_chapters]
        ray.get(ray_futures)
    else:
        with ThreadPoolExecutor(4) as executor:
            futures = [executor.submit(create_chapter_file, ch, text, book_name, output_dir) for ch in missing_chapters]
            for future in as_completed(futures):
                future.result()

    process_logger.info("✅ Retry completed. Checking again...")

    time.sleep(3)  # Allow all writes to finish

    return check_and_retry_missing_jsons(missing_chapters, text, book_name, output_dir, use_ray)  # Recursively check again

def process_chapters(chapters, text, book_name, output_dir):
    """
    Selects the best parallel processing approach based on the number of chapters.
    - If chapters < 13, use ThreadPoolExecutor.
    - If chapters == 26:
        - First 13 chapters → Process using ThreadPoolExecutor.
        - Ensure all JSONs are created.
        - Wait for 7 seconds before starting Ray.
        - Remaining 13 chapters → Process using Ray.
        - Ensure all JSONs are created.
    - If chapters > 13 (and not 26), use Ray.
    """
    num_chapters = len(chapters)
    process_logger.info(f"📖 Book has {num_chapters} chapters.")

    json_start_time = time.time()

    if num_chapters < 13:
        process_logger.info("⚡ Using ThreadPoolExecutor (Approach 2) for parallel processing.")
        check_and_retry_missing_jsons(chapters, text, book_name, output_dir, use_ray=False)

    elif num_chapters == 26:
        process_logger.info("🛠️ Splitting tasks: First 13 chapters (ThreadPoolExecutor), then delay, then Last 13 (Ray)")

        first_half = chapters[:13]  # First 13 chapters
        second_half = chapters[13:]  # Remaining 13 chapters

        # ✅ Process first 13 chapters with ThreadPoolExecutor
        #with ThreadPoolExecutor(4) as executor:
        #    thread_futures = [executor.submit(create_chapter_file, chapter, text, book_name, output_dir) for chapter in first_half]
        #    for future in as_completed(thread_futures):  
        #        future.result()  # Ensure all threads complete first

        time.sleep(5)  # ✅ Allow file writes to settle

        check_and_retry_missing_jsons(first_half, text, book_name, output_dir, use_ray=False)

        time.sleep(7)  # ✅ Ensure no overlap between approaches

        process_logger.info("🚀 Starting Ray processing for remaining 13 chapters.")
        ray_futures = [create_chapter_file_parallel.remote(chapter, text, book_name, output_dir) for chapter in second_half]
        ray.get(ray_futures)

        time.sleep(5)  # ✅ Allow file writes to settle

        check_and_retry_missing_jsons(second_half, text, book_name, output_dir, use_ray=True)

    else:
        process_logger.info("🚀 Using Ray (Approach 1) for parallel processing.")
        futures = [create_chapter_file_parallel.remote(chapter, text, book_name, output_dir) for chapter in chapters]
        ray.get(futures)

        time.sleep(5)  # ✅ Allow file writes to settle

        check_and_retry_missing_jsons(chapters, text, book_name, output_dir, use_ray=True)

    json_end_time = time.time()
    json_duration = json_end_time - json_start_time
    time_logger.info(f"Total time for JSON file creation: {json_duration} seconds")
    process_logger.info("✅ All JSON files have been processed.")
