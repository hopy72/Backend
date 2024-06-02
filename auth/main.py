import uvicorn
from auth.auth import auth

if __name__ == "__main__":
    uvicorn.run("auth.auth:auth", host="0.0.0.0", port=8001, reload=True)
