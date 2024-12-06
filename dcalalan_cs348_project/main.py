"""Main script for running the project

CD INTO DIRECTORY FIRST
Run with `uvicorn main:app --reload`
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine, session_local
from sqlalchemy.orm import Session
from sqlalchemy import text
import sqlalchemy
import pandas as pd
import duckdb

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class ArtistsBase(BaseModel):
        artist_name: str

class ListenersBase(BaseModel):
        username: str

class TracksBase(BaseModel):
        track_name: str
        album_id: int
        genre: str

class AlbumsBase(BaseModel):
        album_name: str
        artist_id: int

#class GenresBase(BaseModel):
        # Empty???

class PlaylistsBase(BaseModel):
        playlist_name: str
        user_id: int

#class PlaylistTracksBase(BaseModel):
        # Also Empty???

def get_db():
        db = session_local()
        try:
                yield db
        finally:
                db.close()

db_dependency = Annotated[Session, Depends(get_db)]
        
@app.get("/", status_code=status.HTTP_200_OK)
async def list_all_tracks(db:db_dependency):
        all_tracks = db.query(models.Tracks).all()

        # Create an empty DataFrame with the desired columns
        df = pd.DataFrame(columns=['track_id', 'track_name', 'album_id', 'artist_id', 'genre'])

        track_dfs = [pd.DataFrame({'track_id': track.track_id,
                                'track_name': track.track_name,
                                'album_id': track.album_id,
                                'artist_id': track.artist_id,
                                'genre': track.genre}, index=[0]) for track in all_tracks]

        df = pd.concat(track_dfs, ignore_index=True)

        df.to_html('./html_files/basic.html', index=False)

        # Instantiate playlists tables as of now
        all_playlists = db.query(models.Playlists).all()

        if (not all_playlists):
               playlist_df = pd.DataFrame(columns=['playlist_id', 'playlist_name', 'user_id'])
        else:

                # Create an empty DataFrame with the desired columns
                playlist_df = pd.DataFrame(columns=['playlist_id', 'playlist_name', 'user_id'])

                playlists_dfs = [pd.DataFrame({'playlist_id': playlist.playlist_id,
                                        'playlist_name': playlist.playlist_name,
                                        'user_id': playlist.user_id}, index=[0]) for playlist in all_playlists]

                playlist_df = pd.concat(playlists_dfs, ignore_index=True)

        playlist_df.to_html('./html_files/playlist.html', index=False)

        # Open root html page
        try:
                with open('./html_files/root.html', 'r') as f:
                        root = f.read()

                return HTMLResponse(content=root, status_code=200)
                #return templates.TemplateResponse("root.html", {"all_playlists": all_playlists})
        
        except FileNotFoundError as e:
                raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")
        except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error reading files: {str(e)}")

@app.get("/main_table", response_class=HTMLResponse)
async def main_table(db:db_dependency):
        all_tracks = db.query(models.Tracks).all()
        all_albums = db.query(models.Albums).all()
        all_artists = db.query(models.Artists).all()
        all_genres = db.query(models.Genres).all()
        all_playlists = db.query(models.Playlists).all()
        all_listeners = db.query(models.Listeners).all()

        try:
                # Read main.html
                with open("./html_files/main.html", "r") as main_file:
                        main_content = main_file.read()
                
                # Read basic.html
                with open("./html_files/basic.html", "r") as basic_file:
                        basic_content = basic_file.read()

                # Create dropdown options for tracks
                track_options = ""
                for track in all_tracks:
                        track_options += f"<option value='{track.track_id}'>{track.track_name}</option>"

                track_id_options = ""
                for track in all_tracks:
                        track_id_options += f"<option value='{track.track_id}'>{track.track_id}</option>"

                # Create dropdown options for albums
                album_options = ""
                for album in all_albums:
                        album_options += f"<option value='{album.album_id}'>{album.album_name}</option>"
                
                # Create dropdown options for artists
                artist_options = ""
                for artist in all_artists:
                        artist_options += f"<option value='{artist.artist_id}'>{artist.artist_name}</option>"

                # Create dropdown options for genres
                genre_options = ""
                for genre in all_genres:
                        genre_options += f"<option value='{genre.genre}'>{genre.genre}</option>"

                playlist_options = ""
                for playlist in all_playlists:
                        playlist_options += f"<option value='{playlist.playlist_id}'>{playlist.playlist_name}</option>"

                listener_options = ""
                for listener in all_listeners:
                        listener_options += f"<option value='{listener.user_id}'>{playlist.user_id}</option>"
                
                # Find the closing </body> tag and insert basic_content before it
                merged_content = main_content.replace("</body>", f"""
                <div class="data-content">
                        <h3>For Artists: Add to database</h3>
                        <form method="POST" action="/added_tracks">
                                <label for="track_name">Track Name:</label>
                                <input type="text" id="track_name" name="track_name">
                                <select name="album_to_add_to">
                                {album_options}
                                </select>
                                <select name="artist_to_add_to">
                                {artist_options}
                                </select>
                                <select name="genre_to_add_to">
                                {genre_options}
                                </select>
                                <input type="submit" value="Add Track...">
                        </form>

                        <form method="POST" action="/added_album">
                                <label for="album_name">Album Name:</label>
                                <input type="text" id="album_name" name="album_name">
                                <select name="artist_to_add_to">
                                {artist_options}
                                </select>
                                <input type="submit" value="Add Album...">
                        </form>

                        <form method="POST" action="/added_artist">
                                <label for="artist_name">Artist Name:</label>
                                <input type="text" id="artist_name" name="artist_name">
                                <input type="submit" value="Add Artist...">
                        </form>

                        <h3>For Artists: Delete from database</h3>
                        <form method="POST" action="/delete_track">
                                <label for="track_to_delete">Track to Delete:</label>
                                <select name="track_to_delete" id="track_to_delete">
                                {track_options}
                                </select>
                                <input type="submit" value="Delete Track">
                        </form>

                        <h3>For Artists: Update from database</h3>
                        <form method="POST" action="/update_track">
                                <label for="track_to_update">Track to Update:</label>
                                <select name="track_to_update" id="track_to_update">
                                {track_id_options}
                                </select>
                                <label for="new_track_name">New Track Name:</label>
                                <input type="text" id="new_track_name" name="new_track_name">
                                <label for="new_album_id">New Album ID:</label>
                                <input type="text" id="new_album_id" name="new_album_id">
                                <label for="new_genre">New Genre:</label>
                                <select name="new_genre" id="new_genre">
                                        <option value="">Select Genre</option>
                                        {genre_options}
                                </select>
                                <input type="submit" value="Update Track">
                        </form>

                        <h3>For Users: Add New Playlist</h3>
                        <form method="POST" action="/added_playlist">
                                <label for="playlist_name">Playlist Name:</label>
                                <input type="text" id="playlist_name" name="playlist_name">
                                <label for="user_id">User ID:</label>
                                <select name="user_id">
                                <option value="">Select User</option>
                                {listener_options}
                                </select>
                                <input type="submit" value="Add Playlist...">
                        </form>

                        <h3>For Users: Add to Playlist</h3>
                        <form method="POST" action="/added_to_playlist">
                                <label for="playlist_name">Playlist Name:</label>
                                <select name="playlist_to_add_to">
                                {playlist_options}
                                </select>
                                <label for="track">Select Track:</label>
                                <select name="track" id="track">
                                        <option value="">Select Track</option>
                                        {track_options}
                                </select>
                                <input type="submit" value="Add to Playlist...">
                        </form>
                                                      
                        {basic_content}

                        <h3>For Artists: View report</h3>
                        <a href="/report" class="btn btn-primary">View report</a>

                </div>
                </body>""")

                return merged_content
                
        except FileNotFoundError as e:
                raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")
        except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error reading files: {str(e)}")

@app.get("/report")
async def report(request: Request, db:db_dependency):
        try:
                result = db.execute(sqlalchemy.sql.text('CALL TopTracksPerArtist()'))

                df = pd.DataFrame(columns=['artist_name', 'most_popular_track', 'playlist_count'])

                for artist, track, count in result.fetchall():
                        df = df._append({'artist_name': artist, 'most_popular_track': track, 'playlist_count': count}, ignore_index=True)

                print(df)

                html_table = df.to_html(index=False)

                # Create HTML response
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                <title>Report</title>
                </head>
                <body>
                <h1>Report</h1>
                <h2>This report shows each artists' most popular track and the number of times it was added to a playlist.</h2>
                <h2>Multiple instances of an artist indicates a tie in their most popular track.</h2>
                <table>
                        {html_table}
                </table>
                <br>
                <a href="/main_table">Return to Main Table</a> 
                </body>
                </html>
                """

                return HTMLResponse(content=html_content)
        except Exception as e:
                db.rollback()
                raise HTTPException(status_code=500, detail=str(e))

