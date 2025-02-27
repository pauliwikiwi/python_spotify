# SCRIPT PYTHON 

Proyecto de python que hace llamadas recursivas a la api de python para recoger la info de un artista y sus artistas relacionados.

## Requisitos
- Tener instalado Python
- Tener instalado pip
- Tener instalado MySQL
- Proyecto configurado en spotify

##Configuración de proyecto Spotify
Entra en la pagina de [Spotify API](https://developer.spotify.com/documentation/web-api)
Inicia sesión con tu cuenta de Spotify
Entra en el Dashboard y dale a `Create App`
Rellena los datos, son orientativos

##Creadenciales Spotify
Para sacar las credenciales que necesitaras en el script, deberas seleccionar este proyecto y te saldra una ventana con dicha información

>[!IMPORTANT]
>Antes de ejecutar el script debes crear una base de datos. O crearla a través del proyecto de php que va unico a este.

## Creacion de base de datos
```
CREATE TABLE artists (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    genres TEXT,
    popularity INT,
    followers INT
);

CREATE TABLE albums (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    artist_id VARCHAR(255),
    release_date DATE,
    total_tracks INT,
    FOREIGN KEY (artist_id) REFERENCES artists(id) ON DELETE CASCADE
);

CREATE TABLE tracks (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    album_id VARCHAR(255),
    artist_id VARCHAR(255),
    duration_ms INT,
    popularity INT,
    FOREIGN KEY (album_id) REFERENCES albums(id) ON DELETE CASCADE,
    FOREIGN KEY (artist_id) REFERENCES artists(id) ON DELETE CASCADE
);
```

# CONFIGURACION DEL SCRIPT

## Instalacion de dependencias
`pip install mysql-connector-python spotipy python-dotenv`

## Configuraciones
Agrega un archico `.env.py` al mismo directorio donde se encuentra el `main.py` y configura lo siguiente
```
SPOTIPY_CLIENT_ID=tu_spotify_client_id
SPOTIPY_CLIENT_SECRET=tu_spotify_client_secret

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=tu_usuario
MYSQL_PASSWORD=tu_contraseña
MYSQL_DATABASE=tu_base_de_datos
```

## Ejecutar el acript
El código requiere dos argumentos:

- ID del artista inicial de Spotify.
- Cantidad máxima de artistas a insertar.

Por terminal debemos ejecutar
`python main.py 790FomKkXshlbRYZFtlgla 10`

