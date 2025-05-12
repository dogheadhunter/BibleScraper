import re
import difflib
import os
import datetime # Added for timestamp in output filename

# --- Configuration ---
BASE_DIR = "normalized_texts" # Changed from "scraped_texts"
OUTPUT_DIR = "compared_results"

CANONICAL_BOOK_NAMES = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
    "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings",
    "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther", "Job",
    "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon", "Isaiah",
    "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
    "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai",
    "Zechariah", "Malachi", "Matthew", "Mark", "Luke", "John", "Acts",
    "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
    "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James",
    "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude", "Revelation"
]

# --- Helper Functions for User Selection ---

def list_available_texts(directory):
    """Lists .txt files in the specified directory and returns their names."""
    try:
        files = [f for f in os.listdir(directory) if f.endswith('.txt') and os.path.isfile(os.path.join(directory, f))]
        if not files:
            print(f"No .txt files found in directory: {directory}")
            return []
        return sorted(files)
    except FileNotFoundError:
        print(f"Error: Directory not found at {directory}")
        return []

def choose_files_for_comparison(available_files):
    """Prompts the user to select 2 or 3 files for comparison."""
    if not available_files:
        return []

    print("\nAvailable Bible texts for comparison:")
    for i, filename in enumerate(available_files):
        print(f"  {i + 1}. {filename}")

    num_to_compare = 0
    while num_to_compare not in [2, 3]:
        try:
            num_input = input("Compare 2 or 3 files? (Enter 2 or 3): ")
            num_to_compare = int(num_input)
            if num_to_compare not in [2, 3]:
                print("Invalid input. Please enter 2 or 3.")
        except ValueError:
            print("Invalid input. Please enter a number (2 or 3).")

    selected_file_configs = []
    selected_indices = []
    print(f"\nPlease select {num_to_compare} files by their numbers (e.g., 1,2 or 1,2,3):")
    
    while len(selected_file_configs) < num_to_compare:
        try:
            choices_input = input(f"Enter {'comma-separated numbers for' if num_to_compare > 1 else 'the number for'} file {len(selected_file_configs) + 1}{' to ' + str(num_to_compare) if num_to_compare > 1 else ''}: ")
            chosen_indices_str = choices_input.split(',')
            
            current_selections_count = 0
            for choice_str in chosen_indices_str:
                choice = int(choice_str.strip())
                if 1 <= choice <= len(available_files) and (choice -1) not in selected_indices:
                    selected_indices.append(choice - 1)
                    # Derive a short name, e.g., "study_bible" from "study_bible_edition.txt"
                    full_filename = available_files[choice - 1]
                    short_name = full_filename.replace("_edition.txt", "").replace(".txt", "") # Basic shortening
                    selected_file_configs.append({"path": os.path.join(BASE_DIR, full_filename), "name": short_name})
                    current_selections_count +=1
                    if len(selected_file_configs) == num_to_compare:
                        break 
                else:
                    if not (1 <= choice <= len(available_files)):
                        print(f"  Invalid number: {choice}. Please choose from 1 to {len(available_files)}.")
                    else:
                        print(f"  File {available_files[choice-1]} already selected or invalid input.")
            if len(selected_file_configs) < num_to_compare and current_selections_count < (num_to_compare - len(selected_file_configs) + current_selections_count) and chosen_indices_str :
                 print(f"  {num_to_compare - len(selected_file_configs)} more file(s) needed.")


        except ValueError:
            print("  Invalid input. Please enter numbers separated by commas if multiple.")
        if len(selected_file_configs) == num_to_compare:
            print("Selected files for comparison:")
            for conf in selected_file_configs:
                print(f"  - {conf['name']} ({os.path.basename(conf['path'])})")
            return selected_file_configs
        elif not chosen_indices_str and len(selected_file_configs) < num_to_compare : # User pressed enter without input
             print(f"  Please select {num_to_compare - len(selected_file_configs)} more file(s).")
    return selected_file_configs


