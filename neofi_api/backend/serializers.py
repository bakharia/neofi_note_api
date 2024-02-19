from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Note

class AlphaNumericValidator:
    """
    Validator to ensure that a string contains only alphanumeric characters.
    """

    def __call__(self, value):
        if not value.isalnum():
            raise ValidationError(
                _("Password must contain only alphanumeric characters."),
                code='password_not_alphanumeric'
            )

class TitleLengthValidator:
    """
    Validator to ensure that the length of the title does not exceed 255 characters.
    """

    def __call__(self, value):
        if len(value) > 255:
            raise ValidationError(
                _("Title must not exceed 255 characters."),
                code='title_too_long'
            )

class ContentLengthValidator:
    """
    Validator to ensure that the length of the content does not exceed a certain limit.
    """

    max_length = 1000  # Define the maximum length for the content

    def __call__(self, value):
        if len(value) > self.max_length:
            raise ValidationError(
                _("Content must not exceed {max_length} characters.").format(max_length=self.max_length),
                code='content_too_long'
            )

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    This serializer is used for creating and updating User instances.

    Attributes:
        password (CharField): The password field is write-only for security reasons.

    Methods:
        create(validated_data): Creates a new user instance using validated data.

    """
    password = serializers.CharField(write_only=True, validators=[AlphaNumericValidator()])  # Hide password field in response

    class Meta:
        model = User  # Specify the model to be serialized
        fields = ['username', 'email', 'password']  # Define the fields to include in the serialization
    
    def create(self, validated_data):
        """
        Method to create a new user instance.

        Args:
            validated_data (dict): The validated data for creating a new user.

        Returns:
            User: The newly created user instance.

        """
        user = User.objects.create_user(**validated_data)  # Create a new user with the provided data
        return user  # Return the created user

class NoteSerializer(serializers.ModelSerializer):
    """
    Serializer for the Note model.

    This serializer is used for serializing Note instances.

    """

    title = serializers.CharField(validators=[TitleLengthValidator()])  # Apply title length validator
    content = serializers.CharField(validators=[ContentLengthValidator()])  # Apply content length validator

    class Meta:
        model = Note  # Specify the model to be serialized
        fields = ['id', 'user', 'title', 'content', 'created_at', 'updated_at']  # Define the fields to include in the serialization
