import json

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

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

    # CalendarAgent scaffolding kept for future use; not invoked here.
    _agent = CalendarAgent()

    return JsonResponse(
        {
            "barber_id": barber.id,
            "email": barber.email,
            "twilio_phone_number": barber.twilio_phone_number,
        }
    )
