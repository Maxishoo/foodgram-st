from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F, Sum
from django.http import HttpResponse
from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from djoser.serializers import SetPasswordSerializer
from django.contrib.auth import update_session_auth_hash
from rest_framework.decorators import action
from recipes.models import (Recipe, Favorite,
                            ShoppingList, IngredientInRecipe,
                            Ingredient)
from users.models import Subscription
from .serializers import (IngredientSerializer, AvatarSerializer,
                          RecipeGetSerializer, FavoriteSerializer,
                          RecipePostSerializer, RecipeShortSerializer,
                          ShoppingListSerializer, UserGetSerializer,
                          UserPostSerializer, UserWithRecipesSerializer,
                          SubscriptionSerializer)
from .filters import RecipeFilter, IngredientFilter
from .pagination import CustomPagination
from .utils import post_and_delete_action
from .permissions import IsAuthorOrAdminOrReadOnly

from django.contrib.auth import get_user_model
User = get_user_model()


class AvatarView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AvatarSerializer

    def put(self, request):
        user = request.user
        serializer = AvatarSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomUserViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()
    pagination_class = CustomPagination

    def get_instance(self):
        return self.request.user

    def get_serializer_class(self):
        if self.action in ['subscriptions', 'subscribe']:
            return UserWithRecipesSerializer
        elif self.request.method == 'POST':
            return UserPostSerializer
        elif self.request.method == 'GET':
            return UserGetSerializer

    def get_permissions(self):
        if self.action == 'retrieve':
            self.permission_classes = [IsAuthenticated, ]
        return super(self.__class__, self).get_permissions()

    @action(
        detail=False,
        methods=['get', 'put', 'patch', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
        url_name='user-me-avatar'
    )
    def me_avatar(self, request, *args, **kwargs):
        return AvatarView.as_view()(request._request)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(
        ["POST"],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request, *args, **kwargs):
        serializer = SetPasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data['new_password'])
        self.request.user.save()
        update_session_auth_hash(self.request, self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        users = User.objects.filter(
            following__user=request.user
        ).prefetch_related('recipes')
        page = self.paginate_queryset(users)

        if page is not None:
            serializer = UserWithRecipesSerializer(
                page, many=True,
                context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = UserWithRecipesSerializer(
            users, many=True, context={'request': request}
        )

        return Response(serializer.data)

    @action(
        ["POST", "DELETE"],
        detail=True,
        permission_classes=[],
    )
    def subscribe(self, request, **kwargs):
        return post_and_delete_action(
            self, request, User, Subscription, SubscriptionSerializer, **kwargs
        )

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrAdminOrReadOnly, ]
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        elif self.action in ['favorite', 'shopping_cart', ]:
            return RecipeShortSerializer

        return RecipePostSerializer

    @action(["POST", "DELETE"], detail=True)
    def favorite(self, request, **kwargs):
        return post_and_delete_action(
            self,
            request,
            Recipe,
            Favorite,
            FavoriteSerializer,
            **kwargs
        )

    @action(["POST", "DELETE"], detail=True)
    def shopping_cart(self, request, **kwargs):
        return post_and_delete_action(
            self,
            request,
            Recipe,
            ShoppingList,
            ShoppingListSerializer,
            **kwargs
        )

    @action(
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=user).values(
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')).annotate(
            amount=Sum('amount')
        )
        data = []
        for ingredient in ingredients:
            data.append(
                f'{ingredient["name"]} - '
                f'{ingredient["amount"]} '
                f'{ingredient["measurement_unit"]}'
            )
        content = 'Список продуктов:\n\n' + '\n'.join(data)
        filename = 'ist_of_products.txt'
        request = HttpResponse(content, content_type='text/plain')
        request['Content-Disposition'] = f'attachment; filename={filename}'
        return request
