import streamlit as st
import requests
import pandas as pd

API_BASE_URL = "http://localhost:8000"
st.set_page_config(layout="wide", page_title="Movie Recommender", page_icon="🎬")


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
    body = {"movieIds": ids}
    return requests.post(f"{API_BASE_URL}/get_movies", json=body).json()


def select_user(email: str, username: str):
    body = {"email": email, "username": username}
    res = requests.post(f"{API_BASE_URL}/select_user", json=body)
    return res.status_code == 200


def local_css():
    css = """
    <style>
    /* Set the main app background color */
    .stApp {
        background-color: #0E1117;
    }
    /* Set global text colors */
    body, .stText, .stMarkdown, .stTitle, .stHeader, .stSubheader {
        color: #FAFAFA;
    }
    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: #262730;
    }
    /* Customize button appearance */
    .stButton>button {
        background-color: #FF4B4B;
        color: #FAFAFA;
        border: none;
    }
    .stButton>button:hover {
        background-color: #FF6B6B;
    }
    /* Optional: style the slider label and container borders */
    .stSlider, .stDivider {
        color: #FAFAFA;
    }
    /* Additional styling for markdown headings within containers */
    .stContainer h2, .stContainer h3 {
        color: #FAFAFA;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


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
                actors = movie["Actors"]
                director = movie["Director"]
                plot = movie["Plot"]
                poster = movie["Poster"]
                language = movie["Language"]
                runtime = movie["Runtime"]

                with st.container():
                    st.divider()
                    st.markdown(f"<h2 style='text-align: center;'>{title}</h2>", unsafe_allow_html=True)
                    st.divider()

                    col1, col2 = st.columns([4, 1])

                    with col1:
                        col1_, col2_, col3_, col4_ = st.columns([2, 2, 2, 2])
                        with col1_:
                            st.badge(f"Genres: {genres}", color="blue")
                        with col2_:
                            st.badge(f"Weighted Rating: {weight_rating}", color="primary")
                        with col3_:
                            st.badge(f"Duration: {runtime}", color="green")
                        with col4_:
                            st.badge(f"Language: {language}", color="violet")

                        temp1, _ = st.columns([7, 1])
                        with temp1:
                            st.header("📝 Plot")
                            st.markdown(f"<p style='text-align:justify;font-size:20px;'>{plot}</p>", unsafe_allow_html=True)

                        here, _, star = st.columns([2, 1, 2])
                        with here:
                            st.markdown("<h2>🎯 Rating</h2>", unsafe_allow_html=True)
                            slider = st.slider("", min_value=0.0, max_value=5.0, step=0.5, value=3.0,
                                                 key=f"user_{user}_rate_{movieId}")
                        if st.button("Rate!", key=f"user_{user}_button_{movieId}"):
                            if rate_movie(movie_id=movieId, rating=slider):
                                get_recommendations.clear()
                                st.toast(f"Rated {title} with {slider} ⭐")
                                st.session_state.search_results = []
                                st.rerun()

                    with col2:
                        st.image(poster, use_container_width=True)
                        st.text("Actors: " + ", ".join(actors))
                        st.text("Directors: " + ", ".join(director))


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
    for genre in results:
        genre_name = next(iter(genre))
        movies = [item for item in genre[genre_name]]

        with st.container():
            st.markdown('<div class="recommend-card">', unsafe_allow_html=True)
            st.markdown(f"<div class='recommend-title'>{genre_name}</div>", unsafe_allow_html=True)

            num_columns = 5
            for i in range(0, len(movies), num_columns):
                cols = st.columns(num_columns)
                for idx, movie in enumerate(movies[i:i+num_columns]):
                    poster = movie["Poster"]
                    title = movie["title"]
                    with cols[idx]:
                        st.image(f"{poster}", use_container_width=True)
                        st.markdown(f"<div class='movie-title'>🎬 {title}</div>", unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)


def history_section():
    history = get_user_ratings()
    if (len(history) < 1):
        return
    ids = [item["movieId"] for item in history]

    res = get_movie_infos(ids)
    temp_df = pd.json_normalize(res)
    temp_df2 = pd.json_normalize(history)

    merged = temp_df.merge(temp_df2, on="movieId")
    for idx, item in merged.iterrows():
        poster = item["Poster"]
        title = item["title"]
        user_rate = item["user_rate"]
        timestamp = item["timestamp"]
        actors = ", ".join(item["Actors"])
        director = ", ".join(item["Director"])

        st.markdown('<div class="history-card">', unsafe_allow_html=True)
        col1, col2 = st.columns([4, 1])

        with col1:
            st.subheader(title)
            st.markdown(f"<div class='user-rating'> You rated this: {user_rate} ⭐</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='timestamp'>📅 Watched on: {timestamp}</div>", unsafe_allow_html=True)

        with col2:

            st.image(f"{poster}", use_container_width=True)
            st.text(f"Actors: {actors}")
            st.text(f"Directors: {director}")
        st.markdown('</div>', unsafe_allow_html=True)


def main():

    st.markdown("""
    <style>
    body {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .recommend-card {
        background-color: #1F222A;
        border-radius: 16px;
        padding: 2px;
        margin-bottom: 15px;
        box-shadow: 0 0 10px rgba(255, 75, 75, 0.1);
    }
    .recommend-title {
        color: #FF4B4B;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .movie-title {
        color: #F0A500;
        font-weight: 600;
        text-align: center;
        margin-top: 8px;
    }
    .history-card {
        background-color: #2B2D36;
        border-radius: 12px;
        padding:2px;
        margin-bottom: 15px;
    }
    .user-rating {
        color: #FFD700;
        font-weight: bold;
        font-size: 25px;
    }
    .timestamp {
        color: #B0B0B0;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)


    # Inject custom CSS styles into the app
    local_css()

    if "switch_user" not in st.session_state:
        st.session_state.switch_user = False
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in or st.session_state.switch_user:
        render_login_page()
        return

    st.title("🎬 Movie Recommendation System 🎬")

    col1, _, col2 = st.columns([1, 6, 1])

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
    st.header("Maybe you like these movies...")
    with st.expander("Show results", expanded=True):
        recommend_section(rcms)

    st.header("History")
    with st.expander("Show history"):
        get_user_ratings.clear()
        history_section()


if __name__ == "__main__":
    main()
