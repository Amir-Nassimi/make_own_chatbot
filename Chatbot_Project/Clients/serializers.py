from django.db import transaction, IntegrityError

from rest_framework.serializers import  ModelSerializer, ReadOnlyField, ValidationError

from .models import Users



class UserSerializer(ModelSerializer):
    Joined = ReadOnlyField()

    class Meta:
        model = Users
        exclude =['user_permissions', 'groups', 'date_joined', 'is_superuser', 'last_login', 'password']


class RegisterSerializer(ModelSerializer):

    class Meta:
        model = Users
        fields = ['email', 'password', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}


    def create(self, validated_data):
        try:
            with transaction.atomic():
                user = Users.objects.create_user(**validated_data)

                return user
        except IntegrityError:
            raise ValidationError("There was an error creating the users. Please try again.")