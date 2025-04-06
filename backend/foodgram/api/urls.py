from rest_framework.routers import SimpleRouter
from django.urls import re_path, include
from . import views

router = SimpleRouter()
router.register(r'recipes', views.RecipeViewSet, basename='recipes')
router.register(r'ingredients', views.IngredientViewSet,
                basename='ingredients')

urlpatterns = [
    re_path(r'^', include(router.urls)),
]
