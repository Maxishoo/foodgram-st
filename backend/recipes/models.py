from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(verbose_name='название', max_length=128)
    measurement_unit = models.CharField(
        verbose_name='единицы измерения', max_length=64)

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='автор',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(verbose_name='название', max_length=256)
    image = models.ImageField(
        verbose_name='изображение',
        upload_to='recipes/images/',
        blank=False
    )
    text = models.TextField(verbose_name='описание', blank=False)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='ингредиенты',
        related_name='recipes'
    )
    cooking_time = models.IntegerField(
        verbose_name='время приготовления в минутах',
        validators=[MinValueValidator(1)],
        blank=False
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ['name']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='ingredient_amounts')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe'
            )
        ]
        ordering = ['ingredient__name']
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        name = self.ingredient.name
        unit = self.ingredient.measurement_unit
        return f"{name} - {self.amount}{unit}"
