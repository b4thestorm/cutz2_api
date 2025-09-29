import requests
import logging
import json
import pdb

from django.db import models
from adminprofile.models import Barber, Services

class GCalIntegration(models.Model):
    user = models.ForeignKey(Barber, on_delete=models.CASCADE)
    refresh_token = models.CharField(max_length=255, null=True)
    access_token = models.CharField(max_length=255)
    expiration_time = models.IntegerField(default=0)
    calendar_id = models.CharField(max_length=255, null=True)

    
    def get_calendar(self):
        try:
            response = requests.get(f"https://www.googleapis.com/calendar/v3/users/me/calendarList",
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            })
            payload = response.json()
            if response.status_code == 401:
                error = payload.get('error', None).get('message', None)
                raise ValueError(f"{error}")
            items = payload.get('items', None)
            if items:
                for item in items:
                    id = item.get('id', None)  
                    if id == self.user.email:
                        return id
        except requests.exceptions.JSONDecodeError as error:
            raise ValueError(f"{error}")
        
    def get_service_events(self):
        try:
            response = requests.get(f"https://www.googleapis.com/calendar/v3/calendars/{self.calendar_id}/events?q=Service%20id%3A%202", headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            })
            payload = response.json()
            if response.status_code == 401:
                error = payload.get('error', None).get('message', None)
                raise ValueError(f"{error}")
            items = payload.get('items', None)
            if len(items) > 0:
                return items
            else:
                return []
        except requests.exceptions.HTTPError as error:
             logging.info(f"Unauthorized access: {error}")
             raise ValueError(f"{error} - user {self.user.email} no access")
        except requests.exceptions.JSONDecodeError as error:
            raise ValueError(f"{error}")

    def insert_service_event(self, body):
        start_time = body.get('start_time', None)
        end_time = body.get('end_time', None)
        description = body.get('description', None)
        service_id = body.get('service_id', None)

        try:
            service = Services.objects.get(id=service_id)
        except:
            raise ValueError('Service not available')

        data = {
                "end": {
                    "dateTime": self._format_time(end_time),
                    "timeZone": "EST"
                },
                "start": {
                    "dateTime": self._format_time(start_time),
                    "timeZone": "EST"
                },
                "description": description
            }
        
        data = json.dumps(data)
        try:
            response = requests.post(f"https://www.googleapis.com/calendar/v3/calendars/{self.calendar_id}/events?alt=json",
                                      headers={
                                        "Authorization": f"Bearer {self.access_token}",
                                        "Content-Type": "application/json"
                                        },
                                      data=data)

            response = response.json()
            event_id = response.get('id', None)
            pdb.set_trace()
            booking = Booking(
                        eventid=event_id,
                        start_time=start_time,
                        end_time=end_time,
                        user_id=self.user.id,
                        service_id=service,
                        integration_id=self
                    )
            booking.save()
        except requests.exceptions.HTTPError as error:
            logging.info(f"{error} - user {self.user.id}")
            raise ValueError(f"Unauthorized access: {error}")
    
    def cancel_event(self, calendar_id, event_id):
        try:
            requests.delete(f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events/{event_id}?sendUpdates=all", headers=self.headers)
        except requests.exceptions.HTTPError as error:
            logging.info(f"{error} - user {self.user.id}")
            raise ValueError(f"Unauthorized access: {error}")
    
    def _format_time(self, time):
        times = str(time).split(' ')
        return "T".join(times) + 'Z'


class Booking(models.Model):
    eventid = models.CharField(max_length=255, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    service_id = models.ForeignKey(Services, on_delete=models.CASCADE)
    user = models.ForeignKey(Barber, on_delete=models.CASCADE)
    integration_id = models.ForeignKey(GCalIntegration, on_delete=models.CASCADE)