from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Initialize FastAPI app
app = FastAPI()

# Load the movie dataset
df = pd.read_csv('movies.csv')  # Make sure to have your dataset loaded
df = df.dropna()

df['combined_features'] = df['genre'] + ' ' + df['director'] + ' ' + df['actors'] + ' ' + df['plot']

# Vectorize text features
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['combined_features'])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)


# Request Model for Recommendation
class MovieRequest(BaseModel):
    title: str

# Request Model for Search
class SearchRequest(BaseModel):
    query: str
    type: Optional[str] = "title"  # Default to search by title

# Route to recommend movies
@app.post("/recommend")
async def recommend_movies(request: MovieRequest):
    title = request.title
    # Implement cosine similarity-based recommendation as before
    idx = df[df['title'] == df.title].index[0]

    # Compute similarity scores
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:3]  # Top 2 similar movies

    movie_indices = [i[0] for i in sim_scores]
    recommended_movies = df['title'].iloc[movie_indices].tolist()
    return {"recommendations": recommended_movies}

# Route to search movies by title, director, or genre
@app.post("/search")
async def search_movies(request: SearchRequest):
    query = request.query.lower()
    search_type = request.type.lower()

    if search_type == "title":
        results = df[df['title'].str.lower().str.contains(query)]
    elif search_type == "director":
        results = df[df['director'].str.lower().str.contains(query)]
    elif search_type == "genre":
        results = df[df['genre'].str.lower().str.contains(query)]
    else:
        raise HTTPException(status_code=400, detail="Invalid search type. Use 'title', 'director', or 'genre'.")

    if results.empty:
        raise HTTPException(status_code=404, detail="No movies found.")
    
    results = results.fillna('')
    
    # Convert results to list of dictionaries for JSON response
    movies_list = results[['title', 'year', 'genre', 'director']].to_dict(orient="records")
    return {"results": movies_list}

