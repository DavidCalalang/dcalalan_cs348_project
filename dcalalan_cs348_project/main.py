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
        
@app.get("/all_listeners", status_code=status.HTTP_200_OK)
async def list_all_users(db:db_dependency):
        all_listeners = db.query(models.Listeners).all()

        for listener in all_listeners:
                print(listener.username)

        return {"data": all_listeners}

@app.get("/all_artists", status_code=status.HTTP_200_OK)
async def list_all_artists(db:db_dependency):
        all_artists = db.query(models.Artists).all()

        for artist in all_artists:
                print(artist.artist_name)

        return {"data": all_artists}

@app.get("/all_tracks", status_code=status.HTTP_200_OK)
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

        return {"data": all_tracks}


"""
# Opens .html files for rendering in various pages.
with open('./html_files/index.html', 'r') as f:
        root_html_content = f.read()

# Root/landing page
@app.get("/")
async def root():
        return HTMLResponse(content=root_html_content, status_code=200)
"""