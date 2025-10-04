import requests
import logging
import json
import datetime
import re
import pdb

from django.db import models
from django.core.exceptions import ObjectDoesNotExist

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
                "description": description,
                "summary": "Cutz - haircut appointment"
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
           response = requests.delete(f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events/{event_id}?sendUpdates=all", headers={
                                "Authorization": f"Bearer {self.access_token}",
                                "Content-Type": "application/json"
                            },)
           response = response.json()
        except requests.exceptions.HTTPError as error:
            logging.info(f"{error} - user {self.user.id}")
            raise ValueError(f"Unauthorized access: {error}")
    
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
            print(items)
            if len(items) > 0:
                bookings = Booking.process_events(items, self) #('status', [events])
                return bookings
            else:
                return items
        except requests.exceptions.HTTPError as error:
             logging.info(f"Unauthorized access: {error}")
             raise ValueError(f"{error} - user {self.user.email} no access")
        except requests.exceptions.JSONDecodeError as error:
            raise ValueError(f"{error}")
    
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

# {'kind': 'calendar#event', 'etag': '"3517737795374942"', 'id': '33a6dr8q5mjnpo8702r2396t45', 'status': 'confirmed', 'htmlLink': 'https://www.google.com/calendar/event?eid=MzNhNmRyOHE1bWpucG84NzAycjIzOTZ0NDUgYXJub2xkc2FuZGVyQG0', 'created': '2025-09-26T06:41:37.000Z', 'updated': '2025-09-26T06:41:37.687Z', 'summary': 'Cutz - haircut appointment', 'description': 'Arnold\nService id: 2', 'creator': {'email': 'arnoldsander@gmail.com', 'self': True}, 'organizer': {'email': 'arnoldsander@gmail.com', 'self': True}, 'start': {'dateTime': '2025-09-26T10:00:00-04:00', 'timeZone': 'America/New_York'}, 'end': {'dateTime': '2025-09-26T10:30:00-04:00', 'timeZone': 'America/New_York'}, 'iCalUID': '33a6dr8q5mjnpo8702r2396t45@google.com', 'sequence': 0, 'reminders': {'useDefault': True}, 'eventType': 'default'}

    @classmethod
    def process_events(cls, events, integration):
        data = {'status': 'in progess', 'payload': []}
        for event in events:
            eventid = event.get('id', None)
            start = datetime.datetime.fromisoformat(event.get('start').get('dateTime'))
            finished = datetime.datetime.fromisoformat(event.get('end').get('dateTime'))
            name, service_id = cls.process_description(event.get('description'))
        
            try:
                booking = Booking.objects.get(eventid=eventid)
                data['payload'].append(booking)
                continue
            except ObjectDoesNotExist as e:
               pass 

            try:
                service = Services.objects.get(id=service_id)
                booking = Booking(
                    eventid=eventid,
                    start_time=start,
                    end_time=finished,
                    service_id=service,
                    user=integration.user,
                    integration_id=integration
                )
                booking.save()
                data['payload'].append(booking)

            except ObjectDoesNotExist as e:
                print(f"Service {service_id}: does not exist")
                continue
        
        data['status'] = 'done'
        return data
    
    #GITHUB COPILOT MADE THIS function FOR ME -__-
    @classmethod
    def process_description(cls, text):
        if not text:
            return (None, None)
        first = text.splitlines()[0].strip().split()
        first_name = first[0] if first else None
        nums = re.findall(r'\d+', text)
        service_id = int(nums[-1]) if nums else None
        return (first_name, service_id)