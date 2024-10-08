"""Main script for running the project

Run with `uvicorn app:app --host 0.0.0.0 --port 80`
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
        db = SessionLocal()
        try:
                yield db
        finally:
                db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: ListenersBase, db: db_dependency):
        db_user = models.User(**user.dict())
        db.add(db_user)
        db.commit()

"""
# Opens .html files for rendering in various pages.
with open('./html_files/index.html', 'r') as f:
        root_html_content = f.read()

# Root/landing page
@app.get("/")
async def root():
        return HTMLResponse(content=root_html_content, status_code=200)
"""