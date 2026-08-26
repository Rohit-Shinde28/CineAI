import pandas as pd
import ast
import os
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = "models/movies_cleaned.csv"
POSTER_FOLDER = "assets/posters"


# ============================================================
# LOAD MOVIE DATABASE
# ============================================================

movies = pd.read_csv(DATA_PATH)

print("Dataset loaded successfully!")
print("Shape:", movies.shape)


# ============================================================
# CLEAN DATA
# ============================================================

required_columns = [
    "id",
    "title",
    "overview",
    "genres",
    "keywords",
    "cast",
    "crew"
]

for column in required_columns:

    if column not in movies.columns:

        raise ValueError(
            f"Missing required column: {column}"
        )


movies["title"] = movies["title"].fillna("")
movies["overview"] = movies["overview"].fillna("")
movies["genres"] = movies["genres"].fillna("")
movies["keywords"] = movies["keywords"].fillna("")
movies["cast"] = movies["cast"].fillna("")
movies["crew"] = movies["crew"].fillna("")


# ============================================================
# CONVERT JSON DATA TO TEXT
# ============================================================

def convert_to_text(value):

    try:

        data = ast.literal_eval(value)

        if isinstance(data, list):

            result = []

            for item in data:

                if isinstance(item, dict):

                    if "name" in item:

                        result.append(
                            str(item["name"])
                        )

                else:

                    result.append(
                        str(item)
                    )

            return " ".join(result)

        return str(value)

    except (ValueError, SyntaxError, TypeError):

        return str(value)


# ============================================================
# CONVERT JSON DATA TO LIST
# ============================================================

def convert_to_list(value):
    """Return the 'name' fields of a JSON column as a list."""

    try:

        data = ast.literal_eval(value)

        if isinstance(data, list):

            result = []

            for item in data:

                if isinstance(item, dict):

                    if "name" in item:

                        result.append(
                            str(item["name"])
                        )

                else:

                    result.append(
                        str(item)
                    )

            return result

        return []

    except (ValueError, SyntaxError, TypeError):

        return []


# ============================================================
# EXTRACT DIRECTOR
# ============================================================

def get_director(value):

    try:

        data = ast.literal_eval(value)

        if isinstance(data, list):

            for person in data:

                if (
                    isinstance(person, dict)
                    and person.get("job") == "Director"
                ):

                    return str(
                        person.get("name", "")
                    )

        return ""

    except (ValueError, SyntaxError, TypeError):

        return ""


# ============================================================
# CREATE TEXT FEATURES
# ============================================================

movies["genres_text"] = movies["genres"].apply(
    convert_to_text
)

movies["keywords_text"] = movies["keywords"].apply(
    convert_to_text
)

movies["cast_text"] = movies["cast"].apply(
    convert_to_text
)

movies["director"] = movies["crew"].apply(
    get_director
)


# ============================================================
# CREATE TAGS
# ============================================================

movies["tags"] = (
    movies["overview"].fillna("")
    + " "
    + movies["genres_text"].fillna("")
    + " "
    + movies["keywords_text"].fillna("")
    + " "
    + movies["cast_text"].fillna("")
    + " "
    + movies["director"].fillna("")
)


movies["tags"] = movies["tags"].str.lower()

print("Tags created successfully!")


# ============================================================
# CREATE TF-IDF VECTORS
# ============================================================

vectorizer = TfidfVectorizer(
    max_features=5000,
    stop_words="english"
)

vectors = vectorizer.fit_transform(
    movies["tags"]
)

print("Vectors created successfully!")

print(
    "Vector shape:",
    vectors.shape
)


# ============================================================
# COSINE SIMILARITY
# ============================================================

similarity = cosine_similarity(vectors)

print("Similarity calculated successfully!")

print(
    "Similarity shape:",
    similarity.shape
)


# ============================================================
# CREATE POSTER FILENAME
# ============================================================

def create_poster_filename(title):

    filename = str(title).lower()

    filename = re.sub(
        r"[^a-z0-9\s]",
        "",
        filename
    )

    filename = re.sub(
        r"\s+",
        "_",
        filename.strip()
    )

    return filename


# ============================================================
# GET POSTER PATH
# ============================================================

def get_poster_path(movie_title):

    if not movie_title:

        return None

    filename = create_poster_filename(
        movie_title
    )

    extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    ]

    for extension in extensions:

        path = os.path.join(
            POSTER_FOLDER,
            filename + extension
        )

        if os.path.exists(path):

            return path

    return None


