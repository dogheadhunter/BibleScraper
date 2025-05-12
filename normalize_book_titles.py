'''
This script normalizes Bible book titles in text files.

It reads .txt files from a specified input directory, identifies lines
starting with "Book: ", and attempts to replace the found book title with
its canonical name based on a predefined list and a dictionary of aliases.

Normalized content is written to new files in a specified output directory.
Warnings are printed for book titles that cannot be normalized.
'''
import os
import re

# Define the canonical list of Bible book names (66 books)
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

# Define a comprehensive dictionary of aliases for book names
# Keys are various aliases, values are the canonical names
BOOK_NAME_ALIASES = {
    # Genesis
    "gen": "Genesis", "gn": "Genesis", "genesis": "Genesis",
    # Exodus
    "exod": "Exodus", "ex": "Exodus", "exodus": "Exodus",
    # Leviticus
    "lev": "Leviticus", "lv": "Leviticus", "leviticus": "Leviticus",
    # Numbers
    "num": "Numbers", "nm": "Numbers", "numbers": "Numbers",
    # Deuteronomy
    "deut": "Deuteronomy", "dt": "Deuteronomy", "deuteronomy": "Deuteronomy",
    # Joshua
    "josh": "Joshua", "joshua": "Joshua",
    # Judges
    "judg": "Judges", "jdg": "Judges", "judges": "Judges",
    # Ruth
    "ruth": "Ruth", "ru": "Ruth",
    # 1 Samuel
    "1 sam": "1 Samuel", "1sa": "1 Samuel", "1 samuel": "1 Samuel", "first samuel": "1 Samuel",
    # 2 Samuel
    "2 sam": "2 Samuel", "2sa": "2 Samuel", "2 samuel": "2 Samuel", "second samuel": "2 Samuel",
    # 1 Kings
    "1 kgs": "1 Kings", "1ki": "1 Kings", "1 kings": "1 Kings", "first kings": "1 Kings",
    # 2 Kings
    "2 kgs": "2 Kings", "2ki": "2 Kings", "2 kings": "2 Kings", "second kings": "2 Kings",
    # 1 Chronicles
    "1 chron": "1 Chronicles", "1ch": "1 Chronicles", "1 chronicles": "1 Chronicles", "first chronicles": "1 Chronicles",
    # 2 Chronicles
    "2 chron": "2 Chronicles", "2ch": "2 Chronicles", "2 chronicles": "2 Chronicles", "second chronicles": "2 Chronicles",
    # Ezra
    "ezra": "Ezra", "ezr": "Ezra",
    # Nehemiah
    "neh": "Nehemiah", "nehemiah": "Nehemiah",
    # Esther
    "esth": "Esther", "es": "Esther", "esther": "Esther",
    # Job
    "job": "Job", "jb": "Job",
    # Psalms
    "ps": "Psalms", "psa": "Psalms", "psalm": "Psalms", "psalms": "Psalms",
    # Proverbs
    "prov": "Proverbs", "pr": "Proverbs", "proverbs": "Proverbs",
    # Ecclesiastes
    "eccles": "Ecclesiastes", "eccl": "Ecclesiastes", "ecclesiastes": "Ecclesiastes", "qoheleth": "Ecclesiastes",
    # Song of Solomon
    "song of sol": "Song of Solomon", "sos": "Song of Solomon", "song of solomon": "Song of Solomon", "song of songs": "Song of Solomon",
    "the song of solomon": "Song of Solomon", # Added
    # Isaiah
    "isa": "Isaiah", "is": "Isaiah", "isaiah": "Isaiah",
    # Jeremiah
    "jer": "Jeremiah", "je": "Jeremiah", "jeremiah": "Jeremiah",
    # Lamentations
    "lam": "Lamentations", "lamentations": "Lamentations",
    # Ezekiel
    "ezek": "Ezekiel", "eze": "Ezekiel", "ezekiel": "Ezekiel",
    # Daniel
    "dan": "Daniel", "da": "Daniel", "daniel": "Daniel",
    # Hosea
    "hos": "Hosea", "ho": "Hosea", "hosea": "Hosea",
    # Joel
    "joel": "Joel", "jl": "Joel",
    # Amos
    "amos": "Amos", "am": "Amos",
    # Obadiah
    "obad": "Obadiah", "ob": "Obadiah", "obadiah": "Obadiah",
    # Jonah
    "jonah": "Jonah", "jon": "Jonah",
    # Micah
    "mic": "Micah", "micah": "Micah",
    # Nahum
    "nah": "Nahum", "nahum": "Nahum",
    # Habakkuk
    "hab": "Habakkuk", "habakkuk": "Habakkuk",
    # Zephaniah
    "zeph": "Zephaniah", "zep": "Zephaniah", "zephaniah": "Zephaniah",
    # Haggai
    "hag": "Haggai", "haggai": "Haggai",
    # Zechariah
    "zech": "Zechariah", "zec": "Zechariah", "zechariah": "Zechariah",
    # Malachi
    "mal": "Malachi", "malachi": "Malachi",
    # Matthew
    "matt": "Matthew", "mt": "Matthew", "matthew": "Matthew",
    "according to matthew": "Matthew", # Added
    # Mark
    "mark": "Mark", "mk": "Mark", "mrk": "Mark",
    "according to mark": "Mark", # Added
    # Luke
    "luke": "Luke", "lk": "Luke",
    "according to luke": "Luke", # Added
    # John
    "john": "John", "jn": "John", "joh": "John",
    "according to john": "John", # Added
    # Acts
    "acts": "Acts", "act": "Acts",
    "acts of apostles": "Acts", # Added
    # Romans
    "rom": "Romans", "ro": "Romans", "romans": "Romans",
    "to the romans": "Romans", # Added
    # 1 Corinthians
    "1 cor": "1 Corinthians", "1co": "1 Corinthians", "1 corinthians": "1 Corinthians", "first corinthians": "1 Corinthians",
    "the first to the corinthians": "1 Corinthians", # Added
    # 2 Corinthians
    "2 cor": "2 Corinthians", "2co": "2 Corinthians", "2 corinthians": "2 Corinthians", "second corinthians": "2 Corinthians",
    "the second to the corinthians": "2 Corinthians", # Added
    # Galatians
    "gal": "Galatians", "ga": "Galatians", "galatians": "Galatians",
    "to the galatians": "Galatians", # Added
    # Ephesians
    "eph": "Ephesians", "ephes": "Ephesians", "ephesians": "Ephesians",
    "to the ephesians": "Ephesians", # Added
    # Philippians
    "phil": "Philippians", "php": "Philippians", "philippians": "Philippians",
    "to the philippians": "Philippians", # Added
    # Colossians
    "col": "Colossians", "colossians": "Colossians",
    "letter to the colossians": "Colossians", # Added
    # 1 Thessalonians
    "1 thess": "1 Thessalonians", "1th": "1 Thessalonians", "1 thessalonians": "1 Thessalonians", "first thessalonians": "1 Thessalonians",
    "the first to the thessalonians": "1 Thessalonians", # Added
    # 2 Thessalonians
    "2 thess": "2 Thessalonians", "2th": "2 Thessalonians", "2 thessalonians": "2 Thessalonians", "second thessalonians": "2 Thessalonians",
    "the second to the thessalonians": "2 Thessalonians", # Added
    # 1 Timothy
    "1 tim": "1 Timothy", "1ti": "1 Timothy", "1 timothy": "1 Timothy", "first timothy": "1 Timothy",
    "the first to timothy": "1 Timothy", # Added
    # 2 Timothy
    "2 tim": "2 Timothy", "2ti": "2 Timothy", "2 timothy": "2 Timothy", "second timothy": "2 Timothy",
    "the second to timothy": "2 Timothy", # Added
    # Titus
    "titus": "Titus", "ti": "Titus",
    "to titus": "Titus", # Added
    # Philemon
    "philem": "Philemon", "phm": "Philemon", "philemon": "Philemon",
    "to philemon": "Philemon", # Added
    # Hebrews
    "heb": "Hebrews", "hebrews": "Hebrews",
    "to the hebrews": "Hebrews", # Added
    # James
    "james": "James", "jas": "James", "jm": "James",
    "the letter of james": "James", # Added
    # 1 Peter
    "1 pet": "1 Peter", "1pe": "1 Peter", "1 peter": "1 Peter", "first peter": "1 Peter",
    "the first of peter": "1 Peter", # Added
    # 2 Peter
    "2 pet": "2 Peter", "2pe": "2 Peter", "2 peter": "2 Peter", "second peter": "2 Peter",
    "the second of peter": "2 Peter", # Added
    # 1 John
    "1 john": "1 John", "1jn": "1 John", "1 jn": "1 John", "first john": "1 John",
    "the first of john": "1 John", # Added
    # 2 John
    "2 john": "2 John", "2jn": "2 John", "2 jn": "2 John", "second john": "2 John",
    "the second of john": "2 John", # Added
    # 3 John
    "3 john": "3 John", "3jn": "3 John", "3 jn": "3 John", "third john": "3 John",
    "the third of john": "3 John", # Added
    # Jude
    "jude": "Jude", "jud": "Jude",
    "the letter of jude": "Jude", # Added
    # Revelation
    "rev": "Revelation", "re": "Revelation", "revelation": "Revelation", "apocalypse": "Revelation",
    "a revelation to john": "Revelation", # Added
    # Common variations
    "song of sol.": "Song of Solomon",
    "song": "Song of Solomon", # Ambiguous, but often refers to Song of Solomon in context
    "ps.": "Psalms",
    "acts of the apostles": "Acts",
    "revelation of john": "Revelation",
    "letter to the hebrews": "Hebrews",
    "first letter of paul to the corinthians": "1 Corinthians",
    "second letter of paul to the corinthians": "2 Corinthians",
    "the gospel according to matthew": "Matthew",
    "the gospel according to mark": "Mark",
    "the gospel according to luke": "Luke",
    "the gospel according to john": "John",
    "i samuel": "1 Samuel", "ii samuel": "2 Samuel",
    "i kings": "1 Kings", "ii kings": "2 Kings",
    "i chronicles": "1 Chronicles", "ii chronicles": "2 Chronicles",
    "i corinthians": "1 Corinthians", "ii corinthians": "2 Corinthians",
    "i thessalonians": "1 Thessalonians", "ii thessalonians": "2 Thessalonians",
    "i timothy": "1 Timothy", "ii timothy": "2 Timothy",
    "i peter": "1 Peter", "ii peter": "2 Peter",
    "i john": "1 John", "ii john": "2 John", "iii john": "3 John",
    "1st samuel": "1 Samuel", "2nd samuel": "2 Samuel",
    "the first of samuel": "1 Samuel", # Added
    "the second of samuel": "2 Samuel", # Added
    "1st kings": "1 Kings", "2nd kings": "2 Kings",
    "the first of kings": "1 Kings", # Added
    "the second of kings": "2 Kings", # Added
    "1st chronicles": "1 Chronicles", "2nd chronicles": "2 Chronicles",
    "the first of chronicles": "1 Chronicles", # Added
    "the second of chronicles": "2 Chronicles", # Added
    "1st corinthians": "1 Corinthians", "2nd corinthians": "2 Corinthians",
    "1st thessalonians": "1 Thessalonians", "2nd thessalonians": "2 Thessalonians",
    "1st timothy": "1 Timothy", "2nd timothy": "2 Timothy",
    "1st peter": "1 Peter", "2nd peter": "2 Peter",
    "1st john": "1 John", "2nd john": "2 John", "3rd john": "3 John",
}

