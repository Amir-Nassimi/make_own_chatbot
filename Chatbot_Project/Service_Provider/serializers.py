from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField

from .models import ChatBot, TrainableData



class TrainableDataSerializer(ModelSerializer):
    class Meta:
        model = TrainableData
        fields = '__all__'
        extra_kwargs = {
            'bot': {'write_only':True},
            'used': {'read_only':True}
        }


class ChatBotSerializer(ModelSerializer):
    Chatbot_TrainableData = TrainableDataSerializer(many=True, read_only=True)

    class Meta:
        model = ChatBot
        fields = '__all__'
        extra_kwargs = {
            'user': {'write_only':True},
            'ip': {'required': False},
            'port': {'required': False}
        }