@app.post("/added_playlist")
async def added_playlist(request: Request, db:db_dependency, playlist_name: str = Form(...), user_id: str = Form(...)):

        try:
                new_playlist = models.Playlists(playlist_name = playlist_name, user_id = user_id)

                db.add(new_playlist)
                db.commit()
                db.refresh(new_playlist)

                return RedirectResponse(url="/main_table", status_code=status.HTTP_303_SEE_OTHER)

        except Exception as e:
                db.rollback()
                raise HTTPException(status_code=500, detail=str(e))
        
@app.post("/added_to_playlist")
async def added_to_playlist(request: Request, db:db_dependency, playlist_to_add_to: str = Form(...), track: str = Form(...)):

        try:
                new_playlist_track = models.Playlist_Tracks(playlist_id = playlist_to_add_to, track_id = track)

                db.add(new_playlist_track)
                db.commit()
                db.refresh(new_playlist_track)

                return RedirectResponse(url="/main_table", status_code=status.HTTP_303_SEE_OTHER)

        except Exception as e:
                db.rollback()
                raise HTTPException(status_code=500, detail=str(e))


@app.post("/added_tracks")
async def added_tracks(request: Request, db:db_dependency, track_name: str = Form(...), album_to_add_to: str = Form(...), artist_to_add_to: str = Form(...),
                        genre_to_add_to: str = Form(...)):
       
        try:
                new_track = models.Tracks(track_name = track_name, album_id = album_to_add_to, artist_id = artist_to_add_to, genre = genre_to_add_to)

                db.add(new_track)
                db.commit()
                db.refresh(new_track)

                all_tracks = db.query(models.Tracks).all()

                # Create an empty DataFrame with the desired columns
                df = pd.DataFrame(columns=['track_id', 'track_name', 'album_id', 'artist_id', 'genre'])

                track_dfs = [pd.DataFrame({'track_id': track.track_id,
                                        'track_name': track.track_name,
                                        'album_id': track.album_id,
                                        'artist_id': track.artist_id,
                                        'genre': track.genre}, index=[0]) for track in all_tracks]

                df = pd.concat(track_dfs, ignore_index=True)

                df.to_html('./html_files/basic.html', index=False)

                return RedirectResponse(url="/main_table", status_code=status.HTTP_303_SEE_OTHER)

        except Exception as e:
                db.rollback()
                raise HTTPException(status_code=500, detail=str(e))
        
