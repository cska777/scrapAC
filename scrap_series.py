from requests_html import HTMLSession
from bs4 import BeautifulSoup
import json
import time

def convert_duree_to_minutes(duree):
    try:
        if 'h' in duree and 'min' in duree:
            heures, minutes = map(int, duree.replace('h', '').replace('min', '').split())
            return heures * 60 + minutes
        elif 'h' in duree:
            heures = int(duree.replace('h', '').strip())
            return heures * 60
        elif 'min' in duree:
            minutes = int(duree.replace('min', '').strip())
            return minutes
        else:
            return None
    except ValueError:
        return None

def scrape_allocine_series(base_url, num_pages):
    session = HTMLSession()
    all_series = []

    for page_num in range(1, num_pages + 1):
        url = f"{base_url}?page={page_num}"

        response = session.get(url)
        response.html.render()

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            series = []

            for series_div in soup.select('div.card.entity-card'):
                try:
                    series_info = {}

                    # Titre de la série
                    titre_elem = series_div.select_one('a.meta-title-link')
                    titre = titre_elem.text.strip() if titre_elem else "Titre non disponible"
                    series_info['titre'] = titre

                    # Note de la presse
                    presse_score_elem = series_div.select_one('.stareval-note')
                    presse_score = float(presse_score_elem.text.replace(',', '.')) if presse_score_elem and presse_score_elem.text != '--' else None
                    series_info['press_score'] = presse_score

                    # Illustration de la série
                    illustration_elem = series_div.select_one('img.thumbnail-img')
                    # Illustration de la série
                    if illustration_elem:
                        if illustration_elem.get('data-src'):
                            # Récupération à partir de data-src pour les séries autres que les deux premières
                            illustration_url = illustration_elem.get('data-src')
                        else:
                            # Récupération à partir de src pour les deux premières séries
                            illustration_url = illustration_elem.get('src', "Illustration non disponible")
                    else:
                        illustration_url = "Illustration non disponible"
                    series_info['illustration_url'] = illustration_url

                    # Informations supplémentaires
                    meta_info_elem = series_div.select_one('.meta-body-item.meta-body-info')
                    if meta_info_elem:
                        info_text = meta_info_elem.text.strip()
                        info_parts = info_text.split('|')
                        if len(info_parts) >= 3:
                            # Transforme la date de sortie en entier (année)
                            series_info['date_de_sortie'] = int(info_parts[0].strip().split()[-1])
                            series_info['duree'] = info_parts[1].strip()
                            series_info['genres'] = [genre.strip() for genre in info_parts[2].split(',')]

                    # Synopsis de la série
                    synopsis_elem = series_div.select_one('.content-txt')
                    synopsis = synopsis_elem.text.strip() if synopsis_elem else "Synopsis non disponible"
                    series_info['synopsis'] = synopsis

                    # Conversion de la durée en minutes
                    series_info['duree_moyenne_episode'] = convert_duree_to_minutes(series_info['duree'])

                    # Garder uniquement la durée par épisode
                    series_info.pop('duree')

                    # Créateurs de la série
                    createurs_elem = series_div.select_one('.meta-body-item.meta-body-direction')
                    createurs = [a.text.strip() for a in createurs_elem.select('.dark-grey-link')] if createurs_elem else []
                    series_info['createurs'] = createurs

                    # Acteurs de la série
                    acteurs_elem = series_div.select_one('.meta-body-item.meta-body-actor')
                    acteurs = [a.text.strip() for a in acteurs_elem.select('.dark-grey-link')] if acteurs_elem else []
                    series_info['acteurs'] = acteurs

                    series.append(series_info)

                    # Genre de l'oeuvre
                    series_info['genre_oeuvre'] = "serie"

                except Exception as e:
                    print(f"Erreur lors du traitement d'une série : {e}")

            all_series.extend(series)
            time.sleep(0.5)
            print(f"Page {page_num} effectuée sur {num_pages}")
        else:
            print(f"Erreur : {response.status_code} pour la page {page_num}")

    return all_series

if __name__ == "__main__":
    allocine_base_url = "https://www.allocine.fr/series-tv/"
    num_pages_to_scrape = 1344

    top_series = scrape_allocine_series(allocine_base_url, num_pages_to_scrape)

    if top_series:
        with open('allocine_top_series.json', 'w', encoding='utf-8') as json_file:
            json.dump(top_series, json_file, ensure_ascii=False, indent=4)
        print("Les informations des séries ont été stockées dans allocine_top_series.json.")
    else:
        print("Aucune donnée n'a été récupérée. Vérifiez le script pour des messages d'erreur.")