def choose_books_for_comparison(parsed_data_list, file_names_list):
    """Prompts the user to select books for comparison from the parsed data, in canonical order."""
    all_books_found_in_files = set()
    for data in parsed_data_list:
        if data and 'books' in data:
            all_books_found_in_files.update(data['books'].keys())
    
    if not all_books_found_in_files:
        print("No books found in the selected files to compare.")
        return []

    # Filter and order available books according to CANONICAL_BOOK_NAMES
    canonically_ordered_available_books = [
        book for book in CANONICAL_BOOK_NAMES if book in all_books_found_in_files
    ]

    if not canonically_ordered_available_books:
        print("No common books (matching canonical list) found in the selected files to compare.")
        # Optionally, list books found but not in canonical list for debugging or user info
        # print("Books found in files but not in canonical list:", 
        #       all_books_found_in_files - set(CANONICAL_BOOK_NAMES))
        return []

    print("\nAvailable books for comparison (in canonical order):")
    print("  0. All available books (listed below)")
    for i, book_name in enumerate(canonically_ordered_available_books):
        print(f"  {i + 1}. {book_name}")

    selected_books_final = []
    while True:
        try:
            choices_input = input(f"Enter book numbers to compare (comma-separated, e.g., 1,3,5 or 0 for all from the list above): ")
            if not choices_input.strip():
                print("No input provided. Please make a selection.")
                continue

            choices_str = choices_input.split(',')
            
            if '0' in [c.strip() for c in choices_str]:
                print("  Selected: All available books (in canonical order)")
                return canonically_ordered_available_books # Return all available books in canonical order

            temp_selected_book_names = []
            valid_selection = True
            for choice_str in choices_str:
                choice = int(choice_str.strip())
                if 1 <= choice <= len(canonically_ordered_available_books):
                    selected_book_name = canonically_ordered_available_books[choice - 1]
                    if selected_book_name not in temp_selected_book_names:
                        temp_selected_book_names.append(selected_book_name)
                    else:
                        print(f"  Book '{selected_book_name}' already selected.")
                else:
                    print(f"  Invalid book number: {choice}. Please choose from 1 to {len(canonically_ordered_available_books)} (or 0 for all).")
                    valid_selection = False
                    break 
            
            if valid_selection and temp_selected_book_names:
                # Ensure the final list preserves the canonical order of selection
                selected_books_final = [
                    book for book in canonically_ordered_available_books if book in temp_selected_book_names
                ]
                print("  Selected books for comparison (in canonical order):")
                for book in selected_books_final:
                    print(f"    - {book}")
                return selected_books_final
            elif valid_selection and not temp_selected_book_names and choices_input.strip():
                 print("  No valid books selected. Please try again.")
            elif not valid_selection : 
                 print("  Please correct your selection.")

        except ValueError:
            print("  Invalid input. Please enter numbers (e.g., 1,3,5 or 0 for all).")
        except Exception as e: 
            print(f"An unexpected error occurred during book selection: {e}")
            return []


# --- Parsing Logic ---

