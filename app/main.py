import os
from fastapi import FastAPI
from dotenv import load_dotenv

from app.database import engine, Base
from app.routers import auth, upload

# Create database tables
Base.metadata.create_all(bind=engine)

load_dotenv()

app = FastAPI(
    title=os.getenv("APP_NAME", "Capstone Backend"),
    version="0.1.0"
)

app.include_router(auth.router)
app.include_router(upload.router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app_name": os.getenv("APP_NAME"),
        "environment": os.getenv("APP_ENV", "unknown")
    }

@app.get("/")
def read_root():
    return {"message": "Welcome to the Capstone Backend API. Visit /docs for the API documentation."}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
