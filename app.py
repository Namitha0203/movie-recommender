import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import ast
import requests

import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import ast
import requests  # if you're using TMDB API

# 🔹 Add this block immediately after imports
st.markdown("""
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1524985069026-dd778a71c7b4");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: white; /* Makes all text white */
    }

    h1, h2, h3, h4, h5, h6, p, div, span {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 🔹 Overlay for readability
st.markdown("""
    <style>
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.6); /* white overlay with 60% opacity */
        z-index: -1;
    }
    </style>
    """, unsafe_allow_html=True)


#side bar

st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #f0f0f0;  /* Light gray background */
        color: black;
        padding: 20px;
        border-radius: 10px;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] h5,
    [data-testid="stSidebar"] h6,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p {
        color: black !important;
        font-family: 'Arial', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# 🔹 Genre dropdown styling
st.markdown("""
    <style>
    [data-testid="stSidebar"] select {
        font-family: 'Georgia', serif;
        font-size: 16px;
        color: black;
        background-color: #eaeaea;
        border-radius: 8px;
        padding: 6px;
        border: 1px solid #ccc;
    }
    </style>
    """, unsafe_allow_html=True)








# Load and process data
movies = pd.read_csv('movies.csv')
movies = movies[['id', 'title', 'overview', 'genres', 'keywords']]
movies.dropna(inplace=True)

def convert(obj):
    L = []
    for i in ast.literal_eval(obj):
        L.append(i['name'])
    return L

movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)
movies['tags'] = movies['overview'] + ' ' + movies['genres'].apply(lambda x: ' '.join(x)) + ' ' + movies['keywords'].apply(lambda x: ' '.join(x))
movies['tags'] = movies['tags'].apply(lambda x: x.lower())

cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(movies['tags']).toarray()
similarity = cosine_similarity(vectors)



def recommend(movie, genre_filter="All"):
    movie = movie.lower()
    if movie not in movies['title'].str.lower().values:
        return ["Movie not found in dataset."]
    
    index = movies[movies['title'].str.lower() == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    recommended = []
    for i in distances[1:]:
        title = movies.iloc[i[0]].title
        genres = movies.iloc[i[0]].genres
        if genre_filter == "All" or genre_filter in genres:
            recommended.append(title)
        if len(recommended) == 5:
            break
    return recommended




def fetch_poster(title):
    api_key = "9bf6c8d968ec3a70b8127769f9b06b0d"  # Replace with your actual TMDB API key
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={title}"
    response = requests.get(url)
    data = response.json()
    if data['results']:
        poster_path = data['results'][0].get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return None


# Streamlit UI .. move towards a side 
st.sidebar.title("🎬 Find Your Movie Match")
movie_name = st.sidebar.text_input("Enter a movie name:")
# 🔹 Add custom header to main area
st.markdown("<h1 style='text-align:center; font-family:Georgia;'>🎥 MovieMatch Recommender</h1>", unsafe_allow_html=True)

# Extract all unique genres
all_genres = sorted(set(g for sublist in movies['genres'] for g in sublist))

# Add genre filter to sidebar
selected_genre = st.sidebar.selectbox("🎞️ Choose a genre", ["All"] + all_genres)



 #Displays a title and input box

if movie_name:
    recommendations = recommend(movie_name, selected_genre)
    st.subheader(f"Movies similar to '{movie_name.title()}' in genre '{selected_genre}':")

   

    for title in recommendations:
        match = movies[movies['title'].str.lower() == title.lower()]
        if not match.empty:
            movie_data = match.iloc[0]
            poster_url = fetch_poster(movie_data.title)
            if poster_url:
                st.image(poster_url, width=200)
            st.markdown(f"### 🎬 {movie_data.title}")
            st.caption(movie_data.overview)
            st.markdown("---")
        else:
            st.markdown(f"### 🎬 {title}")
            st.caption("Overview not available.")
            st.markdown("---")

