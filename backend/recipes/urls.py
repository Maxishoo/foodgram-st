from rest_framework.routers import SimpleRouter
from django.urls import re_path, include, path
from . import views
from .views import ShoppingCartAPIView, FavoriteAPIView

router = SimpleRouter()
router.register(r'recipes', views.RecipeViewSet, basename='recipes')
router.register(r'ingredients', views.IngredientViewSet,
                basename='ingredients')

urlpatterns = [
    path('recipes/download_shopping_cart/',
         ShoppingCartAPIView.as_view(), name='download-shopping-list'),
    path(
        'recipes/<int:pk>/shopping_cart/',
        ShoppingCartAPIView.as_view(),
        name='shopping-cart'
    ),
    path(
        'recipes/<int:pk>/favorite/',
        FavoriteAPIView.as_view(),
        name='favorite'
    ),

    re_path(r'^', include(router.urls)),
]
