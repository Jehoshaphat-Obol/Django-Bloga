from rest_framework import serializers
from django.contrib.auth.models import Group, User
from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.HyperlinkedModelSerializer):
    old_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['url', 'username', 'first_name', 'last_name', 'email', 'password', 'old_password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'write_only': True},
            'old_password': {'write_only': True, 'required': False},
            'url': {'view_name': "v1:user-detail", "lookup_field": "username"}
        }

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        
        old_password = validated_data.get('old_password', None)
        new_password = validated_data.get('password', None)

        # Check if the old password is provided and validate it
        if old_password:
            if not check_password(old_password, instance.password):
                raise serializers.ValidationError({'old_password': 'Old password is incorrect.'})

        # If new password is provided, set the new password
        if new_password:
            instance.set_password(new_password)
        
        instance.save()
        return instance

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url",'name']
        extra_kwargs = {
            "url": {"view_name": "v1:group-detail", "lookup_field": "name"}
        }
                