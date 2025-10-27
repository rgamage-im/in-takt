"""
Microsoft Graph API Serializers
"""
from rest_framework import serializers


class UserProfileSerializer(serializers.Serializer):
    """
    Serializer for Microsoft Graph user profile data
    """
    id = serializers.CharField(read_only=True)
    displayName = serializers.CharField(read_only=True)
    givenName = serializers.CharField(read_only=True, required=False)
    surname = serializers.CharField(read_only=True, required=False)
    mail = serializers.EmailField(read_only=True, required=False)
    userPrincipalName = serializers.CharField(read_only=True)
    jobTitle = serializers.CharField(read_only=True, required=False)
    department = serializers.CharField(read_only=True, required=False)
    officeLocation = serializers.CharField(read_only=True, required=False)
    mobilePhone = serializers.CharField(read_only=True, required=False)
    businessPhones = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
        required=False
    )


class UserListSerializer(serializers.Serializer):
    """
    Serializer for list of users
    """
    value = UserProfileSerializer(many=True, read_only=True)
    odataNextLink = serializers.CharField(
        read_only=True, 
        required=False,
        source='@odata.nextLink'
    )
    odataCount = serializers.IntegerField(
        read_only=True,
        required=False,
        source='@odata.count'
    )
