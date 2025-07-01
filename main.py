import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel  # Import Pydantic BaseModel
import asyncio
import logging
import json
import os
import gc
from thread import start_timer
from chat_util import *  # Assuming chat_util.py contains necessary functions

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as needed for your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("data.json", "r") as file:
    data = json.load(file)

# Read company information from the file
with open("company_info.txt", "r") as file:
    company_info = file.read()

# Configure logging
error_handler = logging.FileHandler("error.log")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

general_handler = logging.FileHandler("general.log")
general_handler.setLevel(logging.INFO)
general_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

logger = logging.getLogger()
logger.addHandler(error_handler)
logger.addHandler(general_handler)
logger.setLevel(logging.DEBUG)

i = 0  # Global variable

# Define a Pydantic model for the request body
class ChatRequest(BaseModel):
    message: str  # Define the message parameter

async def chat_with_bot(user_input, ip):
    global i
    if i >= 10000:
        i = 0  # Reinitialize i to reset it to 0

    try:
        logger.info(f"Chatting with bot. User input: {user_input}, IP: {ip}")  # Log user input and IP

        # Switch between API keys for each consecutive function call
        if i % 2 == 1:
            os.environ["OPENAI_API_KEY"] = data["keys"][0]["key1"]
        else:
            os.environ["OPENAI_API_KEY"] = data["keys"][1]["key2"]

        # Main chat OpenAI initialization with threads
        remove_idle_conversations()
        conversation_chain = get_or_create_conversation_chain(ip)  # Pass only the IP
        logger.info(f"Conversation chain created for IP: {ip}")  # Log conversation chain creation

        response = await asyncio.to_thread(predict_and_return_response, conversation_chain, user_input)
        logger.info(f"Response from OpenAI: {response}")  # Log the response from OpenAI

        bot_reply = response  # OpenAI response

        i += 1
        logger.info(f"Bot reply: {bot_reply}")
        return bot_reply
    except Exception as e:
        logging.error(f"Error in chat_with_bot: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/chat")
async def chat(request: ChatRequest, request_obj: Request):  # Use the Pydantic model and rename Request object
    try:
        user_input = request.message  # Access the message parameter
        logger.info(f"Received user input from API: {user_input}")

        if user_input is None:
            return {"message": "Please provide a message."}
        elif not user_input.strip():  # Check if the user input is empty
            return {"message": "Please provide a non-empty message."}
        else:
            real_ip = request_obj.headers.get("X-Forwarded-For", request_obj.client.host)  # Access headers from Request
            bot_reply = await chat_with_bot(user_input, real_ip)
            logger.info(f"Sending bot reply to API: {bot_reply}")
            return {"response": bot_reply}
    except Exception as ex:
        logging.error(f"Error in chat route: {ex}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        gc.collect()  # Force garbage collection

if __name__ == "__main__":
    start_timer()  # Keep this function call as you had it