def parse_bible_text_file(filepath):
    """
    Parses a Bible text file into a structured dictionary:
    {
        "books": {
            "BookName": {
                "chapters": {
                    ChapterNum: {
                        "verses": {
                            VerseNum: ["Sentence 1.", "Sentence 2."],
                            # ... more verses
                        }
                    },
                    # ... more chapters
                }
            },
            # ... more books
        }
    }
    """
    parsed_data = {"books": {}}
    current_book_name = None
    current_chapter_number = None # Stores the leading chapter number from citation, e.g., 16 from "16:1-16"

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        # This will be caught by the main execution block
        raise
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        raise # Or handle more gracefully depending on desired behavior

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("Book: "):
            current_book_name = line.replace("Book: ", "").strip()
            if current_book_name not in parsed_data["books"]:
                parsed_data["books"][current_book_name] = {"chapters": {}}
            current_chapter_number = None # Reset chapter when new book starts
            i += 1
            # Skip potential blank line after "Book:"
            if i < len(lines) and not lines[i].strip():
                i += 1
            continue

        # Match chapter citation like "16:1-16" or "1:1"
        citation_match = re.match(r"(\d+):\d+(?:-\d+)?", line)
        if citation_match and current_book_name:
            # Use the first number in the citation as the chapter number
            current_chapter_number = int(citation_match.group(1))

            if current_chapter_number not in parsed_data["books"][current_book_name]["chapters"]:
                parsed_data["books"][current_book_name]["chapters"][current_chapter_number] = {"verses": {}}
            
            i += 1 # Move past citation line
            # Skip potential blank line after citation
            if i < len(lines) and not lines[i].strip():
                i += 1
            
            verse_text_block_lines = []
            # Collect lines belonging to the current chapter's main text block
            while i < len(lines):
                line_to_check = lines[i].strip()
                # Stop if blank line, new Book, or new citation
                if not line_to_check:
                    i += 1 # Consume blank line
                    break 
                if line_to_check.startswith("Book: ") or re.match(r"(\d+):\d+(?:-\d+)?", line_to_check):
                    break
                verse_text_block_lines.append(lines[i]) # Keep original spacing within line
                i += 1
            
            full_chapter_text = "".join(verse_text_block_lines).strip()
            
            # Split the chapter text into verse blocks. Verses start with a number.
            # Regex: (?=\d+\s) - positive lookahead for digits followed by a space.
            # This splits the text *before* each verse number.
            raw_verse_chunks = re.split(r'(?=\d+\s)', full_chapter_text)

            for chunk in raw_verse_chunks:
                chunk = chunk.strip()
                if not chunk:
                    continue
                
                # Extract verse number and text
                verse_num_match = re.match(r"(\d+)\s+(.*)", chunk, re.DOTALL)
                if verse_num_match:
                    verse_num = int(verse_num_match.group(1))
                    verse_text = verse_num_match.group(2).strip()
                    
                    # Sentence tokenization (basic regex version)
                    # Splits after '.', '?', '!' followed by whitespace. Handles cases like "Mr. Smith."
                    sentences = re.split(r'(?<=[.?!])\s+', verse_text)
                    sentences = [s.strip() for s in sentences if s.strip()]

                    parsed_data["books"][current_book_name]["chapters"][current_chapter_number]["verses"][verse_num] = sentences
            continue # Continue outer loop to find next Book/Citation

        i += 1 # Default increment if no specific condition met
    return parsed_data

# --- Comparison Logic ---

