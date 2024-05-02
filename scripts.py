import csv
import re
from base.models import Anime  # Assuming this is your model
import argparse

def clean_synopsis(synopsis):
    """Removes content within square brackets `[]` and parentheses `()`.

    Args:
        synopsis (str): The synopsis string containing potentially bracketed content.

    Returns:
        str: The cleaned synopsis with bracketed content removed.
    """
    pattern = r"\[(.*?)\]|\((.*?)\)"  # Matches any characters inside brackets
    return re.sub(pattern, "", synopsis)

def clean_genre(genre):
    """Cleans up the genre string, removing unnecessary characters and splitting by commas.

    Args:
        genre (str): The raw genre string.

    Returns:
        list: A list of cleaned genre strings.
    """
    genre = genre.strip('[]')  # Remove leading/trailing brackets
    genre = genre.replace("'", "").strip()  # Remove quotes and extra spaces
    return genre.split(', ')  # Split by comma and whitespace

def extract_release_year(aired):
    """Attempts to extract the release year from the 'aired' string.

    Handles different formats like "YYYY", "Season YYYY", or the entire string
    if parsing fails.

    Args:
        aired (str): The string containing aired information.

    Returns:
        str: The extracted release year (if possible), or the original string.
    """
    if len(aired) <= 9:
        return aired[:4]  # Just the first 4 characters for YYYY format
    try:
        parts = aired.split()
        return parts[2]  # Assuming year is the third word (e.g., "Season 2023")
    except:
        return aired  # Return original string if parsing fails

def is_float(element) -> bool:
    """Checks if a value can be converted to a float, handling potential errors.

    Args:
        element (any): The value to be checked.

    Returns:
        bool: True if the value can be converted to a float, False otherwise.
    """
    if element is None:
        return False
    try:
        float(element)
        return True
    except ValueError:
        return False

def insert_data_from_csv(csv_file, reset=False):
    """Inserts data from a CSV file into your Anime model (assuming it's defined).

    Includes options to reset existing data and error handling for common issues.

    Args:
        csv_file (str): The path to the CSV file.
        reset (bool, optional): Whether to reset existing data before insertion.
            Defaults to False.
    """

    if reset:
        Anime.objects.all().delete()  # Reset existing data if needed

    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                cleaned_genre = clean_genre(row['genre'])
                release_year = extract_release_year(row['aired'])
                cleaned_synopsis = clean_synopsis(row['synopsis'])

                # Handle potential errors during data conversion and insertion:
                try:
                    episodes = int(float(row['episodes'])) if is_float(row['episodes']) else None
                    popularity = int(float(row['popularity'])) if is_float(row['popularity']) else None
                    score = float(row['score']) if is_float(row['score']) else None
                except ValueError:
                    print(f"Error converting data for row with UID: {row['uid']}")
                    continue  # Skip to next row on conversion error

                anime = Anime(
                    id=row['uid'],
                    title=row['title'],
                    synopsis=cleaned_synopsis,
                    genre=cleaned_genre,
                    aired=release_year,
                    episodes=episodes,
                    popularity=popularity,
                    ranked=int(float(row['ranked'])) if is_float(row['ranked']) else None,
                    score=score,
                    img_url=row['img_url']
                )
                anime.save()
                print(f"{row['uid']} - {row['title']} inserted successfully")

    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found")

insert_data_from_csv('datasets/MyAnimeList/animes.csv', reset=True)
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('integers', metavar='N', type=int, nargs='+',
                    help='an integer for the accumulator')
parser.add_argument('--sum', dest='accumulate', action='store_const',
                    const=sum, default=max,
                    help='sum the integers (default: find the max)')

def main():
    csv_file_path = "datasets/MyAnimeList/animes.csv"
    reset = True

    insert_data_from_csv(csv_file_path, reset)

if __name__ == '__main__':
    main()

