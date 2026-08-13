import streamlit as st

from recommender import recommend
from tmdb_api import (
    search_movie,
    get_movie_details,
    get_movie_trailer,
    get_watch_providers
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="CineAI",
    page_icon="🎬",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("🎬 CineAI")
st.write("AI-powered Movie Recommendation System")


# ============================================================
# SEARCH BAR
# ============================================================

movie_name = st.text_input(
    "🔍 Search for a movie",
    placeholder="e.g. Inception"
)


# ============================================================
# MOVIE SEARCH
# ============================================================

if movie_name.strip():

    with st.spinner("Searching for movie..."):

        movie = search_movie(movie_name)


    # --------------------------------------------------------
    # MOVIE NOT FOUND
    # --------------------------------------------------------

    if movie is None:

        st.error(
            "❌ Movie not found. Please try another movie."
        )

    else:

        movie_id = movie.get("id")


        # ====================================================
        # GET MOVIE DATA
        # ====================================================

        with st.spinner("Loading movie information..."):

            details = get_movie_details(movie_id)

            trailer = get_movie_trailer(movie_id)

            providers = get_watch_providers(
                movie_id,
                "IN"
            )


        # ====================================================
        # MOVIE DETAILS
        # ====================================================

        st.divider()

        st.header("🎬 Movie Details")

        col1, col2 = st.columns(
            [1, 2]
        )


        # ----------------------------------------------------
        # POSTER
        # ----------------------------------------------------

        with col1:

            poster_path = details.get(
                "poster_path"
            )

            if poster_path:

                poster_url = (
                    "https://image.tmdb.org/t/p/w500"
                    + poster_path
                )

                st.image(
                    poster_url,
                    width=300
                )

            else:

                st.info(
                    "Poster not available."
                )


        # ----------------------------------------------------
        # INFORMATION
        # ----------------------------------------------------

        with col2:

            title = details.get(
                "title",
                movie_name
            )

            st.title(title)


            # Rating
            rating = details.get(
                "vote_average"
            )

            if rating is not None:

                st.write(
                    f"⭐ **Rating:** "
                    f"{rating:.1f}/10"
                )


            # Release date
            release_date = details.get(
                "release_date"
            )

            if release_date:

                st.write(
                    f"📅 **Release Date:** "
                    f"{release_date}"
                )


            # Genres
            genres = details.get(
                "genres",
                []
            )

            if genres:

                genre_names = ", ".join(
                    genre.get("name", "")
                    for genre in genres
                )

                st.write(
                    f"🎭 **Genres:** "
                    f"{genre_names}"
                )


            # Runtime
            runtime = details.get(
                "runtime"
            )

            if runtime:

                st.write(
                    f"⏱️ **Runtime:** "
                    f"{runtime} minutes"
                )


            # Overview
            overview = details.get(
                "overview"
            )

            if overview:

                st.subheader(
                    "📝 Overview"
                )

                st.write(
                    overview
                )


        # ====================================================
        # TRAILER
        # ====================================================

        st.divider()

        st.header("▶️ Watch Trailer")


        if trailer:

            st.video(
                trailer
            )

        else:

            st.info(
                "Trailer is not available."
            )


        # ====================================================
        # WHERE TO WATCH
        # ====================================================

        st.divider()

        st.header("📺 Where to Watch")

        if providers:

            watch_link = providers.get(
                "link"
            )

            streaming = providers.get(
                "flatrate",
                []
            )

            rent = providers.get(
                "rent",
                []
            )

            buy = providers.get(
                "buy",
                []
            )


            # ------------------------------------------------
            # STREAMING
            # ------------------------------------------------

            if streaming:

                st.subheader(
                    "📺 Streaming"
                )

                for provider in streaming:

                    provider_name = provider.get(
                        "provider_name"
                    )

                    if provider_name:

                        st.write(
                            f"▶️ {provider_name}"
                        )


            # ------------------------------------------------
            # RENT
            # ------------------------------------------------

            if rent:

                st.subheader(
                    "💳 Rent"
                )

                for provider in rent:

                    provider_name = provider.get(
                        "provider_name"
                    )

                    if provider_name:

                        st.write(
                            f"🎬 {provider_name}"
                        )


            # ------------------------------------------------
            # BUY
            # ------------------------------------------------

            if buy:

                st.subheader(
                    "🛒 Buy"
                )

                for provider in buy:

                    provider_name = provider.get(
                        "provider_name"
                    )

                    if provider_name:

                        st.write(
                            f"🎬 {provider_name}"
                        )


            # ------------------------------------------------
            # TMDB WATCH LINK
            # ------------------------------------------------

            if watch_link:

                st.link_button(
                    "🔗 View Legal Streaming Options",
                    watch_link
                )


            # ------------------------------------------------
            # NOTHING AVAILABLE
            # ------------------------------------------------

            if not streaming and not rent and not buy:

                st.info(
                    "No streaming, rental, or purchase "
                    "options are currently listed."
                )

        else:

            st.info(
                "No legal streaming information "
                "is currently available in India."
            )


        # ====================================================
        # RECOMMENDATIONS
        # ====================================================

        st.divider()

        st.header(
            "🍿 Recommended Movies"
        )


        with st.spinner(
            "Finding similar movies..."
        ):

            recommendations = recommend(
                movie_name
            )


        if recommendations:

            for recommended_movie in recommendations:

                # ------------------------------------------------
                # Search recommended movie on TMDB
                # ------------------------------------------------

                rec_movie = search_movie(
                    recommended_movie
                )


                col1, col2 = st.columns(
                    [1, 3]
                )


                # ------------------------------------------------
                # POSTER
                # ------------------------------------------------

                with col1:

                    if (
                        rec_movie
                        and rec_movie.get(
                            "poster_path"
                        )
                    ):

                        poster_url = (
                            "https://image.tmdb.org/t/p/w500"
                            + rec_movie["poster_path"]
                        )

                        st.image(
                            poster_url,
                            width=140
                        )

                    else:

                        st.info(
                            "Poster unavailable"
                        )


                # ------------------------------------------------
                # INFORMATION
                # ------------------------------------------------

                with col2:

                    st.subheader(
                        f"🎬 {recommended_movie}"
                    )


                    if rec_movie:

                        rating = rec_movie.get(
                            "vote_average"
                        )

                        if rating is not None:

                            st.write(
                                f"⭐ **Rating:** "
                                f"{rating:.1f}/10"
                            )


                        release_date = rec_movie.get(
                            "release_date"
                        )

                        if release_date:

                            st.write(
                                f"📅 **Release Date:** "
                                f"{release_date}"
                            )


                st.divider()


        else:

            st.warning(
                "No recommendations found."
            )