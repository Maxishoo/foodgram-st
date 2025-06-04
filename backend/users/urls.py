from django.urls import include, path

from .views import (CustomAuthToken, LogoutView, AvatarView,
                    UserDetailView, UserListView, SubscriptionsView)

urlpatterns = [
    path('users/subscriptions/',
         SubscriptionsView.as_view(), name='subscriptions'),
    path('users/<int:id>/subscribe/',
         SubscriptionsView.as_view(), name='subscriptions_manager'),
    path('users/me/avatar/', AvatarView.as_view(), name='user_avatar'),

    path('', include('djoser.urls')),
    path('auth/token/login/',
         CustomAuthToken.as_view(),
         name='token_login'),
    path('auth/token/logout/', LogoutView.as_view(), name='token_logout'),
]