INPUT_DIR = "c:\\Users\\doghe\\Python Webscraper\\scraped_texts"
OUTPUT_DIR = "c:\\Users\\doghe\\Python Webscraper\\normalized_texts"

def normalize_book_title(title):
    '''Attempts to normalize a book title to its canonical form.'''
    # Preprocess title: lowercase, remove leading/trailing whitespace and punctuation
    processed_title = title.lower().strip(" .:,;")
    
    # Direct match in canonical names (case-insensitive)
    for canonical_name in CANONICAL_BOOK_NAMES:
        if canonical_name.lower() == processed_title:
            return canonical_name
            
    # Match in aliases
    if processed_title in BOOK_NAME_ALIASES:
        return BOOK_NAME_ALIASES[processed_title]
    
    # Try removing "the book of " prefix if present
    if processed_title.startswith("the book of "):
        processed_title_no_prefix = processed_title[len("the book of "):].strip()
        if processed_title_no_prefix in BOOK_NAME_ALIASES:
            return BOOK_NAME_ALIASES[processed_title_no_prefix]
        for canonical_name in CANONICAL_BOOK_NAMES:
            if canonical_name.lower() == processed_title_no_prefix:
                return canonical_name

    return None # Cannot normalize

def process_file(filepath, output_dir):
    '''Reads a file, normalizes book titles, and writes to the output directory.'''
    filename = os.path.basename(filepath)
    output_filepath = os.path.join(output_dir, filename)
    
    processed_lines = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f_in:
            for line_number, line in enumerate(f_in, 1):
                stripped_line = line.strip()
                if stripped_line.startswith("Book: "):
                    original_book_title = stripped_line[len("Book: "):].strip()
                    canonical_title = normalize_book_title(original_book_title)
                    
                    if canonical_title:
                        processed_lines.append(f"Book: {canonical_title}\n")
                    else:
                        processed_lines.append(line) # Keep original if not normalized
                        print(f"Warning: Could not normalize book title '{original_book_title}' in {filename} (line {line_number})")
                else:
                    processed_lines.append(line)
        
        with open(output_filepath, 'w', encoding='utf-8') as f_out:
            f_out.writelines(processed_lines)
        print(f"Successfully processed and normalized '{filename}' -> '{output_filepath}'")

    except FileNotFoundError:
        print(f"Error: File not found - {filepath}")
    except Exception as e:
        print(f"Error processing file {filepath}: {e}")

def main():
    '''Main function to orchestrate the normalization process.'''
    if not os.path.exists(INPUT_DIR):
        print(f"Error: Input directory not found: {INPUT_DIR}")
        return

    if not os.path.exists(OUTPUT_DIR):
        try:
            os.makedirs(OUTPUT_DIR)
            print(f"Created output directory: {OUTPUT_DIR}")
        except OSError as e:
            print(f"Error creating output directory {OUTPUT_DIR}: {e}")
            return
            
    print(f"Starting normalization process...")
    print(f"Input directory: {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")

    found_files = False
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".txt"):
            found_files = True
            filepath = os.path.join(INPUT_DIR, filename)
            print(f"Processing file: {filepath}")
            process_file(filepath, OUTPUT_DIR)
            
    if not found_files:
        print(f"No .txt files found in {INPUT_DIR}")

    print("Normalization process completed.")

if __name__ == "__main__":
    main()
