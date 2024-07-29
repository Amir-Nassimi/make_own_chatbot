from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from django.contrib.auth import authenticate

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



class AuthViewSet(ViewSet):
    permission_classes = [AllowAny]


    @swagger_auto_schema(
        operation_description="User login",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Username to login'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password')
            }
        ),
        responses={200: 'Access and Refresh tokens', 400: 'BAD REQUEST', 401: 'UNAUTHORIZED'}
    )
    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            serializer = TokenObtainPairSerializer(data=request.data)
            if serializer.is_valid():
                return Response(serializer.validated_data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


    @swagger_auto_schema(
        operation_description="User logout",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token')
            }
        ),
        responses={205: 'Successfully logged out', 400: 'Bad request'}
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as error:
            return Response({'detail': f'{error}'}, status=status.HTTP_400_BAD_REQUEST)