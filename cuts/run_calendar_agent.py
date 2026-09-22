import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cuts.settings')
django.setup()

from adminprofile.models import CustomUser
from chat.models import CalendarAgent
from langchain_core.messages import HumanMessage

def run_agent(user_input="Hello!"):
    print(f"--- Running Calendar Agent with input: '{user_input}' ---")
    try:
        barber = CustomUser.objects.get(pk=1)
    except CustomUser.DoesNotExist:
        print("Error: Barber with pk=1 not found.")
        return

    agent = CalendarAgent()
    
    # Thread configuration for checkpointer
    config = {"configurable": {"thread_id": "test_thread_123"}}
    
    # Initial state
    initial_state = {
        "user_id": barber.pk,
        "to": None,
        "from_": None,
        "start_time": None,
        "end_time": None,
        "description": "",
        "messages": [HumanMessage(content=user_input)],
        "channel_id": None,
    }
    
    try:
        # FIRST RUN: This will hit the interrupt in welcome_message
        print("\n[Step 1] Invoking agent for the first time...")
        result = agent.graph.invoke(initial_state, config=config)
        
        # Because of the interrupt, the graph stops. We check if it stopped.
        # In LangGraph, the state is saved. We can now "resume" by providing the input
        # that the interrupt was waiting for.
        
        print("\n[Step 2] Resuming agent with user choice: 'I want to see services'...")
        # To resume an interrupt, we call invoke again with the same config 
        # and a Command(resume=...) or simply the value if using older patterns.
        # In latest LangGraph, we use Command(resume="...").
        from langgraph.types import Command
        
        result = agent.graph.invoke(Command(resume="I want to see services"), config=config)
        
        # Print all AI responses generated during the entire interaction
        if result and "messages" in result:
            print("\n--- Agent Interaction ---")
            for msg in result["messages"]:
                if hasattr(msg, "content") and not isinstance(msg, HumanMessage):
                    print(f"Agent: {msg.content}")
            print("------------------------\n")
        else:
            print("No response received from the agent.")
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_text = " ".join(sys.argv[1:])
    else:
        user_text = "Hello!"
    
    run_agent(user_text)
