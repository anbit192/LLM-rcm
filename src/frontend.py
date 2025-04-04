import streamlit as st
import requests

# Configuration
API_BASE_URL = "http://localhost:8000"

def search_movies(query: str) -> list:
    response = requests.get(f"{API_BASE_URL}/search/{query}")
    return response.json() if response.status_code == 200 else []

def rate_movie(movie_id: int, rating: float) -> bool:
    data = {"movieId": movie_id, "user_rate": rating}
    response = requests.post(f"{API_BASE_URL}/input_user_movies", json=data)
    return response.status_code == 200

def get_recommendations() -> list:
    response = requests.get(f"{API_BASE_URL}/get_recommend_movies")
    return response.json() if response.status_code == 200 else []

def main():
    st.set_page_config(layout="wide", page_title="Movie Recommender")
    st.title("🍿 Movie Recommendation System")
    
    # Initialize session state
    if 'user_ratings' not in st.session_state:
        st.session_state.user_ratings = {}
    if 'rated_movies_info' not in st.session_state:
        st.session_state.rated_movies_info = []
    
    # Main layout columns
    search_col, rec_col = st.columns([1, 1], gap="large")
    
    with search_col:
        st.header("Find & Rate Movies")
        search_query = st.text_input("Search for movies:", placeholder="Type a movie title...")
        
        if search_query:
            movies = search_movies(search_query)
            if movies:
                st.success(f"Found {len(movies)} movies matching '{search_query}'")
                for movie in movies[:5]:  # Show top 5 results
                    movie_id = movie['movieId']
                    already_rated = movie_id in st.session_state.user_ratings
                    
                    # Movie card with title and genres
                    with st.container(border=True):
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.subheader(movie.get('title', 'Untitled'))
                            genres = ", ".join(movie.get('genres', ['Unknown']))
                            st.caption(f"🎭 {genres}")
                        
                        with col2:
                            if movie.get('year'):
                                st.markdown(f"**{movie['year']}**")
                        
                        # Rating section
                        if already_rated:
                            st.success(f"You rated this: {st.session_state.user_ratings[movie_id]}⭐")
                        else:
                            rating = st.slider(
                                "Your rating (1-5 stars)", 
                                1.0, 5.0, 3.0, 0.5,
                                key=f"rate_{movie_id}"
                            )
                            if st.button("Submit Rating", 
                                        key=f"btn_{movie_id}",
                                        use_container_width=True):
                                if rate_movie(movie_id, rating):
                                    st.session_state.user_ratings[movie_id] = rating
                                    st.session_state.rated_movies_info.append({
                                        'title': movie.get('title', 'Untitled'),
                                        'year': movie.get('year', '?'),
                                        'genres': movie.get('genres', []),
                                        'rating': rating
                                    })
                                    st.success("Rating saved!")
                                    # st.experimental_rerun()
                                else:
                                    st.error("Failed to save rating")
            else:
                st.warning("No movies found, try a different search")
    
    with rec_col:
        st.header("Recommendations")
        
        # Display rated movies list
        if st.session_state.rated_movies_info:
            st.subheader("Your Watched Movies:")
            for movie in st.session_state.rated_movies_info:
                with st.container(border=True):
                    st.write(f"**{movie['title']}** ({movie.get('year', '?')})")
                    st.write(f"⭐ {movie['rating']} | 🎭 {', '.join(movie.get('genres', ['Unknown']))}")
            
            st.divider()
            
            if st.button("Get Recommendations", type="primary", use_container_width=True):
                with st.spinner("Finding your perfect movies..."):
                    recommendations = get_recommendations()
                
                if recommendations:
                    st.balloons()
                    st.success("Recommended For You:")
                    for genre_group in recommendations:
                        for genre, movies in genre_group.items():
                            with st.expander(f"🎬 {genre}"):
                                for movie in movies[:3]:
                                    st.write(f"▪ {movie.get('title', 'Untitled')}")
                else:
                    st.info("Rate more movies to get better recommendations")
        else:
            st.info("Search and rate movies to get started")
            st.image("https://cor-cdn-static.bibliocommons.com/list_jacket_covers/live/863842447.png", 
                    use_container_width=True)

if __name__ == "__main__":
    main()