@app.post("/added_album")
async def added_album(request: Request, db:db_dependency, album_name: str = Form(...), artist_to_add_to: str = Form(...)):
       
        try:
                new_album = models.Albums(album_name = album_name, artist_id = artist_to_add_to)

                db.add(new_album)
                db.commit()
                db.refresh(new_album)

                return RedirectResponse(url="/main_table", status_code=status.HTTP_303_SEE_OTHER)

        except Exception as e:
                db.rollback()
                raise HTTPException(status_code=500, detail=str(e))
        
@app.post("/added_artist")
async def added_artist(request: Request, db:db_dependency, artist_name: str = Form(...)):
       
        try:
                new_artist = models.Artists(artist_name = artist_name)

                db.add(new_artist)
                db.commit()
                db.refresh(new_artist)

                return RedirectResponse(url="/main_table", status_code=status.HTTP_303_SEE_OTHER)

        except Exception as e:
                db.rollback()
                raise HTTPException(status_code=500, detail=str(e))
        
@app.post("/delete_track")
async def delete_track(request: Request, db:db_dependency, track_to_delete: str = Form(...)):
       
        try:
                track_to_delete = db.query(models.Tracks).filter(models.Tracks.track_id == track_to_delete).first()
                #print(track_to_delete)

                db.delete(track_to_delete)
                db.commit()

                all_tracks = db.query(models.Tracks).all()

                # Create an empty DataFrame with the desired columns
                df = pd.DataFrame(columns=['track_id', 'track_name', 'album_id', 'artist_id', 'genre'])

                track_dfs = [pd.DataFrame({'track_id': track.track_id,
                                        'track_name': track.track_name,
                                        'album_id': track.album_id,
                                        'artist_id': track.artist_id,
                                        'genre': track.genre}, index=[0]) for track in all_tracks]

                df = pd.concat(track_dfs, ignore_index=True)

                df.to_html('./html_files/basic.html', index=False)

                return RedirectResponse(url="/main_table", status_code=status.HTTP_303_SEE_OTHER)

        except Exception as e:
                db.rollback()
                raise HTTPException(status_code=500, detail=str(e))
        
@app.post("/update_track")
async def update_track(request: Request, db:db_dependency,
                       track_to_update: str = Form(...),
                       new_track_name: str = Form(None),
                       new_album_id: str = Form(None),
                       new_genre: str = Form(None)):

        try:

                track_to_update = db.query(models.Tracks).filter(models.Tracks.track_id == track_to_update).first()

                if new_track_name:
                        track_to_update.track_name = new_track_name
                if new_album_id:
                        track_to_update.album_id = new_album_id
                if new_genre:
                        track_to_update.genre = new_genre
                db.commit() 

                all_tracks = db.query(models.Tracks).all()

                # Create an empty DataFrame with the desired columns
                df = pd.DataFrame(columns=['track_id', 'track_name', 'album_id', 'artist_id', 'genre'])

                track_dfs = [pd.DataFrame({'track_id': track.track_id,
                                        'track_name': track.track_name,
                                        'album_id': track.album_id,
                                        'artist_id': track.artist_id,
                                        'genre': track.genre}, index=[0]) for track in all_tracks]

                df = pd.concat(track_dfs, ignore_index=True)

                df.to_html('./html_files/basic.html', index=False)


                return RedirectResponse(url="/main_table", status_code=status.HTTP_303_SEE_OTHER)

        except Exception as e:
                db.rollback()
                raise HTTPException(status_code=500, detail=str(e))


