import os
import uuid
from time import sleep
from twilio.rest import Client as TwilioClient
from django.http import HttpResponse
from langchain_core.messages import HumanMessage, AIMessage
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from adminprofile.models import Client, CustomUser
from chat.models import CalendarAgent

def send_sms(to: str, from_: str, body: str):
    """Send a text message via Twilio."""
    # Pull credentials from environment
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    if not all([account_sid, auth_token]):
        return {"messages": [AIMessage(content="⚠️ Twilio credentials not set; SMS not sent.")]}

    client = TwilioClient(account_sid, auth_token)
    client.messages.create(body=body, from_=from_, to=to)
    return {"messages": [AIMessage(content="✅ SMS sent.")]}
    # except Exception as e:
        # return {"messages": [AIMessage(content=f"❗️ Failed to send SMS: {e}")]}

#make this work with the CalendarAgent and the StateGraph to handle incoming messages and respond appropriately.
#The view should extract the necessary information from the request, look up the corresponding barber, and invoke the CalendarAgent to generate a response.
@csrf_exempt
@require_http_methods(["POST"])
def barber_agent(request):
    """Handle incoming Twilio webhooks for the barber agent."""
    to_barbers_agent = request.POST.get('To', None)
    from_client = request.POST.get('From', None)
    body = request.POST.get('Body', None)
    channel_id = request.POST.get('uuid', None)

    try:
        barber = CustomUser.objects.get(
            role=CustomUser.Role.BARBER,
            twilio_phone_number=to_barbers_agent,
        )
    except CustomUser.DoesNotExist:
        return JsonResponse(
            {"error": "No barber found for that phone_number."},
            status=404,
        )

    if not barber.is_platform_paid:
        return JsonResponse(
            {"error": "Platform subscription required. Please complete payment to use the agent."},
            status=402,
        )

    if not channel_id:
        channel_id = str(uuid.uuid4())

    config = {"configurable": {"thread_id": channel_id}}
    _agent = CalendarAgent()

    # Check if the graph is currently interrupted
    state = _agent.graph.get_state(config)
    
    if state.next:
        # Graph is interrupted, resume it with the new input
        from langgraph.types import Command
        try:
            result_state = _agent.graph.invoke(Command(resume=body), config=config)
        except Exception as e:
            return JsonResponse({"error": f"Error resuming agent: {str(e)}"}, status=500)
    else:
        # Start a new interaction or continue a finished one
        init_state = {
            "user_id": barber.pk,
            "to": to_barbers_agent,
            "from_": from_client,
            "start_time": None,
            "end_time": None,
            "description": body,
            "messages": [HumanMessage(content=body)],
            "channel_id": channel_id,
        }
        try:
            result_state = _agent.graph.invoke(init_state, config=config)
        except Exception as e:
            return JsonResponse({"error": f"Error invoking agent: {str(e)}"}, status=500)

    agent_reply = ""
    if result_state and result_state.get("messages"):
        last_msg = result_state["messages"][-1]
        agent_reply = getattr(last_msg, "content", str(last_msg))
        
        # Send SMS response back to client
        send_sms(
            to=from_client,
            from_=to_barbers_agent,
            body=agent_reply,
        )

    return JsonResponse(
        {
            "barber_id": barber.id,
            "email": barber.email,
            "twilio_phone_number": barber.twilio_phone_number,
            "agent_response": agent_reply,
            "channel_id": channel_id
        }
    )
