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
        )
        read_only_fields = ('id', 'username', 'email')

    def validate_email(self, value):
        if Person.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email уже зарегистрирован.")
        return value

class ManagerSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Person (Руководитель).
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
            'id',
            'username',
            'phone_number',
            'first_name',
            'last_name',
            'surname',
            'birthday',
            'email',
            'manager'
        )
        read_only_fields = ('id','username', 'email')




class DummyDetailSerializer(serializers.Serializer):
    status = serializers.IntegerField()


class DummyDetailAndStatusSerializer(serializers.Serializer):
    status = serializers.IntegerField()
    details = serializers.CharField()