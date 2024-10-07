from sqlalchemy import Boolean, Column, Integer, String
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