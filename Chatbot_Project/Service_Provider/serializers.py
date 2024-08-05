from rest_framework.serializers import ModelSerializer

from .models import ChatBot, TrainableData



class ChatBotSerializer(ModelSerializer):
    class Meta:
        model = ChatBot
        fields = '__all__'
        extra_kwargs = {
            'user': {'write_only':True},
            'ip': {'required': False},
            'port': {'required': False}
        }


class TrainableDataSerializer(ModelSerializer):
    bot = ChatBotSerializer(required=False, many=True)

    class Meta:
        model = TrainableData
        fields = '__all__'
