from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "username", "phone", "birth_date", "password"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(TokenObtainPairSerializer):


    def validate(self, attrs):

        data = super().validate(attrs)
        data['user'] = {
            "id": self.user.id,
            "email": self.user.email,
            "username": self.user.username,
            "phone": self.user.phone,
            "birth_date": self.user.birth_date,
            "role": self.user.role
        }
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token