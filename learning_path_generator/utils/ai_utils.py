from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain, ConversationChain
from langchain.memory import ConversationBufferMemory
import os
from dotenv import load_dotenv
load_dotenv()


def create_llm():
    model = ChatGoogleGenerativeAI(
        google_api_key=os.environ.get("GEMINI_KEY"), 
        model="gemini-2.0-flash"
    )
    memory = ConversationBufferMemory()
    llm = ConversationChain(llm=model, memory=memory, verbose=False)
    return llm, memory

class SessionManager:
    _sessions = {}

    @classmethod
    def get_session(cls, user_id):
        if user_id not in cls._sessions:
            cls._sessions[user_id] = {
                "llm": create_llm(),
                "chat_history": []
            }
        return cls._sessions[user_id]

    @classmethod
    def clear_session(cls, user_id):
        if user_id in cls._sessions:
            del cls._sessions[user_id]