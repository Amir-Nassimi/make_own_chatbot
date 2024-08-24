from django.db import transaction

from rest_framework.serializers import ModelSerializer

from .models import ChatBot, TrainableData, QuestionsData



class QuestionsDataSerializer(ModelSerializer):
    class Meta:
        model = QuestionsData
        fields = ['question']
        extra_kwargs = {
            'trainable': {'read_only': True}
        }


class TrainableDataSerializer(ModelSerializer):
    Questions = QuestionsDataSerializer(many=True)

    class Meta:
        model = TrainableData
        fields = '__all__'
        extra_kwargs = {
            'bot': {'write_only':True},
            'used': {'read_only':True}
        }

    def create(self, validated_data):
        questions_data = validated_data.pop('Questions')

        with transaction.atomic():
            trainable_data = TrainableData.objects.create(**validated_data)
            for question in questions_data:
                QuestionsData.objects.create(trainable=trainable_data, **question)
        
        return trainable_data

class ChatBotSerializer(ModelSerializer):
    Chatbot_TrainableData = TrainableDataSerializer(many=True, read_only=True)

    class Meta:
        model = ChatBot
        fields = '__all__'
        extra_kwargs = {
            'user': {'write_only':True},
            'IP': {'required': False},
            'PID': {'required': False},
            'PORT': {'required': False}
        }
