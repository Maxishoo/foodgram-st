from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from recipes.models import (
    Recipe, Ingredient, IngredientInRecipe
)

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertEqual(self.user.role, 'user')
        self.assertFalse(self.user.is_admin)

    def test_admin_user(self):
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='adminpass123'
        )
        self.assertTrue(admin_user.is_admin)


class RecipeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='chef@example.com',
            username='chef',
            password='chefpass123'
        )
        self.ingredient = Ingredient.objects.create(
            name='Flour',
            measurement_unit='g'
        )
        self.recipe = Recipe.objects.create(
            author=self.user,
            name='Test Recipe',
            text='Test description',
            cooking_time=30
        )
        IngredientInRecipe.objects.create(
            recipe=self.recipe,
            ingredient=self.ingredient,
            amount=200
        )

    def test_recipe_creation(self):
        self.assertEqual(self.recipe.name, 'Test Recipe')
        self.assertEqual(self.recipe.author, self.user)
        self.assertEqual(self.recipe.cooking_time, 30)
        self.assertEqual(self.recipe.ingredients.count(), 1)
