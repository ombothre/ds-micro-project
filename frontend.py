import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Set up the Streamlit app
st.title("Movie Recommendation and Search System")

tab = st.sidebar.selectbox("Choose an action", ["Recommendations", "Search"])

# Load the movie dataset
df = pd.read_csv('movies.csv')  # Make sure your dataset is available
df = df.dropna()
df['combined_features'] = df['genre'] + ' ' + df['director'] + ' ' + df['actors'] + ' ' + df['plot']

# Vectorize text features
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['combined_features'])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Fetch recommendations locally
def fetch_recommendations(movie_title):
    try:
        idx = df[df['title'].str.lower() == movie_title.lower()].index[0]
        # Compute similarity scores
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:3]  # Top 2 similar movies

        movie_indices = [i[0] for i in sim_scores]
        recommended_movies = df['title'].iloc[movie_indices].tolist()
        return {"recommendations": recommended_movies}
    except IndexError:
        return {"error": "Movie not found"}

# Search for movies locally
def search_movies(query, search_type):
    query = query.lower()
    search_type = search_type.lower()

    if search_type == "title":
        results = df[df['title'].str.lower().str.contains(query)]
    elif search_type == "director":
        results = df[df['director'].str.lower().str.contains(query)]
    elif search_type == "genre":
        results = df[df['genre'].str.lower().str.contains(query)]
    else:
        return {"error": "Invalid search type. Use 'title', 'director', or 'genre'."}

    if results.empty:
        return {"error": "No movies found."}

    results = results.fillna('')
    movies_list = results[['title', 'year', 'genre', 'director']].to_dict(orient="records")
    return {"results": movies_list}

if tab == "Search":
    st.subheader("Search Movies")

    query = st.text_input("Enter search term (movie title, director, or genre)", "")
    search_type = st.selectbox("Search by", ["Title", "Director", "Genre"])
    
    if st.button("Search"):
        if query:
            search_type_lower = search_type.lower()
            search_results = search_movies(query, search_type_lower)

            if "results" in search_results:
                st.subheader(f"Search results for '{query}' by {search_type_lower}:")
                for movie in search_results["results"]:
                    st.write(f"**Title:** {movie['title']} | **Year:** {movie['year']} | **Genre:** {movie['genre']} | **Director:** {movie['director']}")
            elif "error" in search_results:
                st.error(search_results["error"])
        else:
            st.error("Please enter a search term")

elif tab == "Recommendations":
    st.subheader("Movie Recommendations")
    
    movie_title = st.text_input("Enter a movie title", "")

    if st.button("Get Recommendations"):
        if movie_title:
            recommendations = fetch_recommendations(movie_title)

            if "recommendations" in recommendations:
                st.subheader(f"Movies similar to {movie_title}:")
                for movie in recommendations["recommendations"]:
                    st.write(movie)
            elif "error" in recommendations:
                st.error(recommendations["error"])
        else:
            st.error("Please enter a movie title")
