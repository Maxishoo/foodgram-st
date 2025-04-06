from django.urls import include, path
# from rest_framework.authtoken import views

from .views import CustomAuthToken, LogoutView, AvatarView

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/token/login/',
         CustomAuthToken.as_view(),
         name='token_login'),
    path('auth/token/logout/', LogoutView.as_view(), name='token_logout'),
    path('users/me/avatar/', AvatarView.as_view(), name='user-avatar'),
]
