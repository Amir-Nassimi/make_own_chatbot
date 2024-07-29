from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import UserSerializer, RegisterSerializer



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
    

    @swagger_auto_schema(
        operation_description="Get user information",
        responses={200: UserSerializer},
        security=[{'Bearer': []}]
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def user_info(self, request):
        user = request.user
        return Response(UserSerializer(user, many=False).data, status=status.HTTP_200_OK)