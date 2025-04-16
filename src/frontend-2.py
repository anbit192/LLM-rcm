import streamlit as st
import requests
import pandas as pd

API_BASE_URL = "http://localhost:8000"

@st.cache_data(show_spinner=False)
def search_movies(query: str) -> list:
    response = requests.get(f"{API_BASE_URL}/search/{query}")
    return response.json() if response.status_code == 200 else []


@st.cache_data(show_spinner=False)
def rate_movie(movie_id: int, rating: float) -> bool:
    data = {"movieId": movie_id, "user_rate": rating}
    response = requests.post(f"{API_BASE_URL}/input_user_movies", json=data)
    return response.status_code == 200


@st.cache_data(show_spinner=False)
def get_recommendations() -> list:
    response = requests.get(f"{API_BASE_URL}/get_recommend_movies")
    return response.json() if response.status_code == 200 else []


@st.cache_data(show_spinner=False)
def get_all_user():
    return requests.get(f"{API_BASE_URL}/get_all_users").json()


@st.cache_data(show_spinner=False)
def get_current_user():
    return requests.get(f"{API_BASE_URL}/get_current_user").json()


@st.cache_data(show_spinner=False)
def get_user_ratings():
    return requests.get(f"{API_BASE_URL}/get_user_ratings").json()


def get_movie_infos(ids):
    body = {"movieIds":ids}
    return requests.post(f"{API_BASE_URL}/get_movies", json=body).json()



def select_user(email: str, username: str):
    body = {"email": email, "username": username}
    res = requests.post(f"{API_BASE_URL}/select_user", json=body)
    return res.status_code == 200


def render_search_result():
    search_query = st.text_input("Enter movie's name")
    submit_button = st.button("Search")

    if submit_button and search_query:
        st.session_state.search_results = search_movies(search_query)

    if st.session_state.get("search_results"):
        with st.expander("Search Results"):
            results = st.session_state.search_results

            for movie in results:
                movieId = movie["movieId"]
                title = movie["title"]
                genres = ", ".join(movie["genres"])
                weight_rating = f"{round(movie['weight_rating'], 2)} ⭐"
                user = st.session_state.get("user", {}).get("username", "guest")

                with st.container():
                    st.divider()
                    col1, col2 = st.columns([4, 1])

                    with col1:
                        st.subheader(title)
                        st.badge(f"Genres: {genres}", color="blue")
                        st.badge(f"Weighted Rating: {weight_rating}", color="primary")
                        slider = st.slider("Rating", min_value=0.0, max_value=5.0, step=0.5, value=3.0, key=f"user_{user}_rate_{movieId}")

                        if st.button("Rate!", key=f"user_{user}_button_{movieId}"):
                            if rate_movie(movie_id=movieId, rating=slider):
                                get_recommendations.clear()
                                st.toast(f"Rated {title} with {slider} ⭐")
                                st.session_state.search_results = []
                                st.rerun()

                    with col2:
                        st.image("https://m.media-amazon.com/images/M/MV5BMWVjZmEwYTUtYmEzNC00Mjc0LThmZDAtNjQ5NmZiN2E0OWViXkEyXkFqcGc@._V1_.jpg", use_container_width=True)


def render_login_page():
    st.title("Select User")
    with st.form("login_form"):
        email = st.text_input("Email")
        username = st.text_input("Username")
        login_btn = st.form_submit_button("Go")

        if login_btn:
            if select_user(email, username):
                st.session_state.logged_in = True
                st.session_state.switch_user = False
                st.session_state.user = {"username": username, "email": email}
                get_recommendations.clear()
                st.rerun()
            else:
                st.error("Incorrect credentials!")


def recommend_section(results):
    st.title("Maybe you like...")
    for genre in results:
        genre_name = next(iter(genre))
        movies = [item["title"] for item in genre[genre_name]]

        with st.container():
            st.divider()
            st.subheader(genre_name)

            num_columns = 5
            for i in range(0, len(movies), num_columns):
                cols = st.columns(num_columns)
                for idx, movie in enumerate(movies[i:i+num_columns]):
                    with cols[idx]:
                        st.image("https://m.media-amazon.com/images/M/MV5BMWVjZmEwYTUtYmEzNC00Mjc0LThmZDAtNjQ5NmZiN2E0OWViXkEyXkFqcGc@._V1_.jpg", use_container_width=True)
                        st.markdown(f"🎬 **{movie}**")


def history_section():
    history = get_user_ratings()
    ids = [item["movieId"] for item in history]

    res = get_movie_infos(ids)
    temp_df = pd.json_normalize(res)

    temp_df2 = pd.json_normalize(history)
    # st.dataframe(temp_df2)

    merged = temp_df.merge(temp_df2, on="movieId")

    for idx, item in merged.iterrows():
        # print(item["user_rate"])
        st.divider()
        col1, col2 = st.columns([4, 1])

        with col1:
            st.subheader(item["title"])
            st.write(f"You rated this: {item["user_rate"]} ⭐")
            st.write(f"You watched this on: {item["timestamp"]}")

        with col2:
            st.image("https://m.media-amazon.com/images/M/MV5BMWVjZmEwYTUtYmEzNC00Mjc0LThmZDAtNjQ5NmZiN2E0OWViXkEyXkFqcGc@._V1_.jpg", use_container_width=True)

    # st.write(merged)


def main():
    if "switch_user" not in st.session_state:
        st.session_state.switch_user = False
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in or st.session_state.switch_user:
        render_login_page()
        return
    
    st.set_page_config(layout="wide", page_title="Movie Recommender", page_icon="🎬")
    st.title("🎬 Movie Recommendation System 🎬")

    col1, _ , col2 = st.columns([1, 6, 1])

    with col1:
        user_info = get_current_user()
        user = user_info.get("username", "guest")
        st.badge(f"Current User: {user}", color="green")

    with col2:
        if st.button("Switch User"):
            st.session_state.switch_user = True
            get_current_user.clear()
            st.rerun()

    with st.container():
        render_search_result()

    rcms = get_recommendations()
    with st.expander("Maybe you like....", expanded=True):
        recommend_section(rcms)

    with st.expander("History"):
        get_user_ratings.clear()
        history_section()

if __name__ == "__main__":
    main()
