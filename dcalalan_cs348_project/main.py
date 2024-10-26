"""Main script for running the project

CD INTO DIRECTORY FIRST
Run with `uvicorn main:app --reload`
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
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

@app.post("/listeners/", status_code=status.HTTP_201_CREATED)
async def create_listener(listener: ListenersBase, db: db_dependency):
        db_listener = models.Listeners(**listener.dict())

        db.add(db_listener)
        db.commit()

@app.get("/listeners/{user_id}", status_code=status.HTTP_200_OK)
async def read_user(user_id: int, db:db_dependency):
        user = db.query(models.Listeners).filter(models.Listeners.user_id == user_id).first()
        if user is None:
                raise HTTPException(status_code=404, detail="User not found")
        else:
                return user

"""
@app.get("/all_artists", status_code=status.HTTP_200_OK)
async def list_all_artists(db:db_dependency):
        all_artists = db.query(models.Artists).all()

        for artist in all_artists:
                print(artist.artist_name)

        return {"data": all_artists}
"""
        
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

        # To convert to table to show with html
        print(df)

        df.to_html('./html_files/basic.html', index=False)

        with open('./html_files/main.html', 'r') as f:
                test = f.read()

        return HTMLResponse(content=test, status_code=200)

@app.get("/main_table", response_class=HTMLResponse)
async def main_table():
    try:
        # Read main.html
        with open("./html_files/main.html", "r") as main_file:
            main_content = main_file.read()
        
        # Read basic.html
        with open("./html_files/basic.html", "r") as basic_file:
            basic_content = basic_file.read()
            
        # Find the closing </body> tag and insert basic_content before it
        merged_content = main_content.replace("</body>", f"""
            <div class="data-content">
                {basic_content}
            </div>
        </body>""")
            
        return merged_content
            
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading files: {str(e)}")

@app.get("/test_sql", status_code=status.HTTP_200_OK)
async def test_sql(db:db_dependency):
        all_tracks = db.query(models.Tracks).all()

        # Create an empty DataFrame with the desired columns
        df = pd.DataFrame(columns=['track_id', 'track_name', 'album_id', 'artist_id', 'genre'])

        track_dfs = [pd.DataFrame({'track_id': track.track_id,
                                'track_name': track.track_name,
                                'album_id': track.album_id,
                                'artist_id': track.artist_id,
                                'genre': track.genre}, index=[0]) for track in all_tracks]

        df = pd.concat(track_dfs, ignore_index=True)

        ye = 3
        foo = duckdb.query("SELECT * FROM df WHERE artist_id = " + str(ye)).df()
        foo.to_html('./html_files/basic.html', index=False)
        print(foo)

        with open('./html_files/basic.html', 'r') as f:
                test = f.read()

        return HTMLResponse(content=test, status_code=200)

"""
# Opens .html files for rendering in various pages.
with open('./html_files/index.html', 'r') as f:
        root_html_content = f.read()

# Root/landing page
@app.get("/")
async def root():
        return HTMLResponse(content=root_html_content, status_code=200)
"""