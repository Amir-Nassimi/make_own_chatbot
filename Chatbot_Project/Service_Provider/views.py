from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import TrainableData, ChatBot
from .serializers import TrainableDataSerializer, ChatBotSerializer



class TrainableDataViewSet(ModelViewSet):
    queryset = TrainableData.objects.all()
    serializer_class = TrainableDataSerializer
    permission_classes = [IsAuthenticated]


class ChatBotViewSet(ModelViewSet):
    queryset = ChatBot.objects.all()
    serializer_class = ChatBotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatBot.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)