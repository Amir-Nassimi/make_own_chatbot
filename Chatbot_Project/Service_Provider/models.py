from uuid import uuid4 as UUID

from django.db import models

from Clients.models import Users



class ChatBot(models.Model):
    id = models.UUIDField(default=UUID, primary_key=True, editable=False, unique=True)

    name = models.CharField(max_length=15)
    is_active = models.BooleanField(default=False)
    is_trained = models.BooleanField(default=False)
    PID = models.IntegerField(blank=True, null=True)
    PORT = models.IntegerField(blank=True, null=True)
    IP = models.CharField(max_length=13, blank=True, null=True)

    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='User_Chatbot')


class TrainableData(models.Model):
    id = models.UUIDField(default=UUID, primary_key=True, editable=False, unique=True)

    answers = models.TextField()
    questions = models.TextField()
    topic = models.CharField(max_length=20, unique=True)

    bot = models.ForeignKey(ChatBot, on_delete=models.CASCADE, related_name='Chatbot_TrainableData')