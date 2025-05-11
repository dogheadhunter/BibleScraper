import requests
from bs4 import BeautifulSoup
import time
import os
# import argparse # No longer needed for operational settings

from generate_bible_urls import BIBLE_BOOKS, BASE_URL # Import from generate_bible_urls

# Constants for retry, User-Agent, and delays (these will be defaults for prompts)
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 10 # Increased delay for retries
REQUEST_TIMEOUT_SECONDS = 15 # Timeout for each request
INTER_REQUEST_DELAY_SECONDS = 1 # Delay between successful scrapes
USER_AGENT = "BibleVerseScraper/4.0 (for educational purposes)"

def scrape_website(url, max_retries_param, retry_delay_param, timeout_param):
    headers = {
        'User-Agent': USER_AGENT
    }
    raw_html_content = None
    all_page_text_content = None

    for attempt in range(max_retries_param):
        try:
            response = requests.get(url, headers=headers, timeout=timeout_param)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            raw_html_content = response.text # Store raw HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Attempt to get text from the main content area for a cleaner "all_text" file
            main_content_element = soup.find(id='content') 
            if main_content_element:
                all_page_text_content = main_content_element.get_text(separator=' ', strip=True)
            else:
                # Fallback to getting all text from the page if id='content' is not found
                all_page_text_content = soup.get_text(separator=' ', strip=True)

            book_title_val = None
            citation_text_val = None
            main_bible_text_val = None
            has_content = False

            # Part 1: Book Title
            title_element = soup.find('span', class_='bibleDisplayTitle')
            if title_element:
                book_title_val = title_element.get_text(strip=True)
                if book_title_val: 
                    book_title_val = book_title_val.replace('+', '').replace('*', '') # Remove + and *
                    book_title_val = ' '.join(book_title_val.split()) # Normalize whitespace
                    has_content = True

            # Part 2: Citation
            citation_element = soup.find('span', class_='bibleRangeCitation')
            if citation_element:
                citation_text_val = citation_element.get_text(strip=True)
                if citation_text_val: 
                    citation_text_val = citation_text_val.replace('+', '').replace('*', '') # Remove + and *
                    citation_text_val = ' '.join(citation_text_val.split()) # Normalize whitespace
                    has_content = True
            
            # Part 3: Bible Text
            bible_text_div = soup.find('div', id='bibleText')
            if bible_text_div:
                main_bible_text_val = bible_text_div.get_text(separator=' ', strip=True)
                if main_bible_text_val: 
                    main_bible_text_val = main_bible_text_val.replace('+', '').replace('*', '') # Remove + and *
                    main_bible_text_val = ' '.join(main_bible_text_val.split()) # Normalize whitespace
                    has_content = True
            
            if not has_content:
                print(f"No relevant content (Book, citation, or bible text) found on {url}")
                return None, None, None, raw_html_content, all_page_text_content # Return raw/all_text even if no specific content
            
            return book_title_val, citation_text_val, main_bible_text_val, raw_html_content, all_page_text_content

        except requests.exceptions.Timeout:
            print(f"Timeout occurred for {url} on attempt {attempt + 1}/{max_retries_param}")
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error for {url} on attempt {attempt + 1}/{max_retries_param}: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {url} on attempt {attempt + 1}/{max_retries_param}: {e}")
        
        if attempt < max_retries_param - 1:
            print(f"Waiting {retry_delay_param} seconds before retrying...")
            time.sleep(retry_delay_param)
        else:
            print(f"Max retries reached for {url}. Skipping.")
            
    return None, None, None, raw_html_content, all_page_text_content # Return None for structured data, but potentially raw/all_text if fetched before error

