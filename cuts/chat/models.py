from IPython.display import Image
from langchain.tools import tool
from langchain_core import messages
from langchain_qwq import ChatQwen
from typing import TypedDict, Annotated
from langchain_core.messages import SystemMessage, HumanMessage
from integrations.models import GCalIntegration

class CalendarAgent:
    def __init__(self, calendar=None):
        llm = ChatQwen(model="Qwen/Qwen-7B-Chat", max_retries=2, temperature=0.2)
        messages = [
        (
            "system",
            "You are a helpful assistant that helps a barber manage their calendar. You can use the following tools to interact with the calendar and manage appointments.",
        )
        ]
        llm.bind_tools([self.hello_world])

    @tool
    def hello_world() -> str:
        """Respond for the first time."""
        return "hello Qwen"
    
