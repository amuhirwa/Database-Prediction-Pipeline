from fastapi import FastAPI
from routes import router

app = FastAPI(title="Crop Yield API")

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
