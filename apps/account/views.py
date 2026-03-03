from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.exceptions import ValidationError

# Create your views here.

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except ValidationError as e:
            custom_errors = {}
            for field, errors in e.detail.items():
                if field == 'email' and any(getattr(error, 'code', '') == 'unique' for error in errors):
                    custom_errors[field] = ["A user with this email already exists."]
                elif field == 'username' and any(getattr(error, 'code', '') == 'unique' for error in errors):
                    custom_errors[field] = ["A user with this username already exists."]
                else:
                    custom_errors[field] = [str(err) for err in errors]
            return Response(
                {"error": "Validation failed", "details": custom_errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "Internal server error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LoginView(TokenObtainPairView):
    queryset = User.objects.all()    
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(
                {"error": "Invalid credentials", "details": "Incorrect email or password, or account doesn't exist."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except TokenError as e:
            raise InvalidToken(e.args[0])
        except Exception as e:
            return Response(
                {"error": "Login failed", "details": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