@app.post("/sorted")
async def sorted_table(request: Request, db:db_dependency, sort_attribute: str = Form(...), order: str = Form(...)):
        sorted_tracks = db.query(models.Tracks).all()

        # Create an empty DataFrame with the desired columns
        sorted_df = pd.DataFrame(columns=['track_id', 'track_name', 'album_id', 'artist_id', 'genre'])
 
        track_dfs = [pd.DataFrame({'track_id': track.track_id,
                                'track_name': track.track_name,
                                'album_id': track.album_id,
                                'artist_id': track.artist_id,
                                'genre': track.genre}, index=[0]) for track in sorted_tracks]

        sorted_df = pd.concat(track_dfs, ignore_index=True)

        sort_applied = duckdb.query("SELECT * FROM sorted_df ORDER BY " + str(sort_attribute) + " " + str(order)).df()

        sort_applied.to_html('./html_files/basic.html', index=False)

        return RedirectResponse(url="/main_table", status_code=status.HTTP_303_SEE_OTHER)
        
@app.get("/playlist_report", response_class=HTMLResponse)
async def playlist_report(db:db_dependency):
    all_playlists = db.query(models.Playlists).all()

    try:
        # Read playlist_main.html
        with open("./html_files/playlist_main.html", "r") as main_file:
            main_content = main_file.read()
        
        # Read playlist.html
        with open("./html_files/playlist.html", "r") as basic_file:
            basic_content = basic_file.read()

        dropdown_options = ""
        for playlist in all_playlists:
                dropdown_options += f"<option value='{playlist.playlist_id}'>{playlist.playlist_name}</option>"
            
        # Find the closing </body> tag and insert basic_content before it
        merged_content = main_content.replace("</body>", f"""
            <div class="data-content">
                <form method="POST" action="/playlist_access">
                        <select name="chosen_playlist_id">
                        {dropdown_options}
                        </select>
                        <input type="submit" value="Access Playlist...">
                </form>
                {basic_content}
            </div>
        </body>""")
            
        return merged_content
            
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading files: {str(e)}")
    
@app.post("/playlist_access")
async def playlist_access(request: Request, db:db_dependency, chosen_playlist_id: str = Form(...)):
        all_playlists = db.query(models.Playlists).all()
        chosen_playlist = db.query(models.Playlist_Tracks).filter_by(playlist_id=chosen_playlist_id).all()

        # Create an empty DataFrame with the desired columns
        playlist_df = pd.DataFrame(columns=['playlist_id', 'playlist_name', 'user_id'])

        playlists_dfs = [pd.DataFrame({'playlist_id': playlist.playlist_id,
                                'playlist_name': playlist.playlist_name,
                                'user_id': playlist.user_id}, index=[0]) for playlist in all_playlists]

        playlist_df = pd.concat(playlists_dfs, ignore_index=True)

        playlist_df = duckdb.query("SELECT * FROM playlist_df WHERE playlist_id = " + chosen_playlist_id).df()

        tmp = duckdb.query("SELECT playlist_name FROM playlist_df WHERE playlist_id = " + chosen_playlist_id).fetchone()
        chosen_playlist_name = tmp[0]

        if (not chosen_playlist):
               chosen_playlist_df = pd.DataFrame(columns=['playlist_id', 'track_id'])

        else:
                chosen_playlist_df = pd.DataFrame(columns=['playlist_id', 'track_id'])
                chosen_playlists_dfs = [pd.DataFrame({'playlist_id': playlist_track.playlist_id,
                                        'track_id': playlist_track.track_id}, index=[0]) for playlist_track in chosen_playlist]
                chosen_playlist_df = pd.concat(chosen_playlists_dfs, ignore_index=True)

        chosen_playlist_df.to_html('./html_files/chosen_playlist.html', index=False)
        
        try:
              # Read playlist_access.html
                with open("./html_files/playlist_access.html", "r") as main_file:
                        main_content = main_file.read()

                # Read chosen_playlist.html
                with open("./html_files/chosen_playlist.html", "r") as main_file:
                        chosen_playlist_content = main_file.read()

                # Find the closing </body> tag and insert basic_content before it
                merged_content = main_content.replace("</body>", f"""
                <div class="data-content">
                        <h3>{chosen_playlist_name}</h3>
                        {chosen_playlist_content}
                </div>
                </body>""")

                return HTMLResponse(content=merged_content)

        except FileNotFoundError as e:
                raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")
        except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error reading files: {str(e)}")