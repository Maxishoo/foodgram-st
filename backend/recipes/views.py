from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework import permissions
from recipes.models import Recipe, Ingredient, RecipeIngredient
from .serializers import (
    RecipeSerializer, IngredientSerializer)
from backend.permissions import AuthorOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [AuthorOrReadOnly]
    pagination_class = LimitOffsetPagination

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_authenticated:
            is_favorited = self.request.query_params.get('is_favorited')
            if is_favorited:
                queryset = queryset.filter(id__in=user.favorites.values('id'))

            is_in_shopping_cart = self.request.query_params.get(
                'is_in_shopping_cart')
            if is_in_shopping_cart:
                queryset = queryset.filter(
                    id__in=user.shopping_card.values('id'))

        author_id = self.request.query_params.get('author')
        if author_id:
            queryset = queryset.filter(author__id=author_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        link = request.build_absolute_uri(f'/recipes/{recipe.id}/')

        return Response({
            "short-link": link
        }, status=status.HTTP_200_OK)


class ShoppingCartAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        # Получаем все рецепты из списка покупок пользователя
        recipes_in_cart = user.shopping_card.all()

        # Получаем все ингредиенты для этих рецептов одним запросом
        rec_ingredients = RecipeIngredient.objects.filter(
            recipe__in=recipes_in_cart
        ).select_related('ingredient')

        ingredients = {}

        for rec_ingr in rec_ingredients:
            key = f"{rec_ingr.ingredient.name} ({rec_ingr.ingredient.measurement_unit})"

            if key in ingredients:
                ingredients[key]['amount'] += rec_ingr.amount
            else:
                ingredients[key] = {
                    'amount': rec_ingr.amount,
                    'measurement_unit': rec_ingr.ingredient.measurement_unit
                }

        lines = ["Список покупок:"]
        for name, data in sorted(ingredients.items()):
            lines.append(
                f"{name} — {data['amount']}")

        response = HttpResponse(
            "\n".join(lines),
            content_type='text/plain'
        )
        filename = "shopping_list.txt"
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.user.shopping_card.filter(pk=recipe.pk).exists():
            return Response(
                {'detail': 'Рецепт уже в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.user.shopping_card.add(recipe)
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)

        if not request.user.shopping_card.filter(pk=recipe.pk).exists():
            return Response(
                {'detail': 'Рецепта нет в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.user.shopping_card.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.user.favorites.filter(pk=recipe.pk).exists():
            return Response(
                {'detail': 'Рецепт уже в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.user.favorites.add(recipe)
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)

        if not request.user.favorites.filter(pk=recipe.pk).exists():
            return Response(
                {'detail': 'Рецепта нет в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.user.favorites.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ModelViewSet):
    permission_classes = [AuthorOrReadOnly]
    pagination_class = LimitOffsetPagination

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['^name']

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name', None)

        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset
