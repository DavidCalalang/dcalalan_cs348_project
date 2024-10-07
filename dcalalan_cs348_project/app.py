"""Main script for running the project

Run with `uvicorn app:app --host 0.0.0.0 --port 80`
"""

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Opens .html files for rendering in various pages.
with open('./html_files/index.html', 'r') as f:
        root_html_content = f.read()

# Root/landing page
@app.get("/")
async def root():
        return HTMLResponse(content=root_html_content, status_code=200)