import uvicorn
from fastapi import FastAPI
from routers import user_router, collections_router, pictures_router, tags_router

app = FastAPI()
app.include_router(user_router)
app.include_router(collections_router)
app.include_router(pictures_router)
app.include_router(tags_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
