"""
Notification and Rating serializers.
"""
from rest_framework import serializers
from .models import Notification, Rating


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for notifications.
    """
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'body', 'notification_type', 'data',
            'request', 'is_read', 'read_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RatingSerializer(serializers.ModelSerializer):
    """
    Serializer for ratings.
    """
    rater_name = serializers.CharField(source='rater.full_name', read_only=True)
    
    class Meta:
        model = Rating
        fields = ['id', 'request', 'rater', 'rater_name', 'rated_user', 'score', 'review', 'created_at']
        read_only_fields = ['id', 'rater', 'created_at']


class RatingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating ratings.
    """
    class Meta:
        model = Rating
        fields = ['score', 'review']

    def validate_score(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Score must be between 1 and 5.")
        return value
