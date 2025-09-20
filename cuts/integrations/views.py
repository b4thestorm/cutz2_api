from django.http.response import StreamingHttpResponse
import requests
import webbrowser
import json
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from django_eventstream import send_event
from dotenv import dotenv_values
from rest_framework.views import csrf_exempt

from integrations.models import GCalIntegration


config = dotenv_values("../.env")
client_id = config['GCAL_CLIENT_ID']
client_secret = config['GCAL_CLIENT_SECRET']
redirect_uri = settings.GCAL_REDIRECT_URI

@api_view(['GET'])
def gcal_init(request):
    if request.user.is_authenticated:
        try:
            webbrowser.register('google-chrome', None, webbrowser.BackgroundBrowser('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'))
            chrome = webbrowser.get('google-chrome')
            chrome.open_new_tab(f"https://accounts.google.com/o/oauth2/auth?client_id={client_id}&redirect_uri={redirect_uri}&scope={settings.GCAL_SCOPES}&response_type=code")
        except:
            return Response(403, status=status.HTTP_403_FORBIDDEN)     
        
        return Response(200, status=status.HTTP_200_OK)

@api_view(['GET'])
@csrf_exempt
def gcal_auth(request):
    if request.user.is_authenticated:
        user = request.user
        auth_code = request.GET.get('code', None)

        data = {'code': auth_code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'}
        
        payload = requests.post("https://oauth2.googleapis.com/token", data=data)
        payload = json.loads(payload.text)

        if payload:
            access_token = payload.get('access_token', None)
            refresh_token = payload.get('refresh_token', None)
            expires_in = payload.get('expires_in', None)

            try:
                calendar_token = GCalIntegration.objects.filter(user=user)
                if not calendar_token:
                    calendar = GCalIntegration(user=user, refresh_token=refresh_token, access_token=access_token, expiration_time=expires_in)
                    calendar.save()
                    send_event("gcal_init", "message", {"status": "connected"})
                    return Response(200, status=status.HTTP_200_OK)
                else:
                    send_event("gcal_init", "message", {"status": "connected"})
                    return Response(200, status=status.HTTP_200_OK)
            except:
                raise Exception("Error saving calendar token")


               
    return Response(403, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
def test_stream(request):
    send_event("test", "message", {"text": "test"})
    return Response(200, status=status.HTTP_200_OK, content_type='text/event-stream')

    