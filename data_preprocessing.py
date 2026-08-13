import pandas as pd

# Load datasets
movies = pd.read_csv("data/tmdb_5000_movies.csv")
credits = pd.read_csv("data/tmdb_5000_credits.csv")

# Display basic information
print("Movies Dataset:")
print(movies.shape)
print(movies.columns.tolist())

print("\nCredits Dataset:")
print(credits.shape)
print(credits.columns.tolist())

print("\nMissing values in Movies Dataset:")
print(movies.isnull().sum())

print("\nMissing values in Credits Dataset:")
print(credits.isnull().sum())
print("\nDuplicate movies:", movies.duplicated().sum())
print("Duplicate credits:", credits.duplicated().sum())
# Merge movies and credits datasets
movies = movies.merge(credits, left_on="id", right_on="movie_id")

print("\nMerged Dataset:")
print(movies.shape)
print(movies.columns.tolist())

# Select useful columns for recommendation system
movies = movies[
    [
        "id",
        "title_x",
        "overview",
        "genres",
        "keywords",
        "cast",
        "crew"
    ]
]

# Rename title_x to title
movies.rename(columns={"title_x": "title"}, inplace=True)

print("\nSelected Dataset:")
print(movies.shape)
print(movies.columns.tolist())
# Check missing values in selected columns
print("\nMissing values after selecting columns:")
print(movies.isnull().sum())
# Remove movies with missing overview
movies.dropna(subset=["overview"], inplace=True)

print("\nDataset after removing missing overviews:")
print(movies.shape)

print("\nMissing values after cleaning:")
print(movies.isnull().sum())
# Save cleaned dataset
movies.to_csv("models/movies_cleaned.csv", index=False)

print("\nCleaned dataset saved successfully!")