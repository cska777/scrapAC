import json

# Charger le fichier JSON généré par votre script
with open('allocine_top_movies.json', 'r', encoding='utf-8') as json_file:
    top_movies = json.load(json_file)

# Initialiser un ensemble pour stocker les genres uniques
unique_genres = set()

# Parcourir la liste des films et extraire les genres uniques
for movie in top_movies:
    genres = movie.get('genres', [])
    unique_genres.update(genres)

# Convertir l'ensemble en liste pour faciliter la manipulation
unique_genres_list = list(unique_genres)

# Afficher la liste des genres uniques
print(unique_genres_list)