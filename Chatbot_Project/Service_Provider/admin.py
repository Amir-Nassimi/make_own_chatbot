from django.contrib import admin
from .models import ChatBot, QuestionsData, TrainableData



admin.site.register(ChatBot)
admin.site.register(QuestionsData)
admin.site.register(TrainableData)