def compare_parsed_bibles(parsed_data_list, file_names_list, books_to_compare): # books_to_compare is now canonically ordered
    """ Compares parsed Bible data from multiple files for selected books. 
        Returns a list of strings representing the comparison report.
    """
    report_lines = [] 

    if not (2 <= len(parsed_data_list) <= 3 and len(parsed_data_list) == len(file_names_list)):
        report_lines.append("Error: Comparison requires 2 or 3 datasets and corresponding names.")
        return report_lines

    data1 = parsed_data_list[0]
    name1 = file_names_list[0]
    data2 = parsed_data_list[1]
    name2 = file_names_list[1]
    data3 = parsed_data_list[2] if len(parsed_data_list) == 3 else None
    name3 = file_names_list[2] if len(file_names_list) == 3 else "[N/A]"

    # Iterate through books in the canonically ordered list provided
    for book_name in books_to_compare: 
        report_lines.append(f"\n--- Comparing Book: {book_name} ---")
        
        book1_data = data1['books'].get(book_name)
        book2_data = data2['books'].get(book_name)
        book3_data = data3['books'].get(book_name) if data3 else None

        # Check if book is present in all active files
        book_missing_in_any_active = False
        if not book1_data: report_lines.append(f"  Book '{book_name}' missing in {name1}"); book_missing_in_any_active = True
        if not book2_data: report_lines.append(f"  Book '{book_name}' missing in {name2}"); book_missing_in_any_active = True
        if len(parsed_data_list) == 3 and not book3_data: 
            report_lines.append(f"  Book '{book_name}' missing in {name3}"); book_missing_in_any_active = True
        if book_missing_in_any_active:
            continue

        all_chapter_numbers_set = set(book1_data['chapters'].keys()) | set(book2_data['chapters'].keys())
        if book3_data:
            all_chapter_numbers_set.update(book3_data['chapters'].keys())
        all_chapter_numbers = sorted(list(all_chapter_numbers_set))

        for chap_num in all_chapter_numbers:
            chap1 = book1_data['chapters'].get(chap_num)
            chap2 = book2_data['chapters'].get(chap_num)
            chap3 = book3_data['chapters'].get(chap_num) if book3_data else None
            
            chapter_has_differences_reported = False

            # Check if chapter is present in all active files
            chapter_missing_in_any_active = False
            if not chap1: chapter_missing_in_any_active = True
            if not chap2: chapter_missing_in_any_active = True
            if len(parsed_data_list) == 3 and not chap3: chapter_missing_in_any_active = True

            if chapter_missing_in_any_active:
                if not chapter_has_differences_reported:
                    report_lines.append(f"  -- Chapter {chap_num} (Book: {book_name}) --")
                    chapter_has_differences_reported = True
                if not chap1: report_lines.append(f"    Chapter missing in {name1}")
                if not chap2: report_lines.append(f"    Chapter missing in {name2}")
                if len(parsed_data_list) == 3 and not chap3: report_lines.append(f"    Chapter missing in {name3}")
                continue
            
            all_verse_numbers_set = set(chap1['verses'].keys()) | set(chap2['verses'].keys())
            if chap3:
                all_verse_numbers_set.update(chap3['verses'].keys())
            all_verse_numbers = sorted(list(all_verse_numbers_set))

            for verse_num in all_verse_numbers:
                verse1_sentences = chap1['verses'].get(verse_num)
                verse2_sentences = chap2['verses'].get(verse_num)
                verse3_sentences = chap3['verses'].get(verse_num) if chap3 else None
                
                verse_has_differences_reported = False

                # Check for missing verses
                verse_missing_in_any_active = False
                if verse1_sentences is None: verse_missing_in_any_active = True
                if verse2_sentences is None: verse_missing_in_any_active = True
                if len(parsed_data_list) == 3 and verse3_sentences is None: verse_missing_in_any_active = True

                if verse_missing_in_any_active:
                    if not chapter_has_differences_reported:
                        report_lines.append(f"  -- Chapter {chap_num} (Book: {book_name}) --")
                        chapter_has_differences_reported = True
                    if not verse_has_differences_reported:
                         report_lines.append(f"    Verse {verse_num}:")
                         verse_has_differences_reported = True
                    if verse1_sentences is None: report_lines.append(f"      Missing in {name1}")
                    if verse2_sentences is None: report_lines.append(f"      Missing in {name2}")
                    if len(parsed_data_list) == 3 and verse3_sentences is None: report_lines.append(f"      Missing in {name3}")
                
                max_sentences = 0
                if verse1_sentences: max_sentences = max(max_sentences, len(verse1_sentences))
                if verse2_sentences: max_sentences = max(max_sentences, len(verse2_sentences))
                if len(parsed_data_list) == 3 and verse3_sentences: 
                    max_sentences = max(max_sentences, len(verse3_sentences))

                for i in range(max_sentences):
                    s1_text = verse1_sentences[i] if verse1_sentences and i < len(verse1_sentences) else "[SENTENCE ABSENT]"
                    s2_text = verse2_sentences[i] if verse2_sentences and i < len(verse2_sentences) else "[SENTENCE ABSENT]"
                    s3_text = "[N/A]"
                    if len(parsed_data_list) == 3:
                        s3_text = verse3_sentences[i] if verse3_sentences and i < len(verse3_sentences) else "[SENTENCE ABSENT]"

                    sentences_differ = False
                    if len(parsed_data_list) == 3:
                        if not (s1_text == s2_text and s2_text == s3_text):
                            sentences_differ = True
                    else: # Only 2 files being compared
                        if s1_text != s2_text:
                            sentences_differ = True

                    if sentences_differ:
                        if not chapter_has_differences_reported:
                            report_lines.append(f"  -- Chapter {chap_num} (Book: {book_name}) --")
                            chapter_has_differences_reported = True
                        if not verse_has_differences_reported:
                            report_lines.append(f"    Verse {verse_num}:")
                            verse_has_differences_reported = True
                        
                        report_lines.append(f"      Sentence {i+1} Differs:")
                        report_lines.append(f"        {name1}: {s1_text}")
                        report_lines.append(f"        {name2}: {s2_text}")
                        if len(parsed_data_list) == 3:
                            report_lines.append(f"        {name3}: {s3_text}")
                        
                        pairs_to_diff = []
                        if s1_text != s2_text and s1_text != "[SENTENCE ABSENT]" and s2_text != "[SENTENCE ABSENT]":
                            pairs_to_diff.append((s1_text, s2_text, name1, name2))
                        if len(parsed_data_list) == 3:
                            if s2_text != s3_text and s2_text != "[SENTENCE ABSENT]" and s3_text != "[SENTENCE ABSENT]":
                                pairs_to_diff.append((s2_text, s3_text, name2, name3))
                            if s1_text != s3_text and s1_text != "[SENTENCE ABSENT]" and s3_text != "[SENTENCE ABSENT]":
                                pairs_to_diff.append((s1_text, s3_text, name1, name3))
                        
                        unique_diffs_shown_for_sentence = set()
                        for text_a, text_b, n_a, n_b in pairs_to_diff:
                            pair_key = tuple(sorted((n_a, n_b)))
                            if pair_key not in unique_diffs_shown_for_sentence:
                                report_lines.append(f"        Detailed Diff ({n_a} vs {n_b}):")
                                diff = difflib.ndiff(text_a.splitlines(True), text_b.splitlines(True))
                                for line_diff in diff:
                                    report_lines.append(f"          {line_diff.rstrip('\n')}")
                                unique_diffs_shown_for_sentence.add(pair_key)
                        if pairs_to_diff: report_lines.append("        ----")
    return report_lines


