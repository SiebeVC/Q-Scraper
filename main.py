import requests
import os
import datetime
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()
spot_client = os.getenv('spot_client')
spot_key = os.getenv('spot_key')

# spotify = spotipy.Spotify(
#     client_credentials_manager=SpotifyClientCredentials(client_id=spot_client,client_secret=spot_key),
#     scope='playlist-modify-public')

scope = 'playlist-modify-public playlist-modify-private playlist-read-private'
username = 'siebevc'

token = SpotifyOAuth(scope=scope, username=username, client_secret=spot_key, client_id=spot_client)

spotify = spotipy.Spotify(auth_manager=token)

url_get_editions = os.getenv('url_get_editions')
url_get_top40 = os.getenv('url_get_top40')
playlist_id = os.getenv('playlist_id')


def get_latest_editions():
    try:
        editons = requests.get(url_get_editions).json()
        last_edition = editons['editions'][0]
    except Exception as e:
        print(e)
        print('ERROR getting edition Q-Top 40')
    return last_edition


def get_top40(last_edition):
    try:
        response = requests.get(url_get_top40.format(last_edition["id"]))
        top40 = response.json()['tracks']
    except Exception as e:
        print(e)
        print(f'ERROR getting last edition with id {last_edition["id"]} op datum {last_edition["name"]}')
    return top40


def clear_playlist():
    # Get current songs in playlist
    current_songs = spotify.playlist_items(playlist_id)
    track_ids = list(map(lambda t: t['track']['id'], current_songs['items']))

    # remove all songs
    spotify.playlist_remove_all_occurrences_of_items(playlist_id, track_ids)


def search_track(title, artist):
    result = spotify.search(q=f'{title} {artist}')
    return result['tracks']['items'][0]['id']


def add_songs_to_playlist(top40):
    def get_trackid_from_spoturl(track):
        if 'spotify_url' in track.keys():
            if track['spotify_url'].split('/')[-1] is not None:
                return track['spotify_url'].split('/')[-1][0:22]
        print(f'{top40.index(track) + 1}. ' + track['title'] + ' - ' + track['artist']['name'])
        return search_track(track['title'], track['artist']['name'])


    track_ids = list(map(get_trackid_from_spoturl, top40))
    track_ids = filter(lambda t: t is not None, track_ids)
    spotify.playlist_add_items(playlist_id=playlist_id, items=track_ids)


def change_description():
    now = datetime.datetime.now()
    spotify.playlist_change_details(playlist_id=playlist_id, description=f'De beste hits van het moment in België met wekelijkse updates.  (laatste update: {now.strftime("%m/%d/%Y %H:%M:%S")})')


if __name__ == '__main__':
    latest = get_latest_editions()
    top40 = get_top40(latest)
    clear_playlist()
    add_songs_to_playlist(top40)
    change_description()