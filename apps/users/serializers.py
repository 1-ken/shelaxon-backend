"""
User Serializers
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth. password_validation import validate_password
from .models import WholesalerProfile, RetailerProfile

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers. CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'password_confirm',
            'user_type', 'phone_number', 'business_name', 
            'business_registration_number', 'location', 'city'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data. pop('password')
        user = User. objects.create(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create profile based on user type
        if user.user_type == User.UserType. WHOLESALER:
            WholesalerProfile.objects.create(user=user)
        elif user.user_type == User. UserType.RETAILER:
            RetailerProfile.objects.create(user=user)
        
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'user_type', 'phone_number',
            'business_name', 'location', 'city', 'is_verified',
            'profile_image', 'created_at'
        ]
        read_only_fields = ['id', 'is_verified', 'created_at']


class WholesalerProfileSerializer(serializers. ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = WholesalerProfile
        fields = '__all__'


class RetailerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = RetailerProfile
        fields = '__all__'"""
User Serializers
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth. password_validation import validate_password
from .models import WholesalerProfile, RetailerProfile

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers. CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'password_confirm',
            'user_type', 'phone_number', 'business_name', 
            'business_registration_number', 'location', 'city'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data. pop('password')
        user = User. objects.create(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create profile based on user type
        if user.user_type == User.UserType. WHOLESALER:
            WholesalerProfile.objects.create(user=user)
        elif user.user_type == User. UserType.RETAILER:
            RetailerProfile.objects.create(user=user)
        
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'user_type', 'phone_number',
            'business_name', 'location', 'city', 'is_verified',
            'profile_image', 'created_at'
        ]
        read_only_fields = ['id', 'is_verified', 'created_at']


class WholesalerProfileSerializer(serializers. ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = WholesalerProfile
        fields = '__all__'


class RetailerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = RetailerProfile
        fields = '__all__'