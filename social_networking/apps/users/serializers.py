import datetime
import re

from django.contrib.auth.hashers import check_password
from django.db.models import Q

from rest_framework import serializers

from social_networking.apps.users import models as users_models
from social_networking.apps.commons import constants as commons_constants


class BaseUserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['id', 'name', 'email']
        model = users_models.SocialNetworkingUser


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': commons_constants.MIN_PASSWORD_LENGTH},
        }
        model = users_models.SocialNetworkingUser

    def validate_password(self, password):
        if re.search('[A-Z]', password) is None:
            raise serializers.ValidationError(
                'missing_upper_case'
            )
        if re.search('[a-z]', password) is None:
            raise serializers.ValidationError(
                'missing_lower_case'
            )
        if re.search('[0-9]', password) is None:
            raise serializers.ValidationError('missing_digit')
        return password


class UserTokenSerializer(UserSerializer):
    """
    Serializer for returning token along with user data
    """
    token = serializers.CharField(source='get_token')

    class Meta(UserSerializer.Meta):
        # check this
        fields = '__all__'


class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        """
        Authenticate user
        """
        try:
            user = users_models.SocialNetworkingUser.objects.get(
                email__iexact=data.get('email', '')
            )
        except users_models.SocialNetworkingUser.DoesNotExist:
            raise serializers.ValidationError(
                {'error': 'Invalid Credentials'}
            )
        if check_password(data['password'], user.password):
            data['user'] = user
            return data
        else:
            raise serializers.ValidationError(
                {'error': 'Invalid Credentials'}
            )


class AcceptRejectFriendRequestSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['accept', 'reject'])


class PendingFriendshipRequestSerializer(serializers.ModelSerializer):
    sender_data = BaseUserSerializer(read_only=True, source='sender')

    class Meta:
        model = users_models.FriendshipRequest
        fields = ['id', 'status', 'created_at', 'sender_data']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['status'] = dict(users_models.FriendshipRequest.REQUEST_STATUS_CHOICES).get(instance.status, 'Unknown')
        return representation


class FriendshipRequestSerializer(PendingFriendshipRequestSerializer):
    receiver = serializers.PrimaryKeyRelatedField(queryset=users_models.SocialNetworkingUser.objects.all())
    receiver_data = BaseUserSerializer(read_only=True, source='receiver')

    class Meta:
        model = users_models.FriendshipRequest
        fields = ['id', 'sender', 'receiver', 'status', 'created_at', 'sender_data', 'receiver_data']
        extra_kwargs = {
            'status': {'read_only': True},
            'created_at': {'read_only': True},
            'sender': {'write_only': True},
            'receiver': {'write_only': True},
        }

    def validate(self, attrs):
        sender = attrs.get('sender')
        if users_models.FriendshipRequest.objects.filter(
            sender=sender, created_at__gte=datetime.datetime.now() - datetime.timedelta(minutes=1)
        ).count() > 3:
            raise serializers.ValidationError(
                'You have reached maximum friendship requests per minute limit. '
                'Please wait for a minute to send more requests!!'
            )
        receiver = attrs.get('receiver')
        if sender == receiver:
            raise serializers.ValidationError('You cannot send friend request to yourself!!')
        if users_models.FriendshipRequest.objects.filter(
            sender=sender, receiver=receiver, status=users_models.FriendshipRequest.PENDING
        ):
            raise serializers.ValidationError('One request is already pending with same receiver!!')
        if users_models.Friend.objects.filter(Q(user=sender, friend=receiver) | Q(user=receiver, friend=sender)).exists():
            raise serializers.ValidationError('You both are already friends!!')
        return attrs
