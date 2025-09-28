from database import create_db_and_tables
from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from services.chat.router import router as chat_router
from services.login.router import router as login_router
from services.record.router import router as record_router
from services.history.router import router as history_router
from services.todo.router import router as todo_router
from services.contact.router import router as contact_router

app = FastAPI()

@app.on_event('startup')
def _startup():
    create_db_and_tables()

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
app.include_router(record_router)
app.include_router(history_router)
app.include_router(todo_router)
app.include_router(contact_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)


