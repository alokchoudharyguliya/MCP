import os, json, openai
from qabot import QABotMCP
from pydantic import BaseModel
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()
openai.api_key=os.getenv("OPENAI_API_KEY")
bot=QABotMCP(model="gpt-4")
CONTEXT_FILE="conversation.json"

if not os.path.exists(CONTEXT_FILE):
    with open(CONTEXT_FILE,"w") as f:
        json.dump([],f,indent=2)

def save_context(filename=CONTEXT_FILE):
    with open(filename,"w") as f:
        json.dump(bot.history, f, indent=2)

app=FastAPI()
class Question(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(q:Question):
    answer=bot.ask(q.question)
    save_context()
    return {"answer":answer}

@app.get("/")
async def root():
    return {"message":"MCP Q&A bot server running"}

