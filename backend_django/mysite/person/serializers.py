from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers
from .models import Person

class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = (
            'username',
            'phone_number',
            'first_name',
            'last_name',
            'surname',
            'birthday',
            'password',
            'email',
            'manager'
        )
        read_only_fields = ('username', 'email')

class ManagerSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Manager.
    """
    class Meta:
        model = Person
        fields = ('id', 'username', 'first_name', 'last_name' ,'email')

class PersonSerializer(BaseUserSerializer):
    """
    Сериализатор для модели Person.
    """
    manager = ManagerSerializer(read_only=True)
    class Meta(BaseUserSerializer.Meta):
        model = Person
        fields = (
            'username',
            'phone_number',
            'first_name',
            'last_name',
            'surname',
            'birthday',
            'email',
            'manager'
        )
        read_only_fields = ('username', 'email')


class DummyDetailSerializer(serializers.Serializer):
    status = serializers.IntegerField()


class DummyDetailAndStatusSerializer(serializers.Serializer):
    status = serializers.IntegerField()
    details = serializers.CharField()