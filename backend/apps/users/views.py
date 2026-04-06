"""
User views for authentication and profile management.
"""
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.contrib.auth import get_user_model

from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    UserLocationUpdateSerializer,
    CustomTokenObtainPairSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    FCMTokenSerializer,
)

User = get_user_model()


@extend_schema(tags=['Authentication'])
class RegisterView(generics.CreateAPIView):
    """
    Register a new user account.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens for the new user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Registration successful. Please verify your email.'
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Authentication'])
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Login endpoint that returns JWT tokens and user info.
    """
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(tags=['Authentication'])
class LogoutView(APIView):
    """
    Logout by blacklisting the refresh token.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Users'])
class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update the current user's profile.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


@extend_schema(tags=['Users'])
class UserLocationUpdateView(APIView):
    """
    Update the current user's location.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = UserLocationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        request.user.update_location(
            latitude=serializer.validated_data['latitude'],
            longitude=serializer.validated_data['longitude']
        )
        
        return Response({
            'message': 'Location updated successfully.',
            'latitude': request.user.latitude,
            'longitude': request.user.longitude,
            'updated_at': request.user.last_location_update
        })


@extend_schema(tags=['Authentication'])
class PasswordChangeView(APIView):
    """
    Change the current user's password.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, 
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        
        return Response({'message': 'Password changed successfully.'})


@extend_schema(tags=['Authentication'])
class PasswordResetRequestView(APIView):
    """
    Request a password reset code via email.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email, is_active=True)
            from .services import send_password_reset_email
            send_password_reset_email(user)
        except User.DoesNotExist:
            pass  # Don't reveal whether email exists
        
        return Response({
            'message': 'If an account exists with this email, you will receive a reset code.'
        })


@extend_schema(tags=['Authentication'])
class PasswordResetConfirmView(APIView):
    """
    Confirm password reset with code.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['new_password']
        
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            return Response({'error': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)
        
        from .services import verify_otp
        if not verify_otp(user, code, verification_type='password_reset'):
            return Response({'error': 'Invalid or expired code.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password reset successful.'})


@extend_schema(tags=['Users'])
class FCMTokenUpdateView(APIView):
    """
    Update the user's FCM token for push notifications.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = FCMTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        request.user.fcm_token = serializer.validated_data['fcm_token']
        request.user.save(update_fields=['fcm_token'])
        
        return Response({'message': 'FCM token updated successfully.'})


@extend_schema(tags=['Users'])
class DeleteAccountView(APIView):
    """
    Soft delete the current user's account.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.is_active = False
        user.save(update_fields=['is_active'])
        
        return Response({
            'message': 'Account deactivated successfully.'
        }, status=status.HTTP_200_OK)
