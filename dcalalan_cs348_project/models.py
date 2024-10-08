from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from database import Base

"""
I've been trying to finalize my plan/layout for my project application. I was wondering if I could run my idea by you to see if it's be suitable and
to avoid any issues later when I'm developing.

Basically, I'm thinking of making an application similar to Spotify. A platform that allowed music and tracks to be shared. The two types of users that can
access the application are the artists, and listeners. Artists can add new tracks and albums they make to their discography. While listeners can choose tracks and
albums to add to their own collections (playlists).

For the report requirement, artists can choose to form a report showing information on the how popular their tracks are (which tracks are added to playlists
more, etc.). I'm a little confused reading the requirement on whether we should have one report for each user type? Or just one report in general. Regardless,
if I need one for listeners my report could be a large overview of all their playlists, as well as most commonly chosen artists and things related to this.

Schema:
Artists(artist_id, artist_name)
Listeners(user_id, username)
Tracks(track_id, track_name, album_id, genre)
Albums(album_id, album_name, artist_id)
Genres(genre)
Playlists(playlist_id, playlist_name, user_id)
Playlist_Tracks(playlist_id, track_id)
"""

class Artists(Base):
    __tablename__ = 'artists'

    artist_id = Column(Integer, primary_key=True, index=True)
    artist_name = Column(String(50), unique=True)

class Listeners(Base):
    __tablename__ = 'listeners'

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)

class Tracks(Base):
    __tablename__ = 'tracks'

    track_id = Column(Integer, primary_key=True, index=True)
    track_name = Column(String(50))
    album_id = Column(Integer, ForeignKey('albums.album_id'))
    genre = Column(String(50), ForeignKey('genres.genre'))

class Albums(Base):
    __tablename__ = 'albums'

    album_id = Column(Integer, primary_key=True, index=True)
    album_name = Column(String(50))
    artist_id = Column(Integer, ForeignKey('artists.artist_id'))

class Genres(Base):
    __tablename__ = 'genres'

    genre = Column(String(50), primary_key=True)

class Playlists(Base):
    __tablename__ = 'playlists'

    playlist_id =  Column(Integer, primary_key=True, index=True)
    playlist_name = Column(String(100))
    user_id = Column(Integer, ForeignKey('listeners.user_id'))

class Playlist_Tracks(Base):
    __tablename__ = 'playlist_tracks'

    playlist_id = Column(Integer, ForeignKey('playlists.playlist_id'), primary_key=True)
    track_id = Column(Integer, ForeignKey('tracks.track_id'), primary_key=True)