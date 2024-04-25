
from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions

from social_networking.apps.users import models as users_models


class CustomTokenAuthentication(TokenAuthentication):
    model = users_models.Token

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        return token.user, token
