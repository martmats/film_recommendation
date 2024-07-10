import streamlit as st
import requests
from datetime import datetime

# Configuration
API_KEY = st.secrets["movie_api"]["key"]
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

def fetch_movie_by_name(movie_name):
    url = f"{BASE_URL}/search/movie"
    params = {"api_key": API_KEY, "query": movie_name}
    response = requests.get(url, params=params)
    return response.json()

def fetch_movie_details(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {"api_key": API_KEY}
    response = requests.get(url, params=params)
    return response.json()

def fetch_movie_providers(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/watch/providers"
    params = {"api_key": API_KEY}
    response = requests.get(url, params=params)
    return response.json()

def fetch_recommendations(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/recommendations"
    params = {"api_key": API_KEY}
    response = requests.get(url, params=params)
    return response.json()

def fetch_filtered_movies(provider_filter, rating_filter, year_filter):
    url = f"{BASE_URL}/discover/movie"
    params = {
        "api_key": API_KEY,
        "vote_average.gte": rating_filter,
        "primary_release_date.gte": f"{year_filter[0]}-01-01",
        "primary_release_date.lte": f"{year_filter[1]}-12-31",
        "with_watch_providers": "|".join(provider_filter),
        "watch_region": "US"
    }
    response = requests.get(url, params=params)
    return response.json()

# Format date
def format_date(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj.strftime('%d/%m/%y')

# Format rating
def format_rating(vote_average):
    return f"{vote_average:.1f} stars"

# Format providers
def format_providers(providers):
    return ', '.join([provider['provider_name'] for provider in providers])

# Format genres
def format_genres(genres):
    return ', '.join([genre['name'] for genre in genres])

# Function to display films in styled HTML
def display_films(films, card_class="movie-card"):
    for film in films:
        providers = fetch_movie_providers(film['id'])['results'].get('US', {}).get('flatrate', [])
        providers_html = ''.join([f'<img src="{IMAGE_BASE_URL}{provider["logo_path"]}" class="provider-logo" alt="{provider["provider_name"]}">' for provider in providers if provider.get('logo_path')])
        st.markdown(f"""
        <div class="{card_class}">
            <img src="{IMAGE_BASE_URL}{film['poster_path']}" alt="{film['title']}">
            <div class="movie-info">
                <h4>{film['title']}</h4>
                <p>{format_providers(providers)}</p>
                <p class="rating">{format_rating(film['vote_average'])}</p>
                <details>
                    <summary>More info</summary>
                    <p><strong>Overview:</strong> {film['overview']}</p>
                    <p><strong>Genres:</strong> {format_genres(fetch_movie_details(film['id'])['genres'])}</p>
                </details>
            </div>
            <div class="provider-logo-row">
                {providers_html if providers_html else "<p>No providers available</p>"}
            </div>
        </div>
        """, unsafe_allow_html=True)

def recommendation_page():
    st.title("🎬 Film Recommendations")
    movie_name = st.text_input("Enter a film name to get recommendations")

    if movie_name:
        search_results = fetch_movie_by_name(movie_name)
        if search_results['results']:
            movie = search_results['results'][0]  # Select the first search result
            movie_id = movie['id']

            # Display selected movie details
            movie_details = fetch_movie_details(movie_id)
            providers = fetch_movie_providers(movie_id)['results'].get('US', {}).get('flatrate', [])
            providers_html = ''.join([f'<img src="{IMAGE_BASE_URL}{provider["logo_path"]}" class="provider-logo" alt="{provider["provider_name"]}">' for provider in providers if provider.get('logo_path')])

            st.header("Selected Movie:")
            st.markdown(f"""
                <div class="movie-card">
                    <img src="{IMAGE_BASE_URL}{movie_details['poster_path']}" alt="{movie_details['title']} poster">
                    <div class="movie-info">
                        <h4>{movie_details['title']}</h4>
                        <p>Release Date: {format_date(movie_details['release_date'])}</p>
                        <p class="rating">{format_rating(movie_details['vote_average'])}</p>
                        <details>
                            <summary>More info</summary>
                            <p><strong>Overview:</strong> {movie_details['overview']}</p>
                            <p><strong>Genres:</strong> {format_genres(movie_details['genres'])}</p>
                        </details>
                    </div>
                    <div class="provider-logo-row">
                        {providers_html if providers_html else "<p>No providers available</p>"}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Recommended movies section with filters
            st.subheader("Recommended Films Based on Your Selection")
            st.markdown('<div style="border: 1px solid #ccc; padding: 10px;">', unsafe_allow_html=True)
            selected_genres = st.multiselect(
                "Select Genres",
                options=[genre['name'] for genre in movie_details['genres']],
                default=[genre['name'] for genre in movie_details['genres']]
            )
            min_rating = st.slider("Minimum Rating", 0.0, 10.0, 5.0)
            selected_providers = st.multiselect("Select Providers", ["Netflix", "Hulu", "Disney+", "Amazon Prime", "HBO Max"], default=["Netflix", "Hulu", "Disney+", "Amazon Prime", "HBO Max"])
            st.markdown('</div>', unsafe_allow_html=True)

            recommendations = fetch_recommendations(movie_id)['results']
            filtered_recommendations = [rec for rec in recommendations if rec['vote_average'] >= min_rating and any(genre['name'] in selected_genres for genre in fetch_movie_details(rec['id'])['genres']) and any(provider in selected_providers for provider in fetch_movie_providers(rec['id'])['results'].get('US', {}).get('flatrate', []))]

            if filtered_recommendations:
                for i in range(0, len(filtered_recommendations), 4):
                    cols = st.columns(4)
                    for col, recommendation in zip(cols, filtered_recommendations[i:i+4]):
                        with col:
                            movie_details_rec = fetch_movie_details(recommendation['id'])
                            providers_rec = fetch_movie_providers(recommendation['id'])['results'].get('US', {}).get('flatrate', [])
                            providers_rec_html = ''.join([f'<img src="{IMAGE_BASE_URL}{provider["logo_path"]}" class="provider-logo" alt="{provider["provider_name"]}">' for provider in providers_rec if provider.get('logo_path')])
                            col.markdown(f"""
                                <div class="movie-card">
                                    <img src="{IMAGE_BASE_URL}{recommendation['poster_path']}" alt="{recommendation['title']} poster">
                                    <div class="movie-info">
                                        <h4>{recommendation['title']}</h4>
                                        <p>Release Date: {format_date(recommendation['release_date'])}</p>
                                        <p class="rating">{format_rating(recommendation['vote_average'])}</p>
                                        <details>
                                            <summary>More info</summary>
                                            <p><strong>Overview:</strong> {movie_details_rec['overview']}</p>
                                            <p><strong>Genres:</strong> {format_genres(movie_details_rec['genres'])}</p>
                                        </details>
                                    </div>
                                    <div class="provider-logo-row">
                                        {providers_rec_html if providers_rec_html else "<p>No providers available</p>"}
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
            else:
                st.write("No recommendations found.")
        else:
            st.write("No results found for the film name.")
    else:
        st.write("Please enter a film name to get recommendations.")

def filter_page():
    st.title("🔍 Discover New Films")
    
    # Sidebar with filter options
    with st.sidebar:
        st.header("Filter Options")
        provider_filter = st.multiselect("Select provider", ["Netflix", "Hulu", "Disney+", "Amazon Prime", "HBO Max"], default=["Netflix", "Hulu", "Disney+", "Amazon Prime", "HBO Max"])
        rating_filter = st.slider("Minimum Rating", 0.0, 10.0, 5.0)
        year_filter = st.slider("Release Year", 1900, datetime.now().year, (1900, datetime.now().year))
    
    # Main column to display filtered movies
    filtered_movies = []
    if provider_filter:
        filtered_movies = fetch_filtered_movies(provider_filter, rating_filter, year_filter)['results']

    if filtered_movies:
        cols = st.columns(4)
        for i, movie in enumerate(filtered_movies):
            movie_details = fetch_movie_details(movie['id'])
            providers = fetch_movie_providers(movie['id'])['results'].get('US', {}).get('flatrate', [])
            providers_html = ''.join([f'<img src="{IMAGE_BASE_URL}{provider["logo_path"]}" class="provider-logo" alt="{provider["provider_name"]}">' for provider in providers if provider.get('logo_path')])
            with cols[i % 4]:
                st.markdown(f"""
                    <div class="movie-card">
                        <img src="{IMAGE_BASE_URL}{movie['poster_path']}" alt="{movie['title']} poster">
                        <div class="movie-info">
                            <h4>{movie['title']}</h4>
                            <p>Release Date: {format_date(movie['release_date'])}</p>
                            <p class="rating">{format_rating(movie['vote_average'])}</p>
                            <details>
                                <summary>More info</summary>
                                <p><strong>Overview:</strong> {movie_details['overview']}</p>
                                <p><strong>Genres:</strong> {format_genres(movie_details['genres'])}</p>
                            </details>
                        </div>
                        <div class="provider-logo-row">
                            {providers_html if providers_html else "<p>No providers available</p>"}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.write("No films found for the selected filters.")

# Streamlit app
st.sidebar.title("Menu")
page = st.sidebar.radio("Go to", ["Film Recommendations", "Discover New Films"])

if page == "Film Recommendations":
    recommendation_page()
else:
    filter_page()







