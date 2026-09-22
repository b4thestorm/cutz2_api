from IPython.display import Image
from langchain.tools import tool
from langchain_core import messages
# from langchain_qwq import ChatQwen  # temporarily commented: langchain_qwq 0.3.x requires Python 3.11+, venv is 3.10. See progress.md.
from typing import Annotated
from typing_extensions import TypedDict

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import os
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt
from integrations.models import GCalIntegration, Services
from adminprofile.models import CustomUser

class MessageState(TypedDict):
    """State of the conversation."""
    user_id: int | None
    to: str | None
    from_: str | None
    start_time: str | None
    end_time: str | None
    description: str
    messages: Annotated[list[SystemMessage | HumanMessage | AIMessage], add_messages]
    channel_id: str | None


class CalendarAgent:
    def __init__(self):
        self.calendar = GCalIntegration
        # Initialize LLM – use real Gemini if API key present, otherwise a simple echo fallback
        if os.getenv("GOOGLE_API_KEY"):
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0)
        else:
            class EchoLLM:
                def bind_tools(self, tools):
                    return self
                def invoke(self, messages):
                    # Return an AIMessage echoing the last user message or a static greeting
                    if messages:
                        last = messages[-1]
                        content = getattr(last, "content", "")
                        return AIMessage(content=f"Echo: {content}")
                    return AIMessage(content="Echo: hello")
            llm = EchoLLM()
        self.llm = llm
        # Bind the tools so the LLM can call them

        self.llm = self.llm.bind_tools([self.book_appointment])
        self.graph = StateGraph(MessageState)

        # Nodes
        self.graph.add_node( "welcome_message", self.welcome_message)
        self.graph.add_node("run_llm", self.run_llm)
        self.graph.add_node("view_services", self.view_services)
        # self.graph.add_node("book_appointment", self.book_appointment)

        # START GRAPH
        self.graph.add_edge(START, "welcome_message")
        self.graph.add_edge("welcome_message", "run_llm")
        self.graph.add_conditional_edges(
            "run_llm", 
            self.conditional_edge, 
            {
                "view_services": "view_services", 
                "end": END
            }
        )
        self.graph.add_edge("view_services", END)
        self.graph = self.graph.compile(checkpointer=MemorySaver())


    def view_services(self, state: MessageState):
        """View the services offered by the barber."""
        try:
            user_id = state.get("user_id")
            if not user_id:
                return {"messages": [AIMessage(content="Error: No barber associated with this session.")]}
            
            # Fetch barber from DB using ID to avoid serialization issues
            from adminprofile.models import CustomUser
            barber = CustomUser.objects.get(pk=user_id)
            
            services = Services.objects.filter(barber=barber)
            if not services:
                return {"messages": [AIMessage(content="No services available for this barber.")]}
            
            service_list = "\n".join([f"{service.title}: {service.description} - ${service.price}" for service in services])
            # Return as a message update
            return {"messages": [AIMessage(content=f"Available services:\n{service_list}")]}
        except Exception as e:
            return {"messages": [AIMessage(content=f"Error fetching services: {str(e)}")]}
    
    def welcome_message(self, state: MessageState):
        """Return a friendly welcome message and interrupt for user choice."""
        msg = AIMessage(content="Welcome to the Calendar Agent! I can assist you with seeing the services he provides, and i can help you book a haricut with him. If you are satisfied with the service and want to end this converation, send the message \"Stop\". Ottherwise let me know what you would like to do.")
        
        # Trigger an interrupt to wait for user input before proceeding to the LLM
        interrupt("Waiting for user response to the welcome message.")
        
        return {"messages": [msg]}

    def run_llm(self, state: MessageState):
        """Run the LLM on the current message history and append its response.
        Handles any LLM errors by returning an error message instead of raising.
        """
        try:
            # The LLM expects a list of BaseMessage objects
            response = self.llm.invoke(state["messages"])

        except Exception as e:
            # Return a friendly error message to the user
            return {"messages": [AIMessage(content=f"Error: {str(e)}")]}
        # Ensure we have an AIMessage (ChatOpenAI returns an AIMessage)
        return {"messages": [response]}

    @tool
    def book_appointment(self, body: dict):
        """Book an appointment using GCalIntegration and return a confirmation message."""
        try:
            # In a real implementation, we would call the integration method.
            # Here we simulate a call to GCalIntegration.insert_service_event.
            GCalIntegration().insert_service_event(body)
            return {"messages": [AIMessage(content="✅ Appointment booked.")]}
        except Exception:
            return {"messages": [AIMessage(content="Failed to book appointment.")]}


    def conditional_edge(self, state: MessageState):
        """Determine the next node based on the LLM's last message."""
        if not state["messages"]:
            return "end"
            
        last_message = state["messages"][-1].content.lower()
        if "view services" in last_message or "services" in last_message:
            return "view_services"
        elif "stop" in last_message:
            return "end"
        else:
            # Default to ending if no clear intent is found, or you could route back to run_llm
            return "end"

        






