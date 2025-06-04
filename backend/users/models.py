from django.db import models
from django.db import models
from django.contrib.auth.models import (
    AbstractUser, PermissionsMixin)


class CustomUser(AbstractUser, PermissionsMixin):
    email = models.EmailField(
        "Адрес электронной почты", max_length=150, unique=True)
    username = models.CharField("Никнейм", max_length=150, unique=True)

    avatar = models.ImageField(
        verbose_name="Аватар",
        upload_to='users/',
        blank=True
    )

    subscriptions = models.ManyToManyField(
        'self',
        verbose_name="Подписки",
        symmetrical=False,
        related_name='subscribers',
        blank=True,
    )

    favorites = models.ManyToManyField(
        'recipes.Recipe',
        verbose_name="Избранное",
        related_name='favorite_recipes',
        blank=True
    )

    shopping_card = models.ManyToManyField(
        'recipes.Recipe',
        verbose_name="Список покупок",
        related_name='shopping_card',
        blank=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
