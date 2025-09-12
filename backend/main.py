from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from services.chat.router import router as chat_router
from services.login.router import router as login_router

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Backend is running"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(login_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
