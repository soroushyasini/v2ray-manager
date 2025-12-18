from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from routes import users, stats, config

app = FastAPI(title="V2Ray Manager Dashboard", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(stats.router, prefix="/api", tags=["stats"])
app.include_router(config.router, prefix="/api", tags=["config"])

# Serve static files
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("../frontend/index.html")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
