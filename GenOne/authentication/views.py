# views.py
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.pagination import PageNumberPagination
from rest_framework import status


class LoginView(APIView):
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # Validate input
        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate user
        user = authenticate(username=username, password=password)
        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }, status=status.HTTP_200_OK)
