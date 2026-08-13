import os
import requests
from dotenv import load_dotenv

load_dotenv()

# TMDB configuration
BASE_URL = "https://api.themoviedb.org/3"
API_KEY = os.getenv("TMDB_API_KEY")


def _get(endpoint, params=None):
    """
    Common function for making TMDB API requests.
    """
    if not API_KEY:
        raise ValueError(
            "TMDB_API_KEY is missing. Add it to your .env file."
        )

    if params is None:
        params = {}

    params["api_key"] = API_KEY

    try:
        response = requests.get(
            f"{BASE_URL}{endpoint}",
            params=params,
            timeout=10
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:
        print(f"TMDB API error: {e}")
        return None


def search_movie(movie_name):
    """
    Search for a movie by title.
    Returns the first matching movie.
    """

    data = _get(
        "/search/movie",
        {
            "query": movie_name,
            "language": "en-US",
            "include_adult": False
        }
    )

    if not data:
        return None

    results = data.get("results", [])

    if not results:
        return None

    return results[0]


def get_movie_details(movie_id):
    """
    Get complete details for a movie.
    """

    data = _get(
        f"/movie/{movie_id}",
        {
            "language": "en-US"
        }
    )

    if not data:
        return {}

    return data


def get_movie_trailer(movie_id):
    """
    Get the YouTube trailer URL for a movie.
    """

    data = _get(
        f"/movie/{movie_id}/videos",
        {
            "language": "en-US"
        }
    )

    if not data:
        return None

    videos = data.get("results", [])

    # First look for an official YouTube trailer
    for video in videos:
        if (
            video.get("site") == "YouTube"
            and video.get("type") == "Trailer"
            and video.get("official") is True
        ):
            return f"https://www.youtube.com/watch?v={video['key']}"

    # If official trailer isn't available,
    # look for any YouTube trailer
    for video in videos:
        if (
            video.get("site") == "YouTube"
            and video.get("type") == "Trailer"
        ):
            return f"https://www.youtube.com/watch?v={video['key']}"

    # Last fallback: any YouTube video
    for video in videos:
        if video.get("site") == "YouTube":
            return f"https://www.youtube.com/watch?v={video['key']}"

    return None


def get_watch_providers(movie_id, country="IN"):
    """
    Get legal streaming, rental and purchase providers.
    """

    data = _get(
        f"/movie/{movie_id}/watch/providers"
    )

    if not data:
        return None

    results = data.get("results", {})

    return results.get(country)