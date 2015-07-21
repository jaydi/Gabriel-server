"""
Python Test API implemented using Google Cloud Endpoints.

Defined here are the ProtoRPC messages needed to define Schemas for methods
as well as those methods defined in an API.
"""

import endpoints
from google.appengine.ext import ndb

from protorpc import messages
from protorpc import message_types
from protorpc import remote

from protocols import UserMessage
from protocols import DataMessage
from models import User

import analysis

package = "Gabriel"

@endpoints.api(name = "gabriel", version = "v1")
class GabrielApi(remote.Service):

    ID_RESOURCE = endpoints.ResourceContainer(message_types.VoidMessage, id = messages.IntegerField(1, variant = messages.Variant.INT64, required = True))

    @endpoints.method(UserMessage, UserMessage, name = "users.insert", path = "user", http_method = "POST")
    def users_insert(self, request):
        key = User.put_from_message(request)
        return UserMessage(id = key.id(), name = request.name)

    @endpoints.method(ID_RESOURCE, UserMessage, name = "users.get", path = "user/{id}", http_method = "GET")
    def users_get(self, request):
        user_key = ndb.Key(User, request.id)
        user = user_key.get()
        return user.to_message()

    ECG_SAMPLES = []

    @endpoints.method(DataMessage, message_types.VoidMessage, name = "datas.insert", path = "data", http_method = "POST")
    def datas_insert(self, request):
        user_key = ndb.Key(User, request.user_id)
        user = user_key.get()

        GabrielApi.ECG_SAMPLES += request.ecgs
        if (len(GabrielApi.ECG_SAMPLES) < 512 or len(request.edas) < 1 or len(request.accs) < 1):
            return message_types.VoidMessage()
        elif (len(GabrielApi.ECG_SAMPLES) > 2048):
            GabrielApi.ECG_SAMPLES = GabrielApi.ECG_SAMPLES[len(GabrielApi.ECG_SAMPLES)-2048:len(GabrielApi.ECG_SAMPLES)]

        hr = analysis.HRDetection.analyzeECG(GabrielApi.ECG_SAMPLES)
        eda = analysis.average(request.edas)
        acc = analysis.std_dev(request.accs)
        stress = analysis.stress_detection(hr, eda, acc)
        
        user.hr = hr
        user.eda = eda
        user.acc = acc
        user.stress = stress
        user.put()

        return message_types.VoidMessage()

"""
gabriel_api = endpoints.api(name = "gabriel", version = "v1")

@gabriel_api.api_class(resource_name = "users")
class Users(remote.Service):

    ID_RESOURCE = endpoints.ResourceContainer(message_types.VoidMessage, id = messages.IntegerField(1, variant = messages.Variant.INT64, required = True))

    @endpoints.method(UserMessage, UserMessage, name = "insert", path = "user", http_method = "POST")
    def users_insert(self, request):
        key = User.put_from_message(request)
        return UserMessage(id = key.id(), name = request.name)

    @endpoints.method(ID_RESOURCE, UserMessage, name = "get", path = "user/{id}", http_method = "GET")
    def users_get(self, request):
        user_key = ndb.Key(User, request.id)
        user = user_key.get()
        return user.to_message()

@gabriel_api.api_class(resource_name = "datas")
class Datas(remote.Service):
    ECG_SAMPLES = []

    @endpoints.method(DataMessage, message_types.VoidMessage, name = "insert", path = "data", http_method = "POST")
    def datas_insert(self, request):
        Datas.ECG_SAMPLES += request.ecgs
        if (len(Datas.ECG_SAMPLES) < 512 or len(request.edas) < 1 or len(request.accs) < 1):
            return message_types.VoidMessage()
        elif (len(Datas.ECG_SAMPLES) > 2048):
            Datas.ECG_SAMPLES = Datas.ECG_SAMPLES[len(Datas.ECG_SAMPLES)-2048:len(Datas.ECG_SAMPLES)]

        hr = analysis.HRDetection.analyzeECG(Datas.ECG_SAMPLES)
        eda = analysis.average(request.ecgs)
        acc = analysis.std_dev(request.accs)
        stress = analysis.stress_detection(hr, eda, acc)

        user_key = ndb.Key(User, request.user_id)
        user = user_key.get()
        user.hr = hr
        user.eda = eda
        user.acc = acc
        user.stress = stress
        user.put()

        return message_types.VoidMessage()
"""

APPLICATION = endpoints.api_server([GabrielApi])
