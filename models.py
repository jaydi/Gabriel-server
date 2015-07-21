from google.appengine.ext import ndb

from protocols import UserMessage

class User(ndb.Model):
    name = ndb.StringProperty(required = True)
    hr = ndb.FloatProperty()
    eda = ndb.FloatProperty()
    acc = ndb.FloatProperty()
    stress = ndb.FloatProperty()

    @classmethod
    def put_from_message(cls, message):
        entity = cls(name = message.name)
        return entity.put()

    def to_message(self):
        return UserMessage(id = self.key.id(), name = self.name, hr = self.hr, eda = self.eda, acc = self.acc, stress = self.stress)