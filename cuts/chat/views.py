from django.http import HttpResponse
from langchain_core.messages import HumanMessage, AIMessage
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from adminprofile.models import CustomUser
from chat.models import CalendarAgent


@csrf_exempt
@require_http_methods(["POST"])
def barber_agent(request):
    """Look up the barber whose twilio_phone_number matches the request payload.

    Capability is intentionally fake for now: we just resolve the barber and
    return a small JSON payload. The CalendarAgent scaffolding is preserved
    so the actual agent behavior can be wired in later without restructuring.
    """
    # Parse JSON body (fall back to {} so missing body is handled uniformly).
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    twilio_phone_number = payload.get("twilio_phone_number")
    if not twilio_phone_number:
        return JsonResponse(
            {"error": "Missing required field: twilio_phone_number."},
            status=400,
        )

    try:
        barber = CustomUser.objects.get(
            role=CustomUser.Role.BARBER,
            twilio_phone_number=twilio_phone_number,
        )
    except CustomUser.DoesNotExist:
        return JsonResponse(
            {"error": "No barber found for that twilio_phone_number."},
            status=404,
        )

    # CalendarAgent scaffolding – invoke the agent to get a response
    _agent = CalendarAgent()
    # Build initial messages list from payload (if any)
    raw_messages = payload.get("messages", [])
    messages = []
    for m in raw_messages:
        role = m.get("role")
        content = m.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    # Prepare initial state for the graph (minimal required fields)
    init_state = {
        "user": barber,
        "gcal_integration": None,
        "service": None,
        "start_time": "",
        "end_time": "",
        "description": "",
        "messages": messages,
    }
    try:
        result_state = _agent.graph.invoke(init_state)
        # Grab the last AIMessage content if present
        agent_reply = ""
        if result_state.get("messages"):
            last_msg = result_state["messages"][-1]
            # last_msg may be AIMessage or HumanMessage
            agent_reply = getattr(last_msg, "content", str(last_msg))
    except Exception as e:
        # If the graph fails, fall back to empty response
        agent_reply = ""

    return JsonResponse(
        {
            "barber_id": barber.id,
            "email": barber.email,
            "twilio_phone_number": barber.twilio_phone_number,
            "agent_response": agent_reply,
        }
    )
