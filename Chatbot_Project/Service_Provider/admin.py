from django.contrib import admin

from .models import TrainableData, ChatBot


admin.site.register(ChatBot)
admin.site.register(TrainableData)
