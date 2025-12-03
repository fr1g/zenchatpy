import re
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Contact, UserProfile

class UserSerializer(serializers.ModelSerializer):
    user_type = serializers.CharField(source='userprofile.user_type', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'user_type']

class ContactSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Contact
        fields = ['id', 'user', 'name', 'phone', 'email', 'additional', 'created_at', 'updated_at']
    
    def validate_email(self, value):
        EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$")
        if not EMAIL_REGEX.match(value):
            raise serializers.ValidationError("invalid email")
        return value.lower()
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')
    
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'user_type', 'created_at']