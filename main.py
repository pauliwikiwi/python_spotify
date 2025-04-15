import mysql.connector
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException
import time
import sys
import os
from dotenv import load_dotenv
import json

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env.py'))

SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')

MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_PORT = os.getenv('MYSQL_PORT')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')

auth_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

conn = mysql.connector.connect(
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE
)
cursor = conn.cursor()
artist_insert = 0
artist_list = []

initial_id_artist = sys.argv[1]
max_artist = int(sys.argv[2])


def insert_artist(artist):
    print('insert ' + artist['name'])
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


def rate_limit_control(exc):
    if exc.http_status_code == 429:
        retry_after = exc.headers.get('Retry-After', 5)
        time.sleep(retry_after)
    else:
        raise exc


# Función para obtener información de artistas relacionados
def get_info_artist_related(id_artist, artist_list, artist_insert):
    try:
        # Obtener la información del artista original
        artist_data = sp.artist(id_artist)
        artist_name = artist_data["name"]

        # Buscar artistas similares usando el nombre del artista original
        search_results = sp.search(q=artist_name, type="artist", limit=10)

        for artist in search_results["artists"]["items"]:
            print(f"Procesando artista encontrado: {artist['name']}")

            # Verificar si el artista ya está en la lista o base de datos
            if artist['name'] not in artist_list:
                artist_list.append(artist['name'])  # Añadir a la lista local
                insert_artist(artist)  # Insertar artista en la base de datos
                artist_insert += 1

                print(f"Artistas insertados: {artist_insert}")

                # Pausa entre solicitudes para evitar rate limit
                time.sleep(2)

                # Obtener las canciones más populares en los países hispanohablantes
                countries = ["AR", "BO", "CL", "CO", "CR", "CU", "DO", "EC", "ES", "SV", "GQ", "GT", "HN", "MX", "NI",
                             "PA", "PY", "PE", "PR", "UY", "VE"]
                top_tracks = sp.artist_top_tracks(artist['id'], countries)

                for track in top_tracks['tracks']:
                    print(f"Insertando canción: {track['name']}")
                    album = track['album']
                    insert_album(album, artist['id'])  # Insertar el álbum en la base de datos
                    insert_track(track, album['id'], artist['id'])  # Insertar la canción en la base de datos

                # Limitar la cantidad de artistas a insertar
                if artist_insert >= max_artist:
                    print(f"Se alcanzó el límite de {max_artist} artistas insertados.")
                    sys.exit()

                # Pausa adicional entre artistas
                time.sleep(10)

                # Llamada recursiva para obtener más artistas usando la misma técnica
                get_info_artist_related(artist['id'], artist_list, artist_insert)

    except Exception as e:
        print(f"Error procesando artista {id_artist}: {e}")
        time.sleep(10)  # Esperar para evitar problemas de sobrecarga o rate limit



# Inicia el proceso con un artista inicial (ID)
#https://open.spotify.com/intl-es/artist/790FomKkXshlbRYZFtlgla?si=6E8DXg5AQH6-aojPQyk1Cw
get_info_artist_related(initial_id_artist, artist_list, artist_insert)

cursor.close()
conn.close()
