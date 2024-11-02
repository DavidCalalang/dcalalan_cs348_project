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
                                                      
                        {basic_content}

                </div>
                </body>""")

                return merged_content
                
        except FileNotFoundError as e:
                raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")
        except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error reading files: {str(e)}")

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