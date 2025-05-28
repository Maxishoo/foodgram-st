from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from recipes.models import (
    Recipe, Ingredient, IngredientInRecipe, Favorite, ShoppingList
)
from users.models import Subscription

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


class UserAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_user_registration(self):
        url = reverse('users-list')
        data = {
            'email': 'new@example.com',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_get_current_user(self):
        url = reverse('users-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_set_password(self):
        url = reverse('users-set-password')
        data = {
            'current_password': 'testpass123',
            'new_password': 'newpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(self.user.check_password('newpass123'))


class RecipeAPITest(APITestCase):
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
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_recipes(self):
        url = reverse('recipes-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_recipe(self):
        url = reverse('recipes-list')
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'simple image content',
            content_type='image/jpeg'
        )
        data = {
            'name': 'New Recipe',
            'text': 'New description',
            'cooking_time': 45,
            'ingredients': [{'id': self.ingredient.id, 'amount': 300}],
            'image': image
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipe.objects.count(), 2)

    def test_add_to_favorites(self):
        url = reverse('recipes-favorite', kwargs={'pk': self.recipe.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Favorite.objects.filter(
            user=self.user,
            recipe=self.recipe
        ).exists())


class SubscriptionAPITest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            username='user1',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            username='user2',
            password='pass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

    def test_subscribe(self):
        url = reverse('users-subscribe', kwargs={'pk': self.user2.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Subscription.objects.filter(
            user=self.user1,
            author=self.user2
        ).exists())

    def test_unsubscribe(self):
        Subscription.objects.create(user=self.user1, author=self.user2)
        url = reverse('users-subscribe', kwargs={'pk': self.user2.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Subscription.objects.filter(
            user=self.user1,
            author=self.user2
        ).exists())

    def test_get_subscriptions(self):
        Subscription.objects.create(user=self.user1, author=self.user2)
        url = reverse('users-subscriptions')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)