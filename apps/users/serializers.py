"""
User Serializers
"""

from rest_framework import serializers
from rest_framework import exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import WholesalerProfile, RetailerProfile

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration. Creates a new user account."""
    password = serializers.CharField(write_only=True, validators=[validate_password], help_text="User password (must meet security requirements)")
    password_confirm = serializers.CharField(write_only=True, help_text="Confirm password (must match password)")

    class Meta:
        model = User
        fields = [
            'id', 'username', 'phone_number', 'password', 'password_confirm',
            'user_type', 'business_name', 'city'
        ]
        extra_kwargs = {
            'username': {'help_text': 'Unique username for the account'},
            'phone_number': {'help_text': 'Phone number in international format (e.g., +254712345678)'},
            'user_type': {'help_text': 'Type of user: retailer or wholesaler'},
            'business_name': {'help_text': 'Name of the business'},
            'city': {'help_text': 'City where the business is located'}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create profile based on user type
        if user.user_type == User.UserType.WHOLESALER:
            WholesalerProfile.objects.create(user=user)
        elif user.user_type == User.UserType.RETAILER:
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


class WholesalerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = WholesalerProfile
        fields = '__all__'


class RetailerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = RetailerProfile
        fields = '__all__'


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile details. All fields are optional."""
    username = serializers.CharField(required=False, help_text="Unique username for the user")
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True, help_text="User's email address")
    phone_number = serializers.CharField(required=False, help_text="Phone number in international format (e.g., +254712345678)")
    business_name = serializers.CharField(required=False, help_text="Name of the business")
    location = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text="Business location/address")
    city = serializers.CharField(required=False, help_text="City where the business is located")
    profile_image = serializers.URLField(required=False, allow_blank=True, allow_null=True, help_text="URL to the user's profile image")

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'business_name', 'location', 'city', 'profile_image']

    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_phone_number(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(phone_number=value).exists():
            raise serializers.ValidationError("This phone number is already registered.")
        return value

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.business_name = validated_data.get('business_name', instance.business_name)
        instance.location = validated_data.get('location', instance.location)
        instance.city = validated_data.get('city', instance.city)
        instance.profile_image = validated_data.get('profile_image', instance.profile_image)
        instance.save()
        return instance


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT login with clearer error messages."""

    def validate(self, attrs):
        username = attrs.get(self.username_field)
        password = attrs.get("password")

        if not username or not password:
            raise exceptions.ValidationError("Username and password are required.")

        user = User.objects.filter(**{self.username_field: username}).first()
        if user is None:
            raise exceptions.AuthenticationFailed("User is not registered.", code="user_not_found")

        if not user.is_active:
            raise exceptions.AuthenticationFailed(
                "Account is inactive. Please contact support.",
                code="account_inactive",
            )

        if not user.check_password(password):
            raise exceptions.AuthenticationFailed("Invalid username or password.", code="invalid_credentials")

        self.user = user  # Required so JWT tokens bind to this user
        refresh = self.get_token(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data,
        }


class AdminPasswordResetSerializer(serializers.Serializer):
    """Serializer for admin to reset user password"""
    user_id = serializers.IntegerField(help_text="ID of the user whose password will be reset")
    new_password = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="New password (optional). If not provided, default password 'Reset@123' will be used"
    )
    
    def validate_user_id(self, value):
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for users to change their own password"""
    old_password = serializers.CharField(required=True, help_text="Current password")
    new_password = serializers.CharField(required=True, validators=[validate_password], help_text="New password")
    confirm_password = serializers.CharField(required=True, help_text="Confirm new password")
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "New passwords don't match."})
        return attrs