# ============================================================
# FIND MOVIE INDEX
# ============================================================

def find_movie_index(movie_name):

    if not movie_name:

        return None

    movie_name = movie_name.strip().lower()


    # Exact match

    exact_match = movies[
        movies["title"]
        .str.lower()
        == movie_name
    ]

    if not exact_match.empty:

        return exact_match.index[0]


    # Partial match

    partial_match = movies[
        movies["title"]
        .str.lower()
        .str.contains(
            movie_name,
            na=False,
            regex=False
        )
    ]

    if partial_match.empty:

        return None

    return partial_match.index[0]


# ============================================================
# RECOMMEND MOVIES
# ============================================================

def recommend(
    movie_name,
    number_of_movies=5
):

    index = find_movie_index(
        movie_name
    )

    if index is None:

        return []


    distances = similarity[index]


    movie_list = sorted(
        list(
            enumerate(distances)
        ),
        reverse=True,
        key=lambda x: x[1]
    )


    recommendations = []


    for movie_index, score in movie_list:

        if movie_index == index:

            continue


        movie = movies.iloc[
            movie_index
        ]

        title = movie["title"]


        if title in [
            item["title"]
            for item in recommendations
        ]:

            continue


        recommendations.append({

            "id": int(
                movie["id"]
            ),

            "title": title,

            "overview": movie["overview"],

            "genres": movie["genres_text"],

            "director": movie["director"],

            "score": round(
                float(score),
                3
            ),

            "poster": get_poster_path(
                title
            )

        })


        if len(recommendations) >= number_of_movies:

            break


    return recommendations


# ============================================================
# GET MOVIE DETAILS
# ============================================================

def get_movie(movie_name):

    index = find_movie_index(
        movie_name
    )

    if index is None:

        return None

    movie = movies.iloc[index]


    return {

        "id": int(
            movie["id"]
        ),

        "title": movie["title"],

        "overview": movie["overview"],

        "genres": movie["genres_text"],

        "keywords": movie["keywords_text"],

        "cast": movie["cast_text"],

        "director": movie["director"],

        "poster": get_poster_path(
            movie["title"]
        )

    }


# ============================================================
# GET MOVIE BY TMDB ID
# ============================================================

def get_movie_by_id(movie_id):
    """Look up one movie using its TMDB id.

    The id is the unique identifier, so this returns the exact
    movie that was clicked even when two titles are identical.
    """

    try:

        movie_id = int(movie_id)

    except (TypeError, ValueError):

        return None


    match = movies[
        movies["id"] == movie_id
    ]

    if match.empty:

        return None


    movie = match.iloc[0]


    return {

        "id": int(
            movie["id"]
        ),

        "title": movie["title"],

        "overview": movie["overview"],

        "genres": movie["genres_text"],

        "genres_list": convert_to_list(
            movie["genres"]
        ),

        "cast": movie["cast_text"],

        "cast_list": convert_to_list(
            movie["cast"]
        ),

        "director": movie["director"],

        "poster": get_poster_path(
            movie["title"]
        )

    }


# ============================================================
# GET MOVIES BY GENRE
# ============================================================

def get_movies_by_genre(
    genre,
    number_of_movies=10
):

    if not genre:

        return []


    genre = genre.strip().lower()


    result = movies[
        movies["genres_text"]
        .str.lower()
        .str.contains(
            genre,
            na=False,
            regex=False
        )
    ]


    recommendations = []


    for _, movie in result.head(
        number_of_movies
    ).iterrows():

        recommendations.append({

            "id": int(
                movie["id"]
            ),

            "title": movie["title"],

            "overview": movie["overview"],

            "genres": movie["genres_text"],

            "director": movie["director"],

            "poster": get_poster_path(
                movie["title"]
            )

        })


    return recommendations


# ============================================================
# GET ALL GENRES
# ============================================================

def get_all_genres():

    genres = set()


    for value in movies["genres_text"]:

        if not value:

            continue


        for genre in value.split(","):

            genre = genre.strip()

            if genre:

                genres.add(
                    genre
                )


    return sorted(
        list(genres)
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_movie = "Avatar"


    print()
    print(
        "Movies recommended for:",
        test_movie
    )

    print(
        "--------------------------------"
    )


    results = recommend(
        test_movie,
        number_of_movies=5
    )


    for movie in results:

        print(
            "-",
            movie["title"]
        )

        print(
            "  Poster:",
            movie["poster"]
        )

        print(
            "  Score:",
            movie["score"]
        )

        print()