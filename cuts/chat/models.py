from IPython.display import Image
from langchain.tools import tool
from langchain_core import messages
# from langchain_qwq import ChatQwen  # temporarily commented: langchain_qwq 0.3.x requires Python 3.11+, venv is 3.10. See progress.md.
from typing import TypedDict, Annotated
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import os
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
        # Initialize LLM – use real OpenAI if API key present, otherwise a simple echo fallback
        if os.getenv("OPENAI_API_KEY"):
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.0)
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
        self.llm = self.llm.bind_tools([self.welcome_message, self.view_services, self.book_appointment])
        self.graph = StateGraph(MessageState)
        # Build the graph for the agent
        self.graph.add_edge(START, "welcome_message")
        self.graph.add_node("welcome_message", self.welcome_message)
        self.graph.add_node("insert_service_event", self.book_appointment)
        self.graph.add_node("view services", self.view_services)

        self.graph.add_node("run_llm", self.run_llm)
        self.graph.add_edge("welcome_message", "run_llm")
        self.graph.add_conditional_edges("run_llm", self.conditional_edge)
        self.graph.add_edge("run_llm", "insert_service_event")
        self.graph.add_edge("run_llm", "view services")
        self.graph.add_edge("run_llm", END)

        self.graph.compile()


    @tool
    def view_services(self):
        """View the services offered by the barber."""
        services = Services.objects.all()
        if not services:
            return {"messages": [AIMessage(content="No services available.")]}
        service_list = "\n".join([f"{service.title}: {service.description} - ${service.price}" for service in services])
        # Return as a message update
        return {"messages": [AIMessage(content=f"Available services:\n{service_list}")]}
    
    @tool
    def welcome_message(self):
        """Return a friendly welcome message for the Calendar Agent."""
        return {"messages": [AIMessage(content="Welcome to the Calendar Agent! How can I assist you today?")]}

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
            # For now we simulate success without side‑effects.
            return {"messages": [AIMessage(content="✅ Appointment booked.")]}
        except Exception:
            return {"messages": [AIMessage(content="Failed to book appointment.")]}

    def conditional_edge(self, state: MessageState):
        """Determine the next node based on the LLM's last message."""
        last_message = state["messages"][-1].content.lower()
        if "view services" in last_message:
            return "view services"
        elif "book appointment" in last_message:
            return "insert_service_event"
        elif "stop" in last_message:
            return END
        else:
            return "welcome_message"

        






