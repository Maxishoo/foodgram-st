from django.contrib.auth.models import AbstractUser
from django.db.models import UniqueConstraint
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


def check_username(value):
    if value.lower() == 'me':
        raise ValidationError('Некорректное имя пользователя')


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (USER, 'user'),
        (ADMIN, 'admin'),
    ]

    role = models.CharField(
        'Роль пользователя',
        max_length=5,
        choices=ROLE_CHOICES,
        default=USER,
        blank=True,
    )

    email = models.EmailField(
        'email',
        max_length=254,
        blank=False,
        unique=True
    )

    avatar = models.ImageField(
        verbose_name="аватар",
        upload_to='users/',
        blank=True
    )

    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=False,
        validators=[
            RegexValidator(
                regex=r'^[а-яА-ЯёЁa-zA-Z -]+$',
                message='Введите корректное имя'
            ), check_username
        ]
    )
    
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=False,
        validators=[
            RegexValidator(
                regex=r'^[а-яА-ЯёЁa-zA-Z -]+$',
                message='Введите корректное имя'
            ), check_username
        ]
    )

    password = models.CharField(
        'Пароль',
        max_length=150,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'last_name', 'first_name', ]

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_guest(self):
        return self.role == self.GUEST

    class Meta:
        ordering = ('id',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор, на которого подписываются',
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            UniqueConstraint(fields=['user', 'author'],
                             name='unique_subscription')
        ]
