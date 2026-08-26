import streamlit as st

import movie_details

from recommender import (
    recommend,
    get_movie,
    get_movies_by_genre
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CineAI",
    page_icon="🎬",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 48px;
        font-weight: 800;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 18px;
        margin-bottom: 30px;
    }

    .section-title {
        font-size: 30px;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 20px;
    }

    .movie-title {
        font-size: 17px;
        font-weight: 700;
        margin-top: 8px;
        margin-bottom: 5px;
    }

    .movie-score {
        font-size: 13px;
        color: #777;
    }

    .movie-director {
        font-size: 13px;
        color: #777;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🎬 CineAI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-powered Movie Recommendation System'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# PAGE ROUTING
# ============================================================

if "page" not in st.session_state:

    st.session_state["page"] = "home"


# Show the details page instead of the home page
# when a movie card has been clicked.

if st.session_state["page"] == "details":

    movie_details.render()

    st.stop()


# ============================================================
# OPEN A MOVIE DETAILS PAGE
# ============================================================

def open_details(
    movie_id,
    score=None,
    origin="Recommendations"
):
    """Remember which movie was clicked, then switch pages.

    The TMDB id is stored, never the title, so the details
    page always loads the exact movie that was clicked.

    "origin" is only used to label the Back button, so the
    user returns to the list they actually came from.
    """

    st.session_state["page"] = "details"

    st.session_state["detail_movie_id"] = movie_id

    st.session_state["detail_score"] = score

    st.session_state["detail_origin"] = origin


# ============================================================
# SEARCH BOX
# ============================================================

# The search term is mirrored into "last_search" because
# Streamlit drops widget state while the details page is
# open. Restoring it keeps the recommendations on screen
# when the user comes back.

movie_name = st.text_input(
    "🔎 Search for a movie",
    value=st.session_state.get(
        "last_search",
        ""
    ),
    placeholder="e.g. Avatar, Inception, Titanic",
    key="search_query"
)


st.session_state["last_search"] = movie_name


# ============================================================
# SEARCH MOVIE
# ============================================================

if movie_name.strip():

    movie = get_movie(
        movie_name
    )


    # ========================================================
    # MOVIE NOT FOUND
    # ========================================================

    if movie is None:

        st.warning(
            "❌ Movie not found in the database."
        )

        st.info(
            "Try a movie such as Avatar, "
            "Inception, Titanic, or The Dark Knight."
        )


    # ========================================================
    # MOVIE FOUND
    # ========================================================

    else:

        # ====================================================
        # MOVIE DETAILS
        # ====================================================

        st.markdown(
            '<div class="section-title">'
            '🎥 Movie Details'
            '</div>',
            unsafe_allow_html=True
        )


        col1, col2 = st.columns(
            [1, 2]
        )


        # ----------------------------------------------------
        # POSTER
        # ----------------------------------------------------

        with col1:

            poster = movie.get(
                "poster"
            )


            if poster:

                st.image(
                    poster,
                    width=280
                )

            else:

                st.info(
                    "🎬 Poster unavailable"
                )


        # ----------------------------------------------------
        # DETAILS
        # ----------------------------------------------------

        with col2:

            st.subheader(
                movie["title"]
            )


            # Overview

            if movie.get("overview"):

                st.write(
                    movie["overview"]
                )


            # Genres

            if movie.get("genres"):

                st.write(
                    "🎭 **Genres:**"
                )

                st.write(
                    movie["genres"]
                )


            # Director

            if movie.get("director"):

                st.write(
                    f"🎬 **Director:** "
                    f"{movie['director']}"
                )


            # Cast

            if movie.get("cast"):

                st.write(
                    "👥 **Cast:**"
                )

                st.write(
                    movie["cast"]
                )


            # Open the full details page (rating, trailer)
            # for the searched movie.

            st.button(
                "🎬 View Full Details",
                key=f'search_details_{movie["id"]}',
                on_click=open_details,
                args=(
                    movie["id"],
                    None,
                    "Search"
                )
            )


        # ====================================================
        # RECOMMENDATIONS
        # ====================================================

        st.divider()

        st.markdown(
            '<div class="section-title">'
            '🤖 Recommended Movies'
            '</div>',
            unsafe_allow_html=True
        )


        recommendations = recommend(
            movie["title"],
            5
        )


        if recommendations:

            cols = st.columns(5)


            for i, recommendation in enumerate(
                recommendations
            ):

                with cols[i]:

                    # ------------------------------------------------
                    # POSTER
                    # ------------------------------------------------

                    poster = recommendation.get(
                        "poster"
                    )


                    if poster:

                        st.image(
                            poster,
                            use_container_width=True
                        )

                    else:

                        st.info(
                            "Poster unavailable"
                        )


                    # ------------------------------------------------
                    # TITLE (CLICKABLE)
                    # ------------------------------------------------

                    st.button(
                        f'🎬 {recommendation["title"]}',
                        key=f'rec_{i}_{recommendation["id"]}',
                        use_container_width=True,
                        on_click=open_details,
                        args=(
                            recommendation["id"],
                            recommendation.get("score")
                        )
                    )


                    # ------------------------------------------------
                    # GENRE
                    # ------------------------------------------------

                    if recommendation.get(
                        "genres"
                    ):

                        st.caption(
                            recommendation["genres"]
                        )


                    # ------------------------------------------------
                    # DIRECTOR
                    # ------------------------------------------------

                    if recommendation.get(
                        "director"
                    ):

                        st.markdown(
                            f'<div class="movie-director">'
                            f'🎬 {recommendation["director"]}'
                            f'</div>',
                            unsafe_allow_html=True
                        )


                    # ------------------------------------------------
                    # SIMILARITY SCORE
                    # ------------------------------------------------

                    if recommendation.get(
                        "score"
                    ) is not None:

                        st.markdown(
                            f'<div class="movie-score">'
                            f'AI similarity: '
                            f'{recommendation["score"]}'
                            f'</div>',
                            unsafe_allow_html=True
                        )


        else:

            st.warning(
                "No recommendations found."
            )


# ============================================================
# GENRE SECTION
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">'
    '🎭 Browse by Genre'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# GENRES
# ============================================================

genres = [
    "Action",
    "Adventure",
    "Animation",
    "Comedy",
    "Crime",
    "Drama",
    "Family",
    "Fantasy",
    "Horror",
    "Mystery",
    "Romance",
    "Science Fiction",
    "Thriller"
]


# ============================================================
# GENRE BUTTONS
# ============================================================

for start in range(
    0,
    len(genres),
    5
):

    cols = st.columns(5)


    for i, genre in enumerate(
        genres[start:start + 5]
    ):

        with cols[i]:

            if st.button(
                genre,
                key=f"genre_{genre}",
                use_container_width=True
            ):

                st.session_state[
                    "selected_genre"
                ] = genre


# ============================================================
# SHOW SELECTED GENRE
# ============================================================

if "selected_genre" in st.session_state:

    selected_genre = st.session_state[
        "selected_genre"
    ]


    st.divider()


    st.markdown(
        f'<div class="section-title">'
        f'🎬 {selected_genre} Movies'
        f'</div>',
        unsafe_allow_html=True
    )


    genre_movies = get_movies_by_genre(
        selected_genre,
        10
    )


    if not genre_movies:

        st.warning(
            "No movies found for this genre."
        )


    else:

        cols = st.columns(5)


        for i, movie in enumerate(
            genre_movies
        ):

            with cols[i % 5]:

                # ------------------------------------------------
                # POSTER
                # ------------------------------------------------

                poster = movie.get(
                    "poster"
                )


                if poster:

                    st.image(
                        poster,
                        use_container_width=True
                    )

                else:

                    st.info(
                        "Poster unavailable"
                    )


                # ------------------------------------------------
                # TITLE (CLICKABLE)
                # ------------------------------------------------

                st.button(
                    f'🎬 {movie["title"]}',
                    key=f'genre_movie_{i}_{movie["id"]}',
                    use_container_width=True,
                    on_click=open_details,
                    args=(
                        movie["id"],
                        None,
                        f"{selected_genre} Movies"
                    )
                )


                # ------------------------------------------------
                # DIRECTOR
                # ------------------------------------------------

                if movie.get(
                    "director"
                ):

                    st.caption(
                        f"Director: "
                        f"{movie['director']}"
                    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🎬 CineAI | "
    "Content-Based Movie Recommendation System"
)