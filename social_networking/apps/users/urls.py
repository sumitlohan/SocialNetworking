from django.conf.urls import include, url
from django.urls import path

from social_networking.apps.users import views as users_views

from rest_framework import routers

router = routers.SimpleRouter()

# router.register('user', users_views.UserView, basename='user')

urlpatterns = [
    url(r'^login/$', users_views.LoginView.as_view(), name='login'),
    url(r'user/$', users_views.UserRegisterView.as_view(), name='user'),
    url('search/$', users_views.UserSearchAPIView.as_view(), name='user-search'),
    path('friend-request/<int:request_id>/', users_views.AcceptRejectFriendRequestAPIView.as_view(), name='accept-reject-friend-request'),
    url('friend-request/send/', users_views.SendFriendRequestAPIView.as_view(), name='send-friend-request'),
    url('friends/', users_views.ListFriendsAPIView.as_view(), name='list-friends'),
    url('pending-friend-requests/$', users_views.ListPendingFriendRequestsAPIView.as_view(), name='list-pending-friend-requests'),
    # url(r'', include(router.urls)),
]
