import mysql.connector
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')

MYSQL_HOST = 'host.docker.internal'
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = 'spotify'

auth_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

conn = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE
)
cursor = conn.cursor()
artist_insert = 0
artist_list = []


def insert_artist(artist):
    global artist_insert  # Declarar que queremos usar la variable global
    artist_list.append(artist['name'])
    genres = ','.join(artist.get('genres', []))
    popularity = artist.get('popularity', None)
    followers_total = artist.get('followers', {}).get('total', None)
    cursor.execute('''INSERT IGNORE INTO artists (id, name, genres, popularity, followers)
                      VALUES (%s, %s, %s, %s, %s)''',
                   (artist['id'], artist['name'], genres, popularity, followers_total))
    conn.commit()
    artist_insert += 1


def insert_album(album, artist_id):
    cursor.execute('''INSERT IGNORE INTO albums (id, name, artist_id, release_date, total_tracks)
                      VALUES (%s, %s, %s, %s, %s)''',
                   (album['id'], album['name'], artist_id,
                    album['release_date'], album['total_tracks']))
    conn.commit()


def insert_track(track, album_id, artist_id):
    popularity = track.get('popularity', None)
    cursor.execute('''INSERT IGNORE INTO tracks (id, name, album_id, artist_id, duration_ms, popularity)
                      VALUES (%s, %s, %s, %s, %s, %s)''',
                   (track['id'], track['name'], album_id, artist_id,
                    track['duration_ms'], popularity))
    conn.commit()


def get_info_artist_related(id_artist):
    artist_releated = sp.artist_related_artists(id_artist)
    print(artist_releated)
    for artist in artist_releated:
        #insertar en bbdd los artistas
        if artist['name'] not in artist_list:
            insert_artist(artist)
        top_tracks = sp.artist_top_tracks(artist['id'], 'ES')
        for track in top_tracks:
            print(track)
            #insertar en bbdd las canciones
            album = track['album']
            insert_album(album, artist['id'])
            insert_track(track, album['id'], artist['id'])
        if artist_insert != 5000:
            get_info_artist_related(artist['id'])


# https://open.spotify.com/intl-es/artist/3bvfu2KAve4lPHrhEFDZna?si=cf1AGjrDSVWYegUwAIRlCg
get_info_artist_related('3bvfu2KAve4lPHrhEFDZna')

cursor.close()
conn.close()