def prompt_for_operational_settings(current_settings):
    """Prompts the user for operational settings and returns them."""
    print("\n--- Configure Scraping Settings ---")
    
    new_max_retries = current_settings['max_retries']
    new_retry_delay = current_settings['retry_delay']
    new_timeout = current_settings['timeout']
    new_inter_request_delay = current_settings['inter_request_delay']

    while True:
        try:
            val = input(f"Enter maximum retries per URL (current: {new_max_retries}, default: {MAX_RETRIES}): ").strip()
            if not val: # User pressed Enter, keep current or default if current is initial default
                new_max_retries = new_max_retries if new_max_retries != MAX_RETRIES and current_settings['initial_run'] is False else MAX_RETRIES
            else:
                new_max_retries = int(val)
            if new_max_retries < 0:
                print("Max retries cannot be negative. Please enter a valid number.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a number.")

    while True:
        try:
            val = input(f"Enter delay between retries in seconds (current: {new_retry_delay}, default: {RETRY_DELAY_SECONDS}): ").strip()
            if not val:
                new_retry_delay = new_retry_delay if new_retry_delay != RETRY_DELAY_SECONDS and current_settings['initial_run'] is False else RETRY_DELAY_SECONDS
            else:
                new_retry_delay = int(val)
            if new_retry_delay < 0:
                print("Retry delay cannot be negative. Please enter a valid number.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a number.")

    while True:
        try:
            val = input(f"Enter request timeout in seconds (current: {new_timeout}, default: {REQUEST_TIMEOUT_SECONDS}): ").strip()
            if not val:
                new_timeout = new_timeout if new_timeout != REQUEST_TIMEOUT_SECONDS and current_settings['initial_run'] is False else REQUEST_TIMEOUT_SECONDS
            else:
                new_timeout = int(val)
            if new_timeout <= 0:
                print("Timeout must be a positive number. Please enter a valid number.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a number.")

    while True:
        try:
            val = input(f"Enter delay between successful scrapes in seconds (current: {new_inter_request_delay}, default: {INTER_REQUEST_DELAY_SECONDS}): ").strip()
            if not val:
                new_inter_request_delay = new_inter_request_delay if new_inter_request_delay != INTER_REQUEST_DELAY_SECONDS and current_settings['initial_run'] is False else INTER_REQUEST_DELAY_SECONDS
            else:
                new_inter_request_delay = int(val)
            if new_inter_request_delay < 0:
                print("Inter-request delay cannot be negative. Please enter a valid number.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a number.")
            
    return {
        'max_retries': new_max_retries,
        'retry_delay': new_retry_delay,
        'timeout': new_timeout,
        'inter_request_delay': new_inter_request_delay,
        'initial_run': False # Mark that settings have been potentially modified
    }

