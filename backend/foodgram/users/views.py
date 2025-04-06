from drf_yasg.utils import swagger_auto_schema
from .serializers import AvatarSerializer
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from .serializers import CustomAuthTokenSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class CustomAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_204_NO_CONTENT)
        except Token.DoesNotExist:
            return Response({"detail": "Token not found."}, status=status.HTTP_404_NOT_FOUND)


class AvatarView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AvatarSerializer

    @swagger_auto_schema(
        request_body=AvatarSerializer,
        responses={200: AvatarSerializer}
    )
    def put(self, request):
        user = request.user
        # partial=True позволяет обновлять только avatar
        serializer = AvatarSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
