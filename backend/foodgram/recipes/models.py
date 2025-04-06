from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='название',
        max_length=128)
    measurement_unit = models.CharField(
        verbose_name='еденицы измерения',
        max_length=64)

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = author = models.ForeignKey(
        User,
        verbose_name='автор',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(
        verbose_name='название',
        max_length=256)
    image = models.ImageField(
        verbose_name='изображение',
        upload_to='recipes/images/',
        blank=False
    )
    text = models.TextField(verbose_name='описание', blank=False)
    ingredients = models.ForeignKey(
        Ingredient, verbose_name='ингредиенты', on_delete=models.CASCADE,
        related_name='recipes', blank=False, null=False
    )
    cooking_time = models.IntegerField(
        verbose_name='время приготовления',
        validators=[MinValueValidator(1)],
        blank=False)

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name
