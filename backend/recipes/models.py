from django.db import models
from django.db.models import UniqueConstraint
from django.core.validators import MinValueValidator, RegexValidator

from django.contrib.auth import get_user_model
User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=200,
        validators=[
            RegexValidator(
                regex=r'^[а-яА-ЯёЁa-zA-Z -]+$',
                message='Введите корректное название'
            )
        ]
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=100
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} в {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE
    )

    name = models.CharField(
        'Название рецепта',
        max_length=200,
        validators=[
            RegexValidator(
                regex=r'^[а-яА-ЯёЁa-zA-Z -]+$',
                message='Введите корректное название'
            )
        ]
    )

    text = models.TextField(
        'Текстовое описание',
    )

    image = models.ImageField(
        'Картинка',
        upload_to='recipes/images/',
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
    )

    cooking_time = models.IntegerField(
        'Время приготовления в минутах',
        validators=[
            MinValueValidator(
                1, 'Время приготовление должно быть не меньше минуты'
            )
        ]
    )

    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='IngredientsInRecipe',
        on_delete=models.CASCADE
    )

    ingredient = models.ForeignKey(
        Ingredient,
        related_name='IngredientsInRecipe',
        on_delete=models.CASCADE
    )

    amount = models.IntegerField(
        'Колличество',
        validators=[
            MinValueValidator(
                1, 'Колличество должно быть не менее 1.'
            )
        ]
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return f'{self.ingredient.name} в {self.recipe.name}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='FavoriteRecipe',
        on_delete=models.CASCADE
    )

    recipe = models.ForeignKey(
        Recipe,
        related_name='FavoriteRecipe',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            UniqueConstraint(fields=['user', 'recipe'],
                             name='unique_favorite')
        ]

    def __str__(self):
        return f'{self.recipe.name} в избанном у {self.user.username}'


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        related_name='RecipeInShoppingList',
        on_delete=models.CASCADE,
    )

    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping_cart',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = [
            UniqueConstraint(fields=['user', 'recipe'],
                             name='unique_shopping_list')
        ]

    def __str__(self):
        return f'{self.recipe.name} в покупках у {self.user.username}'
