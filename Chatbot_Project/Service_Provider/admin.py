from django.contrib import admin

from .models import AnswersData, ChatBot, QuestionsData, TrainableData

admin.site.register(ChatBot)
admin.site.register(AnswersData)
admin.site.register(QuestionsData)
admin.site.register(TrainableData)
