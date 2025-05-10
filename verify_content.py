import re
import os

BIBLE_CONTENT_FILE = "bible_text_content.txt"

# Canonical list of Bible books and their chapter counts
# Keys should be lowercase and hyphenated for multi-word names (e.g., "1-samuel", "song-of-solomon")
BIBLE_BOOKS = {
    "genesis": 50, "exodus": 40, "leviticus": 27, "numbers": 36, "deuteronomy": 34,
    "joshua": 24, "judges": 21, "ruth": 4, "1-samuel": 31, "2-samuel": 24,
    "1-kings": 22, "2-kings": 25, "1-chronicles": 29, "2-chronicles": 36, "ezra": 10,
    "nehemiah": 13, "esther": 10, "job": 42, "psalms": 150, "proverbs": 31,
    "ecclesiastes": 12, "song-of-solomon": 8, "isaiah": 66, "jeremiah": 52,
    "lamentations": 5, "ezekiel": 48, "daniel": 12, "hosea": 14, "joel": 3, "amos": 9,
    "obadiah": 1, "jonah": 4, "micah": 7, "nahum": 3, "habakkuk": 3, "zephaniah": 3,
    "haggai": 2, "zechariah": 14, "malachi": 4,
    "matthew": 28, "mark": 16, "luke": 24, "john": 21, "acts": 28, "romans": 16,
    "1-corinthians": 16, "2-corinthians": 13, "galatians": 6, "ephesians": 6,
    "philippians": 4, "colossians": 4, "1-thessalonians": 5, "2-thessalonians": 3,
    "1-timothy": 6, "2-timothy": 4, "titus": 3, "philemon": 1, "hebrews": 13, "james": 5,
    "1-peter": 5, "2-peter": 3, "1-john": 5, "2-john": 1, "3-john": 1, "jude": 1,
    "revelation": 22
}

TITLE_TO_KEY_MAP = {
    "the first of samuel": "1-samuel",
    "the second of samuel": "2-samuel",
    "the first of kings": "1-kings",
    "the second of kings": "2-kings",
    "the first of chronicles": "1-chronicles",
    "the second of chronicles": "2-chronicles",
    "psalm": "psalms",
    "the song of solomon": "song-of-solomon",
    "according to matthew": "matthew",
    "according to mark": "mark",
    "according to luke": "luke",
    "according to john": "john",
    "acts of apostles": "acts",
    "to the romans": "romans",
    "the first to the corinthians": "1-corinthians",
    "the second to the corinthians": "2-corinthians",
    "to the galatians": "galatians",
    "to the ephesians": "ephesians",
    "to the philippians": "philippians",
    "letter to the colossians": "colossians",
    "the first to the thessalonians": "1-thessalonians",
    "the second to the thessalonians": "2-thessalonians",
    "the first to timothy": "1-timothy",
    "the second to timothy": "2-timothy",
    "to titus": "titus",
    "to philemon": "philemon",
    "to the hebrews": "hebrews",
    "the letter of james": "james",
    "the first of peter": "1-peter",
    "the second of peter": "2-peter",
    "the first of john": "1-john",
    "the second of john": "2-john",
    "the third of john": "3-john",
    "the letter of jude": "jude",
    "a revelation to john": "revelation"
    # Add other variations if encountered
}

def parse_bible_content(file_path):
    parsed_data = {}
    current_book_key = None
    
    # Regex to find "Book: BookName"
    book_regex = re.compile(r"^Book: (.+)$")
    # Regex to find "Chapter:StartVerse-EndVerse"
    # e.g., "1:1-25", "10:1-19"
    citation_regex = re.compile(r"^(\d+):(\d+)-(\d+)$")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                book_match = book_regex.match(line)
                if book_match:
                    book_name_from_file = book_match.group(1).strip()
                    # Normalize to match BIBLE_BOOKS keys
                    lower_book_name = book_name_from_file.lower()
                    
                    potential_key = TITLE_TO_KEY_MAP.get(lower_book_name)
                    
                    if not potential_key: # If not in map, try direct normalization
                        potential_key = lower_book_name.replace(" ", "-")
                    
                    if potential_key in BIBLE_BOOKS:
                        current_book_key = potential_key
                        if current_book_key not in parsed_data:
                            parsed_data[current_book_key] = {}
                    else:
                        print(f"WARNING (line {line_num}): Found book title '{book_name_from_file}' in file, but it's not in the expected BIBLE_BOOKS list. This book's chapters will be ignored.")
                        current_book_key = None # Reset so chapters aren't wrongly assigned
                    continue

                if current_book_key: # Only process citations if we are "inside" a known book
                    citation_match = citation_regex.match(line)
                    if citation_match:
                        chapter_num_str = citation_match.group(1)
                        start_verse_str = citation_match.group(2)
                        end_verse_str = citation_match.group(3)
                        
                        try:
                            chapter_num = int(chapter_num_str)
                            # Store the full citation string for later validation
                            parsed_data[current_book_key][chapter_num] = f"{chapter_num_str}:{start_verse_str}-{end_verse_str}"
                        except ValueError:
                            print(f"WARNING (line {line_num}): Invalid chapter number '{chapter_num_str}' for book '{current_book_key}'. Citation: '{line}'")
                        continue
    
    except FileNotFoundError:
        print(f"ERROR: File not found at {file_path}")
        return None
    
    return parsed_data

