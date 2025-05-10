import os

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

BASE_URL = "https://www.jw.org/en/library/bible/bi12/books/" # Changed BASE_URL
OUTPUT_FILENAME = "new_translation_of_the_holy_scriptures_urls.txt" # Changed OUTPUT_FILENAME

def generate_urls():
    urls = []
    # Use the new BASE_URL when generating URLs
    current_base_url = BASE_URL 
    for book, chapters in BIBLE_BOOKS.items():
        for chapter in range(1, chapters + 1):
            urls.append(f"{current_base_url}{book}/{chapter}/")
    return urls

def save_urls_to_file(urls, filename):
    with open(filename, "w") as f:
        for url in urls:
            f.write(url + os.linesep)
    print(f"Generated {len(urls)} URLs and saved to {filename}")

if __name__ == "__main__":
    generated_urls = generate_urls()
    save_urls_to_file(generated_urls, OUTPUT_FILENAME)
