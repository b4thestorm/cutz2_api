from IPython.display import Image
from langchain.tools import tool
from langchain_core import messages
# from langchain_qwq import ChatQwen  # temporarily commented: langchain_qwq 0.3.x requires Python 3.11+, venv is 3.10. See progress.md.
from typing import TypedDict, Annotated
from langchain_core.messages import SystemMessage, HumanMessage
from integrations.models import GCalIntegration

class CalendarAgent:
    def __init__(self, calendar=None):
        # llm = ChatQwen(model="Qwen/Qwen-7B-Chat", max_retries=2, temperature=0.2)  # see comment above
        messages = [
        (
            "system",
            "You are a helpful assistant that helps a barber manage their calendar. You can use the following tools to interact with the calendar and manage appointments.",
        )
        ]
        # llm.bind_tools([self.hello_world])  # see comment above

    @tool
    def hello_world() -> str:
        """Respond for the first time."""
        return "hello Qwen"
    