def verify_content():
    print(f"Starting verification of {BIBLE_CONTENT_FILE}...")
    parsed_content = parse_bible_content(BIBLE_CONTENT_FILE)

    if parsed_content is None:
        return

    all_ok = True

    # Check for expected books and chapters
    for book_key, expected_total_chapters in BIBLE_BOOKS.items():
        book_name_display = book_key.replace("-", " ").title() # For user-friendly printing

        if book_key not in parsed_content:
            print(f"ERROR: Book '{book_name_display}' is MISSING from {BIBLE_CONTENT_FILE}.")
            all_ok = False
            continue # Skip chapter checks for this missing book

        found_chapters_data = parsed_content[book_key]
        
        for expected_chapter_num in range(1, expected_total_chapters + 1):
            if expected_chapter_num not in found_chapters_data:
                print(f"ERROR: Book '{book_name_display}', Chapter {expected_chapter_num} is MISSING.")
                all_ok = False
            else:
                # Validate the citation format for the found chapter
                citation = found_chapters_data[expected_chapter_num]
                match_citation = re.match(r"^(\d+):(\d+)-(\d+)$", citation)
                if not match_citation:
                    print(f"ERROR: Book '{book_name_display}', Chapter {expected_chapter_num} has an INVALID citation format: '{citation}'.")
                    all_ok = False
                else:
                    cite_chap = int(match_citation.group(1))
                    cite_start_verse = int(match_citation.group(2))
                    cite_end_verse = int(match_citation.group(3))

                    if cite_chap != expected_chapter_num:
                        print(f"ERROR: Book '{book_name_display}', Chapter {expected_chapter_num}: Citation chapter number ({cite_chap}) does not match expected chapter number. Citation: '{citation}'.")
                        all_ok = False
                    if cite_start_verse < 1: # Verses usually start at 1
                        print(f"WARNING: Book '{book_name_display}', Chapter {expected_chapter_num}: Citation '{citation}' has a start verse ({cite_start_verse}) less than 1.")
                        # Not necessarily an error for all_ok, but a warning.
                    if cite_end_verse < cite_start_verse:
                         print(f"ERROR: Book '{book_name_display}', Chapter {expected_chapter_num}: Citation '{citation}' has an end verse ({cite_end_verse}) less than its start verse ({cite_start_verse}).")
                         all_ok = False
        
        # Check for extra chapters found in the file for this book
        expected_chapter_nums = set(range(1, expected_total_chapters + 1))
        found_chapter_nums = set(found_chapters_data.keys())
        extra_chapters = found_chapter_nums - expected_chapter_nums
        if extra_chapters:
            print(f"WARNING: Book '{book_name_display}' has EXTRA chapters in the file not defined in BIBLE_BOOKS: {sorted(list(extra_chapters))}.")
            # This is a warning, might not set all_ok to False depending on strictness

    # Check for extra books found in the file but not in BIBLE_BOOKS
    expected_book_keys = set(BIBLE_BOOKS.keys())
    found_book_keys = set(parsed_content.keys())
    extra_books = found_book_keys - expected_book_keys
    if extra_books:
        for extra_book_key in extra_books:
            # Attempt to get the original display name if it was stored, otherwise use key
            # This part is tricky as we only stored known keys.
            # The warning during parsing already covers unknown book titles from file.
            # This check is more about keys in parsed_data that don't map to BIBLE_BOOKS.
            # (which shouldn't happen with current parsing logic if it only adds known keys)
            print(f"INFO: Data for an unexpected book key '{extra_book_key}' was parsed. This might indicate an issue with book name normalization or an unexpected book in the file not caught by earlier warnings.")


    if all_ok:
        print(f"\nVerification COMPLETE. All expected books, chapters, and verse citations appear to be present and correctly formatted in {BIBLE_CONTENT_FILE}.")
    else:
        print(f"\nVerification COMPLETE. ISSUES FOUND. Please review the messages above.")

if __name__ == "__main__":
    verify_content()
