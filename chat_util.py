from langchain.chains import LLMChain
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os
import logging
from fastapi import HTTPException
import time


def get_company_info():
    try:
        with open("./company_info.txt", "r") as file:
            return file.read()
    except Exception as e:
        logging.error(f"Error while reading company_info.txt: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Dictionary to store conversation chains with unique identifiers (e.g., IP addresses)
conversation_chain_dict = {}

# Dictionary to store creation time and last access time for each conversation chain
conversation_times_dict = {}

# Maximum idle time before removing a conversation chain (2 minutes)
MAX_IDLE_TIME_SECONDS = 120

template = """
you are a helpful chatbot.
------
<ctx>
{context}
</ctx>
------
<hs>
{history}
</hs>
------
{question}
Answer:
"""
prompt = PromptTemplate(
    input_variables=["history", "context", "question"],
    template=template,
)


# memory = ConversationBufferMemory(memory_key="chat_history")
def create_llmchain():
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.001)  # Ensure no unsupported parameters are passed
    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True,
        memory=ConversationSummaryBufferMemory(
            llm=llm, max_token_limit=10000, memory_key="history", input_key="question"
        ),
    )
    return llm_chain


def get_or_create_conversation_chain(unique_identifier):
    current_time = time.time()

    if unique_identifier not in conversation_chain_dict:
        conversation_chain_dict[unique_identifier] = create_llmchain()
        conversation_times_dict[unique_identifier] = {
            "created_time": current_time,
            "last_access_time": current_time,
        }
    else:
        # Update the last access time
        conversation_times_dict[unique_identifier]["last_access_time"] = current_time

    return conversation_chain_dict[unique_identifier]


def remove_idle_conversations():
    current_time = time.time()
    for identifier, times in list(conversation_times_dict.items()):
        idle_time = current_time - times["last_access_time"]
        if idle_time > MAX_IDLE_TIME_SECONDS:
            # Remove idle conversation chain
            del conversation_chain_dict[identifier]
            del conversation_times_dict[identifier]


def predict_and_return_response(conversation_chain, input_text):
    response = conversation_chain.predict(
        question=input_text, context=get_company_info()
    )

    return response

