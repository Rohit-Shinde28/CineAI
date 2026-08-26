import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


# ============================================================
# SEARCH MOVIE
# ============================================================

def search_movie(movie_name):
    """Search for a movie on TMDB."""

    if not TMDB_API_KEY:
        print("TMDB API key not found.")
        return None

    url = f"{BASE_URL}/search/movie"

    params = {
        "api_key": TMDB_API_KEY,
        "query": movie_name,
        "language": "en-US"
    }

    for attempt in range(3):

        try:

            response = requests.get(
                url,
                params=params,
                timeout=15
            )

            response.raise_for_status()

            data = response.json()

            results = data.get("results", [])

            if not results:
                return None

            return results[0]

        except requests.exceptions.RequestException as e:

            print(
                f"TMDB search failed "
                f"(attempt {attempt + 1}/3): {e}"
            )

            if attempt < 2:
                time.sleep(1)

    return None


# ============================================================
# GET MOVIE DETAILS
# ============================================================

def get_movie_details(movie_id):
    """Get complete movie details from TMDB."""

    if not TMDB_API_KEY:
        return None

    url = f"{BASE_URL}/movie/{movie_id}"

    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US"
    }

    for attempt in range(3):

        try:

            response = requests.get(
                url,
                params=params,
                timeout=15
            )

            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:

            print(
                f"TMDB details failed "
                f"(attempt {attempt + 1}/3): {e}"
            )

            if attempt < 2:
                time.sleep(1)

    return None


# ============================================================
# GET POSTER BY MOVIE NAME
# ============================================================

def get_movie_poster(movie_name):
    """Get movie poster using movie title."""

    movie = search_movie(movie_name)

    if movie and movie.get("poster_path"):

        return (
            IMAGE_BASE_URL
            + movie["poster_path"]
        )

    return None


# ============================================================
# GET POSTER BY TMDB ID
# ============================================================

def get_movie_poster_by_id(movie_id):
    """Get movie poster directly using TMDB movie ID."""

    if not TMDB_API_KEY:
        return None

    url = f"{BASE_URL}/movie/{movie_id}"

    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US"
    }

    for attempt in range(3):

        try:

            response = requests.get(
                url,
                params=params,
                timeout=15
            )

            response.raise_for_status()

            data = response.json()

            poster_path = data.get("poster_path")

            if poster_path:

                return (
                    IMAGE_BASE_URL
                    + poster_path
                )

            return None

        except requests.exceptions.RequestException as e:

            print(
                f"TMDB poster failed "
                f"(attempt {attempt + 1}/3): {e}"
            )

            if attempt < 2:
                time.sleep(1)

    return None


# ============================================================
# GET TRAILER
# ============================================================

def get_movie_trailer(movie_id):
    """Get official YouTube trailer."""

    if not TMDB_API_KEY:
        return None

    url = f"{BASE_URL}/movie/{movie_id}/videos"

    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US"
    }

    for attempt in range(3):

        try:

            response = requests.get(
                url,
                params=params,
                timeout=15
            )

            response.raise_for_status()

            videos = response.json().get(
                "results",
                []
            )

            # Official trailer first
            for video in videos:

                if (
                    video.get("site") == "YouTube"
                    and video.get("type") == "Trailer"
                    and video.get("official") is True
                ):

                    return (
                        "https://www.youtube.com/watch?v="
                        + video["key"]
                    )

            # Any YouTube trailer
            for video in videos:

                if (
                    video.get("site") == "YouTube"
                    and video.get("type") == "Trailer"
                ):

                    return (
                        "https://www.youtube.com/watch?v="
                        + video["key"]
                    )

            return None

        except requests.exceptions.RequestException as e:

            print(
                f"TMDB trailer failed "
                f"(attempt {attempt + 1}/3): {e}"
            )

            if attempt < 2:
                time.sleep(1)

    return None


# ============================================================
# WATCH PROVIDERS
# ============================================================

def get_watch_providers(movie_id, country="IN"):
    """Get legal streaming/rental providers."""

    if not TMDB_API_KEY:
        return None

    url = (
        f"{BASE_URL}/movie/"
        f"{movie_id}/watch/providers"
    )

    params = {
        "api_key": TMDB_API_KEY
    }

    for attempt in range(3):

        try:

            response = requests.get(
                url,
                params=params,
                timeout=15
            )

            response.raise_for_status()

            data = response.json()

            return (
                data
                .get("results", {})
                .get(country)
            )

        except requests.exceptions.RequestException as e:

            print(
                f"TMDB providers failed "
                f"(attempt {attempt + 1}/3): {e}"
            )

            if attempt < 2:
                time.sleep(1)

    return None