# --- Main Execution ---

if __name__ == "__main__":
    print("Starting Bible text comparison tool...")

    # 1. List available files
    available_files = list_available_texts(BASE_DIR)
    if not available_files:
        print("Exiting: No Bible text files found to compare.")
    else:
        # 2. User chooses 2 or 3 files
        selected_configs = choose_files_for_comparison(available_files)
        if not selected_configs:
            print("Exiting: No files selected for comparison.")
        else:
            # 3. Parse selected files
            parsed_data_list = []
            file_names_list = []
            print("\nParsing selected files...")
            for config in selected_configs:
                filepath = config["path"]
                filename_short = config["name"]
                print(f"  Parsing {filename_short} ({os.path.basename(filepath)})...")
                try:
                    data = parse_bible_text_file(filepath)
                    parsed_data_list.append(data)
                    file_names_list.append(filename_short)
                    print(f"    Successfully parsed {filename_short}.")
                except FileNotFoundError:
                    print(f"    ERROR: File not found - {filepath}. This file will be skipped.")
                except Exception as e:
                    print(f"    ERROR parsing {filepath}: {e}. This file will be skipped.")
            
            if len(parsed_data_list) < 2:
                print("\nExiting: Not enough files successfully parsed to perform a meaningful comparison (Need at least 2).")
            else:
                # 4. User chooses books to compare
                selected_books = choose_books_for_comparison(parsed_data_list, file_names_list)
                if not selected_books:
                    print("Exiting: No books selected for comparison.")
                else:
                    print("\n--- Generating Comparison Report ---")
                    # 5. Generate comparison report
                    report_content_lines = compare_parsed_bibles(parsed_data_list, file_names_list, selected_books)

                    # 6. Create 'compared_results' directory
                    if not os.path.exists(OUTPUT_DIR):
                        try:
                            os.makedirs(OUTPUT_DIR)
                            print(f"Created directory: {OUTPUT_DIR}")
                        except OSError as e:
                            print(f"Error creating directory {OUTPUT_DIR}: {e}")
                            # Fallback to current directory if output dir creation fails
                            # OUTPUT_DIR = "." # Or handle error more gracefully

                    # 7. Write report to a new file
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_names_str = "_vs_".join(file_names_list)
                    books_str = "_allbooks" if len(selected_books) == len(set(b for d in parsed_data_list if d for b in d.get('books', {}).keys())) else "_custombooks"
                    
                    output_filename = f"comparison_{file_names_str}{books_str}_{timestamp}.txt"
                    output_filepath = os.path.join(OUTPUT_DIR, output_filename)

                    # Determine if all books displayed to user were selected for "allbooks" string in filename
                    # This requires knowing the list of books that were available for selection.
                    # We can get this by re-evaluating common books if selected_books matches all common books.
                    
                    # For a more accurate books_str, we need the list of books that were *available* for selection.
                    # Let's refine this part. We can pass the canonically_ordered_available_books from choose_books_for_comparison
                    # or re-calculate common books here for the check.
                    # For simplicity now, this check might not be perfectly robust if selected_books was manually constructed
                    # to be identical to all common books without using the '0' option.
                    
                    # Re-evaluate common books for accurate "books_str"
                    all_common_books_in_files = set()
                    if parsed_data_list:
                        # Initialize with books from the first file
                        if parsed_data_list[0] and 'books' in parsed_data_list[0]:
                            all_common_books_in_files.update(parsed_data_list[0]['books'].keys())
                        # Intersect with books from other files
                        for data in parsed_data_list[1:]:
                            if data and 'books' in data:
                                all_common_books_in_files.intersection_update(data['books'].keys())
                    
                    canonically_ordered_common_books = [
                        book for book in CANONICAL_BOOK_NAMES if book in all_common_books_in_files
                    ]

                    if set(selected_books) == set(canonically_ordered_common_books) and len(selected_books) == len(canonically_ordered_common_books):
                        books_str_for_filename = "_allbooks"
                    else:
                        books_str_for_filename = "_custombooks"


                    output_filename = f"comparison_{file_names_str}{books_str_for_filename}_{timestamp}.txt" # Use refined books_str
                    output_filepath = os.path.join(OUTPUT_DIR, output_filename)

                    try:
                        with open(output_filepath, 'w', encoding='utf-8') as f:
                            # Write header
                            f.write("Bible Text Comparison Report\n")
                            f.write(f"Report generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write("Files Compared:\n")
                            for i, name in enumerate(file_names_list):
                                f.write(f"  - {name} ({os.path.basename(selected_configs[i]['path'])})\n")
                            f.write("\nBooks Compared (in canonical order):\n") # Clarified order in header
                            if books_str_for_filename == "_allbooks":
                                f.write("  - All common available books\n")
                                # Optionally list them if desired, already in selected_books
                                # for book in selected_books:
                                #     f.write(f"    - {book}\n")
                            else:
                                for book in selected_books: # selected_books is already canonically ordered
                                    f.write(f"  - {book}\n")
                            f.write("="*40 + "\n\n")
                            
                            # Write report content
                            for line in report_content_lines:
                                f.write(line + "\n")
                        print(f"\nComparison report successfully written to: {output_filepath}")
                    except IOError as e:
                        print(f"Error writing report to file {output_filepath}: {e}")
                    except Exception as e:
                        print(f"An unexpected error occurred while writing the report: {e}")

    print("\n--- Comparison Tool Finished ---")

