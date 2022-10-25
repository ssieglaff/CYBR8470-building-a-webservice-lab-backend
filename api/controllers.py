#from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import *
from django.contrib.auth import *
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
#from django.shortcuts import render_to_response
from django.template import RequestContext
from django_filters.rest_framework import DjangoFilterBackend


from django.shortcuts import *

# Import models
from django.db import models
from django.contrib.auth.models import *
from api.models import *

#REST API
from rest_framework import viewsets, filters, parsers, renderers
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import *
from rest_framework.decorators import *
from rest_framework.authentication import *

#filters
#from filters.mixins import *

from api.pagination import *
import json, datetime, pytz
from django.core import serializers
import requests


def home(request):
   """
   Send requests to / to the ember.js clientside app
   """
   return render_to_response('ember/index.html',
               {}, RequestContext(request))

def xss_example(request):
  """
  Send requests to xss-example/ to the insecure client app
  """
  return render_to_response('dumb-test-app/index.html',
              {}, RequestContext(request))

class Register(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        # Login
        username = request.POST.get('username') #you need to apply validators to these
        print username
        password = request.POST.get('password') #you need to apply validators to these
        email = request.POST.get('email') #you need to apply validators to these
        gender = request.POST.get('gender') #you need to apply validators to these
        age = request.POST.get('age') #you need to apply validators to these
        educationlevel = request.POST.get('educationlevel') #you need to apply validators to these
        city = request.POST.get('city') #you need to apply validators to these
        state = request.POST.get('state') #you need to apply validators to these

        print request.POST.get('username')
        if User.objects.filter(username=username).exists():
            return Response({'username': 'Username is taken.', 'status': 'error'})
        elif User.objects.filter(email=email).exists():
            return Response({'email': 'Email is taken.', 'status': 'error'})

        #especially before you pass them in here
        newuser = User.objects.create_user(email=email, username=username, password=password)
        newprofile = Profile(user=newuser, gender=gender, age=age, educationlevel=educationlevel, city=city, state=state)
        newprofile.save()

        return Response({'status': 'success', 'userid': newuser.id, 'profile': newprofile.id})

class Session(APIView):
    permission_classes = (AllowAny,)
    def form_response(self, isauthenticated, userid, username, error=""):
        data = {
            'isauthenticated': isauthenticated,
            'userid': userid,
            'username': username
        }
        if error:
            data['message'] = error

        return Response(data)

    def get(self, request, *args, **kwargs):
        # Get the current user
        if request.user.is_authenticated():
            return self.form_response(True, request.user.id, request.user.username)
        return self.form_response(False, None, None)

    def post(self, request, *args, **kwargs):
        # Login
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return self.form_response(True, user.id, user.username)
            return self.form_response(False, None, None, "Account is suspended")
        return self.form_response(False, None, None, "Invalid username or password")

    def delete(self, request, *args, **kwargs):
        # Logout
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

class Events(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (parsers.JSONParser,parsers.FormParser)
    renderer_classes = (renderers.JSONRenderer, )

    # Get list request endpoint
    def get(self, request, format=None):
        events = Event.objects.all()
        json_data = serializers.serialize('json', events)
        content = {'events': json_data}
        return HttpResponse(json_data, content_type='json')
    
    # Post request endpoint
    def post(self, request, *args, **kwargs):
        print 'REQUEST DATA'
        print str(request.data)

        eventtype = request.data.get('eventtype')
        timestamp = int(request.data.get('timestamp'))
        userid = request.data.get('userid')
        requestor = request.META['REMOTE_ADDR']

        newEvent = Event(
            eventtype=eventtype,
            timestamp=datetime.datetime.fromtimestamp(timestamp/1000, pytz.utc),
            userid=userid,
            requestor=requestor
        )

        try:
            newEvent.clean_fields()
            
        except ValidationError as e:
            print e
            return Response({'success':False, 'error':e}, status=status.HTTP_400_BAD_REQUEST)

        newEvent.save()
        print 'New Event Logged from: ' + requestor
        return Response({'success': True}, status=status.HTTP_200_OK)


class ActivateIFTTT(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (parsers.JSONParser,parsers.FormParser)
    renderer_classes = (renderers.JSONRenderer, )

    def post(self,request):
        print 'REQUEST DATA'
        print str(request.data)

        eventtype = request.data.get('eventtype')
        timestamp = int(request.data.get('timestamp'))
        requestor = request.META['REMOTE_ADDR']
        api_key = ApiKey.objects.all().first()
        event_hook = "test"

        print "Creating New event"

        newEvent = Event(
            eventtype=eventtype,
            timestamp=datetime.datetime.fromtimestamp(timestamp/1000, pytz.utc),
            userid=str(api_key.owner),
            requestor=requestor
        )

        print newEvent
        print "Sending Device Event to IFTTT hook: " + str(event_hook)

        #send the new event to IFTTT and print the result
        event_req = requests.post('https://maker.ifttt.com/trigger/'+str(event_hook)+'/with/key/'+api_key.key, data= {
            'value1' : timestamp,
            'value2' : "\""+str(eventtype)+"\"",
            'value3' : "\""+str(requestor)+"\""
        })
        print event_req.text

        #check that the event is safe to store in the databse
        try:
            newEvent.clean_fields()
        except ValidationError as e:
            print e
            return Response({'success':False, 'error':e}, status=status.HTTP_400_BAD_REQUEST)

        #log the event in the DB
        newEvent.save()
        print 'New Event Logged'
        return Response({'success': True}, status=status.HTTP_200_OK)

class DogDetail(APIView):
    permission_classes = (AllowAny,)

    def get(self, dog_id, format=None):
        return HttpResponse(serializers.serialize('json', get_object_or_404(Dog, pk=dog_id)), content_type='json')

    def put(self, request, format=None):
        dog = get_object_or_404(Dog, pk=id)

        dog.name = request.data.get('name')
        dog.age = int(request.data.get('age'))
        dog.breed = get_object_or_404(Breed, pk=int(request.data.get('breed')))
        dog.gender = request.data.get('gender')
        dog.color = request.data.get('color')
        dog.favoritefood = request.data.get('favoritefood')
        dog.favoritetoy = request.data.get('favoritetoy')

        try:
            dog.clean_fields()
        except ValidationError as e:
            return Response("Invalid Entry", status=status.HTTP_400_BAD_REQUEST)
        
        dog.save()
        return Response({'success': True}, status=status.HTTP_200_OK)

    def delete(self, request, format=None):
        dog = get_object_or_404(Dog, pk=id)
        dog.delete()
        return Response({'success': True}, status=status.HTTP_200_OK)

class DogList(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        allDogs = Dog.objects.all()
        return HttpResponse(serializers.serialize('json', allDogs), content_type='json')

    def post(self, request, format=None):
        newDog = Dog(
            name = request.data.get('name'),
            age = int(request.data.get('age')),
            breed = get_object_or_404(Breed, pk=int(request.data.get('breed'))),
            gender = request.data.get('gender'),
            color = request.data.get('color'),
            favoritefood = request.data.get('favoritefood'),
            favoritetoy = request.data.get('favoritetoy')
        )
        try:
            newDog.clean_fields()
        except ValidationError as e:
            return Response("Invalid Entry", status=status.HTTP_400_BAD_REQUEST)
        
        newDog.save()
        return Response({'success': True}, status=status.HTTP_200_OK)


class BreedDetail(APIView):
    permission_classes = (AllowAny,)

class BreedList(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        allBreeds = Breed.objects.all()
        return HttpResponse(serializers.serialize('json', allBreeds), content_type='json')

    def post(self, request, format=None):
        newBreed = Breed(
            name = request.data.get('name'),
            size = request.data.get('size'),
            friendliness = int(request.data.get('friendliness')),
            trainability = int(request.data.get('trainability')),
            sheddingammount = int(request.data.get('sheddingammount')),
            exerciseneeds = int(request.data.get('exerciseneeds'))
            )
        try:
            newBreed.clean_fields()
        except ValidationError as e:
            return Response("Invalid Entry", status=status.HTTP_400_BAD_REQUEST)
        
        newBreed.save()
        return Response({'success': True}, status=status.HTTP_200_OK)
