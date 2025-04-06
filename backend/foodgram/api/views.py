from rest_framework import viewsets
# from rest_framework import permissions
from recipes.models import Recipe, Ingredient
from .serializers import (
    RecipeSerializer, IngredientSerializer)
from .permissions import AuthorOrReadOnly  # , UserOrReadOnly
# from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.pagination import LimitOffsetPagination
# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework import filters

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [AuthorOrReadOnly]
    pagination_class = LimitOffsetPagination

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class IngredientViewSet(viewsets.ModelViewSet):
    permission_classes = [AuthorOrReadOnly]
    pagination_class = LimitOffsetPagination

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
