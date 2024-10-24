from rest_framework import serializers
from django.contrib.auth.models import Group, User
from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from django.contrib.auth.models import User
from authentication.models import Profile

class UserSerializer(serializers.HyperlinkedModelSerializer):
    old_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['url', 'username', 'first_name', 'last_name', 'email', 'password', 'old_password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'write_only': True},
            'old_password': {'write_only': True, 'required': False},
            'url': {'view_name': "user-detail", "lookup_field": "username"}
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
            elif new_password:
                instance.set_password(new_password)
        
        instance.save()
        return instance


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url",'name']
        extra_kwargs = {
            "url": {"view_name": "group-detail", "lookup_field": "name"}
        }



class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = ['url', 'user', 'bio', 'dp', 'follows', 'followers']
        extra_kwargs = {
            'url': {'view_name': 'profile-detail', 'lookup_field':"pk",},
            'user': {'view_name': 'user-detail', 'lookup_field':"username", 'read_only': True},
            'follows': {'view_name': 'user-detail', 'lookup_field':"username", 'queryset': User.objects.all(), 'many': True},
            'followers': {'view_name': 'user-detail', 'lookup_field':"username", 'read_only': True, 'many': True},
            'dp': {'required': False}
        }

    def update(self, instance, validated_data):
        # Custom logic to ensure owner can only modify 'follows' and not 'followers'
        request_user = self.context['request'].user
        if instance.user != request_user:
            raise serializers.ValidationError("You do not have permission to modify this profile.")

        # Handle the follows logic (can only modify follows, not followers)
        follows = validated_data.pop('follows', None)
        
        # Update the follows field if it's provided
        if follows is not None:
            # Sync the followers field for other users
            for user in follows:
                profile, created  = Profile.objects.get_or_create(user=user)
                instance.follow(profile)
                

            for user in instance.follows.all():
                profile, created  = Profile.objects.get_or_create(user=user)
                if user not in follows:
                    instance.unfollow(profile)
        
        instance.bio = validated_data.get('bio', instance.bio)
        instance.dp = validated_data.get('dp', instance.dp)
        instance.save()
        
        return instance