from rest_framework import serializers
from .models import User,FriendRequest
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.utils.translation import gettext_lazy as _

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name']

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        return user
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        email = attrs.get("email").lower()
        password = attrs.get("password")

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                username=email, password=password)

            # Check if user exists with case insensitive email
            try:
                user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                user = None

            if not user:
                raise serializers.ValidationError(
                    _('No active account found with the given credentials'),
                    'no_active_account'
                )

            if not user.is_active:
                raise serializers.ValidationError(
                    _('User account is disabled.'),
                    'no_active_account'
                )

            refresh = self.get_token(user)

            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            if api_settings.UPDATE_LAST_LOGIN:
                update_last_login(None, user)

            return data
        else:
            raise serializers.ValidationError(
                _('Must include "email" and "password".'),
                'no_active_account'
            )

class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(read_only=True)
    to_user = UserSerializer(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'created_at']