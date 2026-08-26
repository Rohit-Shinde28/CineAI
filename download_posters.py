import os
import re
import time

import pandas as pd
import requests
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

CSV_PATH = "models/movies_cleaned.csv"
POSTER_FOLDER = "assets/posters"

TMDB_BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


# ============================================================
# LOAD API KEY
# ============================================================

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")


if not TMDB_API_KEY:

    print()
    print("ERROR: TMDB_API_KEY was not found.")
    print()
    print("Make sure your .env file contains:")
    print()
    print("TMDB_API_KEY=your_api_key")
    print()

    exit()


# ============================================================
# CREATE POSTER DIRECTORY
# ============================================================

os.makedirs(
    POSTER_FOLDER,
    exist_ok=True
)


# ============================================================
# LOAD MOVIE DATABASE
# ============================================================

print()
print("Loading movie database...")
print()

movies = pd.read_csv(
    CSV_PATH
)


print(
    f"Found {len(movies)} movies."
)

print()


# ============================================================
# CHECK REQUIRED COLUMN
# ============================================================

if "id" not in movies.columns:

    print(
        "ERROR: 'id' column was not found "
        "in movies_cleaned.csv."
    )

    exit()


if "title" not in movies.columns:

    print(
        "ERROR: 'title' column was not found "
        "in movies_cleaned.csv."
    )

    exit()


# ============================================================
# CREATE HTTP SESSION
# ============================================================

session = requests.Session()

session.headers.update({
    "User-Agent": "CineAI/1.0",
    "Accept": "application/json"
})


# ============================================================
# CREATE SAFE FILE NAME
# ============================================================

def create_filename(title):
    """
    Convert movie title into a safe poster filename.

    Example:

    The Dark Knight
    ->
    the_dark_knight.jpg
    """

    title = str(title).lower()

    # Remove special characters
    title = re.sub(
        r"[^a-z0-9\s]",
        "",
        title
    )

    # Replace spaces with underscores
    title = re.sub(
        r"\s+",
        "_",
        title.strip()
    )

    return title + ".jpg"


# ============================================================
# DOWNLOAD ONE POSTER
# ============================================================

def download_poster(movie_id, title):

    filename = create_filename(title)

    file_path = os.path.join(
        POSTER_FOLDER,
        filename
    )


    # --------------------------------------------------------
    # Skip if poster already exists
    # --------------------------------------------------------

    if os.path.exists(file_path):

        return "exists"


    # --------------------------------------------------------
    # Request movie details from TMDB
    # --------------------------------------------------------

    url = f"{TMDB_BASE_URL}/movie/{movie_id}"

    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US"
    }


    try:

        response = session.get(
            url,
            params=params,
            timeout=(5, 20)
        )


        # ----------------------------------------------------
        # API key invalid
        # ----------------------------------------------------

        if response.status_code == 401:

            print()
            print("ERROR: TMDB API key is invalid.")
            print()

            return "stop"


        # ----------------------------------------------------
        # Rate limit
        # ----------------------------------------------------

        if response.status_code == 429:

            print(
                "TMDB rate limit reached. "
                "Waiting 10 seconds..."
            )

            time.sleep(10)

            return "retry"


        # ----------------------------------------------------
        # Movie not found
        # ----------------------------------------------------

        if response.status_code == 404:

            return "not_found"


        # ----------------------------------------------------
        # Other API error
        # ----------------------------------------------------

        if response.status_code != 200:

            return "error"


        data = response.json()


        # ----------------------------------------------------
        # Get poster path
        # ----------------------------------------------------

        poster_path = data.get(
            "poster_path"
        )


        if not poster_path:

            return "no_poster"


        poster_url = (
            IMAGE_BASE_URL
            + poster_path
        )


        # ----------------------------------------------------
        # Download poster image
        # ----------------------------------------------------

        image_response = session.get(
            poster_url,
            timeout=(5, 30)
        )


        if image_response.status_code != 200:

            return "image_error"


        # ----------------------------------------------------
        # Save image
        # ----------------------------------------------------

        with open(
            file_path,
            "wb"
        ) as file:

            file.write(
                image_response.content
            )


        return "downloaded"


    except requests.exceptions.Timeout:

        return "timeout"


    except requests.exceptions.ConnectionError:

        return "connection_error"


    except Exception as e:

        print(
            f"Unexpected error for {title}: {e}"
        )

        return "error"


# ============================================================
# DOWNLOAD ALL POSTERS
# ============================================================

print("==============================================")
print("          CineAI Poster Downloader")
print("==============================================")
print()

downloaded = 0
already_exists = 0
no_poster = 0
not_found = 0
errors = 0

total_movies = len(movies)


for position, (_, movie) in enumerate(
    movies.iterrows(),
    start=1
):

    movie_id = movie["id"]
    title = str(movie["title"])


    print(
        f"[{position}/{total_movies}] {title}"
    )


    # --------------------------------------------------------
    # Try downloading
    # --------------------------------------------------------

    while True:

        result = download_poster(
            movie_id,
            title
        )


        if result == "retry":

            continue


        break


    # --------------------------------------------------------
    # Handle result
    # --------------------------------------------------------

    if result == "downloaded":

        downloaded += 1

        print(
            "    ✓ Poster downloaded"
        )


    elif result == "exists":

        already_exists += 1

        print(
            "    ✓ Already exists"
        )


    elif result == "no_poster":

        no_poster += 1

        print(
            "    - No poster available"
        )


    elif result == "not_found":

        not_found += 1

        print(
            "    - Movie not found on TMDB"
        )


    elif result == "stop":

        print()
        print(
            "Downloader stopped."
        )

        break


    else:

        errors += 1

        print(
            "    ✗ Download failed"
        )


    # --------------------------------------------------------
    # Small delay to avoid hitting rate limits
    # --------------------------------------------------------

    time.sleep(0.25)


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("==============================================")
print("          DOWNLOAD COMPLETE")
print("==============================================")
print()

print(
    f"Total movies:       {total_movies}"
)

print(
    f"Downloaded:         {downloaded}"
)

print(
    f"Already existed:    {already_exists}"
)

print(
    f"No poster:          {no_poster}"
)

print(
    f"Movie not found:    {not_found}"
)

print(
    f"Errors:             {errors}"
)

print()

print(
    "Posters are saved in:"
)

print(
    POSTER_FOLDER
)

print()