import uvicorn
from fastapi import FastAPI
from routers import user_router, collections_router

app = FastAPI()
app.include_router(user_router)
app.include_router(collections_router)

if __name__ == "__main__":
    uvicorn.run(app, port=8080)
