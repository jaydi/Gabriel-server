from protorpc import messages

class UserMessage(messages.Message):
    id = messages.IntegerField(1)
    name = messages.StringField(2)
    hr = messages.FloatField(3)
    eda = messages.FloatField(4)
    acc = messages.FloatField(5)
    stress = messages.FloatField(6)


class DataMessage(messages.Message):
    user_id = messages.IntegerField(1)
    ecgs = messages.IntegerField(2, repeated = True)
    edas = messages.IntegerField(3, repeated = True)
    accs = messages.IntegerField(4, repeated = True)