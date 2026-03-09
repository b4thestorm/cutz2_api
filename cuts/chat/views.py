from django.http import HttpResponse
from chat.models import CalendarAgent

def barber_agent(request):
    agent = CalendarAgent()
    if request.method == "POST":
        user_input = request.POST.get("user_input")
        response = agent.invoke(user_input)
        return HttpResponse(response)
    return HttpResponse("Hello World")
