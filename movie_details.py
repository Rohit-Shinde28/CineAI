import streamlit as st

from recommender import get_movie_by_id

from tmdb_api import (
    get_movie_details,
    get_movie_trailer,
    IMAGE_BASE_URL
)


# ============================================================
# CACHED TMDB LOOKUP
# ============================================================

@st.cache_data(
    show_spinner=False,
    ttl=60 * 60 * 24
)
def load_tmdb_details(movie_id):
    """Fetch TMDB details once per movie, then reuse the cache.

    The dataset does not store poster_path, release_date or
    vote_average, so those come from TMDB. Caching keeps this
    to a single request per movie per day.
    """

    return get_movie_details(
        movie_id
    )


# ============================================================
# CACHED TRAILER LOOKUP
# ============================================================

@st.cache_data(
    show_spinner=False,
    ttl=60 * 60 * 24
)
def load_trailer_url(movie_id):
    """Fetch the trailer once per movie, then reuse the cache.

    tmdb_api.get_movie_trailer already prefers the official
    YouTube trailer and falls back to any YouTube trailer.
    Nothing is downloaded, only the YouTube URL is stored.
    """

    return get_movie_trailer(
        movie_id
    )


# ============================================================
# BUILD POSTER URL
# ============================================================

def build_poster_url(details):
    """Turn the TMDB poster_path into a full image URL."""

    if not details:

        return None


    poster_path = details.get(
        "poster_path"
    )

    if not poster_path:

        return None


    return (
        IMAGE_BASE_URL
        + poster_path
    )


# ============================================================
# FORMAT RELEASE DATE
# ============================================================

def format_release(details):
    """Return (year, full_date) from the TMDB release_date."""

    if not details:

        return None, None


    release_date = details.get(
        "release_date"
    )

    if not release_date:

        return None, None


    year = release_date.split("-")[0]

    return year, release_date


# ============================================================
# GO BACK TO THE RECOMMENDATION LIST
# ============================================================

def go_back():

    st.session_state["page"] = "home"

    st.session_state.pop(
        "detail_movie_id",
        None
    )

    st.session_state.pop(
        "detail_score",
        None
    )

    st.session_state.pop(
        "detail_origin",
        None
    )


# ============================================================
# RENDER THE MOVIE DETAILS PAGE
# ============================================================

def render():

    movie_id = st.session_state.get(
        "detail_movie_id"
    )

    score = st.session_state.get(
        "detail_score"
    )


    # The label names the list the user came from, so the
    # same page works for search, recommendations and genres.

    origin = st.session_state.get(
        "detail_origin",
        "Recommendations"
    )

    back_label = f"⬅ Back to {origin}"


    # ========================================================
    # BACK BUTTON
    # ========================================================

    st.button(
        back_label,
        key="back_to_recommendations",
        on_click=go_back
    )


    # ========================================================
    # LOOK UP THE MOVIE BY ID
    # ========================================================

    movie = get_movie_by_id(
        movie_id
    )


    if movie is None:

        st.error(
            "❌ Could not load this movie."
        )

        st.info(
            "Use the button above to go back "
            "to your recommendations."
        )

        return


    # ========================================================
    # TMDB DETAILS (CACHED, MAY BE UNAVAILABLE)
    # ========================================================

    details = load_tmdb_details(
        movie["id"]
    )


    poster_url = build_poster_url(
        details
    )

    year, release_date = format_release(
        details
    )


    # ========================================================
    # HEADING
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🎥 Movie Details'
        '</div>',
        unsafe_allow_html=True
    )


    col1, col2 = st.columns(
        [1, 2]
    )


    # --------------------------------------------------------
    # POSTER
    # --------------------------------------------------------

    with col1:

        if poster_url:

            st.image(
                poster_url,
                width=300
            )


        # Fall back to an already downloaded poster
        # when TMDB is unreachable or has no image.

        elif movie.get("poster"):

            st.image(
                movie["poster"],
                width=300
            )

        else:

            st.info(
                "🎬 Poster unavailable"
            )


    # --------------------------------------------------------
    # DETAILS
    # --------------------------------------------------------

    with col2:

        if year:

            st.subheader(
                f"{movie['title']} ({year})"
            )

        else:

            st.subheader(
                movie["title"]
            )


        # Rating

        rating = None

        if details:

            rating = details.get(
                "vote_average"
            )


        if rating:

            votes = details.get(
                "vote_count"
            ) or 0

            st.markdown(
                f"⭐ **Rating:** "
                f"{round(float(rating), 1)}/10  "
                f"({votes:,} votes)"
            )

        else:

            st.caption(
                "⭐ Rating not available"
            )


        # Release date

        if release_date:

            st.markdown(
                f"📅 **Released:** "
                f"{release_date}"
            )


        # AI similarity score

        if score is not None:

            st.markdown(
                f"🤖 **AI similarity:** "
                f"{score}"
            )


        # Genres

        genres = movie.get(
            "genres_list"
        )

        if genres:

            st.markdown(
                f"🎭 **Genres:** "
                f"{', '.join(genres)}"
            )


        # Director

        if movie.get("director"):

            st.markdown(
                f"🎬 **Director:** "
                f"{movie['director']}"
            )


        # Cast

        cast = movie.get(
            "cast_list"
        )

        if cast:

            st.markdown(
                f"👥 **Cast:** "
                f"{', '.join(cast[:10])}"
            )


    # ========================================================
    # OVERVIEW
    # ========================================================

    overview = movie.get(
        "overview"
    )


    if not overview and details:

        overview = details.get(
            "overview"
        )


    st.divider()

    st.markdown(
        '<div class="section-title">'
        '📖 Overview'
        '</div>',
        unsafe_allow_html=True
    )


    if overview:

        st.write(
            overview
        )

    else:

        st.info(
            "No description available "
            "for this movie."
        )


    # ========================================================
    # TRAILER
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="section-title">'
        '🎬 Official Trailer'
        '</div>',
        unsafe_allow_html=True
    )


    # Looked up by TMDB id, so the trailer always belongs
    # to the movie currently on screen.

    trailer_url = load_trailer_url(
        movie["id"]
    )


    if trailer_url:

        st.video(
            trailer_url
        )

    else:

        st.info(
            "🎬 Trailer not available "
            "for this movie."
        )


    # ========================================================
    # BACK BUTTON (BOTTOM)
    # ========================================================

    st.divider()

    st.button(
        back_label,
        key="back_to_recommendations_bottom",
        on_click=go_back
    )


    # ========================================================
    # NOTE WHEN TMDB IS UNAVAILABLE
    # ========================================================

    if details is None:

        st.caption(
            "Live TMDB data (poster, rating, "
            "release date) is unavailable right now."
        )
