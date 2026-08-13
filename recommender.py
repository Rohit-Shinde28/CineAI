import pandas as pd

# Load cleaned movie dataset
movies = pd.read_csv("models/movies_cleaned.csv")

print("Dataset loaded successfully!")
print(movies.shape)
print(movies.head())
# Combine important movie information
movies["tags"] = (
    movies["overview"].fillna("") + " " +
    movies["genres"].fillna("") + " " +
    movies["keywords"].fillna("") + " " +
    movies["cast"].fillna("") + " " +
    movies["crew"].fillna("")
)

print("\nTags created successfully!")
print(movies[["title", "tags"]].head())

# Convert tags to lowercase
movies["tags"] = movies["tags"].str.lower()

print("\nTags converted to lowercase!")
print(movies[["title", "tags"]].head())
from sklearn.feature_extraction.text import CountVectorizer

# Convert tags into numerical vectors
cv = CountVectorizer(max_features=5000, stop_words="english")

vectors = cv.fit_transform(movies["tags"]).toarray()

print("\nVectors created successfully!")
print("Vector shape:", vectors.shape)

from sklearn.metrics.pairwise import cosine_similarity

# Calculate similarity between movies
similarity = cosine_similarity(vectors)

print("\nSimilarity calculated successfully!")
print("Similarity shape:", similarity.shape)
# Recommendation function
def recommend(movie):
    # Find the movie index
    movie_index = movies[movies["title"].str.lower() == movie.lower()].index[0]

    # Get similarity scores for this movie
    distances = similarity[movie_index]

    # Get the 5 most similar movies
    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    print("\nMovies recommended for:", movie)

    for i in movie_list:
        print(movies.iloc[i[0]].title)

        recommend("Avatar")

        # Recommendation function
# Recommendation function
def recommend(movie):
    movie_matches = movies[
        movies["title"].str.lower() == movie.lower()
    ]

    if movie_matches.empty:
        return []

    movie_index = movie_matches.index[0]
    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommendations = []

    for i in movie_list:
        recommendations.append(movies.iloc[i[0]]["title"])

    return recommendations

recommendations = recommend("Avatar")

print("\nRecommended Movies:")
for movie in recommendations:
    print("-", movie)