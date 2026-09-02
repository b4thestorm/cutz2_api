from IPython.display import Image
from langchain.tools import tool
from langchain_core import messages
# from langchain_qwq import ChatQwen  # temporarily commented: langchain_qwq 0.3.x requires Python 3.11+, venv is 3.10. See progress.md.
from typing import TypedDict, Annotated
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import graph
from langgraph.graph import StateGraph, START, END
from integrations.models import GCalIntegration, Services
from adminprofile.models import Services, CustomUser

class MessageState(TypedDict):
    """State of the conversation."""
    user: CustomUser
    gcal_integration: GCalIntegration
    service: Services
    start_time: str
    end_time: str
    description: str
    messages: Annotated[list[SystemMessage | HumanMessage], "The messages exchanged in the conversation."]

class CalendarAgent:
    def __init__(self, data=None):
        self.calendar = GCalIntegration
        # self.llm = ChatQwen(model="Qwen/Qwen-7B-Chat", max_retries=2, temperature=0.2)  # see comment above
        self.graph = StateGraph(MessageState)
        # Build the graph for the agent
        self.graph.add_node("welcome_message", self.welcome_message)
        self.graph.add_node("insert_service_event", GCalIntegration.insert_service_event)
        self.graph.add_node("view services", self.view_services)

        self.graph.add_edge(START, "welcome_message")
        self.graph.add_conditional_edges("welcome_message", self.conditional_edge)
        self.graph.add_edge("insert_service_event", END)
        self.graph.add_edge("view services", END)

        self.graph.compile()


    @tool
    def view_services(self):
        """View the services offered by the barber."""
        services = Services.objects.all()
        if not services:
            return "No services available."
        service_list = "\n".join([f"{service.title}: {service.description} - ${service.price}" for service in services])
        return f"Available services:\n{service_list}"
    
    @tool
    def welcome_message(self):
        """Return a friendly welcome message for the Calendar Agent."""
        return """
               Welcome to the Calendar Agent! How can I assist you today?
        """

    def conditional_edge(self, state: MessageState):
        """Determine the next state based on the user's input."""
        last_message = state["messages"][-1].content.lower()
        if "view services" in last_message:
            return "view services"
        elif "book appointment" in last_message:
            return "insert_service_event"
        else:
            return "welcome_message"
        







