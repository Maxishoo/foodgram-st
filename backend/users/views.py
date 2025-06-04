from drf_yasg.utils import swagger_auto_schema
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from .serializers import (CustomUserAuthTokenSerializer,
                          CustomUserViewSerializer, AvatarSerializer)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from backend.permissions import GetOnly
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.generics import ListAPIView, RetrieveAPIView

User = get_user_model()


class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserViewSerializer


class UserDetailView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserViewSerializer
    lookup_field = 'id'


class AvatarView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AvatarSerializer

    @swagger_auto_schema(
        request_body=AvatarSerializer,
        responses={200: AvatarSerializer}
    )
    def put(self, request):
        user = request.user
        serializer = AvatarSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionsView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get(self, request):
        subscriptions = request.user.subscriptions.all()

        paginator = self.pagination_class()
        paginated_subscriptions = paginator.paginate_queryset(
            subscriptions, request)

        user_data = CustomUserViewSerializer(
            paginated_subscriptions,
            many=True,
            context={'request': request}
        ).data

        from recipes.serializers import ShortRecipeSerializer
        from recipes.models import Recipe
        recipes_limit = int(request.query_params.get('recipes_limit', 3))
        for user in user_data:
            recipes = Recipe.objects.filter(author__id=user['id'])[
                :recipes_limit]
            user['recipes'] = ShortRecipeSerializer(recipes, many=True).data
            user['recipes_count'] = Recipe.objects.filter(
                author__id=user['id']).count()

        return paginator.get_paginated_response(user_data)

    def post(self, request, id):
        user = request.user
        subscriber = get_object_or_404(User, pk=id)

        if subscriber in user.subscriptions.all():
            return Response(
                {"detail": "Нельзя подписаться дважды"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if subscriber == user:
            return Response(
                {"detail": "Нельзя подписаться на самого себя"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.subscriptions.add(subscriber)
        user.save()

        serializer = CustomUserViewSerializer(
            subscriber, context={'request': request})
        response_data = serializer.data

        from recipes.serializers import ShortRecipeSerializer
        from recipes.models import Recipe
        recipes_limit = int(request.query_params.get('recipes_limit', 3))
        recipes = Recipe.objects.filter(author=subscriber)[:recipes_limit]
        response_data['recipes'] = ShortRecipeSerializer(
            recipes, many=True).data
        response_data['recipes_count'] = Recipe.objects.filter(
            author=subscriber).count()

        return Response(response_data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        subscriber = get_object_or_404(User, pk=id)

        if subscriber not in user.subscriptions.all():
            return Response(
                {"detail": "Нельзя отписаться от того, на кого не подписан"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if subscriber == user:
            return Response(
                {"detail": "Нельзя отписаться и подписаться на самого себя"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.subscriptions.remove(subscriber)
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomAuthToken(ObtainAuthToken):
    serializer_class = CustomUserAuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'auth_token': token.key
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_204_NO_CONTENT
            )
        except Token.DoesNotExist:
            return Response(
                {"detail": "Token not found."},
                status=status.HTTP_404_NOT_FOUND
            )
