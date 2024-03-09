from requests_html import HTMLSession
from bs4 import BeautifulSoup
import json
import time

def convert_duree_to_minutes(duree):
    try:
        total_minutes = 0
        parts = duree.split()
        for part in parts:
            if 'h' in part:
                heures = int(part.replace('h', ''))
                total_minutes += heures * 60
            elif 'min' in part:
                minutes = int(part.replace('min', ''))
                total_minutes += minutes
            else:
                # Gérer les cas où une partie de la durée n'est pas 'h' ou 'min'
                pass
        return total_minutes
    except ValueError:
        return None  # Erreur de conversion


def scrape_allocine_movies(base_url, num_pages):
    session = HTMLSession()
    all_movies = []

    for page_num in range(1, num_pages + 1):
        url = f"{base_url}?page={page_num}"

        response = session.get(url)
        response.html.render()

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            movies = []

            for movie_div in soup.select('div.card.entity-card'):
                try:
                    # Skip movie_div within a div with class "gd"
                    if movie_div.find_parent(class_='gd'):
                        continue

                    movie_info = {}

                    # Titre du film
                    titre_elem = movie_div.select_one('a.meta-title-link')
                    titre = titre_elem.text.strip() if titre_elem else "Titre non disponible"
                    movie_info['titre'] = titre

                    # Note de la presse
                    presse_score_elem = movie_div.select_one('.stareval-note')
                    presse_score = float(presse_score_elem.text.replace(',', '.')) if presse_score_elem and presse_score_elem.text != '--' else None
                    movie_info['press_score'] = presse_score

                    # Illustration du film
                    illustration_elem = movie_div.select_one('img.thumbnail-img')
                    if illustration_elem:
                        if illustration_elem.get('data-src'):
                            # Récupération à partir de data-src pour les séries autres que les deux premières
                            illustration_url = illustration_elem.get('data-src')
                        else:
                            # Récupération à partir de src pour les deux premières séries
                            illustration_url = illustration_elem.get('src', "Illustration non disponible")
                    else:
                        illustration_url = "Illustration non disponible"
                    movie_info['illustration_url'] = illustration_url

                    # Informations supplémentaires
                    meta_info_elem = movie_div.select_one('.meta-body-item.meta-body-info')
                    if meta_info_elem:
                        info_text = meta_info_elem.text.strip()
                        info_parts = info_text.split('|')
                        if len(info_parts) >= 3:
                            # Date de sortie et durée
                            movie_info['date_de_sortie'] = int(info_parts[0].strip().split()[-1])
                            duree = info_parts[1].strip()
                            movie_info['genres'] = [genre.strip() for genre in info_parts[2].split(',')]

                            # Conversion de la durée en minutes
                            movie_info['duree_en_minutes'] = convert_duree_to_minutes(duree)

                    # Synopsis du film
                    synopsis_elem = movie_div.select_one('.content-txt')
                    synopsis = synopsis_elem.text.strip() if synopsis_elem else "Synopsis non disponible"
                    movie_info['synopsis'] = synopsis

                    # Créateurs du film
                    createurs_elem = movie_div.select_one('.meta-body-item.meta-body-direction')
                    createurs = [a.text.strip() for a in createurs_elem.select('.dark-grey-link')] if createurs_elem else []
                    movie_info['createurs'] = createurs

                    # Acteurs du film
                    acteurs_elem = movie_div.select_one('.meta-body-item.meta-body-actor')
                    acteurs = [a.text.strip() for a in acteurs_elem.select('.dark-grey-link')] if acteurs_elem else []
                    movie_info['acteurs'] = acteurs

                    movies.append(movie_info)

                    # Genre de l'oeuvre
                    movie_info['genre_oeuvre'] = "film"

                except Exception as e:
                    print(f"Erreur lors du traitement d'un film : {e}")

            all_movies.extend(movies)
            time.sleep(0.5)
            print(f"Page {page_num} effectuée sur {num_pages}")
        else:
            print(f"Erreur : {response.status_code} pour la page {page_num}")

    return all_movies

if __name__ == "__main__":
    allocine_base_url = "https://www.allocine.fr/films/"
    num_pages_to_scrape = 7854

    top_movies = scrape_allocine_movies(allocine_base_url, num_pages_to_scrape)

    if top_movies:
        for movie in top_movies:
            # Supprimer la clé 'duree' du dictionnaire movie_info
            if 'duree' in movie:
                del movie['duree']
        
        with open('allocine_top_movies.json', 'w', encoding='utf-8') as json_file:
            json.dump(top_movies, json_file, ensure_ascii=False, indent=4)
        print("Les informations des films ont été stockées dans allocine_top_movies.json.")
    else:
        print("Aucune donnée n'a été récupérée. Vérifiez le script pour des messages d'erreur.")
