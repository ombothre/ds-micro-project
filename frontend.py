import streamlit as st
import requests

# Set up the Streamlit app
st.title("Movie Recommendation and Search System")

tab = st.sidebar.selectbox("Choose an action", ["Recommendations", "Search"])

def fetch_recommendations(movie_title):
    response = requests.post(
        "http://localhost:8000/recommend", 
        json={"title": movie_title}
    )
    return response.json()

def search_movies(query, search_type):
    response = requests.post(
        "http://localhost:8000/search", 
        json={"query": query, "type": search_type}
    )
    return response.json()

if tab == "Search":
    st.subheader("Search Movies")

    query = st.text_input("Enter search term (movie title, director, or genre)", "")

    search_type = st.selectbox("Search by", ["Title", "Director", "Genre"])
    
    if st.button("Search"):
        if query:
            try:
                search_type_lower = search_type.lower()
                search_results = search_movies(query, search_type_lower)

                if "results" in search_results:
                    st.subheader(f"Search results for '{query}' by {search_type_lower}:")
                    for movie in search_results["results"]:
                        st.write(f"**Title:** {movie['title']} | **Year:** {movie['year']} | **Genre:** {movie['genre']} | **Director:** {movie['director']}")
                else:
                    st.error("No movies found")
            except Exception as e:
                st.error(f"Error fetching search results: {e}")
        else:
            st.error("Please enter a search term")

elif tab == "Recommendations":
    st.subheader("Movie Recommendations")
    
    movie_title = st.text_input("Enter a movie title", "")

    if st.button("Get Recommendations"):
        if movie_title:
            try:
                recommendations = fetch_recommendations(movie_title)

                if "recommendations" in recommendations:
                    st.subheader(f"Movies similar to {movie_title}:")
                    for movie in recommendations["recommendations"]:
                        st.write(movie)
                else:
                    st.error("No recommendations found")
            except Exception as e:
                st.error(f"Error fetching recommendations: {e}")
        else:
            st.error("Please enter a movie title")
