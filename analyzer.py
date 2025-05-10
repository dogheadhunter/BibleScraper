'''
Script to analyze the content of bible_text_content.txt.
Can count letter frequencies or occurrences of specified names.
'''
import re
from collections import Counter

BIBLE_CONTENT_FILE = "bible_text_content.txt"


def read_text_content(file_path):
    '''Reads the content of the specified file.'''
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None

def clean_text_for_analysis(text):
    '''Removes verse numbers and other non-alphabetic content for better analysis.'''
    # Remove verse numbers like "1:1-10", "10:1-19", etc.
    text = re.sub(r"\n\n\d+:\d+-\d+\n\n", " ", text) 
    # Remove book titles that might be at the start of the file or change
    text = re.sub(r"^Book: [A-Za-z ]+\n\n", " ", text, flags=re.MULTILINE)
    # Keep only alphabetic characters and spaces, convert to lowercase
    text = re.sub(r"[^a-zA-Z\s]", "", text).lower()
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

def count_letter_frequency(text):
    '''Counts the frequency of each letter in the text.'''
    cleaned_text = re.sub(r"[^a-zA-Z]", "", text).lower()
    return Counter(cleaned_text)

def count_name_occurrences(text, names_to_count):
    '''Counts occurrences of a list of names in the text (case-insensitive).'''
    # Clean text for name counting: remove non-alphanumeric, normalize space, lowercase
    # This is a simpler cleaning than for letter frequency, as we need to preserve words.
    processed_text = re.sub(r"[^a-zA-Z0-9\s]", "", text).lower()
    words = processed_text.split()
    
    name_counts = Counter()
    for name in names_to_count:
        lower_name = name.lower()
        # Simple word matching. For more complex scenarios (e.g., "David's"), more advanced NLP might be needed.
        name_counts[name] = words.count(lower_name) 
    return name_counts

if __name__ == "__main__":
    content = read_text_content(BIBLE_CONTENT_FILE)
    if content:
        analysis_type = input("Choose analysis type (1 for letters, 2 for names): ")

        if analysis_type == '1':
            # Clean text specifically for letter frequency (remove all non-alpha)
            text_for_letters = clean_text_for_analysis(content) # Use a more aggressive clean for letters
            letter_counts = count_letter_frequency(text_for_letters)
            print("\nLetter Frequencies:")
            for letter, count in sorted(letter_counts.items()):
                print(f"{letter}: {count}")
        
        elif analysis_type == '2':
            # For name counting, we use the raw content and let the function handle specific cleaning.
            names_input = input("Enter names to count, separated by commas (e.g., David, Solomon, Jehovah): ")
            if not names_input.strip():
                print("No names provided. Skipping name count.")
            else:
                names = [name.strip() for name in names_input.split(',') if name.strip()]
                if not names: # Handles cases like input being just "," or ", ,"
                    print("No valid names provided after parsing. Skipping name count.")
                else:
                    print(f"\nCounting occurrences for names: {names}")
                    name_counts = count_name_occurrences(content, names)
                    print("\nName Occurrences:")
                    for name, count in name_counts.items():
                        print(f"{name}: {count}")
        else:
            print("Invalid choice. Please run again and select 1 or 2.")
