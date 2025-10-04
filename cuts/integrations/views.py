import pdb
import requests
import webbrowser
import json

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django_eventstream import send_event
from dotenv import dotenv_values
from rest_framework.views import csrf_exempt

from integrations.serializer import BookingSerializer
from integrations.models import Booking, GCalIntegration


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
    print("request.user.is_authenticated", request.user.is_authenticated)
    if request.user.is_authenticated:
        user = request.user
        auth_code = request.GET.get('code', None)
        print("auth_code ", auth_code)
        data = {'code': auth_code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'}
        
        payload = requests.post("https://oauth2.googleapis.com/token", data=data)
        payload = json.loads(payload.text)
        print("I made a POST request back to Google ", payload)
        if payload:
            access_token = payload.get('access_token', None)
            refresh_token = payload.get('refresh_token', None)
            expires_in = payload.get('expires_in', None)
            try:
                calendar_token = GCalIntegration.objects.filter(user=user)
                if  len(calendar_token) == 0:
                    calendar = GCalIntegration(user=user, refresh_token=refresh_token, access_token=access_token, expiration_time=expires_in)
                    calendar.save()
                    send_event("gcal_init", "message", {"status": "connected"})
                    return Response(200, status=status.HTTP_200_OK)
                else:
                    calendar = calendar_token[0]
                    if calendar.access_token:
                        send_event("gcal_init", "message", {"status": "connected"})
                    else:
                        calendar.access_token = access_token
                        calendar.expiration_time = expires_in
                        calendar.refresh_token = refresh_token
                        calendar.save()

                    return Response(200, status=status.HTTP_200_OK)
            except:
                raise Exception("Error saving calendar token")
               
    return Response(403, status=status.HTTP_403_FORBIDDEN)

# /integrations/calendar_events
@api_view(['GET'])
def calendar_events(request):
    today = timezone.now().date()
    bookings = Booking.objects.filter(start_time__date=today)
    if len(bookings) > 0:
        serializer = BookingSerializer(bookings, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
    
    # manual = request.GET.get('manual')
    # if manual:    
    #     calendar_id = request.GET('calendar_id', None)
    #     try:
    #         calendar = GCalIntegration.objects.get(calendar_id=calendar_id)
    #         booking_events = calendar.get_service_events() #works if access token is recent
         
    #         serializer = BookingSerializer(data=booking_events['payload'])
    #         return Response(data=serializer.data, status=status.HTTP_200_OK)
    #     except ObjectDoesNotExist:
    #         return Response(status=status.HTTP_404_NOT_FOUND)

    return Response(data=serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def test_stream(request):
    send_event("test", "message", {"text": "test"})
    return Response(200, status=status.HTTP_200_OK, content_type='text/event-stream')

    