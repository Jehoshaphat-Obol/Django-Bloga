from api.v1.authentication import serializers

class UserSerializer(serializers.UserSerializer):
    class Meta(serializers.UserSerializer.Meta):
        extra_kwargs = {
            'password': {'write_only': True, "style": {"input_type": "password"}},
            'email': {'write_only': True},
            'old_password': {'write_only': True, 'required': False, "style": {"input_type": "password"}},
            'url': {'view_name': "v2:user-detail", "lookup_field": "username"}
        }
        