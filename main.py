"""
Creates a Spotify Playlist based on the Top-40 playlist of Q-music. (https://qmusic.be/hitlijsten/q-top-40)

When Q-music shares a new Top-40 the program gets executed and checks whether the playlist has 40 tracks. It uses the Q-music api.
When it does, it searches spotify to get all te correct songs, and adds this to the playlist.

When it gets fully updated the description of the playlist changes to the last updated date.
"""

import requests
import os
import os.path
import datetime
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()
spot_client = os.getenv('spot_client')
spot_key = os.getenv('spot_key')
username = os.getenv('username')


scope = 'playlist-modify-public playlist-modify-private playlist-read-private'

token = SpotifyOAuth(scope=scope, username=username, client_secret=spot_key, client_id=spot_client)

spotify = spotipy.Spotify(auth_manager=token)

url_get_editions = os.getenv('url_get_editions')
url_get_top40 = os.getenv('url_get_top40')
playlist_id = os.getenv('playlist_id')


def get_latest_editions() -> dict:
    """
    Checks the id of the latest update. When this is the same as the previous execution the program gets canceled
    :return: The latest id of the most recent top-40
    """
    try:
        editons = requests.get(url_get_editions).json()
        last_edition = editons['editions'][0]

        if os.path.isfile('last.txt'):
            f = open('last.txt', 'r')
            last_version = f.read()
            if last_version == str(last_edition['id']):
                print('Version not updated\nQuiting Program..')
                f.close()
                exit()

    except Exception as e:
        print(e)
        print('ERROR getting edition Q-Top 40')
    return last_edition


def get_top40(last_edition: dict) -> list:
    """
    Contacts the api to get all the latest tracks in the top-40.
    When there are not 40 tracks the program gets canceled

    :param last_edition: The id from the top-40 ranking
    :return: All 40 tracks in the latest top-40
    """
    top40 = []
    try:
        response = requests.get(url_get_top40.format(last_edition["id"]))
        top40 = response.json()['tracks']
        if len(top40) != 40:
            print(f'Geen 40 tracks gevonden ({len(top40)})\nQuiting Program')
            exit()
        print('40 tracks gevonden')
    except Exception as e:
        print(e)
        print(f'ERROR getting last edition with id {last_edition["id"]} op datum {last_edition["name"]}')
    return top40


def clear_playlist() -> None:
    """
    Removes all current songs in the top-40 playlist on spotify using the Spotify API
    :return: None
    """
    # Get current songs in playlist
    current_songs = spotify.playlist_items(playlist_id)
    track_ids = list(map(lambda t: t['track']['id'], current_songs['items']))

    # remove all songs
    spotify.playlist_remove_all_occurrences_of_items(playlist_id, track_ids)


def search_track(title: str, artist: str) -> str:
    """
    When there is no Spotify url mentioned in the api, this method searches Spotify to get the correct link to the track.
    :param title: Title of the track
    :param artist: Artist of the track
    :return: The correct spotify-link to the track
    """
    result = spotify.search(q=f'{title} {artist}')
    return result['tracks']['items'][0]['id']


def add_songs_to_playlist(top40: list) -> None:
    """
    Adds all tracks to the Spotify playlist
    :param top40: top 40 from api
    :return: None
    """
    def get_trackid_from_spoturl(track):
        """
        Gets track id from api, or searches it when not mentioned.
        :param track: track in api
        :return: Track id
        """
        if 'spotify_url' in track.keys():
            if track['spotify_url'].split('/')[-1] is not None:
                return track['spotify_url'].split('/')[-1][0:22]
        print(f'{top40.index(track) + 1}. ' + track['title'] + ' - ' + track['artist']['name'])
        return search_track(track['title'], track['artist']['name'])

    track_ids = list(map(get_trackid_from_spoturl, top40))
    track_ids = filter(lambda t: t is not None, track_ids)
    spotify.playlist_add_items(playlist_id=playlist_id, items=track_ids)


def change_description() -> None:
    """
    Updates description on Spotify playlist to the latest update date.
    :return: None
    """
    now = datetime.datetime.now()
    spotify.playlist_change_details(playlist_id=playlist_id, description=f'De beste hits van het moment in België met wekelijkse updates.  (laatste update: {now.strftime("%d/%m/%Y %H:%M:%S")})')


def save_new_version(latest: dict) -> None:
    """
    Saved the latest id in a local file.
    :param latest: latest from api
    :return: None
    """
    f = open('last.txt', 'w')
    f.write(str(latest['id']))
    f.close()


if __name__ == '__main__':
    latest: dict = get_latest_editions()
    print('Updating Playlist')
    top40 = get_top40(latest)
    clear_playlist()
    add_songs_to_playlist(top40)
    change_description()
    save_new_version(latest)