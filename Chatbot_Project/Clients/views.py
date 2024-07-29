from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .serializers import RegisterSerializer



class UsersViewSet(ViewSet):
    @swagger_auto_schema(
        operation_description="User registration",
        request_body=RegisterSerializer,
        responses={
            201: 'User registered successfully',
            400: 'Bad request'
        }
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)