from djoser.conf import settings
from djoser.serializers import UserSerializer
from rest_framework import serializers

from .models import User


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta():
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        read_only_fields = (settings.LOGIN_FIELD, 'is_subscribed',)

    def get_is_subscribed(self, obj):
        user = self.context['request'].user.username
        author = obj.subscribers.filter(subscriber__username=user)
        return author.exists()
