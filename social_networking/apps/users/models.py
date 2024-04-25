
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

from social_networking.apps.commons import (
    constants as commons_constants,
    models as commons_models,
    utils as commons_utils
)


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, password=password, **extra_fields)
        user.save(using=self._db)
        return user

    def create(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class SocialNetworkingUser(AbstractBaseUser, PermissionsMixin, commons_models.TimeStamp):
    name = models.CharField(max_length=commons_constants.NAME_LENGTH)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(
        'staff status', default=False,
        help_text='Designates whether the user can log into this admin site.',
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name',]

    objects = UserManager()

    def __str__(self):
        return f'{self.name}'

    @property
    def get_token(self):
        token, created = Token.objects.get_or_create(user=self)
        if created:
            return token.key
        else:
            '''delete already existing token and generate a new one and return'''
            token.delete()
            return Token.objects.create(user=self).key

    def save(self, *args, **kwargs):
        # set password will come into action only if password changed
        # we are setting password here because this is the common place for all flows including django admin.
        if not self.id or 'password' in kwargs.get('update_fields', []):
            self.set_password(self.password)
        return super().save(*args, **kwargs)


class Token(commons_models.TimeStamp):
    """ Authentication Token Model """

    key = models.CharField('key', max_length=500)
    user = models.OneToOneField(
        SocialNetworkingUser, on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.user} {self.key}'

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = commons_utils.generate_key()
        return super().save(*args, **kwargs)


class FriendshipRequest(commons_models.TimeStamp):
    PENDING = 1
    ACCEPTED = 2
    REJECTED = 3
    REQUEST_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected')
    ]
    sender = models.ForeignKey(SocialNetworkingUser, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(SocialNetworkingUser, related_name='received_requests', on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(default=PENDING, choices=REQUEST_STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender} -> {self.receiver} -> {dict(self.REQUEST_STATUS_CHOICES).get(self.status)}'


class Friend(commons_models.TimeStamp):
    user = models.ForeignKey(SocialNetworkingUser, related_name='friends', on_delete=models.CASCADE)
    friend = models.ForeignKey(SocialNetworkingUser, related_name='user_friends', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} -> {self.friend}'
