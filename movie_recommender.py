import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import ast


# Load dataset
movies = pd.read_csv('movies.csv')

# Check the first few rows
print(movies.head())

# Select relevant columns
movies = movies[['id', 'title', 'overview', 'genres', 'keywords']]
movies.dropna(inplace=True)

# Convert stringified lists to actual Python lists
def convert(obj):
    L = []
    for i in ast.literal_eval(obj):
        L.append(i['name'])
    return L

movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)

# Combine overview, genres, and keywords into one string
movies['tags'] = movies['overview'] + ' ' + movies['genres'].apply(lambda x: ' '.join(x)) + ' ' + movies['keywords'].apply(lambda x: ' '.join(x))

# Convert tags to lowercase
movies['tags'] = movies['tags'].apply(lambda x: x.lower())

# Vectorize tags
cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(movies['tags']).toarray()

# Compute similarity matrix
similarity = cosine_similarity(vectors)

def recommend(movie):
    movie = movie.lower()
    if movie not in movies['title'].str.lower().values:
        print("Movie not found in dataset.")
        return
    index = movies[movies['title'].str.lower() == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    print(f"\nMovies similar to '{movie.title()}':")
    for i in distances[1:6]:
        print(movies.iloc[i[0]].title)

while True:
    user_input = input("\nEnter a movie name (or type 'exit' to quit): ")
    if user_input.lower() == 'exit':
        break
    recommend(user_input)




#it is just to just
#recommend('Avatar')
