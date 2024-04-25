
from datetime import datetime

from rest_framework import response, status, views
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from django.db.models import Q

from social_networking.apps.users import (
    models as users_models,
    serializers as users_serializers,
)


class UserRegisterView(views.APIView):
    """
    Save Data of user on sign up
    """

    def post(self, request):
        serializer = users_serializers.UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return response.Response(
            users_serializers.UserTokenSerializer(user).data,
            status=status.HTTP_201_CREATED
        )


class LoginView(views.APIView):
    """
    Login API for user
    """

    def post(self, request):
        """
        create token when user successfully authenticated
        """
        serializer = users_serializers.LoginSerializer()
        data = serializer.validate(data=request.data)
        user = data.get('user')
        serializer = users_serializers.UserTokenSerializer(user)
        data = serializer.data
        # update last_login of user.
        user.last_login = datetime.now()
        user.save()
        return response.Response(data, status.HTTP_202_ACCEPTED)


class UserSearchAPIView(APIView):
    """
    Api to allow users to search for users to generate friend requests etc
    We need to pass q named query param in the url to search for users with email or name
    For Ex: <domain>/accounts/search?q=sumit
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get query parameters for search
        search_keyword = request.query_params.get('q', '')
        q_filter = ~Q(id=request.user.id)

        # First try to match a user by exact email, if not found then get users whose name contains search param
        users = users_models.SocialNetworkingUser.objects.filter(q_filter, email__iexact=search_keyword) | (
            users_models.SocialNetworkingUser.objects.filter(q_filter, name__icontains=search_keyword).order_by('-id')
        )

        # Pagination
        paginator = PageNumberPagination()
        paginated_users = paginator.paginate_queryset(users, request)

        # Serialize the queryset
        serializer = users_serializers.BaseUserSerializer(paginated_users, many=True)

        return paginator.get_paginated_response(serializer.data)


class SendFriendRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.data['sender'] = request.user.id
        serializer = users_serializers.FriendshipRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # we can just send status code in response,
            # i am sending the data just to have clarity while evaluating through postman
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AcceptRejectFriendRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, request_id):
        serializer = users_serializers.AcceptRejectFriendRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Filter only those friend requests whose receiver is logged in user and status is pending.
        friendship_request = users_models.FriendshipRequest.objects.filter(
            pk=request_id, receiver=request.user, status=users_models.FriendshipRequest.PENDING
        )
        if not friendship_request:
            return response.Response(
                data={'Error': 'No such pending friend request for this user'}, status=status.HTTP_404_NOT_FOUND
            )
        friendship_request = friendship_request.first()
        action = serializer.data['action']
        if action == 'accept':
            friendship_request.status = users_models.FriendshipRequest.ACCEPTED
            friendship_request.save()
            # Create Friend object if user is accepting the request.
            friend = users_models.Friend(user=friendship_request.sender, friend=request.user)
            friend.save()
        elif action == 'reject':
            friendship_request.status = users_models.FriendshipRequest.REJECTED
            friendship_request.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class ListFriendsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        friends = users_models.Friend.objects.filter(Q(user=request.user)|Q(friend=request.user)).order_by('-id')

        # Pagination
        paginator = PageNumberPagination()
        paginated_requests = paginator.paginate_queryset(friends, request)

        # In Friend model, logged in user can be Friend.user and Friend.friend for different Friend objects.
        # So, filter only those users who don't match with logger in user and return.
        friend_users = [friend.friend if friend.user_id == request.user.id else friend.user for friend in paginated_requests]

        serializer = users_serializers.BaseUserSerializer(friend_users, many=True)
        return paginator.get_paginated_response(serializer.data)


class ListPendingFriendRequestsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pending_requests = users_models.FriendshipRequest.objects.filter(
            receiver=request.user, status=users_models.FriendshipRequest.PENDING
        ).order_by('-id')

        # Pagination
        paginator = PageNumberPagination()
        paginated_requests = paginator.paginate_queryset(pending_requests, request)

        serializer = users_serializers.PendingFriendshipRequestSerializer(paginated_requests, many=True)
        return paginator.get_paginated_response(serializer.data)
