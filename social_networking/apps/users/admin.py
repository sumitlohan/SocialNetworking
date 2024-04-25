from django.contrib import admin

from social_networking.apps.users import models as users_models


# Register your models here.
admin.site.register(users_models.SocialNetworkingUser)
admin.site.register(users_models.Friend)
admin.site.register(users_models.FriendshipRequest)