if __name__ == "__main__":
    # Initialize operational settings with defaults
    operational_settings = {
        'max_retries': MAX_RETRIES,
        'retry_delay': RETRY_DELAY_SECONDS,
        'timeout': REQUEST_TIMEOUT_SECONDS,
        'inter_request_delay': INTER_REQUEST_DELAY_SECONDS,
        'initial_run': True # Flag to indicate if settings are still initial defaults
    }

    url_lists_dir = "url_lists"
    available_url_files = []
    try:
        all_files_in_dir = os.listdir(url_lists_dir)
        for filename in all_files_in_dir:
            if filename.endswith("_urls.txt"):
                available_url_files.append(filename)
    except FileNotFoundError:
        print(f"Error: The directory '{url_lists_dir}' was not found. Please create it and add your URL list files (e.g., version_urls.txt).")
        exit()

    if not available_url_files:
        print(f"No URL list files (ending with '_urls.txt') found in the '{url_lists_dir}' directory. Exiting.")
        exit()

    chosen_url_list_filename = None
    while True: # Loop for version selection / settings configuration
        print("\nAvailable Bible versions (from URL lists):")
        for i, filename in enumerate(available_url_files):
            display_name = filename[:-len("_urls.txt")].replace("_", " ").title()
            print(f"  {i + 1}: {display_name} (from {filename})")
        
        config_option_number = len(available_url_files) + 1
        print(f"  {config_option_number}: Configure Operational Settings")

        try:
            choice_str = input(f"Enter your choice (1-{config_option_number}): ").strip()
            if not choice_str: # Handle empty input
                print("No choice made. Please enter a number.")
                continue
            choice = int(choice_str)

            if 1 <= choice <= len(available_url_files):
                selected_index = choice - 1
                chosen_url_list_filename = available_url_files[selected_index]
                print(f"You selected: {chosen_url_list_filename}")
                break # Exit the loop once a version is chosen
            elif choice == config_option_number:
                operational_settings = prompt_for_operational_settings(operational_settings)
                # Loop continues to re-display the menu
            else:
                print(f"Invalid choice. Please enter a number between 1 and {config_option_number}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Assign final operational settings from the dictionary
    current_max_retries = operational_settings['max_retries']
    current_retry_delay = operational_settings['retry_delay']
    current_timeout = operational_settings['timeout']
    current_inter_request_delay = operational_settings['inter_request_delay']
            
    print(f"\nScript settings: Max Retries={current_max_retries}, Retry Delay={current_retry_delay}s, Timeout={current_timeout}s, Inter-Request Delay={current_inter_request_delay}s")

    _URL_LIST_FILE_PATH = os.path.join(url_lists_dir, chosen_url_list_filename)
    # --- End of new code for selecting URL list ---

    # --- Start of new interactive prompts for books, start_at, limit ---
    user_specified_books = None
    specify_books_choice = input("Do you want to scrape specific books? (yes/no, default: no, all books in list): ").strip().lower()
    if specify_books_choice == 'yes':
        books_input = input("Enter comma-separated book keys (e.g., genesis,exodus): ").strip()
        if books_input:
            user_specified_books = [key.strip().lower() for key in books_input.split(',') if key.strip()]
        else:
            print("No specific books entered, will use all books from the selected list.")

    user_specified_start_at = None
    specify_start_at_choice = input("Do you want to specify a starting book and chapter? (yes/no, default: no, start from beginning): ").strip().lower()
    if specify_start_at_choice == 'yes':
        start_at_input = input("Enter start book and chapter (format: book_key:chapter_num, e.g., genesis:5): ").strip()
        if start_at_input:
            user_specified_start_at = start_at_input
        else:
            print("No starting point entered, will start from the beginning of the list/books.")

    user_specified_limit = None
    specify_limit_choice = input("Do you want to limit the number of chapters to scrape? (yes/no, default: no, no limit): ").strip().lower()
    if specify_limit_choice == 'yes':
        limit_input = input("Enter the maximum number of chapters to scrape: ").strip()
        if limit_input.isdigit():
            user_specified_limit = int(limit_input)
            if user_specified_limit <= 0:
                print("Limit must be a positive number. No limit will be applied.")
                user_specified_limit = None
        else:
            print("Invalid input for limit. No limit will be applied.")
    # --- End of new interactive prompts ---

    # Derive bible_version_identifier from the URL list filename
    url_list_basename = os.path.basename(_URL_LIST_FILE_PATH)
    if url_list_basename.endswith("_urls.txt"):
        bible_version_identifier = url_list_basename[:-len("_urls.txt")]
    elif url_list_basename.endswith(".txt"):
        bible_version_identifier = os.path.splitext(url_list_basename)[0]
    else:
        # Fallback if the pattern is unexpected
        bible_version_identifier = url_list_basename 

    # --- Directory for processed URL files ---
    PROCESSED_URLS_DIR = "processed_url_lists"
    os.makedirs(PROCESSED_URLS_DIR, exist_ok=True)
    # --- End of directory for processed URL files ---

    # Dynamically set OUTPUT_FILENAME and PROCESSED_URLS_FILENAME based on the version
    OUTPUT_FILENAME = f"scraped_texts/{bible_version_identifier}_edition.txt"
    PROCESSED_URLS_FILENAME = os.path.join(PROCESSED_URLS_DIR, f"processed_urls_{bible_version_identifier}.txt")
    
    # This variable is used later to open the file.
    URL_LIST_FILENAME = _URL_LIST_FILE_PATH

    RAW_HTML_DIR = "raw_html"
    ALL_TEXT_DIR = "all_text"
    # INTER_REQUEST_DELAY_SECONDS is now current_inter_request_delay, defined by prompt

    all_urls_to_consider = []

    # Ensure output directories exist
    os.makedirs(os.path.dirname(OUTPUT_FILENAME), exist_ok=True)
    os.makedirs(RAW_HTML_DIR, exist_ok=True)
    os.makedirs(ALL_TEXT_DIR, exist_ok=True)

    # --- Start of revised logic for populating and filtering URLs ---
    master_url_list = []
    try:
        # URL_LIST_FILENAME is _URL_LIST_FILE_PATH, which correctly points to the user-selected file
        with open(URL_LIST_FILENAME, "r", encoding="utf-8") as f:
            master_url_list = [line.strip() for line in f if line.strip()]
        if not master_url_list:
            print(f"The selected URL list file {URL_LIST_FILENAME} is empty. Nothing to process.")
            exit()
        print(f"Loaded {len(master_url_list)} URLs from {URL_LIST_FILENAME}.")
    except FileNotFoundError:
        print(f"Error: The selected URL list file {URL_LIST_FILENAME} not found. Please ensure the file exists. Exiting.")
        exit()

    all_urls_to_consider = master_url_list[:] # Start with all URLs from the chosen file

    # Filter by user_specified_books if provided
    if user_specified_books:
        print(f"Filtering for specified books: {', '.join(user_specified_books)}")
        filtered_urls_by_book = []
        for url in all_urls_to_consider:
            try:
                # Extract book_key from URL (e.g., https://.../books/book_key/chapter_num/)
                path_segments = [s for s in url.split('/') if s] # Remove empty segments
                if len(path_segments) >= 2: # Need at least book and chapter segments
                    # url_chapter_candidate = path_segments[-1]
                    url_book_key_candidate = path_segments[-2]
                    # Further check if 'books' is a parent segment to be more robust, if necessary
                    # For now, assume the structure is consistent enough.
                    if url_book_key_candidate in user_specified_books:
                        filtered_urls_by_book.append(url)
                else:
                    print(f"Warning: Could not parse book from URL (too few segments): {url}")
            except Exception as e:
                print(f"Warning: Error parsing book from URL {url}: {e}")
                continue
        
        all_urls_to_consider = filtered_urls_by_book
        if not all_urls_to_consider:
            print(f"No URLs found in {URL_LIST_FILENAME} matching the specified books: {', '.join(user_specified_books)}. Exiting.")
            exit()
        print(f"After book filtering, {len(all_urls_to_consider)} URLs remain.")

    # Load processed URLs (PROCESSED_URLS_FILENAME is already version-specific)
    processed_urls = set()
    try:
        with open(PROCESSED_URLS_FILENAME, "r", encoding="utf-8") as f:
            processed_urls = {line.strip() for line in f if line.strip()}
        print(f"Loaded {len(processed_urls)} already processed URLs from {PROCESSED_URLS_FILENAME}.")
    except FileNotFoundError:
        print(f"{PROCESSED_URLS_FILENAME} not found. Starting with an empty set of processed URLs.")

    # Apply start_at if specified, by finding it in the current all_urls_to_consider list
    if user_specified_start_at:
        try:
            start_book_key_input, start_chapter_str_input = user_specified_start_at.split(':')
            start_chapter_num_input = int(start_chapter_str_input)
            start_book_key_input = start_book_key_input.strip().lower()

            # Optional: Validate against BIBLE_BOOKS, but primary is finding in list
            if start_book_key_input not in BIBLE_BOOKS:
                print(f"Info: Start book key '{start_book_key_input}' not in BIBLE_BOOKS constant. Proceeding with direct URL match.")
            elif not (1 <= start_chapter_num_input <= BIBLE_BOOKS.get(start_book_key_input, float('inf'))):
                print(f"Warning: Start chapter {start_chapter_num_input} for book '{start_book_key_input}' is outside range (1-{BIBLE_BOOKS.get(start_book_key_input, 'N/A')}) according to BIBLE_BOOKS. Will still attempt to find exact match in URL list.")

            found_start_url_in_list = False
            start_index_in_list = 0
            for i, url in enumerate(all_urls_to_consider):
                try:
                    path_segments = [s for s in url.split('/') if s]
                    if len(path_segments) >= 2:
                        url_chapter_str = path_segments[-1]
                        url_book_key = path_segments[-2]
                        if url_book_key == start_book_key_input and int(url_chapter_str) == start_chapter_num_input:
                            start_index_in_list = i
                            found_start_url_in_list = True
                            break
                    else:
                        print(f"Warning: Could not parse book/chapter from URL for start_at matching (too few segments): {url}")
                except Exception as e:
                    print(f"Warning: Error parsing book/chapter from URL {url} for start_at: {e}")
                    continue
            
            if found_start_url_in_list:
                print(f"Starting scrape from {all_urls_to_consider[start_index_in_list]} (index {start_index_in_list} in current list).")
                all_urls_to_consider = all_urls_to_consider[start_index_in_list:]
            else:
                print(f"Error: Specified start point {user_specified_start_at} (parsed as book '{start_book_key_input}', chapter {start_chapter_num_input}) not found in the current list of URLs to consider. Exiting.")
                exit()

        except ValueError:
            print(f"Error: Invalid format for start_at '{user_specified_start_at}'. Expected 'book_key:chapter_num'. Exiting.")
            exit()
        except Exception as e:
            print(f"An unexpected error occurred while processing --start_at: {e}. Exiting.")
            exit()

    # Apply limit if specified
    if user_specified_limit is not None:
        if user_specified_limit <= 0:
            print("Warning: Limit cannot be zero or negative. Ignoring limit.")
        else:
            all_urls_to_consider = all_urls_to_consider[:user_specified_limit]
            print(f"Limited to scraping a maximum of {user_specified_limit} chapters. {len(all_urls_to_consider)} URLs remain.")
    
    # Final list of URLs to actually scrape for this run
    urls_to_scrape = [url for url in all_urls_to_consider if url not in processed_urls]

    if not urls_to_scrape:
        print("All selected URLs (after filtering and considering start_at/limit) have already been processed or the list is empty. Nothing to do.")
        exit()
    
    print(f"Starting main scraping loop for {len(urls_to_scrape)} URLs.")
    # --- End of revised logic ---

    # The existing main loop starting with "for url_to_scrape in urls_to_scrape:" will use the correctly prepared list.
    # Ensure no old conflicting code for all_urls_to_consider, processed_urls, or urls_to_scrape remains below this point until the loop.
    # ... (The main scraping loop follows)
    # for url_to_scrape in urls_to_scrape:
    # ...existing code...

    last_book_title_written_to_file = None # This needs to be smarter for resume
    # To correctly handle book titles on resume, we might need to peek at the last lines of OUTPUT_FILENAME
    # For now, it might reprint the Book title if resuming mid-book.
    is_first_successful_scrape_in_this_run = True 

    # The main loop iterates over urls_to_actually_process
    for i, target_url in enumerate(urls_to_scrape):
        print(f"Scraping URL {i+1}/{len(urls_to_scrape)}: {target_url}")
        # Pass the configured settings to scrape_website
        book_name, citation, main_text, raw_html, all_text = scrape_website(target_url, current_max_retries, current_retry_delay, current_timeout)

        # Generate directory and file names from URL for the new structure
        book_key_for_dir = "unknown_book" # Default
        chapter_filename_part = f"file_{i}" # Default

        try:
            url_parts = target_url.strip('/').split('/')
            # Assuming URL structure like .../books/book_key/chapter_num/
            if len(url_parts) >= 2: 
                book_key_for_dir = url_parts[-2]
                chapter_filename_part = url_parts[-1]
            else:
                # This case might occur if a URL in the list is not in the expected format
                print(f"Warning: URL '{target_url}' does not have expected book/chapter segments. Using fallback names.")
                # Fallback names are already set above, but we could make them more specific if needed
                # For example, chapter_filename_part = f"malformed_url_{i}"
        except Exception as e: # Catch any unexpected error during parsing
            print(f"Error parsing book/chapter from URL '{target_url}': {e}. Using fallback names.")
            # Fallback names are already set

        if raw_html:
            # Construct the target directory path: raw_html/version/book/
            raw_html_target_dir = os.path.join(RAW_HTML_DIR, bible_version_identifier, book_key_for_dir)
            os.makedirs(raw_html_target_dir, exist_ok=True)
            # Filename will now just be chapter_number.html
            raw_html_filepath = os.path.join(raw_html_target_dir, f"{chapter_filename_part}.html")
            
            with open(raw_html_filepath, "w", encoding="utf-8") as f_html:
                f_html.write(raw_html)
            print(f"Saved raw HTML to {raw_html_filepath}")

        if all_text:
            # Construct the target directory path: all_text/version/book/
            all_text_target_dir = os.path.join(ALL_TEXT_DIR, bible_version_identifier, book_key_for_dir)
            os.makedirs(all_text_target_dir, exist_ok=True)
            # Filename will now just be chapter_number.txt
            all_text_filepath = os.path.join(all_text_target_dir, f"{chapter_filename_part}.txt")

            with open(all_text_filepath, "w", encoding="utf-8") as f_all_text:
                f_all_text.write(all_text)
            print(f"Saved all text to {all_text_filepath}")
        
        if book_name or citation or main_text: # If any specific formatted data was scraped
            lines_to_write = []

            # Logic to handle book title printing (might need refinement for perfect resume)
            if book_name and book_name != last_book_title_written_to_file:
                lines_to_write.append(f"Book: {book_name}")
                lines_to_write.append("") 
                last_book_title_written_to_file = book_name
            elif not last_book_title_written_to_file and book_name and is_first_successful_scrape_in_this_run:
                lines_to_write.append(f"Book: {book_name}")
                lines_to_write.append("")
                last_book_title_written_to_file = book_name

            if citation:
                lines_to_write.append(citation)
                lines_to_write.append("") # Blank line
            
            if main_text:
                lines_to_write.append(main_text)
            elif lines_to_write and lines_to_write[-1] == "": # If no main_text, and last line added was blank
                lines_to_write.pop() # Remove that trailing blank line

            if lines_to_write: 
                with open(OUTPUT_FILENAME, "a", encoding="utf-8") as f:
                    if not is_first_successful_scrape_in_this_run:
                        f.write("\n") 
                    
                    f.write("\n".join(lines_to_write))
                    f.write("\n") 
                
                is_first_successful_scrape_in_this_run = False
                print(f"Successfully extracted and appended content from {target_url}")
                
                # Add to processed URLs
                with open(PROCESSED_URLS_FILENAME, "a", encoding="utf-8") as f_processed:
                    f_processed.write(target_url + "\n")
        else:
            print(f"No content extracted or error for {target_url} after retries. Check logs above.")
        
        if i < len(urls_to_scrape) - 1: 
            print(f"Waiting for {current_inter_request_delay} seconds...")
            time.sleep(current_inter_request_delay)
    
    print(f"Finished scraping. Results saved to {OUTPUT_FILENAME}")
